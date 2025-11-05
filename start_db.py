#!/usr/bin/env python
"""
Script de inicialización de base de datos para django-tenants.

Este script:
1. Ejecuta las migraciones del esquema compartido (público)
2. Crea la organización pública con sus dominios

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


def create_public_tenant():
    """Crea la organización pública con sus dominios si no existe."""
    print_header("Paso 2: Creando tenant público")
    
    try:
        # Verificar si la organización pública ya existe
        public_org = Organization.objects.filter(schema_name='public').first()
        
        if public_org:
            print_info("Organización pública ya existe")
        else:
            # Crear la organización pública
            public_org = Organization.objects.create(
                name='Público',
                schema_name='public'
            )
            print_success("Organización pública creada")
        
        # Crear dominio tuvozenruta.com como PRIMARIO (producción)
        main_domain = Domain.objects.filter(domain='tuvozenruta.com').first()
        
        if main_domain:
            print_info("Dominio 'tuvozenruta.com' ya existe")
        else:
            Domain.objects.create(
                tenant=public_org,
                domain='tuvozenruta.com',
                is_primary=True  # ← Cambiado a primario
            )
            print_success("Dominio 'tuvozenruta.com' creado (primario)")
        
        # Crear dominio localhost como SECUNDARIO (desarrollo)
        localhost_domain = Domain.objects.filter(domain='localhost').first()
        
        if localhost_domain:
            print_info("Dominio 'localhost' ya existe")
        else:
            Domain.objects.create(
                tenant=public_org,
                domain='localhost',
                is_primary=False  # ← Cambiado a secundario
            )
            print_success("Dominio 'localhost' creado (alias para desarrollo)")
        
        return True
    except Exception as e:
        print_error(f"Error al crear tenant público: {e}")
        import traceback
        traceback.print_exc()
        return False





def verify_installation():
    """Verifica que la instalación sea correcta."""
    print_header("Paso 3: Verificando instalación")
    
    try:
        # Verificar organización pública
        public_org = Organization.objects.filter(schema_name='public').first()
        
        if not public_org:
            print_error("No se encontró la organización pública")
            return False
        
        print_success(f"Organización pública: {public_org.name}")
        
        # Verificar dominios públicos
        public_domains = Domain.objects.filter(tenant=public_org)
        print_success(f"Dominios configurados: {public_domains.count()}")
        
        # Listar dominios públicos
        print("\n" + "-" * 70)
        print("Dominios del tenant público:")
        print("-" * 70)
        
        for domain in public_domains:
            primary_mark = "★" if domain.is_primary else " "
            print(f"  {primary_mark} {domain.domain}")
        
        print("\n" + "-" * 70)
        
        return True
    except Exception as e:
        print_error(f"Error al verificar instalación: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Función principal del script."""
    print_header("🚀 Inicialización de Base de Datos - Django Tenants")
    
    print_info("Este script inicializará la base de datos con:")
    print_info("  1. Esquema compartido (público)")
    print_info("  2. Organización pública con dominios")
    print()
    
    # Ejecutar pasos
    steps = [
        ("Migraciones compartidas", run_shared_migrations),
        ("Creación de tenant público", create_public_tenant),
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
    print("  1. Crea un superusuario para el esquema público:")
    print("     python manage.py createsuperuser --schema=public")
    print("\n  2. Accede al admin público:")
    print("     http://localhost:8000/super-admin/")
    print("\n  3. Crea organizaciones (tenants) desde el admin público")
    print("\n  4. Pobla las organizaciones con datos de prueba:")
    print("     python populate_db.py")
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