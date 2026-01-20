"""
Tests para complaints_service.

Verifica que las funciones de lógica de negocio para quejas
deleguen correctamente al repository y procesen los datos.
"""
from apps.statistical_summary.services import complaints_service
from .. import StatisticalTestCase


class TestGetComplaintsData(StatisticalTestCase):
    """Tests para complaints_service.get_complaints_data()."""
    
    def test_get_complaints_data_with_complaints(self):
        """
        Verifica que get_complaints_data() retorna ComplaintsSummary con:
        - total_complaints = 8
        - by_reason con 2 motivos
        """
        # Arrange
        # 8 quejas pre-cargadas distribuidas entre 2 motivos
        
        # Act
        summary = complaints_service.get_complaints_data({})
        
        # Assert
        self.assertEqual(summary.total_complaints, 8)
        
        # Verificar que hay quejas por motivo
        self.assertEqual(len(summary.by_reason), 2)
        self.assertIn("Mal servicio", summary.by_reason)
        self.assertIn("Llegada tardía", summary.by_reason)
        
        # Verificar que los conteos suman 8
        total = sum(summary.by_reason.values())
        self.assertEqual(total, 8)


class TestGetComplaintsByUnitData(StatisticalTestCase):
    """Tests para complaints_service.get_complaints_by_unit_data()."""
    
    def test_get_complaints_by_unit_data_with_complaints(self):
        """
        Verifica que get_complaints_by_unit_data() retorna diccionario con:
        - Claves = transit_numbers
        - Valores = conteos de quejas
        - Ordenado descendente por cantidad
        """
        # Arrange
        # 8 quejas distribuidas en diferentes unidades
        
        # Act
        by_unit = complaints_service.get_complaints_by_unit_data({})
        
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
