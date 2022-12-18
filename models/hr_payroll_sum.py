from odoo import fields, models, api, _, tools
import babel
from datetime import datetime, time
from odoo.exceptions import ValidationError

class HrPayrollSum(models.Model):
    _name = "hr.payroll.sum"

    amount = fields.Monetary(string="Cost", currency_field="currency_id")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, readonly=True)
    date_from = fields.Date(string="Date_from", required="1")
    date_to = fields.Date(string="Date To", required="1")
    month = fields.Integer(string="Month")

    @api.constrains
    def _check_date_from_date_to(self):
        if self.date_to < self.date_from:
            raise ValidationError("Date from can't greater than date to")

    @api.onchange("date_from")
    def onchange_month(self):
        for rec in self:
            if rec.date_from:
                rec.month = rec.date_from.month

    @api.model
    def create(self, vals):
        payroll_sum = self.search([
            ('date_from', '=', vals['date_from']),
            ('date_to', '=', vals['date_to']),
        ])
        payroll = self.env['hr.payroll'].search([
            ('date_from', '=', vals['date_from']),
            ('date_to', '=', vals['date_to']),
        ])
        if not payroll:
            raise ValidationError("Can't find any payroll in this range")
        if payroll_sum:
            payroll_sum.unlink()
        return super(HrPayrollSum, self).create(vals)

    def compute_salary_by_year(self):
        data = self.env['hr.payroll'].read_group(
                    domain=[('date_from', '=', self.date_from), ('date_to', '=', self.date_to)],
                    fields=['take_home_pay', 'date_from'],
                    groupby=['date_from'],
                )
        if data:
            self.amount = data[0].get("take_home_pay", False)
        else:
            raise ValidationError("Can't find any payroll in this range")
