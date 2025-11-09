/**
 * complaints_by_unit_chart.js
 * 
 * Gráfica de barras horizontales para mostrar quejas agrupadas por unidad (número de tránsito).
 * Utiliza Chart.js para renderizar la visualización.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Obtener el canvas de la gráfica de quejas por unidad
    const complaintsByUnitCanvas = document.getElementById('complaintsByUnitChart');
    
    // Verificar si el canvas existe en el DOM
    if (!complaintsByUnitCanvas) {
        console.info('Canvas de gráfica de quejas por unidad no encontrado.');
        return;
    }
    
    // Obtener datos del contexto Django (inyectados desde el template)
    const complaintsByUnitDataRaw = complaintsByUnitCanvas.getAttribute('data-complaints-by-unit');
    
    if (!complaintsByUnitDataRaw) {
        console.warn('No hay datos de quejas por unidad disponibles para la gráfica.');
        return;
    }
    
    try {
        // Parsear datos JSON: {'transit_number': count, ...}
        const complaintsByUnitData = JSON.parse(complaintsByUnitDataRaw);
        
        // Validar que haya datos
        if (!complaintsByUnitData || Object.keys(complaintsByUnitData).length === 0) {
            console.warn('Datos de quejas por unidad vacíos o inválidos.');
            return;
        }
        
        // Convertir objeto a arrays para Chart.js
        const transitNumbers = Object.keys(complaintsByUnitData);
        const complaintCounts = Object.values(complaintsByUnitData);
        
        // Limitar a las 10 unidades con más quejas para mejor visualización
        const maxUnits = 10;
        const limitedTransitNumbers = transitNumbers.slice(0, maxUnits);
        const limitedComplaintCounts = complaintCounts.slice(0, maxUnits);
        
        // Configuración de la gráfica
        const ctx = complaintsByUnitCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: limitedTransitNumbers,
                datasets: [{
                    label: 'Número de Quejas',
                    data: limitedComplaintCounts,
                    backgroundColor: 'rgba(245, 158, 11, 0.8)',  // Color warning (naranja)
                    borderColor: 'rgba(245, 158, 11, 1)',
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
                                return `${value} queja${value !== 1 ? 's' : ''}`;
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
                            text: 'Cantidad de Quejas',
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
        
        console.info('Gráfica de quejas por unidad renderizada exitosamente.');
        
    } catch (error) {
        console.error('Error al parsear o renderizar la gráfica de quejas por unidad:', error);
    }
});
