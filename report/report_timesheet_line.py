from odoo import fields, api, models, _, tools
import datetime, calendar


class HrTimesheetLineReport(models.AbstractModel):
    _name = 'report.kltn.report_timesheet_line_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['hr.timesheet'].browse(docids)

        data = {
            'the_string': "hrhehee",
        }

        return {
            'doc_ids': docids,
            'doc_model': 'hr.timesheet',
            'docs': docs,
            'data': data,
            'num_days': self.get_timesheet_line_data(docids)['num_days'],
            'week_days': self.get_timesheet_line_data(docids)['week_days'],
            'data_for_morning': self.get_timesheet_line_data(docids)['data_for_morning'],
            'data_for_afternoon': self.get_timesheet_line_data(docids)['data_for_afternoon']
        }

    def get_timesheet_line_data(self, timesheet):
        timesheets = self.env['hr.timesheet'].browse(timesheet)

        week_days = []
        num_days = 0
        
        for timesheet in timesheets:
            num_days = calendar.monthrange(timesheet.date_from.year, timesheet.date_from.month)[1]
            week_days = [calendar.day_name[datetime.date(timesheet.date_from.year, timesheet.date_from.month, day).weekday()][:3] for day in range(1, num_days+1)]
            data_for_afternoon = []
            data_for_morning = []

            for idx in range(num_days):
                data_for_afternoon.append("")
                data_for_morning.append("")

            # for day in range(num_days + 1):
            #     for line in timesheet.timesheet_line_ids:
            #         if line.day.day == day and line.day_state == 'afternoon':
            #             data_for_afternoon[day - 1] = line.number

            #         elif line.day.day == day and line.day_state == 'morning':
            #             data_for_morning[day - 1] = line.number
            
        data = {
            'num_days': num_days,
            'week_days': week_days,
            'data_for_morning': data_for_morning,
            'data_for_afternoon': data_for_afternoon,
        }
        return data
