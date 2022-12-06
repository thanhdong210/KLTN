from odoo import fields, models, _

class HrWorkedLine(models.Model):
    _name = "hr.worked.line"
    
    name = fields.Char(string="Name")
    employee_id = fields.Many2one("hr.employee", string="Employee")
    timesheet_id = fields.Many2one("hr.timesheet", string="Timesheet", ondelete='cascade')
    number_of_hours = fields.Float(string="Number of hour")
    number_of_days = fields.Float(string="Number of day")
    timesheet_type_id = fields.Many2one('hr.timesheet.type', string="Timesheet Type")
    code = fields.Char(string="Code")
    date = fields.Date(string="Date")
    payroll_id = fields.Many2one('hr.payroll', string="Payroll")
    contract_id = fields.Many2one('hr.contract', string="Contract")
    is_standard_line = fields.Boolean(string="Standard line")
    


    
    

    
    



    

    


    


