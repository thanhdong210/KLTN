from odoo import fields, models, _

class HrContractTypeInherit(models.Model):
    _name = "hr.timesheet.line"
    
    name = fields.Char(string="Name")
    employee_id = fields.Many2one("hr.employee", string="Employee")
    date = fields.Date(string="Date")
    timesheet_id = fields.Many2one("hr.timesheet", string="Timesheet", ondelete='cascade')
    number_of_hours = fields.Float(string="Number of hour")
    number_of_days = fields.Float(string="Number of day")
    timesheet_type_id = fields.Many2one('hr.timesheet.type', string="Timesheet Type")
    code = fields.Char(string="Code")
    hour_from = fields.Datetime(string="Hour from")
    hour_to = fields.Datetime(string="Hour to")
    


    
    

    
    



    

    


    


