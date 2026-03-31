# -*- coding: utf-8 -*-
{
    'name': 'Catastro Municipal - Suite Completa',
    'version': '17.0.1.0.0',
    'summary': 'Meta-Módulo para instalar TODO el ecosistema catastral con un solo clic',
    'description': """
Módulo Instalador del Ecosistema Catastral
==========================================
Este módulo no contiene código propio, pero depende de todos los submódulos.
Al instalar este, Odoo instalará y ordenará automáticamente:
1. Catastro Predios (Base)
2. Catastro Mapa Geográfico
3. Catastro Avalúos
4. Catastro Impuestos
5. Catastro Transferencias
6. Catastro Gravámenes
7. Catastro Certificados
    """,
    'author': 'Gobierno Autónomo Municipal de Vallegrande',
    'website': 'https://github.com/Pothoko/catastro_01',
    'category': 'Government/Cadastre',
    'license': 'LGPL-3',
    'depends': [
        'catastro_predio',
        'catastro_mapa',
        'catastro_avaluo',
        'catastro_impuestos',
        'catastro_transferencia',
        'catastro_gravamen',
        'catastro_certificados',
    ],
    'data': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'icon': 'catastro_predio/static/description/icon.png',
}
