"""
Tests para questions_service.

Verifica que las funciones de lógica de negocio para preguntas
calculan correctamente estadísticas según el tipo de pregunta.
"""
from django.utils import timezone
from apps.statistical_summary.services import questions_service
from .. import StatisticalTestCase


class TestGetQuestionsStatisticsRating(StatisticalTestCase):
    """Tests para questions_service.get_questions_statistics() con RATING."""
    
    def test_get_questions_statistics_with_rating_question(self):
        """
        Verifica que get_questions_statistics() retorna estadísticas correctas
        para preguntas tipo RATING con promedio calculado.
        """
        # Arrange
        # 5 preguntas activas incluyendo 1 RATING con 10 respuestas
        
        # Act
        stats = questions_service.get_questions_statistics(None)
        
        # Assert
        self.assertIn("¿Cómo califica el servicio?", stats)
        
        rating_stat = stats["¿Cómo califica el servicio?"]
        self.assertEqual(rating_stat.type, "calificación")
        
        # Verificar que el summary es un promedio en formato "X.X/5"
        self.assertRegex(rating_stat.summary, r'^\d+\.\d+/5$')


class TestGetQuestionsStatisticsChoice(StatisticalTestCase):
    """Tests para questions_service.get_questions_statistics() con CHOICE."""
    
    def test_get_questions_statistics_with_choice_question(self):
        """
        Verifica que get_questions_statistics() retorna estadísticas correctas
        para preguntas tipo CHOICE con conteos por opción.
        """
        # Arrange
        # 2 preguntas CHOICE con opciones predefinidas
        
        # Act
        stats = questions_service.get_questions_statistics(None)
        
        # Assert
        self.assertIn("¿El conductor fue amable?", stats)
        
        choice_stat = stats["¿El conductor fue amable?"]
        self.assertEqual(choice_stat.type, "opción")
        
        # Verificar que el summary es un diccionario
        self.assertIsInstance(choice_stat.summary, dict)
        self.assertIn("Sí", choice_stat.summary)
        self.assertIn("No", choice_stat.summary)


class TestGetQuestionsStatisticsMultiChoice(StatisticalTestCase):
    """Tests para questions_service.get_questions_statistics() con MULTI_CHOICE."""
    
    def test_get_questions_statistics_with_multi_choice_question(self):
        """
        Verifica que get_questions_statistics() retorna estadísticas correctas
        para preguntas tipo MULTI_CHOICE con conteos de selecciones.
        """
        # Arrange
        # 2 preguntas MULTI_CHOICE con opciones múltiples
        
        # Act
        stats = questions_service.get_questions_statistics(None)
        
        # Assert
        self.assertIn("¿Qué amenidades tiene?", stats)
        
        multi_stat = stats["¿Qué amenidades tiene?"]
        self.assertEqual(multi_stat.type, "múltiples opciones")
        
        # Verificar que el summary es un diccionario
        self.assertIsInstance(multi_stat.summary, dict)
        self.assertGreater(len(multi_stat.summary), 0)
