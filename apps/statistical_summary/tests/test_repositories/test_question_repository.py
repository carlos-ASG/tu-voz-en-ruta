"""
Tests para question_repository.

Verifica que las funciones de Question y Answer retornan estadísticas
correctas para cada tipo de pregunta (RATING, CHOICE, MULTI_CHOICE).
"""
from django.utils import timezone
from apps.statistical_summary.repositories import question_repository
from .. import StatisticalTestCase


class TestGetActiveQuestions(StatisticalTestCase):
    """Tests para question_repository.get_active_questions()."""
    
    def test_get_active_questions_returns_active_only(self):
        """
        Verifica que get_active_questions() retorna solo preguntas
        con active=True.
        """
        # Arrange
        # 5 preguntas activas pre-cargadas
        
        # Act
        questions = question_repository.get_active_questions()
        
        # Assert
        self.assertEqual(questions.count(), 5)
        
        # Verificar que todas están activas
        for question in questions:
            self.assertTrue(question.active)


class TestGetFilteredAnswers(StatisticalTestCase):
    """Tests para question_repository.get_filtered_answers()."""
    
    def test_get_filtered_answers_with_filters(self):
        """
        Verifica que get_filtered_answers() retorna respuestas correctas
        para una pregunta específica.
        """
        # Arrange
        question = self.question_rating
        
        # Act
        answers = question_repository.get_filtered_answers(
            question, None, None, None
        )
        
        # Assert
        # Debe haber 10 respuestas (una por cada envío)
        self.assertEqual(answers.count(), 10)
        
        # Verificar que todas las respuestas son para la pregunta correcta
        for answer in answers:
            self.assertEqual(answer.question, question)


class TestGetRatingAverage(StatisticalTestCase):
    """Tests para question_repository.get_rating_average()."""
    
    def test_get_rating_average_with_ratings(self):
        """
        Verifica que get_rating_average() calcula correctamente el promedio
        de ratings.
        """
        # Arrange
        question = self.question_rating
        answers = question_repository.get_filtered_answers(
            question, None, None, None
        )
        
        # Act
        average = question_repository.get_rating_average(answers)
        
        # Assert
        # Los ratings alternaban entre 3, 4, 5 (10 respuestas)
        # Esperar un promedio entre 3 y 5
        self.assertIsNotNone(average)
        self.assertGreaterEqual(average, 3)
        self.assertLessEqual(average, 5)
        
        # Verificar que es un número decimal
        self.assertIsInstance(average, float)


class TestGetChoiceCounts(StatisticalTestCase):
    """Tests para question_repository.get_choice_counts()."""
    
    def test_get_choice_counts_with_choices(self):
        """
        Verifica que get_choice_counts() retorna diccionario con:
        - Claves = textos de opciones
        - Valores = conteos
        """
        # Arrange
        question = self.question_choice1  # "¿El conductor fue amable?" (Sí/No)
        answers = question_repository.get_filtered_answers(
            question, None, None, None
        )
        
        # Act
        counts = question_repository.get_choice_counts(answers, question)
        
        # Assert
        # Los 10 envíos alternaban entre Sí y No
        self.assertEqual(len(counts), 2)
        self.assertIn("Sí", counts)
        self.assertIn("No", counts)
        
        # Verificar que los conteos suman 10
        total = sum(counts.values())
        self.assertEqual(total, 10)


class TestGetMultiChoiceCounts(StatisticalTestCase):
    """Tests para question_repository.get_multi_choice_counts()."""
    
    def test_get_multi_choice_counts_with_selections(self):
        """
        Verifica que get_multi_choice_counts() retorna diccionario con
        conteos de selecciones múltiples.
        """
        # Arrange
        question = self.question_multi1  # "¿Qué amenidades tiene?" (Wi-Fi, USB, AC)
        # Los 10 envíos seleccionaban Wi-Fi y USB
        answers = question_repository.get_filtered_answers(
            question, None, None, None
        )
        
        # Act
        counts = question_repository.get_multi_choice_counts(answers, question)
        
        # Assert
        # Debe haber conteos para Wi-Fi y USB
        self.assertGreater(len(counts), 0)
        self.assertIn("Wi-Fi", counts)
        self.assertIn("USB", counts)
        
        # Wi-Fi y USB deben tener 10 selecciones cada uno
        self.assertEqual(counts["Wi-Fi"], 10)
        self.assertEqual(counts["USB"], 10)
        
        # AC no debe aparecer
        self.assertNotIn("AC", counts)
