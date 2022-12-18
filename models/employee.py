from odoo import api, fields, models, tools, _, exceptions
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, timedelta
import calendar
from . import common
from datetime import time
import math
from pytz import timezone
import pytz
from odoo.addons.kltn.models import common
from dateutil.relativedelta import relativedelta


class HrEmployeeInherit(models.Model):
    _inherit = "hr.employee"

    trigger_compute_total_leave = fields.Boolean("Triger Total Leave")
    total_leaves = fields.Float(string="Total Leaves", compute="_compute_total_leaves", store=True)
    contract_type_id = fields.Many2one('hr.contract.type', related='contract_id.contract_type_id', string="Contract Type", store=True)
    leave_taken = fields.Float(string="Leave Taken", default=0)
    code = fields.Char(string="Code")

    @api.depends("trigger_compute_total_leave")
    def _compute_total_leaves(self):
        for rec in self:
            print("=================hhahdasjdbasdb")
            leave_type_for_compute = rec.env['ir.config_parameter'].sudo(
            ).get_param('leave_type_for_compute')
            if leave_type_for_compute:
                leave_type_for_compute = leave_type_for_compute.split(',')
            total_leaves = rec.env['hr.leave.allocation.inherit'].search([
                ('employee_id', '=', rec.id),
                ('state', '=', 'validate'),
                ('timesheet_code', 'in', leave_type_for_compute),
                ('is_child', '=', True),
            ])
            
            total = 0
            for data in total_leaves:
                total += data.number_of_day
            rec.write({
                'total_leaves': total
            })

    def action_employee_test(self):
        mail_template = self.env.ref("kltn.mail_template_employee_test")
        mail_template.sudo().send_mail(self.id, force_send=True)

    def get_detail_employee(self):
        data = {}
        date_from = datetime(datetime.now().year, datetime.now().month, 1)
        date_to = datetime(datetime.now().year, datetime.now().month, calendar.monthrange(
            datetime.now().year, datetime.now().month)[1])

        attendance_data = self.env['hr.attendance'].search([
            ("employee_id", "=", self.env.user.employee_id.id),
            '&',
            ("check_in", ">=", date_from),
            ("check_in", "<=", date_to)
        ])

        attendance_date = attendance_data.mapped("check_in_date")
        attendance_date_data = list(dict.fromkeys(attendance_date))

        attendance_request_data = self.env['hr.attendance.request'].search([
            ("employee_id", "=", self.env.user.employee_id.id),
            '&',
            ("date_from", ">=", date_from),
            ("date_from", "<=", date_to)
        ])

        businesstrip_data = self.env['hr.attendance.request'].search([
            ("employee_id", "=", self.env.user.employee_id.id),
            '&',
            ("date_from", ">=", date_from),
            ("date_from", "<=", date_to),
            ("attendance_option", "=", 'business_trip'),
            ("state", "=", 'validate')
        ])

        number_of_day_businesstrip = 0
        for data in businesstrip_data:
            number_of_day_businesstrip += data.number_of_days

        leave_data = self.env['hr.leave.inherit'].search([
            ("employee_id", "=", self.env.user.employee_id.id),
            '&',
            ("date_from", ">=", date_from),
            ("date_from", "<=", date_to),
            ("state", "=", 'validated')
        ])

        total_day = sum(leave_data.mapped("number_of_days"))

        overtime_data = self.env['hr.overtime.request'].search([
            ("employee_id", "=", self.env.user.employee_id.id),
            '&',
            ("date", ">=", date_from),
            ("date", "<=", date_to),
            ("state", "=", 'validated')
        ])

        number_of_hour_overtime = 0
        for data in overtime_data:
            number_of_hour_overtime += data.number_of_hours

        employee = self.search([('user_id', '=', self._uid)], limit=1)

        result = self.search_read([('parent_id', '=', employee.id)], [
                                  'id', 'name', 'code', 'department_id', 'job_title', 'work_email', 'work_phone'])

        member_ids = []
        for emp in result:
            member_ids.append(emp.get('id'))

        attendance_request_to_approve = self.env['hr.attendance.request'].search([
            ('target', '=', 'employee'),
            ('state', 'in', ['approve']),
            ('employee_id', 'in', member_ids),
            ('attendance_option', '=', 'attendance_request'),
        ]).ids

        business_trip_to_approve = self.env['hr.attendance.request'].search([
            ('target', '=', 'employee'),
            ('state', 'in', ['approve']),
            ('employee_id', 'in', member_ids),
            ('attendance_option', '=', 'business_trip'),
        ]).ids

        leave_request_to_approve = self.env['hr.leave.inherit'].search([
            ('target', '=', 'employee'),
            ('state', 'in', ['approve']),
            ('employee_id', 'in', member_ids),
        ]).ids

        overtime_request_to_approve = self.env['hr.overtime.request'].search([
            ('target', '=', 'employee'),
            ('state', 'in', ['approve']),
            ('employee_id', 'in', member_ids),
        ]).ids

        employee = self.search_read([('user_id', '=', self.env.user.id)], [
                                    'id', 'name', 'code', 'department_id', 'job_title', 'work_email', 'work_phone'], limit=1)

        employee_id = self.search([
            ('user_id', '=', self.env.user.id)
        ])

        base_worked_day = employee_id.compute_worked_day_data(fields.Date.today())

        data = {
            'base_worked_day': base_worked_day.get("number_of_days", 0),
            "attendance_count": len(attendance_date_data),
            "attendance_request_count": len(attendance_request_data),
            "leave_count": total_day,
            "total_leaves": employee_id.total_leaves,
            "overtime_count": len(overtime_data),
            "overtime_hour_count": number_of_hour_overtime,
            "businesstrip_count": len(businesstrip_data),
            "businesstrip_days_count": float(number_of_day_businesstrip),
            "team_member": result,
            "member_ids": member_ids,
            "attendance_request_to_approve": len(attendance_request_to_approve),
            "attendance_request_to_approve_ids": attendance_request_to_approve,
            "business_trip_to_approve": len(business_trip_to_approve),
            "business_trip_to_approve_ids": business_trip_to_approve,
            "leave_request_to_approve": len(leave_request_to_approve),
            "leave_request_to_approve_ids": leave_request_to_approve,
            "overtime_request_to_approve": len(overtime_request_to_approve),
            "overtime_request_to_approve_ids": overtime_request_to_approve,
            "employee": employee
        }
        return [data]

    # def write(self, vals):
    #     for rec in self:
    #         leave_type_for_compute = rec.env['ir.config_parameter'].sudo().get_param('leave_type_for_compute')
    #         if leave_type_for_compute:
    #             leave_type_for_compute = leave_type_for_compute.split(',')
    #         total_leaves = rec.env['hr.leave.allocation.inherit'].search([
    #             ('employee_id', '=', rec.id),
    #             ('state', '=', 'validate'),
    #             ('leave_type_code', 'in', leave_type_for_compute),
    #             ('is_child', '=', True),
    #         ])

    #         total = 0
    #         for data in total_leaves:
    #             total += data.number_of_day
    #         vals['total_leaves'] = total
    #         return super(HrEmployeeInherit, rec).write(vals)

    def _get_employee_resource_calendar(self, date_from, date_to, is_half=False):
        # TODO check if date_from and date_to is in attendance_ids
        # local = pytz.timezone(str(self.env.user.tz))
        local = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
        if date_from and date_to:
            list_data = []
            for dt in common.daterange(date_from, date_to):
                for attendance in self.contract_id.resource_calendar_id.attendance_ids:
                    if int(attendance.dayofweek) == int(dt.weekday()):
                        check_in = datetime.combine(dt, time(hour=math.floor(
                            attendance.hour_from), minute=int(math.modf(attendance.hour_from)[0]*60)))
                        check_out = datetime.combine(dt, time(hour=math.floor(
                            attendance.hour_to), minute=int(math.modf(attendance.hour_to)[0]*60)))

                        check_in_data = check_in - timedelta(hours=7)
                        check_out_data = check_out - timedelta(hours=7)
                        value = {
                            'employee_id': self.id,
                            'check_in': check_in_data,
                            'check_out': check_out_data
                        }
                        list_data.append(value)
            return list_data
        if date_from and is_half:
            list_data = []
            for attendance in self.contract_id.resource_calendar_id.attendance_ids:
                if int(attendance.dayofweek) == int(date_from.weekday()):
                    check_in_data = datetime.combine(date_from, time(hour=math.floor(
                        attendance.hour_from), minute=int(math.modf(attendance.hour_from)[0]*60)))
                    check_out_data = datetime.combine(date_from, time(hour=math.floor(
                        attendance.hour_to), minute=int(math.modf(attendance.hour_to)[0]*60)))

                    # check_in = pytz.utc.localize(check_in_data).astimezone('utc').replace(tzinfo=None)
                    # check_out = pytz.utc.localize(check_out_data).astimezone('utc').replace(tzinfo=None)

                    check_in_data = check_in_data - timedelta(hours=7)
                    check_out_data = check_out_data - timedelta(hours=7)
                    value = {
                        'employee_id': self.id,
                        'check_in': check_in_data,
                        'check_out': check_out_data
                    }
                    list_data.append(value)
            return list_data

    def compute_worked_day_data(self, date):
        employee_calendar = self.contract_id.resource_calendar_id
        days = common.compute_days_in_month(date.year, date.month)
        avai_day_in_week = employee_calendar.attendance_ids.mapped('dayofweek')
        avai_day_in_week_value = list(dict.fromkeys(avai_day_in_week))
        number_of_days = 0
        number_of_hours = 0
        data = {}
        
        for day in days:
            if str(day.weekday()) in avai_day_in_week_value:
                number_of_days += 1
                number_of_hours += employee_calendar.hours_per_day

        data.update({
            'number_of_days': number_of_days,
            'number_of_hours': number_of_hours,
        })

        return data

    def _attendance_action_change(self):
        """ Check In/Check Out action
            Check In: create a new attendance record
            Check Out: modify check_out field of appropriate attendance record
        """
        self.ensure_one()
        action_date = fields.Datetime.now()

        timesheet_type_id = self.env['ir.model.data']._xmlid_to_res_id('kltn.work_day_rule_timesheet_type')

        if self.attendance_state != 'checked_in':
            vals = {
                'employee_id': self.id,
                'check_in': action_date,
                'timesheet_type_id': timesheet_type_id
            }
            return self.env['hr.attendance'].create(vals)
        attendance = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('check_out', '=', False)], limit=1)
        if attendance:
            attendance.check_out = action_date
        else:
            raise exceptions.UserError(_('Cannot perform check out on %(empl_name)s, could not find corresponding check in. '
                'Your attendances have probably been modified manually by human resources.') % {'empl_name': self.sudo().name, })
        return attendance
