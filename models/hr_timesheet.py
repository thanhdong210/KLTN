from odoo import fields, models, _

class HrContractTypeInherit(models.Model):
    _name = "hr.timesheet"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string="Name")
    employee_id = fields.Many2one("hr.employee", string="Employee")
    date_from = fields.Date(string="Date from")
    date_to = fields.Date(string="Date to")
    description = fields.Char(string="Description")
    timesheet_line_ids = fields.One2many("hr.timesheet.line", 'timesheet_id', string="Details")
    worked_line_ids = fields.One2many("hr.worked.line", 'timesheet_id', string="Worked Line")
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('confirmed', 'To Approve'),
    ], string='Status', store=True, tracking=True, copy=False, readonly=False, default="draft")
    show_button_confirm = fields.Boolean()

    def action_confirm(self):
        for rec in self:
            rec.write({
                'state': 'confirmed'
            })

    def action_compute_sheet(self):
        self._create_timesheet_line()
        self.compute_worked_day()

    def _create_timesheet_line(self):
        datas_attendance = self.create_attendance_data()
        timesheet_line = self.env['hr.timesheet.line']
        for data in datas_attendance.items():
            vals = {
                'date': data[1].get("date", False),
                'number_of_hour': data[1].get("number_of_hour", 0),
                'timesheet_type_id': data[1].get("timesheet_type_id", False).id,
                'timesheet_id': self.id,
                'code': data[1].get("code", "")
            }
            timesheet_line.create(vals)

    def compute_worked_day(self):
        for rec in self:
            # data = {}
            # for line in rec.timesheet_line_ids:
            #     data_line = data.setdefault(line.get('timesheet_type_id', False), {
            #         'timesheet_type_id': line.get('timesheet_type_id', False),
            #         'number_of_hour': 0.0
            #     })
            pass

    def action_draft(self):
        datas = self.env['hr.timesheet.line'].search([
            ('timesheet_id', '=', self.id)
        ])

        for data in datas:
            data.unlink()

        self.write({
            'state': 'draft'
        })

    def create_attendance_data(self):
        datas_attendance = self.env['hr.attendance.data'].search([
            ('employee_id', '=', self.employee_id.id),
            ('check_in_date', '>=', self.date_from),
            ('check_out_date', '<=', self.date_to)
        ])

        data = {}
        for data_attendance in datas_attendance:
            date = data_attendance.check_in_date
            date_date = data.setdefault(date, {
                'date': data_attendance.check_in_date,
                'number_of_hour': 0.0,
                'timesheet_type_id': data_attendance.timesheet_type_id,
                'code': data_attendance.timesheet_type_id.code,
            })

            date_date['number_of_hour'] += data_attendance.number_of_hour
        
        return data
    
    

    
    



    

    


    


