# -*- coding: utf-8 -*-

{
    'name': 'UTAR Hospital Management',
    'version': '1.0.0',
    'category': 'Hospital',
    'author': 'Mini Project - G1',
    'sequence': -100,
    'summary': 'Management Information System',
    'description': """Hospital Management System""",
    'depends': [],
    'data': [
        'security/ir.model.access.csv', #security file must at first
        'data/sequence_data.xml',
        'views/menu.xml',
        'views/patient_view.xml',
        'views/appointment_view.xml',
    ],
    'demo': [],
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
