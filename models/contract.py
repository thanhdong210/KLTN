from odoo import fields, models, _

class HrContractTypeInherit(models.Model):
    _inherit = "hr.contract.type"
    
    active = fields.Boolean(string="Active", default=True)
    code = fields.Char(string="Contract code")

class HrContractInherit(models.Model):
    _inherit = "hr.contract"

    benefit_ids = fields.Many2many('hr.benefit', string="Benefit")
    
    

    
    



    

    


    


