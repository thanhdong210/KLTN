from odoo import fields, models, _

class HrContractTypeInherit(models.Model):
    _name = "hr.attendance.request.type"
    
    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    is_second_approve = fields.Char(string="Second Approve")
    

    
    

    
    



    

    


    


