from odoo import fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import timedelta, datetime, time

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

    def action_confirm(self):
        for rec in self:
            rec.write({
                'state': 'confirmed'
            })

    def action_compute_sheet(self):
        self.timesheet_line_ids.unlink()
        self._create_timesheet_line()
        self.compute_worked_day()

    def _create_timesheet_line(self):
        datas_attendance = self.create_attendance_data()
        timesheet_line = self.env['hr.timesheet.line']
        list_data = []
        for data in datas_attendance.items():
            vals = {
                'date': data[1].get("date", False),
                'number_of_hours': data[1].get("number_of_hour", 0),
                'timesheet_type_id': data[1].get("timesheet_type_id", False).id,
                'timesheet_id': self.id,
                'code': data[1].get("code", ""),
                'hour_from':  data[1].get("hour_from", False),
                'hour_to': data[1].get("hour_to", False),
            }
            self.filter_timesheet_line(self.employee_id.contract_id, self.employee_id.contract_id.resource_calendar_id, vals)
            timesheet_line.create(vals)
            # list_data.append(vals)

        # datas = {}
        # for data_line in list_data:
        #     date_date = datas.setdefault(data_line.get("date", False), {
        #         'date': data_line.get("date", False),
        #         'number_of_hours': 0.0,
        #         'number_of_days': 0.0,
        #         'timesheet_type_id': data_line.get("timesheet_type_id", False),
        #         'code': data_line.get("code", False),
        #         'timesheet_id': data_line.get("timesheet_id", False),
        #     })

        #     date_date['number_of_hours'] += data_line.get("number_of_hour", 0.0)
        #     date_date['number_of_days'] += data_line.get("number_of_days", 0.0)

        # for data in datas.items():
        #     print("==============", data[1])
        #     timesheet_line.create(data[1])
        

    def filter_timesheet_line(self, contract, calendar, vals):
        intervals = contract.resource_calendar_id.attendance_ids.filtered(lambda x: int(x.dayofweek) == vals.get("hour_from", False).weekday())
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
                    vals['number_of_days'] = 0.5

    def compute_worked_day(self):
        for rec in self:
            data = {}
            # for line in rec.timesheet_line_ids:
            #     data_line = data.setdefault(line.get('timesheet_type_id', False), {
            #         'timesheet_type_id': line.get('timesheet_type_id', False),
            #         'number_of_hour': 0.0
            #     })
            pass

    def action_draft(self):
        datas = self.env['hr.timesheet.line'].search([
            ('timesheet_id', '=', self.id)
        ])

        for data in datas:
            data.unlink()

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
    
    

    
    



    

    


    


