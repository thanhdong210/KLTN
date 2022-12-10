from odoo import fields, models, _, api
from dateutil.relativedelta import relativedelta
from datetime import timedelta, datetime, time
from pytz import timezone, UTC
from odoo.addons.kltn.models import common
import math

class HrContractTypeInherit(models.Model):
    _name = "hr.timesheet"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string="Name")
    employee_id = fields.Many2one("hr.employee", string="Employee")
    date_from = fields.Date(string="Date from")
    date_to = fields.Date(string="Date to")
    description = fields.Char(string="Description")
    timesheet_line_ids = fields.One2many("hr.timesheet.line", 'timesheet_id', string="Details")
    worked_line_ids = fields.One2many("hr.worked.line", 'timesheet_id', string="Worked Line")
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('confirmed', 'To Approve'),
    ], string='Status', store=True, tracking=True, copy=False, readonly=False, default="draft")
    show_button_confirm = fields.Boolean()
    total_day = fields.Float(string="Total Day", compute="_compute_total_day", store=True)

    @api.depends("worked_line_ids")
    def _compute_total_day(self):
        for rec in self:
            if rec.worked_line_ids:
                total_day = sum(rec.worked_line_ids.mapped("number_of_days"))
                rec.total_day = total_day
            else:
                self.total_day = 0

    def action_confirm(self):
        for rec in self:
            rec.write({
                'state': 'confirmed'
            })

    def action_compute_sheet(self):
        self.get_overtime_data()
        self.get_leave_data()
        self.timesheet_line_ids.unlink()
        self.worked_line_ids.unlink()
        self._create_timesheet_line()
        self.compute_worked_day()

    # def get_employee_intervals_filter(self, employee, date):

    def get_employee_intervals(self, employee, date):
        return employee.contract_id.resource_calendar_id.attendance_ids.filtered(lambda x: int(x.dayofweek) == date.weekday()).sorted(key=lambda x: x.hour_from)

    def _create_timesheet_line(self):
        datas_attendance = self.create_attendance_data()
        datas_leave = self.get_leave_data()
        datas_overtime = self.get_overtime_data()
        timesheet_line = self.env['hr.timesheet.line']
        list_data = []
        
        for data in datas_attendance.items():
            intervals = self.get_employee_intervals(self.employee_id, data[1].get("hour_from", False))
            hour_from_interval = intervals.mapped("hour_from")
            hour_to_interval = intervals.mapped("hour_to")

            if (data[1].get("hour_from", False).hour + 7) < min(hour_to_interval) and (data[1].get("hour_to", False).hour + 7) > max(hour_from_interval):
                number_of_hour_morning = min(hour_to_interval) - (data[1].get("hour_from", False).hour + 7)
                vals1 = {
                    'date': data[1].get("date", False),
                    'number_of_hours': number_of_hour_morning,
                    'timesheet_type_id': data[1].get("timesheet_type_id", False).id,
                    'timesheet_id': self.id,
                    'code': data[1].get("code", ""),
                    'hour_from':  data[1].get("hour_from", False),
                    'hour_to': datetime.combine(data[1].get("hour_from", False).date(), (datetime.min + timedelta(hours=min(hour_to_interval) - 7)).time()),
                    'day_state': 'morning'
                }
                list_data.append(vals1)
                number_of_hour_afternoon = (data[1].get("hour_to", False).hour + 7) - max(hour_from_interval)
                vals2 = {
                    'date': data[1].get("date", False),
                    'number_of_hours': number_of_hour_afternoon,
                    'timesheet_type_id': data[1].get("timesheet_type_id", False).id,
                    'timesheet_id': self.id,
                    'code': data[1].get("code", ""),
                    'hour_from': datetime.combine(data[1].get("hour_from", False).date(), (datetime.min + timedelta(hours=max(hour_from_interval) - 7)).time()),
                    'hour_to':  data[1].get("hour_to", False),
                    'day_state': 'afternoon'
                }
                list_data.append(vals2)
            else: 
                vals = {
                    'date': data[1].get("date", False),
                    'number_of_hours': data[1].get("number_of_hour", 0),
                    'timesheet_type_id': data[1].get("timesheet_type_id", False).id,
                    'timesheet_id': self.id,
                    'code': data[1].get("code", ""),
                    'hour_from':  data[1].get("hour_from", False),
                    'hour_to': data[1].get("hour_to", False),
                }
                if vals['hour_from'].hour + 7 <= 12:
                    vals.update({
                        'day_state': 'morning'
                    })
                elif vals['hour_from'].hour + 7 > 12:
                    vals.update({
                        'day_state': 'afternoon'
                    })
                list_data.append(vals)

        for data in datas_leave:
            list_data.append(data)

        for data in datas_overtime:
            list_data.append(data)

        if list_data:
            for vals in list_data:
                self.filter_timesheet_line(self.employee_id.contract_id.resource_calendar_id, intervals, vals)
                timesheet_line.create(vals)
        

    def filter_timesheet_line(self, calendar, intervals, vals):
        from_datetime = datetime.combine(vals.get("hour_from", False), datetime.min.time())
        reality_hours_count = 0
        expect_hours_count = 0
        
        if self.employee_id.contract_id and self.employee_id.contract_id.resource_calendar_id.mode == 'begin_end_time':
            if intervals:
                for idx, item in enumerate(intervals):
                    
                    calendar_date_start = from_datetime + relativedelta(hours=item.hour_from - 7 + (idx == 0 and calendar.hour_late or 0))
                    calendar_date_end = from_datetime + relativedelta(hours=item.hour_to - 7 - ((idx == len(intervals) -1) and calendar.hour_soon or 0))
                    in_sooner = vals.get("hour_from", False) <= calendar_date_start
                    out_later = vals.get("hour_to", False) >= calendar_date_end
                    expect_hours_count += (item.hour_to - item.hour_from)
                    
                    if (in_sooner and out_later):
                        reality_hours_count += (item.hour_to - item.hour_from)
                number_of_days = 0
                if reality_hours_count:
                    number_of_days += reality_hours_count/expect_hours_count
                if number_of_days:
                    vals['number_of_days'] = number_of_days

    def compute_worked_day(self):
        for rec in self:
            worked_days = []
            data = {}
            for line in rec.timesheet_line_ids:
                data_line = data.setdefault(line.timesheet_type_id, {
                    'timesheet_type_id': line.timesheet_type_id.id,
                    'number_of_hours': 0.0,
                    'number_of_days': 0.0,
                    'timesheet_id': line.timesheet_id.id,
                    'code': line.code,
                    'date': line.date,
                })

                data_line['number_of_hours'] += line.number_of_hours
                data_line['number_of_days'] += line.number_of_days
            for val in data.values():
                worked_days.append(val)

            for worked_day in worked_days:
                rec.worked_line_ids.create(worked_day)


    def action_draft(self):
        datas = self.env['hr.timesheet.line'].search([
            ('timesheet_id', '=', self.id)
        ])

        for data in datas:
            data.unlink()

        self.worked_line_ids.unlink()

        self.write({
            'state': 'draft'
        })

    def create_attendance_data(self):
        datas_attendance = self.env['hr.attendance.data'].search([
            ('employee_id', '=', self.employee_id.id),
            ('check_in_date', '>=', self.date_from),
            ('check_out_date', '<=', self.date_to)
        ])

        data = {}
        for data_attendance in datas_attendance:
            date_date = data.setdefault(data_attendance.id, {
                'date': data_attendance.check_in_date,
                'number_of_hour': 0.0,
                'timesheet_type_id': data_attendance.timesheet_type_id,
                'code': data_attendance.timesheet_type_id.code,
                'hour_from': data_attendance.check_in,
                'hour_to': data_attendance.check_out,
            })

            date_date['number_of_hour'] += data_attendance.number_of_hour
        return data

    def get_leave_data(self):
        # leave_type_for_compute = self.env['ir.config_parameter'].sudo().get_param('leave_type_for_compute')
        # if leave_type_for_compute:
        #     leave_type_for_compute = leave_type_for_compute.split(',')
        datas_leave = self.env['hr.leave.inherit'].search([
            ('employee_id', '=', self.employee_id.id),
            ('date_from', '>=', self.date_from),
            ('date_to', '<=', self.date_to),
            ('state', '=', 'validated'),
        ])
        
        leave_data_list = []
        for data in datas_leave:
            leave_data = {}
            if data.is_half_day:
                leave_data = {
                    'timesheet_id': self.id,
                    'date': data.date_from,
                    'timesheet_type_id': data.leave_type_id.timesheet_type_id.id,
                    'code': data.leave_type_id.timesheet_type_id.code,
                }
                if data.is_half_selection == 'morning':
                    interval_data = self.get_employee_intervals(data.employee_id, data.date_from)
                    interval = interval_data.filtered(lambda x: x.day_period == 'morning')
                    check_in = datetime.combine(data.date_from, time(int(interval.hour_from), 0, 0))
                    check_out = datetime.combine(data.date_from, time(int(interval.hour_to), 0, 0))

                    leave_data.update({
                        'hour_from': check_in,
                        'hour_to': check_out,
                        'number_of_hours': interval.hour_to - interval.hour_from,
                        'number_of_days': 0.5,
                        'day_state': 'morning'
                    })
                elif data.is_half_selection == 'afternoon':
                    interval_data = self.get_employee_intervals(data.employee_id, data.date_from)
                    interval = interval_data.filtered(lambda x: x.day_period == 'afternoon')
                    check_in = datetime.combine(data.date_from, time(int(interval.hour_from), 0, 0))
                    check_out = datetime.combine(data.date_from, time(int(interval.hour_to), 0, 0))
                    
                    leave_data.update({
                        'hour_from': check_in,
                        'hour_to': check_out,
                        'number_of_hours': interval.hour_to - interval.hour_from,
                        'number_of_days': 0.5,
                        'day_state': 'afternoon'
                    })
                leave_data_list.append(leave_data)
            else:
                for dt in common.daterange(data.date_from, data.date_to):
                    interval_data = self.get_employee_intervals(data.employee_id, dt)
                    for interval in interval_data:
                        check_in = datetime.combine(dt, time(int(interval.hour_from) - 7, 0, 0))
                        check_out = datetime.combine(dt, time(int(interval.hour_to) - 7, 0, 0))
                        leave_data = {
                            'timesheet_id': self.id,
                            'date': dt,
                            'timesheet_type_id': data.leave_type_id.timesheet_type_id.id,
                            'code': data.leave_type_id.timesheet_type_id.code,
                            'hour_from': check_in,
                            'hour_to': check_out,
                            'number_of_hours': interval.hour_to - interval.hour_from,
                            'number_of_days': 0.5,
                        }
                        if interval.hour_from <= 12 and interval.hour_to <= 12:
                            leave_data.update({
                                'day_state': 'morning'
                            })
                        else:
                            leave_data.update({
                                'day_state': 'afternoon'
                            })
                        leave_data_list.append(leave_data)
        return leave_data_list

    def get_overtime_data(self):
        overtime_datas = self.env['hr.overtime.request'].search_read([
            ('employee_id', '=', self.employee_id.id),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('state', '=', 'validated'),
        ], ['date', 'employee_id', 'timesheet_type_id', 'request_hour_from', 'request_hour_to', 'number_of_hours'])

        list_data = []

        for data in overtime_datas:
            timesheet_type = self.env['hr.timesheet.type'].browse(data.get("timesheet_type_id")[0])
            frac_from, whole_from = math.modf(float(data.get('request_hour_from')))
            frac_to, whole_to = math.modf(float(data.get('request_hour_to')))

            hour_from = int(whole_from) - 7
            hour_to = int(whole_to) - 7
            from_date = data.get('date')
            to_date = data.get('date')
            if hour_from < 0:
                hour_from += 24
                from_date -= timedelta(days=1)

            if hour_to < 0:
                hour_to += 24 
                to_date -= timedelta(days=1)

            date_from = datetime.combine(from_date, time(hour_from, int(60 * frac_from), 0))
            date_to = datetime.combine(to_date, time(hour_to, int(60 * frac_to), 0))
            data_dict = {
                'timesheet_id': self.id,
                'date': data.get("date", False),
                'timesheet_type_id': timesheet_type.id,
                'code': timesheet_type.code,
                'hour_from': date_from,
                'hour_to': date_to,
                'number_of_hours': data.get('number_of_hours', 0),
                'number_of_days': 0,
            }

            list_data.append(data_dict)
        
        return list_data
    

    
    



    

    


    


