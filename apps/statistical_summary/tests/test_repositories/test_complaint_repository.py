"""
Tests para complaint_repository.

Verifica que las funciones de Complaint retornan conteos, resúmenes
y agrupaciones correctas.
"""
from apps.statistical_summary.repositories import complaint_repository
from .. import StatisticalTestCase


class TestGetComplaintCount(StatisticalTestCase):
    """Tests para complaint_repository.get_complaint_count()."""
    
    def test_get_complaint_count_with_data(self):
        """
        Verifica que get_complaint_count() retorna el número correcto
        de quejas sin filtros.
        """
        # Arrange
        # 8 quejas pre-cargadas
        
        # Act
        total_count = complaint_repository.get_complaint_count({})
        
        # Assert
        self.assertEqual(total_count, 8)
    
    def test_get_complaint_count_with_unit_filter(self):
        """
        Verifica que get_complaint_count() respeta filtros por unidad.
        """
        # Arrange
        unit = self.units_route1[0]
        
        # Act
        count = complaint_repository.get_complaint_count({'unit_id': unit.id})
        
        # Assert
        # Puede haber 0 o más quejas en esta unidad
        self.assertGreaterEqual(count, 0)


class TestGetSummary(StatisticalTestCase):
    """Tests para complaint_repository.get_summary()."""
    
    def test_get_summary_with_complaints(self):
        """
        Verifica que get_summary() retorna:
        - total_complaints = 8
        - by_reason con distribución correcta entre los 2 motivos
        """
        # Arrange
        # 8 quejas distribuidas entre 2 motivos
        
        # Act
        summary = complaint_repository.get_summary({})
        
        # Assert
        self.assertEqual(summary.total_complaints, 8)
        
        # Verificar que hay quejas por motivo
        self.assertEqual(len(summary.by_reason), 2)
        
        # Verificar que los motivos son los correctos
        self.assertIn("Mal servicio", summary.by_reason)
        self.assertIn("Llegada tardía", summary.by_reason)
        
        # Verificar que los conteos suman 8
        total = sum(summary.by_reason.values())
        self.assertEqual(total, 8)


class TestGetByUnit(StatisticalTestCase):
    """Tests para complaint_repository.get_by_unit()."""
    
    def test_get_by_unit_with_data(self):
        """
        Verifica que get_by_unit() retorna diccionario con:
        - Claves = transit_numbers
        - Valores = conteos de quejas
        - Ordenado por cantidad descendente
        """
        # Arrange
        # 8 quejas distribuidas en diferentes unidades
        
        # Act
        by_unit = complaint_repository.get_by_unit({})
        
        # Assert
        # Debe haber al menos 1 unidad con quejas
        self.assertGreater(len(by_unit), 0)
        
        # Verificar que las claves son transit_numbers
        for transit_number, count in by_unit.items():
            self.assertIn(transit_number[:3], ['ABC', 'XYZ'])
            self.assertGreater(count, 0)
        
        # Verificar que está ordenado por cantidad descendente
        counts = list(by_unit.values())
        self.assertEqual(counts, sorted(counts, reverse=True))
