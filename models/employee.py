from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date
import calendar

class HrEmployeeInherit(models.Model):
    _inherit = "hr.employee"
    
    test_field = fields.Char("Total time")

    def action_employee_test(self):
        mail_template = self.env.ref("KLTN.mail_template_employee_test")
        mail_template.sudo().send_mail(self.id, force_send=True)

    def get_detail_employee(self):
        data = {}
        date_from = datetime(datetime.now().year, datetime.now().month, 1)
        date_to = datetime(datetime.now().year, datetime.now().month, calendar.monthrange(
            datetime.now().year, datetime.now().month)[1])


        attendance_data = self.env['hr.attendance'].search([
            ("employee_id", "=", self.env.user.employee_id.id),
            '&',
                ("check_in", ">=", date_from),
                ("check_in", "<=", date_to)
        ])

        leave_data = self.env['hr.leave'].search([
            ("employee_id", "=", self.env.user.employee_id.id),
            '&',
                ("date_from", ">=", date_from),
                ("date_from", "<=", date_to)
        ])

        overtime_data = self.env['hr.overtime.request'].search([
            ("employee_id", "=", self.env.user.employee_id.id),
            '&',
                ("date", ">=", date_from),
                ("date", "<=", date_to)
        ])

        number_of_hour_overtime = 0
        for data in overtime_data:
            number_of_hour_overtime += data.number_of_hours
        
        data = {
            "attendance_count": len(attendance_data),
            "leave_count": len(leave_data),
            "overtime_count": len(overtime_data),
            "overtime_hour_count": number_of_hour_overtime
        }

    
    



    

    


    


