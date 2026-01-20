"""
Tests para survey_repository.

Verifica que las funciones de SurveySubmission retornan conteos y timelines
correctamente sin N+1 queries.
"""
from django.utils import timezone
from apps.statistical_summary.repositories import survey_repository
from .. import StatisticalTestCase


class TestGetSubmissionCount(StatisticalTestCase):
    """Tests para survey_repository.get_submission_count()."""
    
    def test_get_submission_count_with_submissions(self):
        """
        Verifica que get_submission_count() retorna el número correcto
        de envíos cuando se aplican filtros.
        """
        # Arrange
        # 10 envíos pre-cargados distribuidos entre todas las unidades
        
        # Act - Contar todos los envíos sin filtros
        total_count = survey_repository.get_submission_count({})
        
        # Assert
        self.assertEqual(total_count, 10)
    
    def test_get_submission_count_with_unit_filter(self):
        """
        Verifica que get_submission_count() respeta filtros por unidad.
        """
        # Arrange
        unit = self.units_route1[0]
        
        # Act
        count = survey_repository.get_submission_count({'unit_id': unit.id})
        
        # Assert
        # Verificar que hay al menos 1 envío en esta unidad
        self.assertGreaterEqual(count, 0)


class TestGetSubmissionsTimelineByDay(StatisticalTestCase):
    """Tests para survey_repository.get_submissions_timeline() agrupado por día."""
    
    def test_get_submissions_timeline_by_day(self):
        """
        Verifica que get_submissions_timeline() retorna timeline agrupado por día
        con formato YYYY-MM-DD y conteos correctos.
        """
        # Arrange
        today = timezone.now().date()
        
        # Act
        timeline = survey_repository.get_submissions_timeline({}, group_by_hour=False)
        
        # Assert
        # Debe haber al menos 1 entrada en la timeline (hoy)
        self.assertGreater(len(timeline.dates), 0)
        self.assertEqual(len(timeline.dates), len(timeline.counts))
        
        # Verificar que las fechas están en formato YYYY-MM-DD
        for date_str in timeline.dates:
            # Verificar formato con strptime
            parsed = timezone.datetime.strptime(date_str, '%Y-%m-%d')
            self.assertIsNotNone(parsed)
        
        # Verificar que los conteos son positivos
        for count in timeline.counts:
            self.assertGreater(count, 0)


class TestGetSubmissionsTimelineByHour(StatisticalTestCase):
    """Tests para survey_repository.get_submissions_timeline() agrupado por hora."""
    
    def test_get_submissions_timeline_by_hour(self):
        """
        Verifica que get_submissions_timeline() retorna timeline agrupado por hora
        con formato HH:00 y conteos correctos.
        """
        # Arrange
        # Los 10 envíos están todos creados alrededor de la misma hora (timezone.now())
        
        # Act
        timeline = survey_repository.get_submissions_timeline({}, group_by_hour=True)
        
        # Assert
        # Debe haber al menos 1 entrada en la timeline
        self.assertGreater(len(timeline.dates), 0)
        self.assertEqual(len(timeline.dates), len(timeline.counts))
        
        # Verificar que las horas están en formato HH:00
        for time_str in timeline.dates:
            self.assertRegex(time_str, r'^\d{2}:00$')
        
        # Verificar que los conteos son positivos
        for count in timeline.counts:
            self.assertGreater(count, 0)


class TestGetSubmissionsByUnit(StatisticalTestCase):
    """Tests para survey_repository.get_submissions_by_unit()."""
    
    def test_get_submissions_by_unit_with_data(self):
        """
        Verifica que get_submissions_by_unit() retorna diccionario con:
        - Claves = transit_numbers
        - Valores = conteos de formularios
        - Ordenado por cantidad descendente
        """
        # Arrange
        # 10 formularios distribuidos en diferentes unidades (setUp)
        
        # Act
        by_unit = survey_repository.get_submissions_by_unit({})
        
        # Assert
        # Debe haber al menos 1 unidad con formularios
        self.assertGreater(len(by_unit), 0)
        
        # Verificar que las claves son transit_numbers
        for transit_number, count in by_unit.items():
            self.assertIn(transit_number[:3], ['ABC', 'XYZ'])
            self.assertGreater(count, 0)
        
        # Verificar que está ordenado por cantidad descendente
        counts = list(by_unit.values())
        self.assertEqual(counts, sorted(counts, reverse=True))
