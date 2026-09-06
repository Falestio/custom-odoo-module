# -*- coding: utf-8 -*-
{
    'name': 'Filter By Date Range',
    'version': '18.0.1.0',
    'category': 'web',
    'summary': 'Search by date range in List view',
    'description': """
This module adds date range and numeric range search filters directly in list view.
    """,
    'author': 'Falestio Hanif Al Hakim',
    'website': 'https://falestio.my.id/about',
    'depends': ['web'],
    'images': [
        'static/description/banner.png',
    ],
    'assets': {
        'web.assets_backend': [
            'filter_by_date_range/static/src/components/search_by_date_range.css',
            'filter_by_date_range/static/src/components/search_by_date_range.js',
            'filter_by_date_range/static/src/components/search_by_date_range.xml',
        ],
        'web.assets_backend_lazy': [
            'filter_by_date_range/static/src/components/search_by_date_range_pivot.js',
            'filter_by_date_range/static/src/components/search_by_date_range_pivot.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
