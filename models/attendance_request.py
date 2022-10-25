from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError

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
    company_id = fields.Many2one('res.company', string="Company")
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('approve', 'To Approve'),
        ('second_approve', 'To Second Approve'),
        ('validate', 'Approved'),
        ('refuse', 'Refused'),
    ], string='Status', compute='_compute_state', store=True, tracking=True, copy=False, readonly=False, default="draft")
    number_of_days = fields.Float(string="Number of days")
    target = fields.Selection([
        ('employee', 'By Employee'),
        ('department', 'By Department'),
        ('employees', 'By Employees'),
        ('company', 'By Conpany'),
    ], string='Mode', compute='_compute_state', store=True, tracking=True, copy=False, readonly=False)
    show_button_approve = fields.Boolean(string="Check Button Approve", compute="_compute_show_button_approve")
    show_button_validate = fields.Boolean(string="Check Button Validate", compute="_compute_show_button_validate")
    timesheet_type_id = fields.Many2one('hr.timesheet.type', string="Timesheet Type")

    @api.constrains('date_to', 'date_from')
    def _check_date_from_date_to(self):
        for rec in self:
            if (rec.date_to and rec.date_from) and (rec.date_to < rec.date_from):
                raise ValidationError(_("'Date To' must greater than 'Date From'"))

    @api.onchange('date_to', 'is_half')
    def _onchange_is_half(self):
        if self.is_half == True:
            self.date_to = False

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
        if self.user_has_groups('KLTN.group_attendance_request'):
            return True
        employee_manager = self.create_uid.employee_id.parent_id.user_id
        if self.create_uid.employee_id.coach_id:
            employee_manager |= self.env.user.employee_id.coach_id.user_id
        if employee_manager and self.env.user in employee_manager:
            return True
        return False

    def check_button_validate(self):
        if self.user_has_groups('KLTN.group_attendance_request'):
            return True
        employee_coach = self.create_uid.employee_id.coach_id.user_id
        if employee_coach and self.env.user in employee_coach:
            return True
        return False

    def _compute_state(self):
        pass

    def action_confirm(self):
        self.write({
            'state': 'approve'
        })

    def action_approve(self):
        self.write({
            'state': 'second_approve'
        })

    def action_validate(self):
        self.write({
            'state': 'validate'
        })
        if self.is_half:
            if self.target == 'employee':
                datas = self.employee_id._get_employee_resource_calendar(self.date_from, False, True)
        else:
            datas = self.employee_id._get_employee_resource_calendar(self.date_from, self.date_to)

        if datas:
            for data in datas:
                data.update({
                    'timesheet_type_id': self.timesheet_type_id.id,
                    'attendance_request_id': self.id
                })
                self.env['hr.attendance.data'].create(data)

    def action_refuse(self):
        attendances_to_delete = self.env['hr.attendance.data'].search([
            ('attendance_request_id', '=', self.id)
        ])
        for attendance in attendances_to_delete:
            attendance.unlink()
        self.write({
            'state': 'refuse'
        })

    def action_draft(self):
        self.write({
            'state': 'draft'
        })

    def _compute_is_half(self):
        pass

    @api.model_create_multi
    def create(self, vals):
        data = self.env['hr.attendance.request'].search([
            ('employee_id', '=', vals[0]['employee_id']),
            ('date_from', '=', vals[0]['date_from']),
        ])
        if data:
            raise UserError(_("This employee already have attendance request on this day."))
        print("===========", data)

        res = super(HrContractTypeInherit, self).create(vals)
        for response in res:
            if response.create_uid.employee_id and not response.create_uid.employee_id.parent_id:
                raise UserError(_("This user dont have manager"))

        return res
        

    
    

    
    



    

    


    


