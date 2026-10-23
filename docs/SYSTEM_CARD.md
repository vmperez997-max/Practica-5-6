# System Card · Recomendador

## Usuarios y propósito

Laboratorio académico individual de Victor Perez, INF-8239, UASD. Amplía el proyecto base docente de Edwin Ramón José Nolasco. Ordena películas para estudiar señales, costos y errores; no se ha validado en un servicio de producción.

## Catálogo y candidatos

9,742 películas. Todos los métodos evaluados puntúan el catálogo completo, excluyendo ratings vistos del usuario. El baseline suavizado usa percentil 80 del conteo como evidencia mínima; los demás candidatos reciben media global en esa señal. No se muestrean negativos ni se filtran previamente 100 candidatos por MF. Se asume catálogo disponible sin comprobar fecha real de lanzamiento: límite de esta evaluación.

## Señales utilizadas

Ratings explícitos y géneros. El perfil de contenido es promedio TF-IDF ponderado por max(rating-2.5, 0.1). Incluso ratings bajos aportan peso pequeño: puede incorporar géneros no deseados. El tokenizador original divide etiquetas como Sci-Fi; no se usa texto libre, etiquetas ni demografía.

## Modelos y fallback

- Popularidad: `(n*media_item + m*media_global)/(n+m)`, con m percentil 80 del conteo. LAB08 usa todos los ratings para descripción; evaluación usa entrenamiento.
- Contenido: coseno entre perfil y géneros. La app consulta una película de referencia, sin historial personal.
- MF: media global + producto de vectores usuario e ítem, SGD con learning rate .01, regularización .05, inicialización normal .1. Comparación 8 factores/4 épocas y 20/12. Predicciones sin clipping; puede producir valores fuera de escala. No aprende sesgos individuales.
- Híbrido: `alpha*minmax(CF)+(1-alpha)*minmax(contenido)` sobre los mismos candidatos. Si el rango es cero la señal normalizada vale cero. alpha .25 y .75, semillas 17, 42 y 83.
- Usuario nuevo: popularidad suavizada no personalizada, sin inventar señal CF. Ítem nuevo: media global en CF; contenido sigue disponible si hay géneros.

Los empates de ranking del motor evaluado se resuelven por movieId ascendente. El recomendador de consultas de LAB08 conserva el orden de similitud del código base. Los vectores latentes no tienen interpretación semántica garantizada.

## Métricas offline

Corte por último evento por usuario elegible, desempate movieId. Entrena sobre 100,226 y prueba sobre 610. Todos los métodos tienen el mismo denominador, incluyendo 23 ítems no vistos en entrenamiento. RMSE usa media global ante ítem desconocido. Popularidad usa predictor de media global para RMSE; su score de ranking no se evalúa como rating. El RMSE mostrado para híbrido corresponde a MF, no a la mezcla normalizada.

HR@10 principal considera el evento retenido relevante independientemente de estrellas; P@10=HR/10, porque existe un único objetivo. También HR entre 363 eventos positivos (rating >=4). Cobertura es unión de Top-10 / 9,742. Tiempo = fit MF + ranking de 610 usuarios, sin descarga, carga, TF-IDF ni I/O. Tamaño = pickle del estado por método (ids, scores de popularidad, contenido y MF si aplica), sin historial ni entorno. No se guardan pickles en Git.

Tres semillas para métodos estocásticos; deterministas una vez. Medias y desviación muestral HR en `reports/pareto.csv`. Pareto maximiza HR y cobertura y minimiza segundos y bytes. Cambian factores y épocas conjuntamente: no se atribuye mejora solo a factores. No se midieron emisiones ni consumo eléctrico.

## Cold start, cobertura y diversidad

Perfiles: máximo historial, mínimo historial observado (19 ratings) y usuario sintético -1 sin historial. Las listas completas y Jaccard entre semillas figuran en reports. No se mide precisión del usuario sintético por falta de verdad observada. Cobertura no equivale a diversidad individual. La app permite probar tres consultas y muestra procedencia, método y advertencia interpretativa.

## Riesgos y monitoreo

Popularidad concentra exposición; contenido puede repetir géneros y MF amplifica patrones de consumo. Faltan exposiciones e impresiones: no se distinguen ítems ignorados de desconocidos. No hay demografía para auditorías poblacionales. Recomendaciones futuras pueden alterar el entrenamiento.

94 empates de tiempo impiden orden estricto en el límite. El corte por usuario admite futuro de otros usuarios y no filtra catálogo por disponibilidad temporal. Se usa la prueba para comparar configuraciones, sin validación ni test final separado: elección exploratoria, no estimación imparcial del modelo seleccionado. Las semillas no son particiones independientes ni permiten afirmar significancia.

Decisión y siguiente paso: `docs/CONCLUSION.md`. Mantener baseline económico; investigar híbrido 20/12/.75 por exposición, con validación independiente. Antes de producción: corte global estricto, múltiples positivos, diversidad/novelty por usuario, monitoreo de concentración y reranking diversificado.
