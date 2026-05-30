{
    'name': 'Custom Log-Note Control',
    'version': '1.0.0',
    'category': 'Productivity/Discuss',
    'summary': 'Restrict chatter deletion to the Administrator and log every deletion',
    'author': 'MohsinAli Masi',
    'depends': ['mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/audit_views.xml',
        'views/delete_reason_wizard.xml',
        'views/audit_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_log_note_controls/static/src/**/*.js',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
