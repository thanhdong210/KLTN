from odoo import fields, models, _

class HrContractTypeInherit(models.Model):
    _name = "hr.attendance.request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _mail_post_access = 'read'
    
    name = fields.Char(string="Name")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    is_half = fields.Boolean(string="Half day")
    is_half_selection = fields.Selection([
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
    ], string='Status', tracking=True, copy=False, readonly=False,)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    department_id = fields.Many2one('hr.department', string="Department")
    employee_ids = fields.Many2many('hr.employee', string="Employees")
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
    ], string='Status', compute='_compute_state', store=True, tracking=True, copy=False, readonly=False)
    number_of_days = fields.Float(string="Number of days")
    target = fields.Selection([
        ('employee', 'By Employee'),
        ('department', 'By Department'),
        ('employees', 'By Employees'),
    ], string='Status', compute='_compute_state', store=True, tracking=True, copy=False, readonly=False)

    def _compute_state(self):
        pass

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

    def _compute_is_half(self):
        pass

    
    

    
    



    

    


    


