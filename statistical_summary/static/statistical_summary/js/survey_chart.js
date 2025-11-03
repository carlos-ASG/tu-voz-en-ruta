/**
 * survey_chart.js
 * 
 * Gráfica de línea para mostrar la tendencia temporal de envíos de encuestas.
 * Utiliza Chart.js para renderizar la visualización.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Obtener el canvas de la gráfica de encuestas
    const surveysCanvas = document.getElementById('surveysChart');
    
    // Verificar si el canvas existe en el DOM
    if (!surveysCanvas) {
        console.info('Canvas de gráfica de encuestas no encontrado. Es posible que no haya datos para mostrar.');
        return;
    }
    
    // Obtener datos del contexto Django (inyectados desde el template)
    // Los datos se pasan mediante un atributo data-* en el canvas
    const timelineDataRaw = surveysCanvas.getAttribute('data-timeline');
    
    if (!timelineDataRaw) {
        console.warn('No hay datos de timeline de encuestas disponibles para la gráfica.');
        return;
    }
    
    try {
        // Parsear datos JSON: {dates: [...], counts: [...]}
        const timelineData = JSON.parse(timelineDataRaw);
        
        // Validar que haya datos
        if (!timelineData || !timelineData.dates || timelineData.dates.length === 0) {
            console.warn('Datos de timeline vacíos o inválidos.');
            return;
        }
        
        const dates = timelineData.dates;
        const counts = timelineData.counts;
        
        // Detectar si los datos están en formato de hora (HH:00) o fecha (YYYY-MM-DD)
        const isHourlyFormat = dates.length > 0 && /^\d{2}:\d{2}$/.test(dates[0]);
        
        // Formatear fechas para mejor visualización
        let formattedDates;
        if (isHourlyFormat) {
            // Si es formato horario, usar directamente sin conversión
            formattedDates = dates;
        } else {
            // Si es formato de fecha, formatear a día/mes
            formattedDates = dates.map(date => {
                const d = new Date(date);
                // Formato: "15 Ene" o "15/01" según preferencia
                const day = d.getDate();
                const month = d.getMonth() + 1;
                return `${day.toString().padStart(2, '0')}/${month.toString().padStart(2, '0')}`;
            });
        }
        
        // Configuración de la gráfica
        const ctx = surveysCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: formattedDates,
                datasets: [{
                    label: 'Envíos de Encuestas',
                    data: counts,
                    borderColor: 'rgba(52, 152, 219, 1)',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4, // Curvatura de la línea (0 = líneas rectas, 0.4 = suave)
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    pointBackgroundColor: 'rgba(52, 152, 219, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointHoverBackgroundColor: 'rgba(52, 152, 219, 1)',
                    pointHoverBorderColor: '#fff',
                    pointHoverBorderWidth: 3,
                }]
            },
            options: {
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
                                // Mostrar fecha/hora original en el tooltip
                                const index = context[0].dataIndex;
                                const originalDate = dates[index];
                                
                                // Si es formato horario, mostrar solo la hora
                                if (isHourlyFormat) {
                                    return `Hora: ${originalDate}`;
                                }
                                // Si es formato de fecha, mostrar la fecha original
                                return originalDate;
                            },
                            label: function(context) {
                                const value = context.parsed.y;
                                return `${value} envío${value !== 1 ? 's' : ''}`;
                            }
                        }
                    },
                    datalabels: {
                        display: false // Desactivar etiquetas en los puntos para no saturar
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#666',
                            font: {
                                size: 11
                            },
                            maxRotation: 45,
                            minRotation: 0,
                            // Mostrar menos etiquetas en móviles
                            callback: function(value, index) {
                                if (window.innerWidth < 480) {
                                    // En móviles, mostrar cada 2 o 3 etiquetas
                                    return index % 2 === 0 ? this.getLabelForValue(value) : '';
                                }
                                return this.getLabelForValue(value);
                            }
                        },
                        title: {
                            display: true,
                            text: isHourlyFormat ? 'Hora' : 'Fecha',
                            color: '#333',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        }
                    },
                    y: {
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
                            text: 'Cantidad de Envíos',
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
                        right: 10,
                        bottom: 10,
                        left: 10
                    }
                }
            }
        });
        
        console.info('Gráfica de encuestas renderizada exitosamente.');
        
    } catch (error) {
        console.error('Error al parsear o renderizar la gráfica de encuestas:', error);
    }
});
