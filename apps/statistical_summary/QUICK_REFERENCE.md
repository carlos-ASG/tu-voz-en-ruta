# Quick Reference - statistical_summary

## 📥 Imports Comunes

```python
# Para calcular estadísticas del dashboard
from apps.statistical_summary.services import calculate_dashboard_statistics

# Para obtener datos de filtros (rutas y unidades)
from apps.statistical_summary.repositories.transport_repository import get_filter_data

# Para usar dataclasses en type hints
from apps.statistical_summary.schemas import (
    DashboardStatistics,
    TimelineData,
    ComplaintsSummary,
    QuestionStatistic,
    FilterData,
    PeriodType,
)
```

## 🎯 Uso Básico

### Calcular Estadísticas del Dashboard

```python
from apps.statistical_summary.services import calculate_dashboard_statistics

# Sin filtros (todo el tiempo)
stats = calculate_dashboard_statistics("all")

# Por período
stats = calculate_dashboard_statistics("today")
stats = calculate_dashboard_statistics("week")
stats = calculate_dashboard_statistics("month")
stats = calculate_dashboard_statistics("year")

# Con filtro de ruta
stats = calculate_dashboard_statistics("today", route_id="uuid-here")

# Con filtro de unidad
stats = calculate_dashboard_statistics("week", unit_id="uuid-here")

# Acceder a los datos
print(f"Total envíos: {stats.total_submissions}")
print(f"Total quejas: {stats.total_complaints}")
print(f"Período: {stats.period_label}")
print(f"Timeline: {stats.survey_submissions_timeline.dates}")
```

### Obtener Datos para Filtros

```python
from apps.statistical_summary.repositories.transport_repository import get_filter_data

# Obtener rutas y unidades del tenant actual
filter_data = get_filter_data()

# Acceder a rutas
for route in filter_data.routes:
    print(f"Route ID: {route.id}, Name: {route.name}")

# Acceder a unidades
for unit in filter_data.units:
    print(f"Unit ID: {unit.id}, Transit Number: {unit.transit_number}")
```

## 📊 Estructura de Datos

### DashboardStatistics

```python
@dataclass
class DashboardStatistics:
    period_label: str                              # "Hoy", "Esta Semana", etc.
    total_submissions: int                         # Total de envíos
    total_complaints: int                          # Total de quejas
    complaints_by_reason: dict[str, int]           # {"Mal servicio": 10, ...}
    complaints_by_unit: dict[str, int]             # {"ABC123": 5, ...}
    questions_statistics: dict[str, QuestionStatistic]
    survey_submissions_timeline: TimelineData
```

### TimelineData

```python
@dataclass
class TimelineData:
    dates: list[str]    # ["2024-01-01", "2024-01-02", ...]
    counts: list[int]   # [5, 8, 12, ...]
```

### QuestionStatistic

```python
@dataclass
class QuestionStatistic:
    type: QuestionTypeLabel        # "calificación", "opción", "múltiples opciones"
    summary: str | dict[str, int]  # "4.2/5" o {"Sí": 10, "No": 2}
```

## 🔧 Extender Funcionalidad

### Agregar Nuevo KPI

1. **Crear función en repository** (ej. `complaint_repository.py`):
```python
def get_new_kpi(filters: dict[str, Any]) -> int:
    """Nueva métrica."""
    return Complaint.objects.filter(**filters).count()
```

2. **Crear función en service** (ej. `complaints_service.py`):
```python
def get_new_kpi_data(filters: dict[str, Any]) -> int:
    """Obtiene nueva métrica."""
    return complaint_repository.get_new_kpi(filters)
```

3. **Agregar a DashboardStatistics** (`schemas.py`):
```python
@dataclass
class DashboardStatistics:
    # ... campos existentes ...
    new_kpi: int
```

4. **Actualizar orquestador** (`statistics_service.py`):
```python
def calculate_dashboard_statistics(...) -> DashboardStatistics:
    # ... código existente ...
    new_kpi = complaints_service.get_new_kpi_data(complaints_filters)
    
    return DashboardStatistics(
        # ... campos existentes ...
        new_kpi=new_kpi
    )
```

### Agregar Nuevo Filtro

1. **Actualizar filter builders** (`utils/filter_builder.py`):
```python
def build_submission_filters(
    start_date: datetime | None,
    route_id: str | None,
    unit_id: str | None,
    new_filter: str | None = None  # Nuevo parámetro
) -> dict[str, Any]:
    filters: dict[str, Any] = {}
    # ... código existente ...
    
    if new_filter:
        filters['new_field'] = new_filter
    
    return filters
```

2. **Actualizar service principal** (`statistics_service.py`):
```python
def calculate_dashboard_statistics(
    period: PeriodType,
    route_id: str | None = None,
    unit_id: str | None = None,
    new_filter: str | None = None  # Nuevo parámetro
) -> DashboardStatistics:
    # ... usar nuevo filtro ...
```

## 🧪 Testing Examples

### Test Repository (con DB)

```python
def test_get_submission_count():
    # Arrange
    SurveySubmission.objects.create(unit_id="test-uuid")
    filters = {'unit_id': 'test-uuid'}
    
    # Act
    count = survey_repository.get_submission_count(filters)
    
    # Assert
    assert count == 1
```

### Test Service (con mock)

```python
def test_get_submission_total(mocker):
    # Arrange
    mocker.patch(
        'apps.statistical_summary.repositories.survey_repository.get_submission_count',
        return_value=42
    )
    
    # Act
    total = survey_service.get_submission_total({})
    
    # Assert
    assert total == 42
```

### Test Utils (sin DB)

```python
def test_get_period_date_range_today():
    # Act
    start, label = get_period_date_range("today")
    
    # Assert
    assert label == "Hoy"
    assert start is not None
    assert start.hour == 0
    assert start.minute == 0

def test_get_period_date_range_invalid():
    # Act & Assert
    with pytest.raises(ValueError, match="Invalid period"):
        get_period_date_range("invalid")
```

## 🔍 Debugging

### Ver datos de estadísticas

```python
from apps.statistical_summary.services import calculate_dashboard_statistics

stats = calculate_dashboard_statistics("today")

# Imprimir todos los campos
import json
print(json.dumps({
    'period_label': stats.period_label,
    'total_submissions': stats.total_submissions,
    'total_complaints': stats.total_complaints,
    'complaints_by_reason': stats.complaints_by_reason,
    'complaints_by_unit': stats.complaints_by_unit,
    'timeline_dates': stats.survey_submissions_timeline.dates,
    'timeline_counts': stats.survey_submissions_timeline.counts,
}, indent=2, default=str))
```

### Ver queries ejecutadas

```python
from django.db import connection
from django.test.utils import override_settings

with override_settings(DEBUG=True):
    stats = calculate_dashboard_statistics("today")
    
    # Ver todas las queries
    for query in connection.queries:
        print(f"\n{query['sql']}")
        print(f"Time: {query['time']}s")
```

## 📝 Convenciones

- **Repository**: Solo queries, retorna datos primitivos o dataclasses simples
- **Service**: Lógica de negocio, orquesta repositories
- **Utils**: Funciones puras sin dependencias de Django ORM
- **Schemas**: Solo dataclasses y types, sin lógica
- **Constants**: Solo valores constantes, sin funciones

## ⚠️ Evitar

❌ **NO** importar services desde repositories
❌ **NO** poner lógica de negocio en repositories
❌ **NO** poner queries de DB en services (usar repositories)
❌ **NO** poner lógica en views (delegar a services)
❌ **NO** retornar querysets desde repositories (materializar a listas/dicts)
