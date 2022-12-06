from odoo import api, fields, models, tools, _

class HrLeaveTypeInherit(models.Model):
    _inherit = "hr.leave.type"
    
    code = fields.Char("Code")
    time_type = fields.Selection(selection_add=[('paid', 'Paid'), ('not_paid', 'Not Paid')])
    timesheet_type_id = fields.Many2one('hr.timesheet.type', string="Timesheet type")
    

    
    



    

    


    


