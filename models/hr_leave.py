from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class HrLeaveInherit(models.Model):
    _name = "hr.leave.inherit"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string="Reason")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    is_half_day = fields.Boolean("Half Day")
    is_half_selection = fields.Selection([
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
    ], string='Status', tracking=True, copy=False, readonly=False,)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('approve', 'To Approve'),
        ('second_approve', 'To Second Approve'),
        ('validated', 'Approved'),
        ('refused', 'Refused'),
    ], string='Status', compute='_compute_state', store=True, tracking=True, copy=False, readonly=False, default="draft")
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
    show_button_approve = fields.Boolean(string="Check Button Approve", compute="_compute_show_button_approve")
    show_button_validate = fields.Boolean(string="Check Button Validate", compute="_compute_show_button_validate")
    number_of_days = fields.Float(string="Number of days", compute="_compute_number_of_day")

    @api.onchange("date_from", "date_to")
    def _onchange_date_from_to(self):
        for rec in self:
            if (rec.date_from and rec.date_to) and (rec.date_from > rec.date_to):
                raise ValidationError(_("Date to can't be lower than date from!"))

    @api.depends("date_from", "date_to", "is_half_selection")
    def _compute_number_of_day(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                if rec.date_from == rec.date_to:
                    rec.number_of_days = 1
                else:
                    rec.number_of_days = (rec.date_to - rec.date_from).days + 1
            elif rec.date_from and rec.is_half_day:
                rec.number_of_days = 0.5
            else:
                rec.number_of_days = 0

    def _compute_show_button_approve(self):
        for rec in self:
            if rec.state == 'approve':
                rec.show_button_approve = rec.check_button_approve()
            else:
                rec.show_button_approve = False

    def _compute_show_button_validate(self):
        for rec in self:
            if rec.state == 'second_approve':
                rec.show_button_validate = rec.check_button_validate()
            else:
                rec.show_button_validate = False

    def check_button_approve(self):
        if self.user_has_groups('kltn.group_hr_leaves_manager'):
            return True
        employee_manager = self.create_uid.employee_id.parent_id.user_id
        if self.create_uid.employee_id.coach_id:
            employee_manager |= self.env.user.employee_id.coach_id.user_id
        if employee_manager and self.env.user in employee_manager:
            return True
        return False

    def check_button_validate(self):
        if self.user_has_groups('kltn.group_attendance_request'):
            return True
        employee_coach = self.create_uid.employee_id.coach_id.user_id
        if employee_coach and self.env.user in employee_coach:
            return True
        return False
    
    def action_confirm(self):
        employee_total_leave = self.employee_id.total_leaves
        leave_type_for_compute = self.env['ir.config_parameter'].sudo().get_param('leave_type_for_compute')
        if leave_type_for_compute:
            leave_type_for_compute = leave_type_for_compute.split(',')
        total_leave = self.number_of_days + self.employee_id.leave_taken
        print("===============", employee_total_leave)
        print("===============", total_leave)
        if total_leave > employee_total_leave and self.leave_type_id.code in leave_type_for_compute:
            raise ValidationError(_("This employee don't have enough remaining leave"))
        self.write({
            'state': 'approve'
        })

    def action_approve(self):
        self.write({
            'state': 'second_approve'
        })

        leave_taken = self.employee_id.leave_taken + self.number_of_days
        self.employee_id.write({
            'leave_taken': leave_taken
        })

    def action_validate(self):
        self.write({
            'state': 'validated'
        })

    def action_refuse(self):
        self.write({
            'state': 'refused'
        })
        if self.employee_id.leave_taken > 0:
            self.employee_id.leave_taken -= self.number_of_days

    def action_draft(self):
        self.write({
            'state': 'draft'
        })

    def unlink(self):
        for rec in self:
            if rec.state != "draft":
                raise ValidationError(_("Can't delete when state not in draft"))
        return super(HrLeaveInherit, self).unlink()
    

    
    



    

    


    


