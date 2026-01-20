"""
Tests para templatetags de statistical_summary.

Verifica que los filtros custom funcionan correctamente con diferentes
tipos de datos, incluyendo dataclasses y caracteres especiales.
"""
import json
from django.test import TestCase
from django.utils.safestring import SafeString

from apps.statistical_summary.templatetags.stats_filters import tojson
from apps.statistical_summary.schemas import TimelineData


class TestTojsonFilter(TestCase):
    """Tests para el filtro tojson."""
    
    def test_tojson_converts_dict_to_json(self):
        """
        Verifica que tojson convierte un diccionario a JSON válido.
        """
        # Arrange
        test_dict = {'key': 'value', 'count': 42, 'active': True}
        
        # Act
        result = tojson(test_dict)
        
        # Assert
        self.assertIsInstance(result, SafeString)
        # Verificar que es JSON válido
        parsed = json.loads(str(result))
        self.assertEqual(parsed['key'], 'value')
        self.assertEqual(parsed['count'], 42)
        self.assertEqual(parsed['active'], True)
    
    def test_tojson_converts_list_to_json(self):
        """
        Verifica que tojson convierte una lista a JSON.
        """
        # Arrange
        test_list = ['one', 'two', 'three', 42]
        
        # Act
        result = tojson(test_list)
        
        # Assert
        self.assertIsInstance(result, SafeString)
        parsed = json.loads(str(result))
        self.assertEqual(parsed, ['one', 'two', 'three', 42])
    
    def test_tojson_converts_dataclass_to_json(self):
        """
        Verifica que tojson convierte dataclasses automáticamente.
        """
        # Arrange
        timeline = TimelineData(
            dates=['2024-01-20', '2024-01-21'],
            counts=[5, 10]
        )
        
        # Act
        result = tojson(timeline)
        
        # Assert
        self.assertIsInstance(result, SafeString)
        parsed = json.loads(str(result))
        self.assertEqual(parsed['dates'], ['2024-01-20', '2024-01-21'])
        self.assertEqual(parsed['counts'], [5, 10])
    
    def test_tojson_handles_spanish_characters(self):
        """
        Verifica que tojson preserva caracteres especiales y acentos.
        """
        # Arrange
        test_dict = {
            'nombre': 'Estadísticas',
            'descripción': 'Análisis de quejas',
            'ubicación': 'México'
        }
        
        # Act
        result = tojson(test_dict)
        
        # Assert
        result_str = str(result)
        # Verificar que contiene caracteres acentuados (no escapados)
        self.assertIn('Estadísticas', result_str)
        self.assertIn('Análisis', result_str)
        self.assertIn('México', result_str)
        # Verificar que no está escapado como \u00e9
        self.assertNotIn('\\u', result_str)
    
    def test_tojson_handles_nested_structures(self):
        """
        Verifica que tojson maneja estructuras anidadas correctamente.
        """
        # Arrange
        nested = {
            'complaints': {
                'Mal servicio': 10,
                'Llegada tardía': 5
            },
            'units': [
                {'transit_number': 'ABC001', 'count': 3},
                {'transit_number': 'ABC002', 'count': 2}
            ]
        }
        
        # Act
        result = tojson(nested)
        
        # Assert
        parsed = json.loads(str(result))
        self.assertEqual(parsed['complaints']['Mal servicio'], 10)
        self.assertEqual(parsed['units'][0]['transit_number'], 'ABC001')
    
    def test_tojson_returns_safestring(self):
        """
        Verifica que tojson retorna SafeString para prevenir escapado.
        """
        # Arrange
        test_dict = {'key': 'value'}
        
        # Act
        result = tojson(test_dict)
        
        # Assert
        self.assertIsInstance(result, SafeString)
        # Verificar que Django no escapará comillas
        self.assertNotIn('&quot;', str(result))
    
    def test_tojson_handles_empty_dict(self):
        """
        Verifica que tojson maneja diccionarios vacíos.
        """
        # Arrange
        empty_dict = {}
        
        # Act
        result = tojson(empty_dict)
        
        # Assert
        parsed = json.loads(str(result))
        self.assertEqual(parsed, {})
    
    def test_tojson_handles_empty_list(self):
        """
        Verifica que tojson maneja listas vacías.
        """
        # Arrange
        empty_list = []
        
        # Act
        result = tojson(empty_list)
        
        # Assert
        parsed = json.loads(str(result))
        self.assertEqual(parsed, [])
    
    def test_tojson_handles_numeric_values(self):
        """
        Verifica que tojson preserva tipos numéricos.
        """
        # Arrange
        test_dict = {
            'int_value': 42,
            'float_value': 3.14159,
            'negative': -10
        }
        
        # Act
        result = tojson(test_dict)
        
        # Assert
        parsed = json.loads(str(result))
        self.assertEqual(parsed['int_value'], 42)
        self.assertAlmostEqual(parsed['float_value'], 3.14159, places=5)
        self.assertEqual(parsed['negative'], -10)
    
    def test_tojson_handles_boolean_values(self):
        """
        Verifica que tojson preserva booleanos.
        """
        # Arrange
        test_dict = {
            'active': True,
            'inactive': False
        }
        
        # Act
        result = tojson(test_dict)
        
        # Assert
        parsed = json.loads(str(result))
        self.assertTrue(parsed['active'])
        self.assertFalse(parsed['inactive'])
    
    def test_tojson_handles_none_values(self):
        """
        Verifica que tojson maneja valores None correctamente.
        """
        # Arrange
        test_dict = {
            'value': None,
            'other': 'data'
        }
        
        # Act
        result = tojson(test_dict)
        
        # Assert
        parsed = json.loads(str(result))
        self.assertIsNone(parsed['value'])
        self.assertEqual(parsed['other'], 'data')
    
    def test_tojson_handles_non_serializable_gracefully(self):
        """
        Verifica que tojson maneja objetos no serializables sin crash.
        """
        # Arrange
        class CustomObject:
            pass
        
        test_dict = {'obj': CustomObject()}
        
        # Act
        result = tojson(test_dict)
        
        # Assert
        # No debe lanzar excepción, debe retornar error JSON
        self.assertIsInstance(result, SafeString)
        parsed = json.loads(str(result))
        self.assertIn('error', parsed)
