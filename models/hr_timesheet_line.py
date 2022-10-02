from odoo import fields, models, _

class HrContractTypeInherit(models.Model):
    _name = "hr.timesheet.line"
    
    name = fields.Char(string="Name")
    employee_id = fields.Many2one("hr.employee", string="Employee")
    date_from = fields.Date(string="Date from")
    date_to = fields.Date(string="Date to")
    description = fields.Char(string="Description")
    worked_days = fields.Json
    attendance_id = fields.Many2one("hr.attendance", string="Attendance")
    leave_id = fields.Many2one("hr.leave", string="Leave")
    overtime_id = fields.Many2one("hr.overtime", string="Overtime")
    
    

    
    



    

    


    


