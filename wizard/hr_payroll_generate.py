from odoo import fields, api, models, _
from odoo.addons.kltn.models import common

class HrPayrollGenerate(models.TransientModel):
    _name = 'hr.payroll.generate'
    _description = 'Payroll Generate'
    _error_message = ''

    department_ids = fields.Many2many('hr.department', string="Department")
    employee_ids = fields.Many2many('hr.employee', string="Employee")
    payroll_run_id = fields.Many2one('hr.payroll.run', string="Payroll Run")
    date_from = fields.Date(string="Date from")
    date_to = fields.Date(string="Date to")
    company_id = fields.Many2one('res.company', string="Company")

    def generate_payroll(self):
        employees_department = self.env['hr.employee'].search([('department_id', 'in', self.department_ids.ids)])
        employees_single = self.env['hr.employee'].browse(self.employee_ids.ids)
        payroll_run = self.env['hr.payroll.run'].browse(self.payroll_run_id.id)
        for employee in employees_single:
            if employee.id in employees_department.ids:
                continue
            else:
                employees_department += employee

        for payroll in payroll_run.payroll_ids:
            if payroll.employee_id.id in employees_department.ids:
                payroll.unlink()

        for employee in employees_department:
            employee_timesheet = self.env['hr.timesheet'].search([('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to), ('employee_id', '=', employee.id)])
            data = {
                'payroll_run_id': self.payroll_run_id.id,
                'employee_id': employee.id,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'contract_id': employee.contract_id.id,
                'department_id': employee.department_id.id,
                'job_id': employee.job_id.id,
                'state': 'draft',
                'company_id': employee.company_id.id,
                'timesheet_id': employee_timesheet.id or False,
                'is_standard_line': False,
                'real_worked_day': employee_timesheet.total_day,
                'benefit_ids':employee.contract_id.benefit_ids,
                'overtime_hours': employee_timesheet.overtime_hours
            }

            payroll = self.env['hr.payroll'].create(data)
            payroll.onchange_payroll_name()
            
            worked_day_data = employee.compute_worked_day_data(self.date_from)
            timesheet_type_id = self.env['ir.model.data']._xmlid_to_res_id('kltn.work_day_rule_timesheet_type')
            timesheet_type = self.env['hr.timesheet.type'].browse(timesheet_type_id)
            worked_day_line_origin = [(0, 0, {
                'number_of_hours': worked_day_data.get("number_of_hours", 0),
                'number_of_days': worked_day_data.get("number_of_days", 0),
                'timesheet_type_id': timesheet_type_id,
                'code': timesheet_type.code,
                'payroll_id': payroll.id,
                'is_standard_line': True
            })]

            payroll.base_worked_day = worked_day_data.get("number_of_days", 0)

            for worked_line in employee_timesheet.worked_line_ids:
                worked_line_data = [(0, 0, {
                    'number_of_hours': worked_line.number_of_hours,
                    'number_of_days': worked_line.number_of_days,
                    'timesheet_type_id': worked_line.timesheet_type_id.id,
                    'code': worked_line.timesheet_type_id.code,
                    'payroll_id': payroll.id
                })]
                worked_day_line_origin += worked_line_data

            payroll.worked_line_ids = worked_day_line_origin

