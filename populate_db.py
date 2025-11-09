#!/usr/bin/env python
"""
Script para poblar la base de datos con datos de prueba.

Este script crea para cada tenant:
1. Rutas de transporte
2. Unidades (camiones) asignadas a rutas
3. Preguntas de encuesta (todos los tipos)
4. Motivos de queja

Uso:
    python populate_db.py

Requisitos:
    - Base de datos inicializada con start_db.py
    - Organizaciones (tenants) creadas
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

from django_tenants.utils import schema_context
from apps.organization.models import Organization
from apps.transport.models import Route, Unit
from apps.interview.models import Question, QuestionOption, ComplaintReason


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


def create_routes(schema_name, org_name):
    """Crea rutas de transporte para una organización."""
    routes_data = [
        {'name': 'Ruta Centro-Norte', 'metadata': {'horario': '06:00-22:00', 'frecuencia': '10 min'}},
        {'name': 'Ruta Sur-Poniente', 'metadata': {'horario': '05:30-23:00', 'frecuencia': '15 min'}},
        {'name': 'Ruta Oriente-Centro', 'metadata': {'horario': '06:00-21:30', 'frecuencia': '12 min'}},
        {'name': 'Ruta Periférico', 'metadata': {'horario': '05:00-00:00', 'frecuencia': '20 min'}},
        {'name': 'Ruta Express Aeropuerto', 'metadata': {'horario': '04:00-23:00', 'frecuencia': '30 min'}},
    ]
    
    created_routes = []
    
    with schema_context(schema_name):
        for route_data in routes_data:
            # Verificar si la ruta ya existe
            existing_route = Route.objects.filter(name=route_data['name']).first()
            
            if existing_route:
                print_info(f"  Ruta '{route_data['name']}' ya existe")
                created_routes.append(existing_route)
            else:
                route = Route.objects.create(**route_data)
                print_success(f"  Ruta creada: {route_data['name']}")
                created_routes.append(route)
    
    return created_routes


def create_units(schema_name, org_name, routes):
    """Crea unidades (camiones) para una organización."""
    # Prefijos de números de tránsito según la organización
    prefix_map = {
        'alianza': 'AC',
        'autobusesrojos': 'AR',
        'express': 'EX',
    }
    
    prefix = prefix_map.get(schema_name, 'UN')
    
    units_count = 0
    
    with schema_context(schema_name):
        # Crear 8-12 unidades por ruta
        for route in routes:
            units_per_route = 10
            
            for i in range(1, units_per_route + 1):
                transit_number = f"{prefix}-{route.name[:3].upper()}-{i:03d}"
                internal_number = f"{i:04d}"
                
                # Verificar si la unidad ya existe
                existing_unit = Unit.objects.filter(transit_number=transit_number).first()
                
                if existing_unit:
                    continue
                
                # Alternar propietarios
                owners = [
                    'Juan Pérez López',
                    'María García Rodríguez',
                    'Carlos Hernández Martínez',
                    'Ana Sánchez Gómez',
                    'Luis Ramírez Torres',
                ]
                
                unit = Unit.objects.create(
                    transit_number=transit_number,
                    internal_number=internal_number,
                    owner=owners[i % len(owners)],
                    route=route,
                    metadata={
                        'año_modelo': 2018 + (i % 6),
                        'capacidad': 40,
                        'tipo': 'Estándar',
                    }
                )
                units_count += 1
        
        print_success(f"  {units_count} unidades creadas")
    
    return units_count


def create_questions(schema_name, org_name):
    """Crea preguntas de encuesta para una organización."""
    questions_data = [
        # Preguntas tipo RATING
        {
            'text': '¿Qué tan satisfecho estás con el servicio de transporte?',
            'type': Question.QuestionType.RATING,
            'position': 1,
            'options': []
        },
        {
            'text': '¿Cómo calificarías la limpieza de la unidad?',
            'type': Question.QuestionType.RATING,
            'position': 2,
            'options': []
        },
        {
            'text': '¿Qué tan puntual fue el servicio?',
            'type': Question.QuestionType.RATING,
            'position': 3,
            'options': []
        },
        {
            'text': '¿Cómo calificarías la conducción del operador?',
            'type': Question.QuestionType.RATING,
            'position': 4,
            'options': []
        },
        
        # Preguntas tipo CHOICE
        {
            'text': '¿Con qué frecuencia utilizas este servicio?',
            'type': Question.QuestionType.CHOICE,
            'position': 5,
            'options': [
                {'text': 'Diariamente', 'position': 1},
                {'text': '3-4 veces por semana', 'position': 2},
                {'text': '1-2 veces por semana', 'position': 3},
                {'text': 'Ocasionalmente', 'position': 4},
                {'text': 'Primera vez', 'position': 5},
            ]
        },
        {
            'text': '¿Cuál es el principal motivo de tu viaje?',
            'type': Question.QuestionType.CHOICE,
            'position': 6,
            'options': [
                {'text': 'Trabajo', 'position': 1},
                {'text': 'Escuela', 'position': 2},
                {'text': 'Compras', 'position': 3},
                {'text': 'Entretenimiento', 'position': 4},
                {'text': 'Salud', 'position': 5},
                {'text': 'Otro', 'position': 6},
            ]
        },
        
        # Preguntas tipo MULTI_CHOICE
        {
            'text': '¿Qué aspectos del servicio consideras más importantes? (Selecciona todos los que apliquen)',
            'type': Question.QuestionType.MULTI_CHOICE,
            'position': 7,
            'options': [
                {'text': 'Puntualidad', 'position': 1},
                {'text': 'Limpieza', 'position': 2},
                {'text': 'Seguridad', 'position': 3},
                {'text': 'Amabilidad del conductor', 'position': 4},
                {'text': 'Precio', 'position': 5},
                {'text': 'Comodidad', 'position': 6},
            ]
        },
        {
            'text': '¿Qué mejoras te gustaría ver en el servicio? (Selecciona todas las que apliquen)',
            'type': Question.QuestionType.MULTI_CHOICE,
            'position': 8,
            'options': [
                {'text': 'Más frecuencia de unidades', 'position': 1},
                {'text': 'Aire acondicionado', 'position': 2},
                {'text': 'WiFi gratuito', 'position': 3},
                {'text': 'Puertos USB para cargar dispositivos', 'position': 4},
                {'text': 'Mejor iluminación', 'position': 5},
                {'text': 'Mejor ventilación', 'position': 6},
                {'text': 'Más limpieza', 'position': 7},
            ]
        },
        
        # Pregunta tipo TEXT
        {
            'text': '¿Tienes algún comentario o sugerencia adicional?',
            'type': Question.QuestionType.TEXT,
            'position': 9,
            'options': []
        },
    ]
    
    questions_count = 0
    
    with schema_context(schema_name):
        for question_data in questions_data:
            # Verificar si la pregunta ya existe
            existing_question = Question.objects.filter(
                text=question_data['text']
            ).first()
            
            if existing_question:
                print_info(f"  Pregunta '{question_data['text'][:50]}...' ya existe")
                continue
            
            # Crear la pregunta
            options_data = question_data.pop('options', [])
            question = Question.objects.create(**question_data)
            
            # Crear opciones si existen
            for option_data in options_data:
                QuestionOption.objects.create(
                    question=question,
                    **option_data
                )
            
            type_label = dict(Question.QuestionType.choices)[question_data['type']]
            print_success(f"  Pregunta creada: [{type_label}] {question_data['text'][:50]}...")
            questions_count += 1
    
    return questions_count


def create_complaint_reasons(schema_name, org_name):
    """Crea motivos de queja para una organización."""
    reasons_data = [
        'Mal trato del operador',
        'Conducción peligrosa o imprudente',
        'Unidad en malas condiciones',
        'Unidad sucia',
        'Retraso excesivo',
        'No respetó paradas',
        'Operador hablando por teléfono',
        'Música a volumen muy alto',
        'Exceso de velocidad',
        'Cobro incorrecto',
        'No dio cambio',
        'Asientos rotos o dañados',
        'Mal olor en la unidad',
        'Acoso o comportamiento inapropiado',
        'Otro',
    ]
    
    reasons_count = 0
    
    with schema_context(schema_name):
        for reason_label in reasons_data:
            # Verificar si el motivo ya existe
            existing_reason = ComplaintReason.objects.filter(label=reason_label).first()
            
            if existing_reason:
                continue
            
            ComplaintReason.objects.create(label=reason_label)
            reasons_count += 1
        
        print_success(f"  {reasons_count} motivos de queja creados")
    
    return reasons_count


def populate_tenant(organization):
    """Pobla un tenant con datos de prueba."""
    schema_name = organization.schema_name
    org_name = organization.name
    
    print_header(f"Poblando tenant: {org_name} (schema: {schema_name})")
    
    try:
        # 1. Crear rutas
        print_info("Creando rutas...")
        routes = create_routes(schema_name, org_name)
        
        # 2. Crear unidades
        print_info("Creando unidades...")
        units_count = create_units(schema_name, org_name, routes)
        
        # 3. Crear preguntas
        print_info("Creando preguntas de encuesta...")
        questions_count = create_questions(schema_name, org_name)
        
        # 4. Crear motivos de queja
        print_info("Creando motivos de queja...")
        reasons_count = create_complaint_reasons(schema_name, org_name)
        
        print_success(f"\nResumen para '{org_name}':")
        print_success(f"  - Rutas: {len(routes)}")
        print_success(f"  - Unidades: {units_count}")
        print_success(f"  - Preguntas: {questions_count}")
        print_success(f"  - Motivos de queja: {reasons_count}")
        
        return True
    except Exception as e:
        print_error(f"Error al poblar tenant '{org_name}': {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Función principal del script."""
    print_header("🌱 Poblando Base de Datos con Datos de Prueba")
    
    # Obtener todas las organizaciones (excluyendo el esquema público)
    organizations = Organization.objects.exclude(schema_name='public')
    
    if not organizations.exists():
        print_error("No se encontraron organizaciones (tenants) en la base de datos.")
        print_info("Ejecuta primero: python start_db.py")
        sys.exit(1)
    
    print_info(f"Se encontraron {organizations.count()} organización(es):")
    for org in organizations:
        print_info(f"  • {org.name} (schema: {org.schema_name})")
    
    # Pedir confirmación
    response = input("\n¿Deseas poblar estas organizaciones con datos de prueba? (s/n): ").lower().strip()
    
    if response != 's':
        print("\nOperación cancelada.")
        sys.exit(0)
    
    # Poblar cada tenant
    success_count = 0
    failed_count = 0
    
    for organization in organizations:
        success = populate_tenant(organization)
        if success:
            success_count += 1
        else:
            failed_count += 1
    
    # Resumen final
    print_header("📊 Resumen de Población de Datos")
    
    print_success(f"Organizaciones pobladas exitosamente: {success_count}")
    
    if failed_count > 0:
        print_error(f"Organizaciones con errores: {failed_count}")
    
    print("\n📋 Próximos pasos:")
    print("  1. Accede al admin del tenant: http://alianza.localhost:8000/admin/")
    print("  2. Verifica que las rutas, unidades y preguntas se hayan creado")
    print("  3. Genera códigos QR: http://alianza.localhost:8000/qr-generator/")
    print("  4. Escanea un QR para probar la encuesta")
    print("\n💡 Recuerda crear un superusuario para el tenant si aún no tienes uno:")
    print("     python manage.py shell")
    print("     >>> from django_tenants.utils import schema_context")
    print("     >>> from django.contrib.auth.models import User")
    print("     >>> from apps.organization.models import Organization")
    print("     >>> org = Organization.objects.get(schema_name='alianza')")
    print("     >>> with schema_context(org.schema_name):")
    print("     ...     User.objects.create_superuser('admin', 'admin@alianza.com', 'admin123')")
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
