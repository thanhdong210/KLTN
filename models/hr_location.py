from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

class HrLocation(models.Model):
    _name = "hr.location"
    _description = "Location"
    
    city = fields.Char(string="City")
    district = fields.Char(string="District")
    address = fields.Char(string="Address")
        

    
    

    
    



    

    


    


