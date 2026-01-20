"""
Factories de Factory Boy para tests de statistical_summary.

Este módulo contiene todas las factories necesarias para crear datos de prueba
de manera consistente y sin conflictos de unicidad.

Factories disponibles:
- OrganizationFactory
- DomainFactory
- RouteFactory
- UnitFactory
- ComplaintReasonFactory
- QuestionFactory
- QuestionOptionFactory
- SurveySubmissionFactory
- AnswerFactory
- ComplaintFactory
"""
import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
from faker import Faker

from apps.organization.models import Organization, Domain
from apps.transport.models import Route, Unit
from apps.interview.models import (
    Question, QuestionOption, ComplaintReason,
    SurveySubmission, Answer, Complaint
)

fake = Faker()


class OrganizationFactory(DjangoModelFactory):
    """Factory para crear organizaciones (tenants)."""
    
    class Meta:
        model = Organization
    
    name = factory.Sequence(lambda n: f"Test Organization {n}")
    schema_name = factory.Sequence(lambda n: f"test_org_{n}")


class DomainFactory(DjangoModelFactory):
    """Factory para crear dominios asociados a organizaciones."""
    
    class Meta:
        model = Domain
    
    domain = factory.Sequence(lambda n: f"test{n}.localhost")
    tenant = factory.SubFactory(OrganizationFactory)
    is_primary = True


class RouteFactory(DjangoModelFactory):
    """Factory para crear rutas de transporte."""
    
    class Meta:
        model = Route
    
    name = factory.Sequence(lambda n: f"Ruta {n}")


class UnitFactory(DjangoModelFactory):
    """Factory para crear unidades (vehículos)."""
    
    class Meta:
        model = Unit
    
    transit_number = factory.Sequence(lambda n: f"UNIT{n:03d}")
    internal_number = factory.Sequence(lambda n: f"INT{n:03d}")
    route = factory.SubFactory(RouteFactory)


class ComplaintReasonFactory(DjangoModelFactory):
    """Factory para crear motivos de quejas."""
    
    class Meta:
        model = ComplaintReason
    
    label = factory.Sequence(lambda n: f"Motivo de queja {n}")


class QuestionFactory(DjangoModelFactory):
    """Factory para crear preguntas de encuestas."""
    
    class Meta:
        model = Question
    
    text = factory.Sequence(lambda n: f"¿Pregunta {n}?")
    type = Question.QuestionType.RATING
    position = factory.Sequence(lambda n: n)
    active = True


class QuestionOptionFactory(DjangoModelFactory):
    """Factory para crear opciones de preguntas."""
    
    class Meta:
        model = QuestionOption
    
    question = factory.SubFactory(QuestionFactory)
    text = factory.Sequence(lambda n: f"Opción {n}")
    position = factory.Sequence(lambda n: n)


class SurveySubmissionFactory(DjangoModelFactory):
    """Factory para crear envíos de encuestas."""
    
    class Meta:
        model = SurveySubmission
    
    unit = factory.SubFactory(UnitFactory)
    submitted_at = factory.LazyFunction(timezone.now)


class AnswerFactory(DjangoModelFactory):
    """Factory para crear respuestas a preguntas."""
    
    class Meta:
        model = Answer
    
    submission = factory.SubFactory(SurveySubmissionFactory)
    question = factory.SubFactory(QuestionFactory)
    created_at = factory.LazyFunction(timezone.now)
    
    # Los campos específicos (rating_answer, text_answer, etc.)
    # deben ser seteados manualmente según el tipo de pregunta


class ComplaintFactory(DjangoModelFactory):
    """Factory para crear quejas."""
    
    class Meta:
        model = Complaint
    
    unit = factory.SubFactory(UnitFactory)
    reason = factory.SubFactory(ComplaintReasonFactory)
    text = factory.Faker('sentence')
    submitted_at = factory.LazyFunction(timezone.now)
