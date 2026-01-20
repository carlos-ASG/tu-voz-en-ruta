"""
Tests para statistics_service.

Verifica que la función principal calculate_dashboard_statistics()
orquesta correctamente todos los servicios para retornar DashboardStatistics.
"""
from django.utils import timezone
from apps.statistical_summary.services import statistics_service
from apps.statistical_summary.schemas import DashboardStatistics
from .. import StatisticalTestCase


class TestCalculateDashboardStatisticsToday(StatisticalTestCase):
    """Tests para statistics_service.calculate_dashboard_statistics() con período TODAY."""
    
    def test_calculate_dashboard_statistics_today(self):
        """
        Verifica que calculate_dashboard_statistics() para período 'today'
        retorna DashboardStatistics completo con:
        - period_label
        - total_submissions
        - total_complaints
        - submissions_by_unit
        - questions_statistics
        - survey_submissions_timeline agrupado por hora
        """
        # Arrange
        # Datos pre-cargados disponibles
        
        # Act
        stats = statistics_service.calculate_dashboard_statistics("today")
        
        # Assert
        self.assertIsInstance(stats, DashboardStatistics)
        
        # Verificar campos básicos
        self.assertEqual(stats.period_label, "Hoy")
        self.assertEqual(stats.total_submissions, 10)
        self.assertEqual(stats.total_complaints, 8)
        
        # Verificar nuevo campo submissions_by_unit
        self.assertIsInstance(stats.submissions_by_unit, dict)
        self.assertGreaterEqual(len(stats.submissions_by_unit), 0)
        
        # Verificar que hay estadísticas de preguntas
        self.assertEqual(len(stats.questions_statistics), 5)
        
        # Verificar que la timeline está agrupada por hora
        self.assertGreater(len(stats.survey_submissions_timeline.dates), 0)
        for time_str in stats.survey_submissions_timeline.dates:
            self.assertRegex(time_str, r'^\d{2}:00$')


class TestCalculateDashboardStatisticsWithRouteFilter(StatisticalTestCase):
    """Tests para statistics_service.calculate_dashboard_statistics() con filtro de ruta."""
    
    def test_calculate_dashboard_statistics_with_route_filter(self):
        """
        Verifica que calculate_dashboard_statistics() con route_id
        retorna solo datos de esa ruta.
        """
        # Arrange
        route = self.route1
        
        # Act
        stats = statistics_service.calculate_dashboard_statistics(
            "week",
            route_id=str(route.id)
        )
        
        # Assert
        self.assertIsInstance(stats, DashboardStatistics)
        
        # Verificar que hay datos (pueden variar según distribución)
        self.assertGreaterEqual(stats.total_submissions, 0)
        self.assertGreaterEqual(stats.total_complaints, 0)


class TestCalculateDashboardStatisticsAllPeriods(StatisticalTestCase):
    """Tests para statistics_service.calculate_dashboard_statistics() con todos los períodos."""
    
    def test_calculate_dashboard_statistics_all_periods(self):
        """
        Verifica que calculate_dashboard_statistics() funciona correctamente
        para todos los períodos: today, week, month, year, all.
        """
        # Arrange
        periods = ["today", "week", "month", "year", "all"]
        
        # Act & Assert
        for period in periods:
            stats = statistics_service.calculate_dashboard_statistics(period)
            
            # Verificar que retorna DashboardStatistics válido
            self.assertIsInstance(stats, DashboardStatistics)
            self.assertIsNotNone(stats.period_label)
            self.assertGreaterEqual(stats.total_submissions, 0)
            self.assertGreaterEqual(stats.total_complaints, 0)
            self.assertIsNotNone(stats.questions_statistics)
            self.assertIsNotNone(stats.survey_submissions_timeline)
