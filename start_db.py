#!/usr/bin/env python
"""
Script de inicialización de base de datos para django-tenants.

Este script:
1. Ejecuta las migraciones del esquema compartido (público)
2. Crea organizaciones de prueba con sus dominios
3. Ejecuta las migraciones específicas de cada tenant

Uso:
    python start_db.py

Requisitos:
    - Tener configuradas las variables de entorno en .env
    - Base de datos PostgreSQL disponible
"""

import os
import sys
import django
from pathlib import Path

# Configurar la ruta del proyecto
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'buzon_quejas.settings')
django.setup()

from django.core.management import call_command
from organization.models import Organization, Domain
from django.db import connection


def print_header(message):
    """Imprime un encabezado formateado."""
    print("\n" + "=" * 70)
    print(f"  {message}")
    print("=" * 70 + "\n")


def print_success(message):
    """Imprime un mensaje de éxito."""
    print(f"✓ {message}")


def print_error(message):
    """Imprime un mensaje de error."""
    print(f"✗ ERROR: {message}")


def print_info(message):
    """Imprime un mensaje informativo."""
    print(f"ℹ {message}")


def run_shared_migrations():
    """Ejecuta las migraciones del esquema compartido (público)."""
    print_header("Paso 1: Ejecutando migraciones del esquema compartido")
    
    try:
        call_command('migrate_schemas', '--shared', verbosity=2)
        print_success("Migraciones del esquema público completadas")
        return True
    except Exception as e:
        print_error(f"Error al ejecutar migraciones compartidas: {e}")
        return False


def create_public_domain():
    """Crea el dominio público si no existe."""
    print_header("Creando dominio público")
    
    try:
        public_org = Organization.objects.filter(schema_name='public').first()
        
        if public_org:
            print_success("Dominio público 'tuvozenruta.com' creado")
            return True
        
        public_org = Organization.objects.create(
            name='Público',
            schema_name='public'
        )

        public_domain = Domain.objects.create(
            tenant=public_org,
            domain='localhost',
            is_primary=True
        )

        if public_domain:
            print_success("Dominio público 'localhost' creado")
        else:
            print_info("Dominio público 'localhost' ya existe")

        public_domain = Domain.objects.create(
            tenant=public_org,
            domain='tuvozenruta.com',
            is_primary=False
        )

        if public_domain:
            print_success("Dominio público 'tuvozenruta.com' creado")
        else:
            print_info("Dominio público 'tuvozenruta.com' ya existe")

        return True
    except Exception as e:
        print_error(f"Error al crear dominio público: {e}")
        return False

def create_organizations():
    """Crea organizaciones de prueba con sus dominios."""
    print_header("Paso 2: Creando organizaciones de prueba")
    
    organizations_data = [
        {
            'name': 'Alianza de Camioneros',
            'schema_name': 'alianza',
            'domains': [
                {'domain': 'alianza.localhost', 'is_primary': True},
                {'domain': 'alianza.tuvozenruta.com', 'is_primary': False},
            ]
        },
        {
            'name': 'Autobuses Rojos',
            'schema_name': 'autobusesrojos',
            'domains': [
                {'domain': 'autobusesrojos.localhost', 'is_primary': True},
                {'domain': 'autobusesrojos.tuvozenruta.com', 'is_primary': False},
            ]
        },
        {
            'name': 'Ruta Express',
            'schema_name': 'express',
            'domains': [
                {'domain': 'express.localhost', 'is_primary': True},
                {'domain': 'express.tuvozenruta.com', 'is_primary': False},
            ]
        },
    ]
    
    created_count = 0
    
    for org_data in organizations_data:
        try:
            # Verificar si la organización ya existe
            existing_org = Organization.objects.filter(
                schema_name=org_data['schema_name']
            ).first()
            
            if existing_org:
                print_info(f"Organización '{org_data['name']}' ya existe (schema: {org_data['schema_name']})")
                organization = existing_org
            else:
                # Crear la organización
                organization = Organization.objects.create(
                    name=org_data['name'],
                    schema_name=org_data['schema_name']
                )
                print_success(f"Organización creada: {org_data['name']} (schema: {org_data['schema_name']})")
                created_count += 1
            
            # Crear los dominios para esta organización
            for domain_data in org_data['domains']:
                existing_domain = Domain.objects.filter(
                    domain=domain_data['domain']
                ).first()
                
                if existing_domain:
                    print_info(f"  Dominio '{domain_data['domain']}' ya existe")
                else:
                    Domain.objects.create(
                        tenant=organization,
                        domain=domain_data['domain'],
                        is_primary=domain_data['is_primary']
                    )
                    primary_text = "(primario)" if domain_data['is_primary'] else ""
                    print_success(f"  Dominio creado: {domain_data['domain']} {primary_text}")
        
        except Exception as e:
            print_error(f"Error al crear organización '{org_data['name']}': {e}")
    
    print(f"\n✓ Total de organizaciones nuevas creadas: {created_count}")
    return True


