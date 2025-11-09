/**
 * Script para el formulario del generador de códigos QR.
 * Maneja la visibilidad dinámica de las secciones según el tipo de selección.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Obtener elementos del DOM
    const form = document.getElementById('qrForm');
    const selectionRadios = document.querySelectorAll('input[name="selection_type"]');
    
    const allUnitsSection = document.getElementById('allUnitsSection');
    const singleUnitSection = document.getElementById('singleUnitSection');
    const rangeSection = document.getElementById('rangeSection');
    
    /**
     * Actualiza la visibilidad de las secciones según el tipo de selección activo.
     */
    function updateSectionVisibility() {
        const selectedType = document.querySelector('input[name="selection_type"]:checked');
        
        if (!selectedType) return;
        
        const value = selectedType.value;
        
        // Ocultar todas las secciones
        allUnitsSection.style.display = 'none';
        singleUnitSection.style.display = 'none';
        rangeSection.style.display = 'none';
        
        // Mostrar la sección correspondiente
        if (value === 'all') {
            allUnitsSection.style.display = 'block';
        } else if (value === 'single') {
            singleUnitSection.style.display = 'block';
        } else if (value === 'range') {
            rangeSection.style.display = 'block';
        }
    }
    
    // Configurar listeners para los radio buttons
    selectionRadios.forEach(radio => {
        radio.addEventListener('change', updateSectionVisibility);
    });
    
    // Inicializar la visibilidad al cargar la página
    updateSectionVisibility();
    
    /**
     * Validación del formulario antes de enviar.
     */
    form.addEventListener('submit', function(e) {
        const selectedType = document.querySelector('input[name="selection_type"]:checked');
        
        if (!selectedType) {
            e.preventDefault();
            alert('Por favor selecciona un tipo de generación.');
            return false;
        }
        
        const value = selectedType.value;
        
        // Validar según el tipo seleccionado
        if (value === 'single') {
            const singleUnit = document.getElementById('singleUnitSelect');
            if (!singleUnit.value) {
                e.preventDefault();
                alert('Por favor selecciona una unidad.');
                singleUnit.focus();
                return false;
            }
        } else if (value === 'range') {
            const startUnit = document.getElementById('startUnitSelect');
            const endUnit = document.getElementById('endUnitSelect');
            
            if (!startUnit.value || !endUnit.value) {
                e.preventDefault();
                alert('Por favor selecciona ambas unidades para el rango.');
                if (!startUnit.value) {
                    startUnit.focus();
                } else {
                    endUnit.focus();
                }
                return false;
            }
        }
        
        // Mostrar mensaje de carga (opcional)
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle></svg> Generando...';
        }
        
        return true;
    });
});