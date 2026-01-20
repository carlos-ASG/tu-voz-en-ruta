"""
Base test case y configuración para tests de statistical_summary.

StatisticalTestCase proporciona:
- Soporte multi-tenancy con TenantTestCase
- Datos pre-cargados para todos los tests:
  * 1 organización con dominio
  * 2 rutas
  * 20 unidades (10 por ruta)
  * 2 motivos de quejas
  * 5 preguntas (RATING, CHOICE x2, MULTI_CHOICE x2)
  * 10 envíos de formularios completos
  * 8 quejas
"""
from django_tenants.test.cases import TenantTestCase
from django.utils import timezone

from apps.interview.models import Question, Answer
from .factories import (
    OrganizationFactory, DomainFactory, RouteFactory, UnitFactory,
    ComplaintReasonFactory, QuestionFactory, QuestionOptionFactory,
    SurveySubmissionFactory, AnswerFactory, ComplaintFactory
)


class StatisticalTestCase(TenantTestCase):
    """
    Base test case para statistical_summary con datos pre-cargados.
    
    Proporciona los siguientes datos en cada test:
    
    Organización:
    - tenant: Organización con schema='test_org'
    - domain: Dominio 'testorg.localhost'
    
    Rutas (self.route1, self.route2):
    - 2 rutas activas
    
    Unidades (self.units_route1, self.units_route2, self.all_units):
    - 10 unidades por ruta (20 total)
    - Transit numbers: ABC001-ABC010, XYZ001-XYZ010
    
    Motivos de Quejas (self.reason1, self.reason2):
    - "Mal servicio"
    - "Llegada tardía"
    
    Preguntas (5 total):
    - question_rating: ¿Cómo califica el servicio? (RATING)
    - question_choice1: ¿El conductor fue amable? (CHOICE: Sí/No)
    - question_choice2: ¿El vehículo estaba limpio? (CHOICE: Muy limpio/Limpio/Sucio)
    - question_multi1: ¿Qué amenidades tiene? (MULTI_CHOICE: Wi-Fi/USB/AC)
    - question_multi2: ¿Qué mejoraría? (MULTI_CHOICE: Puntualidad/Limpieza/Atención)
    
    Envíos de Formularios (10 total):
    - self.submissions: Lista de 10 SurveySubmission completos
    - Cada uno distribuido en diferentes unidades
    - Cada uno con 5 respuestas (una por pregunta)
    
    Quejas (8 total):
    - self.complaints: Lista de 8 Complaint
    - Distribuidas entre motivos
    """
    
    # El TenantTestCase automaticamente crea un tenant con schema='test'
    # No necesitamos override setUpClass, el tenant estará disponible como cls.tenant
    
    def setUp(self):
        """Crear datos pre-cargados para cada test."""
        super().setUp()
        
        # ==================== 3. CREAR 2 RUTAS ====================
        self.route1 = RouteFactory(name="Ruta Centro-Norte")
        self.route2 = RouteFactory(name="Ruta Este-Oeste")
        
        # ==================== 4. CREAR 20 UNIDADES (10 POR RUTA) ====================
        self.units_route1 = [
            UnitFactory(
                transit_number=f"ABC{i:03d}",
                internal_number=f"INT1{i:02d}",
                route=self.route1
            )
            for i in range(1, 11)
        ]
        
        self.units_route2 = [
            UnitFactory(
                transit_number=f"XYZ{i:03d}",
                internal_number=f"INT2{i:02d}",
                route=self.route2
            )
            for i in range(1, 11)
        ]
        
        self.all_units = self.units_route1 + self.units_route2
        
        # ==================== 5. CREAR 2 MOTIVOS DE QUEJAS ====================
        self.reason1 = ComplaintReasonFactory(label="Mal servicio")
        self.reason2 = ComplaintReasonFactory(label="Llegada tardía")
        
        # ==================== 6. CREAR 5 PREGUNTAS ====================
        
        # PREGUNTA 1: RATING
        self.question_rating = QuestionFactory(
            text="¿Cómo califica el servicio?",
            type=Question.QuestionType.RATING,
            position=1
        )
        
        # PREGUNTA 2: CHOICE (2 opciones)
        self.question_choice1 = QuestionFactory(
            text="¿El conductor fue amable?",
            type=Question.QuestionType.CHOICE,
            position=2
        )
        self.choice1_opt1 = QuestionOptionFactory(
            question=self.question_choice1,
            text="Sí",
            position=1
        )
        self.choice1_opt2 = QuestionOptionFactory(
            question=self.question_choice1,
            text="No",
            position=2
        )
        
        # PREGUNTA 3: CHOICE (3 opciones)
        self.question_choice2 = QuestionFactory(
            text="¿El vehículo estaba limpio?",
            type=Question.QuestionType.CHOICE,
            position=3
        )
        self.choice2_opt1 = QuestionOptionFactory(
            question=self.question_choice2,
            text="Muy limpio",
            position=1
        )
        self.choice2_opt2 = QuestionOptionFactory(
            question=self.question_choice2,
            text="Limpio",
            position=2
        )
        self.choice2_opt3 = QuestionOptionFactory(
            question=self.question_choice2,
            text="Sucio",
            position=3
        )
        
        # PREGUNTA 4: MULTI_CHOICE (3 opciones)
        self.question_multi1 = QuestionFactory(
            text="¿Qué amenidades tiene?",
            type=Question.QuestionType.MULTI_CHOICE,
            position=4
        )
        self.multi1_opt1 = QuestionOptionFactory(
            question=self.question_multi1,
            text="Wi-Fi",
            position=1
        )
        self.multi1_opt2 = QuestionOptionFactory(
            question=self.question_multi1,
            text="USB",
            position=2
        )
        self.multi1_opt3 = QuestionOptionFactory(
            question=self.question_multi1,
            text="AC",
            position=3
        )
        
        # PREGUNTA 5: MULTI_CHOICE (3 opciones)
        self.question_multi2 = QuestionFactory(
            text="¿Qué mejoraría?",
            type=Question.QuestionType.MULTI_CHOICE,
            position=5
        )
        self.multi2_opt1 = QuestionOptionFactory(
            question=self.question_multi2,
            text="Puntualidad",
            position=1
        )
        self.multi2_opt2 = QuestionOptionFactory(
            question=self.question_multi2,
            text="Limpieza",
            position=2
        )
        self.multi2_opt3 = QuestionOptionFactory(
            question=self.question_multi2,
            text="Atención",
            position=3
        )
        
        # ==================== 7. CREAR 10 ENVÍOS DE FORMULARIOS ====================
        self.submissions = []
        
        for i in range(10):
            # Distribuir en diferentes unidades (rotación)
            unit = self.all_units[i % 20]
            submission = SurveySubmissionFactory(unit=unit)
            
            # --- RESPUESTA 1: RATING (alternando 3, 4, 5) ---
            AnswerFactory(
                submission=submission,
                question=self.question_rating,
                rating_answer=(i % 3) + 3  # 3, 4, 5
            )
            
            # --- RESPUESTA 2: CHOICE 1 (alternando Sí/No) ---
            AnswerFactory(
                submission=submission,
                question=self.question_choice1,
                selected_option=self.choice1_opt1 if i % 2 == 0 else self.choice1_opt2
            )
            
            # --- RESPUESTA 3: CHOICE 2 (distribuyendo entre 3 opciones) ---
            choice2_options = [self.choice2_opt1, self.choice2_opt2, self.choice2_opt3]
            AnswerFactory(
                submission=submission,
                question=self.question_choice2,
                selected_option=choice2_options[i % 3]
            )
            
            # --- RESPUESTA 4: MULTI_CHOICE 1 (seleccionar Wi-Fi y USB) ---
            answer_multi1 = AnswerFactory(
                submission=submission,
                question=self.question_multi1
            )
            answer_multi1.selected_options.set([self.multi1_opt1, self.multi1_opt2])
            
            # --- RESPUESTA 5: MULTI_CHOICE 2 (seleccionar Puntualidad y Atención) ---
            answer_multi2 = AnswerFactory(
                submission=submission,
                question=self.question_multi2
            )
            answer_multi2.selected_options.set([self.multi2_opt1, self.multi2_opt3])
            
            self.submissions.append(submission)
        
        # ==================== 8. CREAR 8 QUEJAS ====================
        self.complaints = []
        
        for i in range(8):
            # Distribuir en diferentes unidades (rotación)
            unit = self.all_units[i % 20]
            # Alternar entre motivos
            reason = self.reason1 if i % 2 == 0 else self.reason2
            
            complaint = ComplaintFactory(
                unit=unit,
                reason=reason,
                text=f"Queja de prueba {i + 1}"
            )
            self.complaints.append(complaint)
