from odoo import fields, models, api, _

class HrPayrollRun(models.Model):
    _name = "hr.payroll.run"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    date_from = fields.Date(string="Date from")
    date_to = fields.Date(string="Date to")
    job_id = fields.Many2one('hr.job', string="Job")
    contract_id = fields.Many2one('hr.contract', string="Contract")
    is_paid = fields.Boolean(string="Is paid")
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('confirmed', 'To Approve'),
        ('paid', 'Paid'),
    ], string='Status', store=True, tracking=True, copy=False, readonly=False, default="draft")
    payroll_ids = fields.One2many('hr.payroll', 'payroll_run_id', string="Payrolls")

    def action_confirm(self):
        for rec in self:
            rec.write({
                'state': 'confirmed'
            })

    def action_compute_payroll_run(self):
        pass

    def open_generate_payroll(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Generate Payroll',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'hr.payroll.generate',
            'target': 'new',
            'context': {
                'default_payroll_run_id': self.id,
                'default_date_from': self.date_from,
                'default_date_to': self.date_to,
            },
        }


    def action_draft(self):
        self.write({
            'state': 'draft'
        })