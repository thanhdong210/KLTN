from odoo import fields, api, models, _, tools
import datetime, calendar


class HrPayrollReport(models.AbstractModel):
    _name = 'report.kltn.report_payroll_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['hr.payroll'].browse(docids)

        return {
            'doc_ids': docids,
            'doc_model': 'hr.payroll',
            'docs': docs,
        }
