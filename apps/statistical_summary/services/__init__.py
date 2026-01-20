"""
Services para lógica de negocio.

Los services orquestan repositories y contienen la lógica de negocio
para calcular estadísticas y KPIs del dashboard.
"""
from .statistics_service import calculate_dashboard_statistics
from .complaints_service import get_complaints_data, get_complaints_by_unit_data
from .survey_service import get_submission_total, get_timeline_data
from .questions_service import get_questions_statistics

__all__ = [
    'calculate_dashboard_statistics',
    'get_complaints_data',
    'get_complaints_by_unit_data',
    'get_submission_total',
    'get_timeline_data',
    'get_questions_statistics',
]
