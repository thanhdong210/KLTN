from odoo import fields, models, _

class HrContractTypeInherit(models.Model):
    _name = "hr.timesheet"
    
    name = fields.Char(string="Name")
    employee_id = fields.Many2one("hr.employee", string="Employee")
    date_from = fields.Date(string="Date from")
    date_to = fields.Date(string="Date to")
    description = fields.Char(string="Description")
    timesheet_line_ids = fields.Many2one("hr.timesheet.line", string="Details", compute="_compute_timesheet_line")
    
    
    

    
    



    

    


    


