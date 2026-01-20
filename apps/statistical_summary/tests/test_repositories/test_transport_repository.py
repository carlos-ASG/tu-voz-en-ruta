"""
Tests para transport_repository.

Verifica que la función get_filter_data() retorna rutas y unidades
correctamente formateadas para los filtros del dashboard.
"""
from apps.statistical_summary.repositories import transport_repository
from .. import StatisticalTestCase


class TestGetFilterData(StatisticalTestCase):
    """Tests para transport_repository.get_filter_data()."""
    
    def test_get_filter_data_returns_routes_and_units(self):
        """
        Verifica que get_filter_data() retorna:
        - 2 rutas
        - 20 unidades
        - Datos en formato correcto (FilterData con RouteData y UnitData)
        """
        # Arrange
        # Los datos ya están pre-cargados en StatisticalTestCase.setUp()
        
        # Act
        filter_data = transport_repository.get_filter_data()
        
        # Assert
        # Verificar que se retornan 2 rutas
        self.assertEqual(len(filter_data.routes), 2)
        self.assertEqual(filter_data.routes[0].name, "Ruta Centro-Norte")
        self.assertEqual(filter_data.routes[1].name, "Ruta Este-Oeste")
        
        # Verificar que se retornan 20 unidades
        self.assertEqual(len(filter_data.units), 20)
        
        # Verificar que las unidades están ordenadas correctamente
        transit_numbers = [u.transit_number for u in filter_data.units]
        expected_numbers = [f"ABC{i:03d}" for i in range(1, 11)] + \
                          [f"XYZ{i:03d}" for i in range(1, 11)]
        self.assertEqual(transit_numbers, sorted(expected_numbers))