def run_tenant_migrations():
    """Ejecuta las migraciones de todos los tenants."""
    print_header("Paso 3: Ejecutando migraciones de los tenants")
    
    try:
        # Obtener todas las organizaciones
        organizations = Organization.objects.exclude(schema_name='public')
        
        if not organizations.exists():
            print_info("No hay organizaciones (tenants) para migrar")
            return True
        
        print_info(f"Migrando {organizations.count()} tenant(s)...")
        
        # Ejecutar migraciones para todos los tenants
        call_command('migrate_schemas', verbosity=2)
        
        print_success("Migraciones de tenants completadas")
        return True
    except Exception as e:
        print_error(f"Error al ejecutar migraciones de tenants: {e}")
        return False


def verify_installation():
    """Verifica que la instalación sea correcta."""
    print_header("Paso 4: Verificando instalación")
    
    try:
        # Verificar organizaciones
        org_count = Organization.objects.exclude(schema_name='public').count()
        print_success(f"Organizaciones activas: {org_count}")
        
        # Verificar dominios
        domain_count = Domain.objects.count()
        print_success(f"Dominios configurados: {domain_count}")
        
        # Listar organizaciones con sus dominios
        print("\n" + "-" * 70)
        print("Organizaciones configuradas:")
        print("-" * 70)
        
        for org in Organization.objects.exclude(schema_name='public'):
            print(f"\n• {org.name} (schema: {org.schema_name})")
            domains = Domain.objects.filter(tenant=org)
            for domain in domains:
                primary_mark = "★" if domain.is_primary else " "
                print(f"  {primary_mark} {domain.domain}")
        
        print("\n" + "-" * 70)
        
        return True
    except Exception as e:
        print_error(f"Error al verificar instalación: {e}")
        return False


def main():
    """Función principal del script."""
    print_header("🚀 Inicialización de Base de Datos - Django Tenants")
    
    print_info("Este script inicializará la base de datos con:")
    print_info("  1. Esquema compartido (público)")
    print_info("  2. Organizaciones de prueba")
    print_info("  3. Esquemas de tenants")
    
    # Pedir confirmación
    response = input("\n¿Deseas continuar? (s/n): ").lower().strip()
    
    if response != 's':
        print("\nOperación cancelada.")
        sys.exit(0)
    
    # Ejecutar pasos
    steps = [
        ("Migraciones compartidas", run_shared_migrations),
        ("Creación de dominio público", create_public_domain),
        ("Creación de organizaciones", create_organizations),
        ("Migraciones de tenants", run_tenant_migrations),
        ("Verificación", verify_installation),
    ]
    
    for step_name, step_func in steps:
        success = step_func()
        if not success:
            print_error(f"El paso '{step_name}' falló. Abortando...")
            sys.exit(1)
    
    # Mensaje final
    print_header("✅ Inicialización completada exitosamente")
    
    print("\n📋 Próximos pasos:")
    print("  1. Accede al admin público: http://localhost:8000/super-admin/")
    print("  2. Accede al tenant 'alianza': http://alianza.localhost:8000/admin/")
    print("  3. Crea unidades y rutas en el admin del tenant")
    print("  4. Accede a la encuesta: http://alianza.localhost:8000/interview/")
    print("\n💡 Recuerda crear un superusuario si aún no tienes uno:")
    print("     python manage.py createsuperuser --schema=public")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperación interrumpida por el usuario.")
        sys.exit(0)
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)