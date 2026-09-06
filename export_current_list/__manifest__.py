# -*- coding: utf-8 -*-
{
    'name': 'Export Current List View',
    'version': '18.0.1.0.0',
    'category': 'Web',
    'summary': 'Export selected rows from list view to Excel',
    'description': """
Export Current List View to Excel
    """,
    'author': 'Falestio Hanif Al Hakim',
    'website': 'https://falestio.my.id/about',
    'depends': ['web'],
    'assets': {
        'web.assets_backend': [
            'export_current_list/static/src/components/export_current_list.js',
            'export_current_list/static/src/components/export_current_list.xml',
            'export_current_list/static/src/components/export_current_list.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
