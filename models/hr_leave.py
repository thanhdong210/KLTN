from odoo import api, fields, models, tools, _

class HrLeaveInherit(models.Model):
    _name = "hr.leave.inherit"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string="Reason")
    is_half_day = fields.Boolean("Half Day")
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('refuse', 'Refused'),
        ('validate', 'Approved'),
        ('second_validate', 'Second Approved')
    ], string='Status', store=True, tracking=True, copy=False, readonly=False)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    department_id = fields.Many2one('hr.department', string="Department")
    employee_ids = fields.Many2many('hr.employee', string="Employees")
    company_id = fields.Many2one('res.company', string="Company")
    leave_type_id = fields.Many2one('hr.leave.type', string="Leave Type")
    target = fields.Selection([
        ('employee', 'By Employee'),
        ('department', 'By Department'),
        ('employees', 'By Employees'),
        ('company', 'By Employees'),
    ], string='Status', compute='_compute_state', store=True, tracking=True, copy=False, readonly=False)

    def name_get(self):
        return "hehe"
    
    def action_confirm(self):
        pass

    def action_approve(self):
        pass

    def action_validate(self):
        pass

    def action_refuse(self):
        pass

    def action_draft(self):
        pass
    

    
    



    

    


    


