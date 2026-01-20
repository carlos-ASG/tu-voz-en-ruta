"""
Service principal para orquestación de estadísticas.

Este módulo contiene la función principal que orquesta todos los servicios
para calcular las estadísticas completas del dashboard.
"""
from ..schemas import DashboardStatistics, PeriodType
from ..utils.date_utils import get_period_date_range
from ..utils.filter_builder import build_submission_filters, build_complaint_filters
from . import survey_service, complaints_service, questions_service


def calculate_dashboard_statistics(
    period: PeriodType,
    route_id: str | None = None,
    unit_id: str | None = None
) -> DashboardStatistics:
    """
    Calcula todas las estadísticas del dashboard.
    
    Orquesta todos los servicios necesarios para recolectar KPIs.
    El aislamiento por organización es automático vía schema del tenant.
    
    Args:
        period: Período de tiempo ("today", "week", "month", "year", "all")
        route_id: ID de ruta opcional para filtrar
        unit_id: ID de unidad opcional para filtrar (mutuamente excluyente con route_id)
        
    Returns:
        DashboardStatistics con todos los datos calculados
        
    Raises:
        ValueError: Si period no es válido
        
    Example:
        >>> stats = calculate_dashboard_statistics("today", route_id="uuid")
        >>> print(f"Total submissions: {stats.total_submissions}")
        Total submissions: 42
        >>> print(f"Total complaints: {stats.total_complaints}")
        Total complaints: 15
        >>> print(f"Period: {stats.period_label}")
        Period: Hoy
    """
    # Validación ocurre en get_period_date_range
    # Obtener rango de fechas y label
    start_date, period_label = get_period_date_range(period)
    
    # Construir filtros para queries
    submissions_filters = build_submission_filters(start_date, route_id, unit_id)
    complaints_filters = build_complaint_filters(start_date, route_id, unit_id)
    
    # ==================== KPI 1: Envíos de encuestas ====================
    total_submissions = survey_service.get_submission_total(submissions_filters)
    
    # ==================== KPI 2: Quejas ====================
    complaints_summary = complaints_service.get_complaints_data(complaints_filters)
    complaints_by_unit = complaints_service.get_complaints_by_unit_data(complaints_filters)
    
    # ==================== KPI 2.5: Formularios por Unidad ====================
    submissions_by_unit = survey_service.get_submissions_by_unit_data(submissions_filters)
    
    # ==================== KPI 3: Estadísticas de preguntas ====================
    questions_stats = questions_service.get_questions_statistics(
        start_date, route_id, unit_id
    )
    
    # ==================== KPI 4: Timeline de envíos ====================
    # Si el período es "today", agrupar por hora en lugar de por día
    group_by_hour = (period == "today")
    timeline = survey_service.get_timeline_data(submissions_filters, group_by_hour)
    
    return DashboardStatistics(
        period_label=period_label,
        total_submissions=total_submissions,
        total_complaints=complaints_summary.total_complaints,
        complaints_by_reason=complaints_summary.by_reason,
        complaints_by_unit=complaints_by_unit,
        submissions_by_unit=submissions_by_unit,
        questions_statistics=questions_stats,
        survey_submissions_timeline=timeline
    )
