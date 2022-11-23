from odoo import fields, models, api, _, tools
import babel
from datetime import datetime, time

class HrPayroll(models.Model):
    _name = "hr.payroll"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string="Name")
    employee_id = fields.Many2one('hr.employee', string='Employee')
    date_from = fields.Date(string="Date from")
    date_to = fields.Date(string="Date to")
    department_id = fields.Many2one('hr.department', string="Department")
    job_id = fields.Many2one('hr.job', string="Job")
    contract_id = fields.Many2one('hr.contract', string="Contract")
    is_paid = fields.Boolean(string="Is paid")
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('confirmed', 'To Approve'),
        ('paid', 'Paid'),
    ], string='Status', store=True, tracking=True, copy=False, readonly=False, default="draft")
    worked_line_ids = fields.One2many('hr.worked.line', 'payroll_id', string="Worked Line")
    contract_id = fields.Many2one('hr.contract', string="Contract")
    payroll_run_id = fields.Many2one('hr.payroll.run', string="Payroll Run")
    company_id = fields.Many2one('res.company', string="Company")
    timesheet_id = fields.Many2one('hr.timesheet', string="Timesheet")

    def action_confirm(self):
        for rec in self:
            rec.write({
                'state': 'confirmed'
            })

    def action_draft(self):
        self.worked_line_ids.unlink()

        self.write({
            'state': 'draft'
        })

    def action_paid(self):
        self.worked_line_ids.unlink()

        self.write({
            'state': 'paid'
        })

    def action_compute_payroll(self):
        pass

    @api.onchange('employee_id', 'date_from')
    def onchange_payroll_name(self):
        for rec in self:
            if (not rec.employee_id) or (not rec.date_from) or (not rec.date_to):
                return
            employee = self.employee_id
            date_from = self.date_from
            ttyme = datetime.combine(fields.Date.from_string(date_from), time.min)
            locale = self.env.context.get('lang') or 'en_US'
            self.name = _('Payroll of %s for %s') % (employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))

    def unlink(self):
        if self.worked_line_ids:
            self.worked_line_ids.unlink()
        return super().unlink()

