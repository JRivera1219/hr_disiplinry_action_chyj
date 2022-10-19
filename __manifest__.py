# -*- coding: utf-8 -*-
{
    'name': "hr_disiplinry_action_chyj",

    'summary': """
        Modulo para la gestión  de expedientes en Comisión de Honor y Justicia""",

    'description': """
        Este modulo gestiona el  control de expedientes abiertos o en 
        investigacion en la comisión de honor y justicia. 
    """,

    'author': "SSP",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Generic Modules/Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    # 'depends': ['base', 'hr'],
    'depends': ['base', 'hr',
                'hr_employee_relative',
                'hr_public_security',
                'oh_employee_documents_expiry',
                'history_employee_moves',
                'feature_location',
                ],

    # always loaded
    'data': [
        'views/menu.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/hr_expedient_disciplinary.xml',
        'views/hr_type_exp_disc_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
