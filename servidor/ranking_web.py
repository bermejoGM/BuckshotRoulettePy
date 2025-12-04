from flask import render_template_string

class RankingWeb:
    @staticmethod
    def get_html():
        html = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🎰 Buckshot Roulette - Ranking Global</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    font-family: 'Arial', sans-serif;
                    background: linear-gradient(135deg, #1e1e1e 0%, #3a0000 100%);
                    color: #fff;
                    min-height: 100vh;
                    padding: 20px;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    background: rgba(0, 0, 0, 0.7);
                    border: 3px solid #ff0000;
                    border-radius: 15px;
                    padding: 30px;
                    box-shadow: 0 0 30px rgba(255, 0, 0, 0.5);
                }
                h1 {
                    text-align: center;
                    color: #ff0000;
                    margin-bottom: 30px;
                    text-shadow: 2px 2px 5px #000;
                    font-size: 2.5em;
                }
                .stats {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 15px;
                    margin-bottom: 30px;
                }
                .stat-box {
                    background: #2a2a2a;
                    border: 2px solid #ff0000;
                    border-radius: 8px;
                    padding: 15px;
                    text-align: center;
                }
                .stat-label { font-size: 14px; color: #aaa; }
                .stat-value { font-size: 24px; font-weight: bold; color: #ff0000; margin-top: 5px; }
                .ranking-item {
                    padding: 15px;
                    margin: 10px 0;
                    background: #2a2a2a;
                    border-radius: 8px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    transition: transform 0.2s;
                }
                .ranking-item:hover { transform: translateX(5px); }
                .ranking-item.top3 { border-left: 5px solid #ffd700; }
                .ranking-pos { font-size: 24px; font-weight: bold; margin-right: 15px; }
                .ranking-nombre { flex: 1; font-size: 18px; }
                .ranking-puntos { font-size: 20px; color: #ff0000; font-weight: bold; }
                .ranking-fecha { font-size: 12px; color: #888; margin-left: 10px; }
                .loading { text-align: center; padding: 50px; font-size: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎰 BUCKSHOT ROULETTE</h1>
                <h2 style="text-align: center; color: #ff0000; margin-bottom: 20px;">🏆 RANKING GLOBAL</h2>
                
                <div class="stats" id="stats">
                    <div class="stat-box">
                        <div class="stat-label">Total Partidas</div>
                        <div class="stat-value" id="total-partidas">-</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Promedio Puntos</div>
                        <div class="stat-value" id="promedio-puntos">-</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Récord</div>
                        <div class="stat-value" id="max-puntos">-</div>
                    </div>
                </div>
                
                <div id="ranking-lista" class="loading">Cargando ranking...</div>
            </div>
            
            <script>
                async function cargarDatos() {
                    try {
                        // Cargar ranking
                        const rankingRes = await fetch('/api/ranking?limite=10');
                        const rankingData = await rankingRes.json();
                        
                        // Cargar estadísticas
                        const statsRes = await fetch('/api/estadisticas');
                        const statsData = await statsRes.json();
                        
                        // Mostrar estadísticas
                        if (statsData.estadisticas) {
                            document.getElementById('total-partidas').textContent = statsData.estadisticas.total_partidas;
                            document.getElementById('promedio-puntos').textContent = statsData.estadisticas.promedio_puntos;
                            document.getElementById('max-puntos').textContent = statsData.estadisticas.max_puntos;
                        }
                        
                        // Mostrar ranking
                        const lista = document.getElementById('ranking-lista');
                        if (rankingData.ranking && rankingData.ranking.length > 0) {
                            lista.innerHTML = rankingData.ranking.map((item, index) => {
                                const top3 = index < 3 ? 'top3' : '';
                                const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '';
                                return `
                                    <div class="ranking-item ${top3}">
                                        <div class="ranking-pos">${medal} ${index + 1}</div>
                                        <div class="ranking-nombre">${item.nombre}</div>
                                        <div>
                                            <div class="ranking-puntos">${item.puntos} pts</div>
                                            <div class="ranking-fecha">${new Date(item.fecha).toLocaleDateString()}</div>
                                        </div>
                                    </div>
                                `;
                            }).join('');
                        } else {
                            lista.innerHTML = '<div class="loading">No hay puntuaciones todavía</div>';
                        }
                        
                    } catch (error) {
                        document.getElementById('ranking-lista').innerHTML = 
                            '<div class="loading" style="color: #ff0000;">Error al cargar datos</div>';
                        console.error(error);
                    }
                }
                
                cargarDatos();
                setInterval(cargarDatos, 30000); // Actualizar cada 30s
            </script>
        </body>
        </html>
        """
        return html
