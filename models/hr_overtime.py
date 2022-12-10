from odoo import fields, api, models, _
from odoo.exceptions import ValidationError

class HrContractTypeInherit(models.Model):
    _name = "hr.overtime.request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _mail_post_access = 'read'
    
    name = fields.Char(string="Name")
    date = fields.Date(string="Date")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    department_id = fields.Many2one('hr.department', string="Department")
    employee_ids = fields.Many2many('hr.employee', string="Employees")
    company_id = fields.Many2one('res.company', string="Company")
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('approve', 'To Approve'),
        ('second_approve', 'To Second Approve'),
        ('validated', 'Approved'),
        ('refused', 'Refused'),
    ], string='Status', compute='_compute_state', store=True, tracking=True, copy=False, readonly=False, default="draft")
    number_of_hours = fields.Float(string="Number of hours", compute="_compute_number_of_hour", store=True)
    target = fields.Selection([
        ('employee', 'By Employee'),
        ('department', 'By Department'),
        ('employees', 'By Employees'),
    ], string='Status', compute='_compute_state', store=True, tracking=True, copy=False, readonly=False)
    timesheet_type_id = fields.Many2one('hr.timesheet.type', string="Timesheet Type")
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
    show_button_approve = fields.Boolean(string="Check Button Approve", compute="_compute_show_button_approve")
    show_button_validate = fields.Boolean(string="Check Button Validate", compute="_compute_show_button_validate")
    is_personalhub = fields.Boolean(string="Is Personal Hub")

    @api.onchange("is_personalhub")
    def onchange_user(self):
        for rec in self:
            if rec.is_personalhub:
                rec.employee_id = rec.env.user.employee_id

    @api.depends("request_hour_from", "request_hour_to")
    def _compute_number_of_hour(self):
        for rec in self:
            if rec.request_hour_from and rec.request_hour_to:
                if rec.request_hour_from < rec.request_hour_to:
                    rec.number_of_hours = float(rec.request_hour_to) - float(rec.request_hour_from)
                else:
                    rec.number_of_hours = 0

    @api.onchange("request_hour_from", "request_hour_to", "date")
    def _onchange_hour_from_hour_to(self):
        for rec in self:
            if rec.request_hour_from and rec.request_hour_to and rec.employee_id:
                intervals = rec.employee_id.contract_id.resource_calendar_id.attendance_ids
                list_weekday = []
                for interval in intervals:
                    if int(interval.dayofweek) == int(rec.date.weekday()):
                        list_weekday.append(interval.hour_from)
                        list_weekday.append(interval.hour_to)
                min_hour = min(list_weekday)
                max_hour = max(list_weekday)
                if (float(rec.request_hour_from) > min_hour and float(rec.request_hour_from) < max_hour) or (float(rec.request_hour_to) > min_hour and float(rec.request_hour_to) < max_hour) or (float(rec.request_hour_from) < min_hour and float(rec.request_hour_to) > max_hour):
                    raise ValidationError(_("Overtime hour can't in working hour"))

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
        if self.user_has_groups('kltn.group_hr_overtime_manager'):
            return True
        employee_manager = self.create_uid.employee_id.parent_id.user_id
        if self.create_uid.employee_id.coach_id:
            employee_manager |= self.env.user.employee_id.coach_id.user_id
        if employee_manager and self.env.user in employee_manager:
            return True
        return False

    def check_button_validate(self):
        if self.user_has_groups('kltn.group_hr_overtime_manager'):
            return True
        employee_coach = self.create_uid.employee_id.coach_id.user_id
        if employee_coach and self.env.user in employee_coach:
            return True
        return False

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
            'state': 'validated'
        })

    def action_refuse(self):
        self.write({
            'state': 'refused'
        })

    def action_draft(self):
        self.write({
            'state': 'draft'
        })

    # @api.model
    # def create(self, vals):
    #     pass
    
    

    
    



    

    


    


