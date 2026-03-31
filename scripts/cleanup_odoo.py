#!/usr/bin/env python3
import xmlrpc.client
import sys

ODOO_URL = 'http://localhost:8069'
ODOO_DB = 'odoo'
ODOO_USER = 'admin'
ODOO_PASSWORD = 'admin'

def main():
    print("Conectando a Odoo para limpieza...")
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    if not uid:
        print("Login fallido")
        sys.exit(1)
        
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    
    # Limpiar res.partner (contribuyentes migrados tienen 'ref' configurado y no son company=True a veces, 
    # pero para estar seguros borramos los que tengan ref != False y que no sean usuarios del sistema).
    # Odoo usa ref para guardar el id de Paria.
    print("Buscando partners migrados...")
    partners = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'res.partner', 'search',
        [[['ref', '!=', False], ['ref', '!=', '']]]
    )
    
    if partners:
        print(f"Borrando {len(partners)} contribuyentes migrados...")
        # Odoo requiere unlink
        try:
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.partner', 'unlink', [partners])
            print("Contribuyentes borrados con éxito.")
        except Exception as e:
            print(f"Error borrando partners: {e}")
    else:
        print("No se encontraron contribuyentes para borrar.")

    # Hacer lo mismo con predios y mapas por si acaso
    for model_name in ['catastro.predio', 'catastro.mapa']:
        try:
            records = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, model_name, 'search', [[]])
            if records:
                print(f"Borrando {len(records)} registros de {model_name}...")
                models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, model_name, 'unlink', [records])
        except Exception as e:
            print(f"Error o '{model_name}' no existe aún: {e}")

if __name__ == "__main__":
    main()
