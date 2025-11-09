// filter_script.js
// Mueve el script de filtros desde el template a este archivo.

document.addEventListener('DOMContentLoaded', function() {
    const filterType = document.getElementById('filterType');
    const routeSelect = document.getElementById('routeSelect');
    const unitSelect = document.getElementById('unitSelect');
    const applyFilterBtn = document.getElementById('applyFilterBtn');
    const clearFilterBtn = document.getElementById('clearFilterBtn');

    if (!filterType) {
        // Si no hay controles de filtro en la página, salir silenciosamente.
        return;
    }

    // Mostrar el select correcto al cargar la página
    if (filterType.value === 'route') {
        routeSelect.style.display = 'inline-block';
        applyFilterBtn.style.display = 'inline-block';
    } else if (filterType.value === 'unit') {
        unitSelect.style.display = 'inline-block';
        applyFilterBtn.style.display = 'inline-block';
    }

    // Cambiar entre ruta y unidad
    filterType.addEventListener('change', function() {
        // Ocultar ambos selects
        routeSelect.style.display = 'none';
        unitSelect.style.display = 'none';
        applyFilterBtn.style.display = 'none';

        if (this.value === 'route') {
            routeSelect.style.display = 'inline-block';
            applyFilterBtn.style.display = 'inline-block';
        } else if (this.value === 'unit') {
            unitSelect.style.display = 'inline-block';
            applyFilterBtn.style.display = 'inline-block';
        }
    });

    // Aplicar filtro
    applyFilterBtn.addEventListener('click', function() {
        const currentUrl = new URL(window.location.href);
        const params = new URLSearchParams(currentUrl.search);

        // Limpiar filtros anteriores
        params.delete('route');
        params.delete('unit');

        // Agregar el filtro seleccionado
        if (filterType.value === 'route' && routeSelect.value) {
            params.set('route', routeSelect.value);
        } else if (filterType.value === 'unit' && unitSelect.value) {
            params.set('unit', unitSelect.value);
        }

        // Redirigir con los nuevos parámetros
        window.location.href = currentUrl.pathname + '?' + params.toString();
    });

    // Limpiar filtro
    clearFilterBtn.addEventListener('click', function() {
        const currentUrl = new URL(window.location.href);
        const params = new URLSearchParams(currentUrl.search);

        // Eliminar filtros de ruta y unidad
        params.delete('route');
        params.delete('unit');

        // Redirigir sin los filtros
        window.location.href = currentUrl.pathname + '?' + params.toString();
    });
});
