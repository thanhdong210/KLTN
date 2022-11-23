from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

class HrContractTypeInherit(models.Model):
    _name = "hr.attendance.request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _mail_post_access = 'read'
    _description = "Attendance Request"
    
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
    number_of_days = fields.Float(string="Number of days", compute="_compute_number_of_day")
    target = fields.Selection([
        ('employee', 'By Employee'),
        ('department', 'By Department'),
        ('employees', 'By Employees'),
        ('company', 'By Conpany'),
    ], string='Mode', compute='_compute_state', store=True, tracking=True, copy=False, readonly=False)
    show_button_approve = fields.Boolean(string="Check Button Approve", compute="_compute_show_button_approve")
    show_button_validate = fields.Boolean(string="Check Button Validate", compute="_compute_show_button_validate")
    timesheet_type_id = fields.Many2one('hr.timesheet.type', string="Timesheet Type")

    @api.onchange("date_from", "date_to")
    def _onchange_date_from_to(self):
        for rec in self:
            if (rec.date_from and rec.date_to) and (rec.date_from > rec.date_to):
                raise ValidationError(_("Date to can't be lower than date from!"))

    @api.depends("date_from", "date_to")
    def _compute_number_of_day(self):
        for rec in self:
            rec.number_of_days = 0
            if rec.date_from and rec.date_to:
                if rec.date_from == rec.date_to:
                    rec.number_of_days = 1
                else:
                    rec.number_of_days = (rec.date_to - rec.date_from).days + 1
            elif rec.date_from and rec.is_half and rec.is_half_selection:
                rec.number_of_days = 0.5

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
        if self.user_has_groups('kltn.group_attendance_request'):
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

    def get_employee_manager(self):
        for rec in self:
            if rec.state == 'draft':
                superior = rec.create_uid.employee_id.parent_id.user_id
                if not superior:
                    superior = self.env.user
            elif rec.state == 'aprrove':
                superior = rec.create_uid.employee_id.coach_id.user_id
                if not superior:
                    superior = self.env.user
            else:
                superior = self.env.user
            return superior

    def activitiy_update(self):
        to_clean, to_do = self.env['hr.attendance.request'], self.env['hr.attendance.request']
        for rec in self:
            note = _("%s had requested an attendance", self.employee_id.name)
            if rec.state == 'draft':
                rec.activity_schedule(
                    'kltn.mail_activity_attendance_request',
                    note=note,
                    user_id=rec.sudo().get_employee_manager().id)
            elif rec.state == 'approve':
                rec.activity_feedback(['kltn.mail_activity_attendance_request'])
                rec.activity_schedule(
                    'kltn.mail_activity_attendance_request',
                    note=note,
                    user_id=rec.sudo().get_employee_manager().id)
            elif rec.state == 'second_approve':
                to_do |= rec
            elif rec.state == 'validated':
                to_do |= rec
            elif rec.state == 'refuse':
                to_clean |= rec
        if to_clean:
            to_clean.activity_unlink(['kltn.mail_activity_attendance_request', 'kltn.mail_activity_attendance_request'])
        if to_do:
            to_do.activity_feedback(['kltn.mail_activity_attendance_request', 'kltn.mail_activity_attendance_request'])

    def _compute_state(self):
        pass

    def action_confirm(self):
        self.activitiy_update()
        self.write({
            'state': 'approve'
        })

    def action_approve(self):
        self.activitiy_update()
        self.write({
            'state': 'second_approve'
        })

    def action_validate(self):
        self.activitiy_update()
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
        self.activitiy_update()
        attendances_to_delete = self.env['hr.attendance.data'].search([
            ('attendance_request_id', '=', self.id)
        ])
        for attendance in attendances_to_delete:
            attendance.unlink()
        self.write({
            'state': 'refuse'
        })

    def action_draft(self):
        self.activitiy_update()
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

        res = super(HrContractTypeInherit, self).create(vals)
        for response in res:
            if response.create_uid.employee_id and not response.create_uid.employee_id.parent_id:
                raise UserError(_("This user dont have manager"))

        return res

    # def write(self, vals):
    #     self.activitiy_update()
    #     return super(HrContractTypeInherit, self).write(vals)
        

    
    

    
    



    

    


    


