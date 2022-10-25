from dataclasses import dataclass
from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError

class HrAttendanceData(models.Model):
    _name = "hr.attendance.data"

    name = fields.Char(string="Name")
    check_in = fields.Datetime(string="Check in")
    check_out = fields.Datetime(string="Check out")
    check_in_display = fields.Datetime(string="Check in")
    check_out_display = fields.Datetime(string="Check in")
    check_out = fields.Datetime(string="Check out")
    check_in_date = fields.Date(string="Check in date", compute="_compute_date")
    check_out_date = fields.Date(string="Check out date", compute="_compute_date")
    timesheet_type_id = fields.Many2one('hr.timesheet.type', string="Timesheet Type")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    attendance_request_id = fields.Many2one('hr.attendance.request')
    number_of_hour = fields.Float(string="Number of hour", compute="_compute_number_of_hour")

    @api.depends("check_in", "check_out")
    def _compute_number_of_hour(self):
        for rec in self:
            diff = rec.check_out - rec.check_in
            diff_in_hours = diff.total_seconds() / 3600
            rec.number_of_hour = float(diff_in_hours)

    @api.depends('check_in', 'check_out')
    def _compute_date(self):
        for rec in self:
            rec.check_in_date = rec.check_in.date()
            rec.check_out_date = rec.check_out.date()