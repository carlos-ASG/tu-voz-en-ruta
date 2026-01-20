/**
 * submissions_by_unit_chart.js
 * 
 * Gráfica de barras horizontales para mostrar formularios agrupados por unidad.
 * Limita a top 10 unidades con más envíos.
 * Usa color verde para diferenciarse de quejas (naranja).
 */

document.addEventListener('DOMContentLoaded', function() {
    // Obtener el canvas de la gráfica
    const submissionsByUnitCanvas = document.getElementById('submissionsByUnitChart');
    
    // Verificar si el canvas existe en el DOM
    if (!submissionsByUnitCanvas) {
        console.info('Canvas de gráfica de formularios por unidad no encontrado.');
        return;
    }
    
    // Obtener datos del contexto Django (inyectados desde el template)
    const submissionsByUnitDataRaw = submissionsByUnitCanvas.getAttribute('data-submissions-by-unit');
    
    if (!submissionsByUnitDataRaw) {
        console.warn('No hay datos de formularios por unidad disponibles para la gráfica.');
        return;
    }
    
    try {
        // Parsear datos JSON: {'transit_number': count, ...}
        const submissionsByUnitData = JSON.parse(submissionsByUnitDataRaw);
        
        // Validar que haya datos
        if (!submissionsByUnitData || Object.keys(submissionsByUnitData).length === 0) {
            console.warn('Datos de formularios por unidad vacíos o inválidos.');
            return;
        }
        
        // Convertir objeto a arrays para Chart.js
        const transitNumbers = Object.keys(submissionsByUnitData);
        const submissionCounts = Object.values(submissionsByUnitData);
        
        // Limitar a las 10 unidades con más formularios
        const maxUnits = 10;
        const limitedTransitNumbers = transitNumbers.slice(0, maxUnits);
        const limitedSubmissionCounts = submissionCounts.slice(0, maxUnits);
        
        // Configuración de la gráfica
        const ctx = submissionsByUnitCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: limitedTransitNumbers,
                datasets: [{
                    label: 'Número de Formularios',
                    data: limitedSubmissionCounts,
                    backgroundColor: 'rgba(34, 197, 94, 0.8)',  // Verde (green-500)
                    borderColor: 'rgba(34, 197, 94, 1)',
                    borderWidth: 2,
                    borderRadius: 6,
                    barThickness: 'flex',
                    maxBarThickness: 50,
                }]
            },
            options: {
                indexAxis: 'y',  // Hace que las barras sean horizontales
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        padding: 12,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {
                            title: function(context) {
                                return `Unidad: ${context[0].label}`;
                            },
                            label: function(context) {
                                const value = context.parsed.x;
                                return `${value} formulario${value !== 1 ? 's' : ''}`;
                            }
                        }
                    },
                    datalabels: {
                        display: true,
                        anchor: 'end',
                        align: 'end',
                        color: '#333',
                        font: {
                            weight: 'bold',
                            size: 12
                        },
                        formatter: function(value) {
                            return value;
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1,
                            color: '#666',
                            font: {
                                size: 11
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)',
                            drawBorder: false
                        },
                        title: {
                            display: true,
                            text: 'Cantidad de Formularios',
                            color: '#333',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#666',
                            font: {
                                size: 11,
                                weight: '600'
                            }
                        },
                        title: {
                            display: true,
                            text: 'Número de Tránsito',
                            color: '#333',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        }
                    }
                },
                layout: {
                    padding: {
                        top: 10,
                        right: 30,
                        bottom: 10,
                        left: 10
                    }
                }
            }
        });
        
        console.info('Gráfica de formularios por unidad renderizada exitosamente.');
        
    } catch (error) {
        console.error('Error al parsear o renderizar la gráfica de formularios por unidad:', error);
    }
});
