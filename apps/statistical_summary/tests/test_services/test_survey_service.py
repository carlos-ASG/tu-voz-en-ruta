"""
Tests para survey_service.

Verifica que las funciones de lógica de negocio para encuestas
deleguen correctamente al repository y procesen los datos.
"""
from django.utils import timezone
from apps.statistical_summary.services import survey_service
from .. import StatisticalTestCase


class TestGetSubmissionTotal(StatisticalTestCase):
    """Tests para survey_service.get_submission_total()."""
    
    def test_get_submission_total_with_submissions(self):
        """
        Verifica que get_submission_total() retorna el total correcto
        de envíos delegando al repository.
        """
        # Arrange
        # 10 envíos pre-cargados
        
        # Act
        total = survey_service.get_submission_total({})
        
        # Assert
        self.assertEqual(total, 10)


class TestGetTimelineData(StatisticalTestCase):
    """Tests para survey_service.get_timeline_data()."""
    
    def test_get_timeline_data_by_hour(self):
        """
        Verifica que get_timeline_data() con group_by_hour=True retorna
        timeline agrupado por hora con formato correcto.
        """
        # Arrange
        # Los 10 envíos están creados alrededor de la misma hora
        
        # Act
        timeline = survey_service.get_timeline_data({}, group_by_hour=True)
        
        # Assert
        # Debe haber al menos 1 hora con envíos
        self.assertGreater(len(timeline.dates), 0)
        self.assertEqual(len(timeline.dates), len(timeline.counts))
        
        # Verificar que las horas están en formato HH:00
        for time_str in timeline.dates:
            self.assertRegex(time_str, r'^\d{2}:00$')
    
    def test_get_timeline_data_by_day(self):
        """
        Verifica que get_timeline_data() con group_by_hour=False retorna
        timeline agrupado por día con formato correcto.
        """
        # Arrange
        # Los 10 envíos están creados alrededor de hoy
        
        # Act
        timeline = survey_service.get_timeline_data({}, group_by_hour=False)
        
        # Assert
        # Debe haber al menos 1 día con envíos
        self.assertGreater(len(timeline.dates), 0)
        self.assertEqual(len(timeline.dates), len(timeline.counts))
        
        # Verificar que las fechas están en formato YYYY-MM-DD
        for date_str in timeline.dates:
            parsed = timezone.datetime.strptime(date_str, '%Y-%m-%d')
            self.assertIsNotNone(parsed)
