from odoo import fields, models, api, _, tools
import babel
from datetime import datetime, time
from num2words import num2words

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
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, readonly=True)
    wage = fields.Monetary(related='contract_id.wage', store=True, string="Wage", currency_field="currency_id")
    real_wage = fields.Monetary(string="Real Wage", store=True, compute="_compute_real_wage", currency_field="currency_id")
    base_worked_day = fields.Float(string="Base worked day")
    real_worked_day = fields.Float(string="Real worked day")
    is_standard_line = fields.Boolean(string="Standard line")
    benefit_ids = fields.Many2many('hr.benefit', string="Benefit")
    total_benefit = fields.Monetary(string="Total benefit", compute="_compute_total_benefit", store=True)
    take_home_pay = fields.Monetary(string="Take-Home Pay", compute="_compute_take_home_pay", store=True)
    take_home_pay_word = fields.Char(string="Take-Home Pay Word", compute="_compute_take_home_pay")

    @api.depends("real_wage", "total_benefit")
    def _compute_take_home_pay(self):
        for rec in self:
            if rec.real_wage and rec.total_benefit:
                rec.take_home_pay = rec.real_wage + rec.total_benefit
                rec.take_home_pay_word = num2words((rec.real_wage + rec.total_benefit), lang='vi_VN')
            else:
                rec.total_benefit = 0

    @api.depends("benefit_ids")
    def _compute_total_benefit(self):
        for rec in self:
            if rec.benefit_ids:
                total_benefit = 0
                for benefit in rec.benefit_ids:
                    total_benefit += benefit.price
                rec.total_benefit = total_benefit
            else:
                rec.total_benefit = 0
    
    @api.depends("wage", "real_worked_day", "base_worked_day")
    def _compute_real_wage(self):
        for rec in self:
            if rec.wage and rec.base_worked_day and rec.real_worked_day:
                rec.real_wage = round(rec.real_worked_day * rec.wage / rec.base_worked_day, 2)
            else:
                rec.real_wage = 0

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
        employee = self.employee_id
        self.worked_line_ids.unlink()
        employee_timesheet = self.env['hr.timesheet'].search([('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to), ('employee_id', '=', employee.id)])
        data = {
            'employee_id': employee.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'contract_id': employee.contract_id.id,
            'department_id': employee.department_id.id,
            'job_id': employee.job_id.id,
            'company_id': employee.company_id.id,
            'timesheet_id': employee_timesheet.id or False,
            'real_worked_day': employee_timesheet.total_day,
            'benefit_ids':employee.contract_id.benefit_ids
        }
        
        worked_day_data = employee.compute_worked_day_data(self.date_from)
        timesheet_type_id = self.env['ir.model.data']._xmlid_to_res_id('kltn.work_day_rule_timesheet_type')
        timesheet_type = self.env['hr.timesheet.type'].browse(timesheet_type_id)
        worked_day_line_origin = [(0, 0, {
            'number_of_hours': worked_day_data.get("number_of_hours", 0),
            'number_of_days': worked_day_data.get("number_of_days", 0),
            'timesheet_type_id': timesheet_type_id,
            'code': timesheet_type.code,
            'is_standard_line': True
        })]

        for worked_line in employee_timesheet.worked_line_ids:
            worked_line_data = [(0, 0, {
                'number_of_hours': worked_line.number_of_hours,
                'number_of_days': worked_line.number_of_days,
                'timesheet_type_id': worked_line.timesheet_type_id.id,
                'code': worked_line.timesheet_type_id.code,
            })]
            worked_day_line_origin += worked_line_data

        data.update({
            "worked_line_ids": worked_day_line_origin
        })

        self.write(data)

        return data

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
