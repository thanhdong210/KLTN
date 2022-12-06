from odoo import api, fields, models, tools, _

class HrBenefit(models.Model):
    _name = "hr.benefit"
    
    name = fields.Char("Name")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, readonly=True)
    price = fields.Monetary("Price", currency_field="currency_id")
