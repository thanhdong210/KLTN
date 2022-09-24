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
        'hr_contract'
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/dashboard_views.xml',
        'views/employee_views.xml',
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