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
        'hr_holidays',
        'hr_attendance'
    ],
    'data': [
        'security/ir.model.access.csv',

        'data/ir_actions_server.xml',
        'data/mail_test_template.xml',

        'report/employee_report.xml',

        'views/dashboard_views.xml',
        'views/employee_views.xml',
        'views/contract_type_views.xml',
        'views/leave_views.xml',
        'views/attendance_request_views.xml',
        'views/overtime_views.xml',
        'views/ir_menu.xml',
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'KLTN/static/src/js/dashboard_views.js',
        ],
        'web.assets_qweb': [
            'KLTN/static/src/xml/personal_hub_views.xml'
        ],
    },
    
}