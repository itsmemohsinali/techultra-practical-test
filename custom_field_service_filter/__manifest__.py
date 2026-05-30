{
    'name': 'Custom Field-Service Filter',
    'version': '1.0.0',
    'category': 'Services/Field Service',
    'summary': 'Add an Assigned To side panel filter on the Field Service calendar',
    'author': 'MohsinAli Masi',
    'depends': ['industry_fsm'],
    'data': [
        'views/calendar_view_inherit.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'fieldservice_calendar_assigned_filter/static/src/**/*.js',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
