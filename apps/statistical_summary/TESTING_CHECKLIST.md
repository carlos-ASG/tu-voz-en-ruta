# Testing Checklist - Refactorización statistical_summary

## ✅ Verificación Pre-Producción

### 1. **Verificar Sintaxis Python**
```bash
cd apps/statistical_summary
python -m py_compile schemas.py constants.py
python -m py_compile utils/*.py
python -m py_compile repositories/*.py
python -m py_compile services/*.py
python -m py_compile views.py
```

### 2. **Ejecutar Django Checks**
```bash
python manage.py check
python manage.py check --deploy
```

### 3. **Ejecutar Servidor de Desarrollo**
```bash
python manage.py runserver
```
- ✅ El servidor debe iniciar sin errores
- ✅ No debe haber ImportError ni AttributeError

### 4. **Acceder al Dashboard**
```
URL: http://localhost:8000/statistics/  (o la URL configurada)
```
- ✅ La página debe cargar sin error 500
- ✅ Debe mostrar el header "Dashboard de Estadísticas"
- ✅ Debe mostrar KPIs (Total Envíos, Total Quejas)

### 5. **Probar Filtros de Período**
- ✅ Hoy: `/statistics/?period=today`
  - Debe mostrar "Período: Hoy"
  - Timeline debe mostrar horas (00:00, 01:00, etc.)
  
- ✅ Esta Semana: `/statistics/?period=week`
  - Debe mostrar "Período: Esta Semana"
  - Timeline debe mostrar días
  
- ✅ Este Mes: `/statistics/?period=month`
  - Debe mostrar "Período: Este Mes"
  
- ✅ Este Año: `/statistics/?period=year`
  - Debe mostrar "Período: Este Año"
  
- ✅ Todo el Tiempo: `/statistics/?period=all`
  - Debe mostrar "Período: Todo el Tiempo"

### 6. **Probar Filtros de Ruta/Unidad**
- ✅ Filtro por ruta: `/statistics/?period=today&route=<route_uuid>`
  - Debe filtrar datos por esa ruta
  - Selector de ruta debe estar marcado
  
- ✅ Filtro por unidad: `/statistics/?period=today&unit=<unit_uuid>`
  - Debe filtrar datos por esa unidad
  - Selector de unidad debe estar marcado
  
- ✅ Ambos filtros: `/statistics/?period=today&route=<route_uuid>&unit=<unit_uuid>`
  - Debe priorizar ruta e ignorar unidad
  - Solo selector de ruta debe estar marcado

### 7. **Verificar Gráficas Chart.js**
- ✅ **Gráfica de Timeline** (línea)
  - Debe renderizarse sin errores
  - Debe mostrar datos correctos
  - Hover debe mostrar tooltips
  
- ✅ **Gráfica de Quejas por Motivo** (barras horizontales)
  - Debe renderizarse sin errores
  - Debe mostrar etiquetas de datos
  
- ✅ **Gráfica de Quejas por Unidad** (barras horizontales)
  - Debe renderizarse sin errores
  - Debe limitar a 10 unidades máximo
  
- ✅ **Gráficas de Preguntas** (pie/barras)
  - Deben renderizarse dinámicamente
  - Tipos: calificación, opción, múltiples opciones

### 8. **Verificar Datos JSON**
Abrir DevTools del navegador → Network → Refresh página:
- ✅ `complaints_by_reason_json` debe ser JSON válido
- ✅ `survey_submissions_timeline_json` debe tener `dates` y `counts`
- ✅ `complaints_by_unit_json` debe ser JSON válido

### 9. **Verificar Console del Navegador**
Abrir DevTools → Console:
- ✅ No debe haber errores JavaScript
- ✅ Debe ver mensajes de Chart.js:
  - "🎨 Iniciando carga de gráficas..."
  - "✅ Pie chart creado exitosamente"
  - "✅ Bar chart creado exitosamente"

### 10. **Verificar Permisos**
- ✅ Usuario sin permiso debe ser redirigido/error 403
- ✅ Usuario con permiso `can_view_statistical_dashboard` debe ver dashboard

### 11. **Verificar Multi-tenancy**
- ✅ Acceder desde dominio de tenant 1
  - Debe mostrar solo datos de tenant 1
- ✅ Acceder desde dominio de tenant 2
  - Debe mostrar solo datos de tenant 2
