from odoo import fields, models, _

class HrWorkedLine(models.Model):
    _name = "hr.worked.line"
    
    name = fields.Char(string="Name")
    employee_id = fields.Many2one("hr.employee", string="Employee")
    timesheet_id = fields.Many2one("hr.timesheet", string="Timesheet", ondelete='cascade')
    number_of_hour = fields.Float(string="Number of hour")
    number_of_day = fields.Float(string="Number of day")
    timesheet_type_id = fields.Many2one('hr.timesheet.type', string="Timesheet Type")
    code = fields.Char(string="Code")
    


    
    

    
    



    

    


    


