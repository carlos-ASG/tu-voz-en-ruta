/**
 * complaint_chart.js
 * 
 * Gráfica de barras horizontales para mostrar el resumen de quejas por motivo.
 * Utiliza Chart.js para renderizar la visualización.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Obtener el canvas de la gráfica de quejas
    const complaintsCanvas = document.getElementById('complaintsChart');
    
    // Verificar si el canvas existe en el DOM
    if (!complaintsCanvas) {
        console.info('Canvas de gráfica de quejas no encontrado. Es posible que no haya datos para mostrar.');
        return;
    }
    
    // Obtener datos del contexto Django (inyectados desde el template)
    // Los datos se pasan mediante un atributo data-* en el canvas
    const complaintsDataRaw = complaintsCanvas.getAttribute('data-complaints');
    
    if (!complaintsDataRaw) {
        console.warn('No hay datos de quejas disponibles para la gráfica.');
        return;
    }
    
    try {
        // Parsear datos JSON: ahora es un objeto {motivo: count, ...}
        const complaintsData = JSON.parse(complaintsDataRaw);
        
        // Validar que haya datos
        if (!complaintsData || Object.keys(complaintsData).length === 0) {
            console.warn('Diccionario de quejas vacío.');
            return;
        }
        
        // Extraer labels (motivos) y valores (conteos) del objeto
        const labels = Object.keys(complaintsData);
        const counts = Object.values(complaintsData);
        
        // Generar colores dinámicos para las barras
        const backgroundColors = generateColors(counts.length);
        const borderColors = backgroundColors.map(color => color.replace('0.7', '1'));
        
        // Configuración de la gráfica
        const ctx = complaintsCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Número de Quejas',
                    data: counts,
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 2,
                    borderRadius: 6,
                    barThickness: 'flex',
                    maxBarThickness: 50,
                }]
            },
            options: {
                indexAxis: 'y', // Barras horizontales
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
                            label: function(context) {
                                return `${context.parsed.x} queja${context.parsed.x !== 1 ? 's' : ''}`;
                            }
                        }
                    },
                    datalabels: {
                        display: true,
                        color: '#333',
                        font: {
                            weight: 'bold',
                            size: 12
                        },
                        anchor: 'end',
                        align: 'end',
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
                        ticks: {
                            color: '#333',
                            font: {
                                size: 11,
                                weight: '500'
                            },
                            // Truncar labels largos en móviles
                            callback: function(value, index) {
                                const label = this.getLabelForValue(value);
                                if (window.innerWidth < 480 && label.length > 20) {
                                    return label.substring(0, 17) + '...';
                                }
                                return label;
                            }
                        },
                        grid: {
                            display: false
                        }
                    }
                },
                layout: {
                    padding: {
                        top: 10,
                        right: 40,
                        bottom: 10,
                        left: 10
                    }
                }
            },
            plugins: [ChartDataLabels] // Habilitar plugin de etiquetas
        });
        
        console.info('Gráfica de quejas renderizada exitosamente.');
        
    } catch (error) {
        console.error('Error al parsear o renderizar la gráfica de quejas:', error);
    }
});

/**
 * Genera un array de colores en formato rgba para las barras
 * @param {number} count - Número de colores a generar
 * @returns {Array<string>} Array de colores rgba
 */
function generateColors(count) {
    // Paleta de colores armoniosa para las barras
    const baseColors = [
        'rgba(231, 76, 60, 0.7)',   // Rojo
        'rgba(241, 196, 15, 0.7)',  // Amarillo
        'rgba(52, 152, 219, 0.7)',  // Azul
        'rgba(155, 89, 182, 0.7)',  // Púrpura
        'rgba(46, 204, 113, 0.7)',  // Verde
        'rgba(230, 126, 34, 0.7)',  // Naranja
        'rgba(26, 188, 156, 0.7)',  // Turquesa
        'rgba(236, 240, 241, 0.7)', // Gris claro
    ];
    
    const colors = [];
    for (let i = 0; i < count; i++) {
        colors.push(baseColors[i % baseColors.length]);
    }
    
    return colors;
}
