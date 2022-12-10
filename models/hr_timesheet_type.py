from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError

class HrTimesheetType(models.Model):
    _name = "hr.timesheet.type"

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    mode = fields.Selection([
        ('leave', 'Leave'),
        ('attendance', 'Attendance'),
        ('attendance_request', 'Attendance Request'),
        ('business_trip', 'Business Trip'),
    ], string='Mode', tracking=True, copy=False, readonly=False)