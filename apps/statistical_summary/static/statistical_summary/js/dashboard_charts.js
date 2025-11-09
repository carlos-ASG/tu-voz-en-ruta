document.addEventListener('DOMContentLoaded', function() {
    console.log('🎨 Iniciando carga de gráficas...');
    
    // Chart.js configuration
    const chartColors = {
        primary: '#3498db',
        success: '#2ecc71',
        warning: '#f39c12',
        danger: '#e74c3c',
        info: '#1abc9c',
        purple: '#9b59b6',
        pink: '#e91e63',
        orange: '#ff5722',
        teal: '#16a085',
        indigo: '#6610f2'
    };

    const colorPalette = Object.values(chartColors);

    // Register datalabels plugin if available (ChartDataLabels provided by the included plugin script)
    if (typeof Chart !== 'undefined' && typeof Chart.register === 'function') {
        if (typeof ChartDataLabels !== 'undefined') {
            try {
                Chart.register(ChartDataLabels);
                console.log('🔌 chartjs-plugin-datalabels registrado');
            } catch (regErr) {
                console.warn('⚠️ No se pudo registrar chartjs-plugin-datalabels:', regErr);
            }
        } else {
            console.warn('⚠️ chartjs-plugin-datalabels no está disponible (no cargado)');
        }
    }

    // Get all canvas elements for charts
    const canvasElements = document.querySelectorAll('canvas[data-type]');
    console.log('📊 Canvas encontrados:', canvasElements.length);
    
    canvasElements.forEach((canvas, index) => {
        console.log(`\n--- Procesando canvas ${index + 1} ---`);
        
        const questionType = canvas.dataset.type;
        const questionText = canvas.dataset.question;
        console.log('Tipo:', questionType);
        console.log('Pregunta:', questionText);
        console.log('Data summary raw:', canvas.dataset.summary);
        
        let summaryData;
        
        try {
            summaryData = JSON.parse(canvas.dataset.summary);
            console.log('✅ JSON parseado correctamente:', summaryData);
        } catch (e) {
            console.error('❌ Error parsing summary data for:', questionText, e);
            console.error('Contenido que falló:', canvas.dataset.summary);
            return;
        }

        // Skip if no data
        if (summaryData === "Sin datos" || typeof summaryData === 'string') {
            console.log('⚠️ Sin datos disponibles para esta pregunta');
            canvas.parentElement.innerHTML += '<p class="no-data-message">Sin datos disponibles</p>';
            return;
        }

        if (Object.keys(summaryData).length === 0) {
            console.log('⚠️ Objeto vacío');
            canvas.parentElement.innerHTML += '<p class="no-data-message">Sin datos disponibles</p>';

            return;
        }

        const labels = Object.keys(summaryData);
        const values = Object.values(summaryData);
        const backgroundColors = labels.map((_, i) => colorPalette[i % colorPalette.length]);
        
        console.log('Labels:', labels);
        console.log('Values:', values);
        console.log('Colors:', backgroundColors);

        // Create chart based on type
        if (questionType === 'opción') {
            console.log('🥧 Creando pie chart...');
            // Pie chart for single choice questions
            try {
                const chart = new Chart(canvas, {
                    type: 'pie',
                    data: {
                        labels: labels,
                        datasets: [{
                            data: values,
                            backgroundColor: backgroundColors,
                            borderWidth: 2,
                            borderColor: '#fff'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    padding: 15,
                                    font: {
                                        size: 12
                                    }
                                }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const label = context.label || '';
                                        const value = context.parsed || 0;
                                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                        const percentage = ((value / total) * 100).toFixed(1);
                                        return `${label}: ${value} (${percentage}%)`;
                                    }
                                }
                            },
                            // datalabels: show percentage on each slice
                            datalabels: {
                                color: '#ffffff',
                                formatter: function(value, ctx) {
                                    const data = ctx.dataset.data;
                                    const total = data.reduce((a, b) => a + b, 0);
                                    if (!total) return '';
                                    const pct = (value / total) * 100;
                                    return `${pct.toFixed(1)}%`;
                                },
                                font: {
                                    weight: '600',
                                    size: 11
                                }
                            }
                        }
                    }
                });
                console.log('✅ Pie chart creado exitosamente');
            } catch (error) {
                console.error('❌ Error creando pie chart:', error);
            }
        } else if (questionType === 'múltiples opciones') {
            console.log('📊 Creando bar chart...');
            // Bar chart for multiple choice questions
            try {
                const chart = new Chart(canvas, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Número de respuestas',
                            data: values,
                            backgroundColor: chartColors.primary,
                            borderColor: chartColors.primary,
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    stepSize: 1,
                                    precision: 0
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: false
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        return `Respuestas: ${context.parsed.y}`;
                                    }
                                }
                            },
                            // datalabels: show numeric value on each bar
                            datalabels: {
                                anchor: 'end',
                                align: 'end',
                                color: '#000000',
                                formatter: function(value) {
                                    return value;
                                },
                                font: {
                                    weight: '600',
                                    size: 11
                                }
                            }
                        }
                    }
                });
                console.log('✅ Bar chart creado exitosamente');
            } catch (error) {
                console.error('❌ Error creando bar chart:', error);
            }
        } else {
            console.log('⚠️ Tipo de pregunta no reconocido:', questionType);
        }
    });
    
    console.log('\n🎨 Proceso de carga de gráficas completado');
});