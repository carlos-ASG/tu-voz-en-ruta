document.addEventListener('DOMContentLoaded', function() {
    const ratingContainers = document.querySelectorAll('.rating-stars');

    ratingContainers.forEach(container => {
        const stars = container.querySelectorAll('.star');
        const questionId = container.dataset.question;
        const hiddenInput = document.getElementById('rating_' + questionId);
        const ratingLabel = document.getElementById('ratingLabel_' + questionId);

        stars.forEach((star, index) => {
            star.addEventListener('click', function(e) {
                e.preventDefault();
                const value = parseInt(this.dataset.value);
                if (hiddenInput) hiddenInput.value = value;

                // Actualizar visualización de estrellas
                stars.forEach((s, i) => {
                    if (i < value) {
                        s.classList.add('active');
                    } else {
                        s.classList.remove('active');
                    }
                });

                // Actualizar etiqueta
                const labels = ['', 'Muy malo', 'Malo', 'Regular', 'Bueno', 'Excelente'];
                if (ratingLabel) ratingLabel.textContent = labels[value] || '';
            });

            // Efecto hover
            star.addEventListener('mouseenter', function() {
                const value = parseInt(this.dataset.value);
                stars.forEach((s, i) => {
                    if (i < value) {
                        s.classList.add('hover');
                    } else {
                        s.classList.remove('hover');
                    }
                });
            });
        });

        container.addEventListener('mouseleave', function() {
            stars.forEach(s => s.classList.remove('hover'));
        });
    });

    // Validación del formulario: asegurar que todas las preguntas requeridas estén respondidas
    const form = document.getElementById('surveyForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            const ratingInputs = document.querySelectorAll('input[name^="question_"][type="hidden"]');
            let allRated = true;
            ratingInputs.forEach(input => {
                if (!input.value) {
                    allRated = false;
                }
            });

            if (!allRated) {
                e.preventDefault();
                alert('Por favor califica todas las preguntas con estrellas');
                return;
            }
        });
    }
});
