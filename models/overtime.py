from odoo import fields, models, _

class HrContractTypeInherit(models.Model):
    _name = "hr.overtime.request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _mail_post_access = 'read'
    
    name = fields.Char(string="Name")
    date = fields.Date(string="Date")
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
    number_of_hours = fields.Float(string="Number of hours")
    target = fields.Selection([
        ('employee', 'By Employee'),
        ('department', 'By Department'),
        ('employees', 'By Employees'),
    ], string='Status', compute='_compute_state', store=True, tracking=True, copy=False, readonly=False)
    request_hour_from = fields.Selection([
        ('0', '12:00 AM'), ('0.5', '12:30 AM'),
        ('1', '1:00 AM'), ('1.5', '1:30 AM'),
        ('2', '2:00 AM'), ('2.5', '2:30 AM'),
        ('3', '3:00 AM'), ('3.5', '3:30 AM'),
        ('4', '4:00 AM'), ('4.5', '4:30 AM'),
        ('5', '5:00 AM'), ('5.5', '5:30 AM'),
        ('6', '6:00 AM'), ('6.5', '6:30 AM'),
        ('7', '7:00 AM'), ('7.5', '7:30 AM'),
        ('8', '8:00 AM'), ('8.5', '8:30 AM'),
        ('9', '9:00 AM'), ('9.5', '9:30 AM'),
        ('10', '10:00 AM'), ('10.5', '10:30 AM'),
        ('11', '11:00 AM'), ('11.5', '11:30 AM'),
        ('12', '12:00 PM'), ('12.5', '12:30 PM'),
        ('13', '1:00 PM'), ('13.5', '1:30 PM'),
        ('14', '2:00 PM'), ('14.5', '2:30 PM'),
        ('15', '3:00 PM'), ('15.5', '3:30 PM'),
        ('16', '4:00 PM'), ('16.5', '4:30 PM'),
        ('17', '5:00 PM'), ('17.5', '5:30 PM'),
        ('18', '6:00 PM'), ('18.5', '6:30 PM'),
        ('19', '7:00 PM'), ('19.5', '7:30 PM'),
        ('20', '8:00 PM'), ('20.5', '8:30 PM'),
        ('21', '9:00 PM'), ('21.5', '9:30 PM'),
        ('22', '10:00 PM'), ('22.5', '10:30 PM'),
        ('23', '11:00 PM'), ('23.5', '11:30 PM')], string='Hour from')
    request_hour_to = fields.Selection([
        ('0', '12:00 AM'), ('0.5', '12:30 AM'),
        ('1', '1:00 AM'), ('1.5', '1:30 AM'),
        ('2', '2:00 AM'), ('2.5', '2:30 AM'),
        ('3', '3:00 AM'), ('3.5', '3:30 AM'),
        ('4', '4:00 AM'), ('4.5', '4:30 AM'),
        ('5', '5:00 AM'), ('5.5', '5:30 AM'),
        ('6', '6:00 AM'), ('6.5', '6:30 AM'),
        ('7', '7:00 AM'), ('7.5', '7:30 AM'),
        ('8', '8:00 AM'), ('8.5', '8:30 AM'),
        ('9', '9:00 AM'), ('9.5', '9:30 AM'),
        ('10', '10:00 AM'), ('10.5', '10:30 AM'),
        ('11', '11:00 AM'), ('11.5', '11:30 AM'),
        ('12', '12:00 PM'), ('12.5', '12:30 PM'),
        ('13', '1:00 PM'), ('13.5', '1:30 PM'),
        ('14', '2:00 PM'), ('14.5', '2:30 PM'),
        ('15', '3:00 PM'), ('15.5', '3:30 PM'),
        ('16', '4:00 PM'), ('16.5', '4:30 PM'),
        ('17', '5:00 PM'), ('17.5', '5:30 PM'),
        ('18', '6:00 PM'), ('18.5', '6:30 PM'),
        ('19', '7:00 PM'), ('19.5', '7:30 PM'),
        ('20', '8:00 PM'), ('20.5', '8:30 PM'),
        ('21', '9:00 PM'), ('21.5', '9:30 PM'),
        ('22', '10:00 PM'), ('22.5', '10:30 PM'),
        ('23', '11:00 PM'), ('23.5', '11:30 PM')], string='Hour to')
    test_field = fields.Char(string="test")

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
    
    

    
    



    

    


    


