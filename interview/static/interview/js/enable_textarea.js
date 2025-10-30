document.addEventListener('DOMContentLoaded', function() {
    const reasonSelect = document.getElementById('complaint_reason');
    const complaintTextarea = document.getElementById('complaint_text');

    if (!reasonSelect || !complaintTextarea) return;

    function toggleComplaintField() {
        const hasValue = !!reasonSelect.value;
        if (hasValue) {
            complaintTextarea.removeAttribute('readonly');
            complaintTextarea.removeAttribute('disabled');
        } else {
            complaintTextarea.setAttribute('readonly', 'readonly');
            complaintTextarea.value = '';
        }
    }

    // Inicializar estado
    toggleComplaintField();

    // Escuchar cambios
    reasonSelect.addEventListener('change', toggleComplaintField);
});
