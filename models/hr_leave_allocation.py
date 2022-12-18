from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError

class HrLeaveAllowcationInherit(models.Model):
    _name = "hr.leave.allocation.inherit"
    
    name = fields.Char(string="Name")
    nextcall = fields.Date(string="Next call")
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('refuse', 'Refused'),
        ('validate', 'Approved')
    ], string="Mode", store=True, copy=False, default='draft')
    # leave_type_id = fields.Many2one('hr.leave.type', string="Leave Type")
    # leave_type_code = fields.Char(related='leave_type_id.code', string="Leave Type Code", store=True, readonly=True)
    timesheet_type_id = fields.Many2one('hr.timesheet.type', string="Leave Type")
    timesheet_code = fields.Char(string="Timesheet code", related="timesheet_type_id.code")
    is_accrual = fields.Boolean(string="Accrual")
    number_of_day = fields.Float(string="Day(s) to allocate")
    type = fields.Selection([
        ('employee', 'Employee'),
        ('department', 'Department'),
        ('company', 'Company'),
        ('employees', 'Employees'),
    ], string="Mode", store=True, copy=False)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    department_id = fields.Many2one('hr.department', string="Department")
    employee_ids = fields.Many2many('hr.employee', string="Employees")
    parent_id = fields.Many2one('hr.leave.allocation.inherit', index=True, ondelete='cascade', readonly=True)
    contract_type_id = fields.Many2one('hr.contract.type', string="Contract Type")
    company_id = fields.Many2one('res.company', string="Company")
    is_child = fields.Boolean(string="Child", default=False)

    def action_confirm(self):
        self.allocate_leave()
        self.write({
            'state': 'validate'
        })

    def allocate_leave(self):
        if self.type == "employee":
            employee = self.env['hr.employee'].search([
                ('id', '=', self.employee_id.id),
                ('contract_type_id', '=', self.contract_type_id.id)
            ])
            if not employee.contract_id or employee.contract_id.state != 'open':
                raise UserError(_("This employee still haven't had contract yet!"))
            self.create_child_allocation_leave(employee)
        elif self.type == "department":
            employee_ids = self.env['hr.employee'].search([
                ('department_id', '=', self.department_id.id),
                ('contract_type_id', '=', self.contract_type_id.id)
            ])
            
            for employee in employee_ids:
                if not employee.contract_id or employee.contract_id.state != 'open':
                    raise UserError(_("This employee still haven't had contract yet!"))
                self.create_child_allocation_leave(employee)

    def create_child_allocation_leave(self, employee):
        data = {
            'employee_id': employee.id,
            'state': 'validate',
            'number_of_day': self.number_of_day,
            'parent_id': self.id,
            'timesheet_type_id': self.timesheet_type_id.id,
            'name': (_('Allocation leave for ') + employee.name),
            'is_child': True
        }
        self.create(data)
        employee._compute_total_leaves()

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("You can't delete record which is not draft"))
            return super(HrLeaveAllowcationInherit, rec).unlink()

    def action_refuse(self):
        for rec in self:
            datas_to_delete = rec.env['hr.leave.allocation.inherit'].search([
                ('parent_id', '=', self.id)
            ])
            for data in datas_to_delete:
                data.write({
                    'state': 'draft'
                })
                data.employee_id._compute_total_leaves()
                
                data.unlink()
            rec.write({
                'state': 'refuse'
            })

    def action_draft(self):
        self.write({
            'state': 'draft'
        })

    def _compute_is_half(self):
        pass

    def update_allocation(self):
        allocations = self.search([
            ('state', '=', 'validate'),
            ('is_accrual', '=', True),
        ])
        for allocation in allocations:
            employees = False
            if allocation.type == 'employee':
                employees = allocation.employee_id
            elif allocation.type == 'department':
                employees = self.env['hr.employee'].search([
                    ('department_id', '=', allocation.department_id.id)
                ])
            elif allocation.type == 'company':
                employees = self.env['hr.employee'].search([
                    ('active', '=', True)
                ])
            for employee in employees:
                data = {
                    'employee_id': employee.id,
                    'state': 'validate',
                    'number_of_day': allocation.number_of_day,
                    'parent_id': allocation.id,
                    'timesheet_type_id': allocation.timesheet_type_id.id,
                    'name': (_('Allocation leave for %s in %s %s') % (employee.name, fields.Date.today().month, fields.Date.today().year)),
                    'is_child': True
                }
                self.create(data)
                employee._compute_total_leaves()
            



    
    

    
    



    

    


    


