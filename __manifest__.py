{
    'name': "Parking manage",
    'summary': "Parking manage",
    'description': "Manage car parking in parking lot",
    'author': "Thanh Dong",
    'website': "None",
    'category': 'Uncategorized',
    'version': '1.0',
    'depends': [
        'hr',
        'web',
        'hr_contract',
        'hr_attendance'
    ],
    'data': [
        'data/data_groups.xml',
        'security/ir.model.access.csv',

        'data/ir_actions_server.xml',
        'data/mail_test_template.xml',
        'data/ir_config_parameter.xml',
        'data/data_groups.xml',
        'data/timesheet_type_data.xml',
        'data/mail_activity_type.xml',
        'data/ir_cron.xml',

        'report/employee_report.xml',
        'report/payroll_report.xml',
        'report/timesheet_line_report.xml',
        'report/hr_employee_report.xml',

        'wizard/hr_payroll_generate_views.xml',

        'views/dashboard_views.xml',
        'views/hr_attendance_data_views.xml',
        'views/employee_views.xml',
        'views/contract_type_views.xml',
        'views/contract_views.xml',
        'views/leave_views.xml',
        'views/attendance_request_views.xml',
        'views/hr_overtime_views.xml',
        'views/hr_leave_allocation_views.xml',
        'views/hr_timesheet_views.xml',
        'views/hr_payroll_views.xml',
        'views/hr_payroll_run_views.xml',
        'views/resource_calendar_views.xml',
        'views/hr_timesheet_type_views.xml',
        'views/hr_benefit_views.xml',
        'views/hr_location_views.xml',
        'views/hr_payroll_sum_views.xml',
        'views/ir_menu.xml',
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'kltn/static/src/js/dashboard_views.js',
            'kltn/static/src/js/attendance_data.js',
            'kltn/static/src/js/attendance.js',
            'kltn/static/src/js/chart.js',
        ],
        'web.assets_qweb': [
            'kltn/static/src/xml/personal_hub_views.xml',
            'kltn/static/src/xml/*.xml'
        ],
    },
    
}