"""
Dataclasses y tipos para statistical_summary.

Este módulo contiene todas las estructuras de datos tipadas usadas
en el cálculo y presentación de estadísticas del dashboard.
"""
from dataclasses import dataclass
from typing import Literal

# Type aliases
PeriodType = Literal["today", "week", "month", "year", "all"]
QuestionTypeLabel = Literal["calificación", "opción", "múltiples opciones"]


@dataclass
class TimelineData:
    """Timeline de envíos de encuestas."""
    dates: list[str]
    counts: list[int]


@dataclass
class ComplaintsSummary:
    """Resumen de quejas."""
    total_complaints: int
    by_reason: dict[str, int]


@dataclass
class QuestionStatistic:
    """Estadística de una pregunta."""
    type: QuestionTypeLabel
    summary: str | dict[str, int]


@dataclass
class RouteData:
    """Datos de ruta para filtros."""
    id: str
    name: str


@dataclass
class UnitData:
    """Datos de unidad para filtros."""
    id: str
    transit_number: str


@dataclass
class FilterData:
    """Datos para filtros de dashboard."""
    routes: list[RouteData]
    units: list[UnitData]


@dataclass
class DashboardStatistics:
    """
    Todas las estadísticas del dashboard.
    
    Attributes:
        period_label: Etiqueta legible del período ("Hoy", "Esta Semana", etc.)
        total_submissions: Total de envíos de encuestas
        total_complaints: Total de quejas
        complaints_by_reason: Quejas agrupadas por motivo
        complaints_by_unit: Quejas agrupadas por número de tránsito
        questions_statistics: Estadísticas de preguntas activas
        survey_submissions_timeline: Timeline de envíos
    """
    period_label: str
    total_submissions: int
    total_complaints: int
    complaints_by_reason: dict[str, int]
    complaints_by_unit: dict[str, int]
    questions_statistics: dict[str, QuestionStatistic]
    survey_submissions_timeline: TimelineData
