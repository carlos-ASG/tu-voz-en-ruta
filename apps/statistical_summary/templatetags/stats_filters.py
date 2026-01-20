"""
Filtros custom para templates de statistical_summary.

Este módulo proporciona filtros reutilizables para serialización y
formateo de datos en templates Django.

Filtros disponibles:
    - tojson: Convierte objetos Python a JSON seguro para templates
"""
import json
from django import template
from django.utils.safestring import mark_safe
from dataclasses import asdict, is_dataclass

register = template.Library()


@register.filter(name='tojson')
def tojson(value):
    """
    Convierte un objeto Python a JSON formateado para usar en templates.
    
    Soporta automáticamente:
    - Diccionarios estándar
    - Listas y tuplas
    - Dataclasses (convierte automáticamente con asdict)
    - Tipos primitivos (str, int, float, bool, None)
    
    Características:
    - ensure_ascii=False: Preserva caracteres especiales (acentos, etc.)
    - mark_safe: Previene doble escapado de comillas por Django
    - Manejo automático de dataclasses
    
    Uso en templates:
        <!-- En atributos data-* -->
        <canvas data-values='{{ my_dict|tojson }}'></canvas>
        
        <!-- En tags script -->
        <script>
            const data = {{ my_object|tojson }};
            console.log(data);
        </script>
        
        <!-- Con Canvas y Chart.js -->
        <canvas id="myChart" data-config='{{ chart_config|tojson }}'></canvas>
    
    Args:
        value: Objeto Python a serializar a JSON
        
    Returns:
        str: JSON string marcado como safe para Django (no escapará comillas)
        
    Raises:
        TypeError: Si el objeto no es serializable a JSON
        
    Example:
        >>> # En Python
        >>> my_data = {'key': 'value', 'count': 42}
        >>> my_dataclass = TimelineData(dates=['2024-01-20'], counts=[5])
        
        >>> # En template después de {% load stats_filters %}
        >>> # Para dict:
        >>> tojson(my_data)
        '{"key": "value", "count": 42}'
        
        >>> # Para dataclass:
        >>> tojson(my_dataclass)
        '{"dates": ["2024-01-20"], "counts": [5]}'
    """
    try:
        # Si es un dataclass, convertirlo a dict primero
        if is_dataclass(value):
            value = asdict(value)
        
        # Serializar a JSON con caracteres especiales preservados
        json_str = json.dumps(value, ensure_ascii=False)
        
        # Marcar como safe para que Django no escape el JSON
        # Esto previene que comillas sean convertidas a &quot;
        return mark_safe(json_str)
    
    except TypeError as e:
        # Si el objeto no es serializable, retornar JSON con error
        error_msg = f"Error serializando a JSON: {str(e)}"
        return mark_safe(json.dumps({"error": error_msg}))