- ✅ Los datos NO deben mezclarse entre tenants

### 12. **Verificar Casos Edge**
- ✅ **Sin datos**: Debe mostrar "Sin datos disponibles"
- ✅ **Sin quejas**: Gráfica debe mostrar placeholder
- ✅ **Sin encuestas**: Timeline debe estar vacía
- ✅ **Período inválido**: `/statistics/?period=invalid`
  - Debe mostrar error o usar default ("today")

## 🔧 Debugging si Algo Falla

### Error: ImportError
```bash
# Verificar estructura de imports
python -c "from apps.statistical_summary.services import calculate_dashboard_statistics; print('OK')"

# Si falla, verificar:
ls -la apps/statistical_summary/services/__init__.py
cat apps/statistical_summary/services/__init__.py
```

### Error: AttributeError al acceder a dataclass
```python
# Verificar que stats es DashboardStatistics
from apps.statistical_summary.services import calculate_dashboard_statistics
stats = calculate_dashboard_statistics("today")
print(type(stats))  # Debe ser: <class 'apps.statistical_summary.schemas.DashboardStatistics'>
print(dir(stats))   # Debe listar todos los atributos
```

### Error: Gráficas no se renderizan
1. Abrir DevTools → Console
2. Buscar errores JavaScript
3. Verificar que JSON está bien formado:
   ```javascript
   // En console del navegador
   JSON.parse(document.querySelector('[data-complaints]').dataset.complaints)
   ```

### Error 500 en Dashboard
1. Ver logs del servidor (terminal donde corre `runserver`)
2. Buscar traceback completo
3. Verificar línea que causa el error
4. Común: Error al serializar dataclass a JSON
   - Solución: Convertir manualmente campos complejos

## 📊 Tests Automatizados (Opcional)

### Crear archivo de tests
```python
# apps/statistical_summary/tests.py
from django.test import TestCase
from .services import calculate_dashboard_statistics
from .repositories import transport_repository

class StatisticsServiceTest(TestCase):
    def test_calculate_dashboard_statistics_today(self):
        """Test cálculo de estadísticas para período 'today'"""
        stats = calculate_dashboard_statistics("today")
        
        self.assertIsNotNone(stats)
        self.assertEqual(stats.period_label, "Hoy")
        self.assertGreaterEqual(stats.total_submissions, 0)
        self.assertGreaterEqual(stats.total_complaints, 0)
    
    def test_get_filter_data(self):
        """Test obtención de datos de filtros"""
        filter_data = transport_repository.get_filter_data()
        
        self.assertIsNotNone(filter_data)
        self.assertIsInstance(filter_data.routes, list)
        self.assertIsInstance(filter_data.units, list)

# Ejecutar tests
# python manage.py test apps.statistical_summary
```

## 🔄 Rollback si es Necesario

Si algo sale mal y necesitas volver al código anterior:

```bash
# 1. Restaurar archivo original
mv apps/statistical_summary/utils.py.OLD_BACKUP apps/statistical_summary/utils.py

# 2. Borrar nuevos archivos
rm apps/statistical_summary/schemas.py
rm apps/statistical_summary/constants.py
rm -rf apps/statistical_summary/utils/
rm -rf apps/statistical_summary/repositories/
rm -rf apps/statistical_summary/services/

# 3. Restaurar views.py original desde git
git checkout apps/statistical_summary/views.py

# 4. Verificar
python manage.py runserver
```

## ✅ Sign-off Final

Cuando TODO funcione correctamente:

- [ ] Todos los filtros probados
- [ ] Todas las gráficas se renderizan
- [ ] No hay errores en console
- [ ] Multi-tenancy funciona
- [ ] Permisos funcionan

**Entonces:**
```bash
# Borrar backup
rm apps/statistical_summary/utils.py.OLD_BACKUP

# Hacer commit
git add apps/statistical_summary/
git commit -m "refactor: reorganizar statistical_summary con Clean Architecture

- Separar código en capas: repositories, services, utils
- Implementar dataclasses para estructuras de datos
- Agregar type hints completos (Python 3.12)
- Optimizar queries (evitar N+1)
- Mejorar testabilidad y mantenibilidad

340 líneas en 1 archivo → 1158 líneas en 16 archivos organizados"
```
