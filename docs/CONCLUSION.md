# Conclusión interpretativa

## LAB08

Resultado principal: popularidad suavizada proporciona una referencia económica. LAB08 describe el dataset completo; la evaluación comparativa calcula las señales solo con entrenamiento. El suavizado combina media del ítem y media global, con m igual al percentil 80 de los conteos, y solo admite en el ranking de popularidad ítems con conteo >= m. Ítems fuera de ese grupo reciben media global en el motor de ranking completo.

Evidencia utilizada: `popular_top10.csv`, `content_recommendations.csv`, manifiesto y auditoría. Las consultas son Toy Story (Animation/Adventure/Comedy/Fantasy), The Shawshank Redemption (Crime/Drama) y The Exorcist (Horror/Mystery).

Qué representa la similitud: coseno entre vectores TF-IDF de géneros, no probabilidad de agrado. Películas con idénticos géneros tienen vectores iguales y empatan. Con el tokenizador original, Sci-Fi se separa en tokens; no se interpreta como semántica profunda.

Cold start: el método por contenido puede encontrar similares para una película sin ratings si tiene géneros; un usuario sin historial carece de perfil y recibe popularidad compartida.

Sobre-especialización: The Shawshank Redemption puede producir un Top-10 exclusivamente Crime/Drama; la igualdad de metadatos oculta diferencias de trama, época y calidad. Un siguiente experimento debe diversificar géneros y medir exposición, sin asumir que cobertura equivale a diversidad individual.

## LAB09

Resultado de ratings: MF 20/12 obtiene RMSE medio 1.0277, frente a 1.1169 del predictor de media global. El RMSE del híbrido es el de su componente MF: la mezcla de scores normalizados no predice estrellas. El baseline de RMSE usa media global y no debe confundirse con la política de ranking por popularidad suavizada.

Resultado de ranking: popularidad HR@10 3.1148%; colaborativo 20/12 3.3880%; híbrido 20/12, alpha .75 3.2787%. Híbrido alpha .25 obtiene 1.4208%. Con alpha .75 domina la señal colaborativa; .25 favorece contenido. Los scores de ambas señales se normalizan min-max sobre los mismos candidatos antes de mezclarse.

Cobertura: popularidad 0.69%, colaborativo 7.34%, híbrido .75 9.56% e híbrido .25 13.12% del catálogo de 9,742 películas. Cobertura es la unión de todos los Top-10, no una métrica de satisfacción ni de equidad.

Usuario frío: -1 es sintético y recibe la misma lista de popularidad para todas las configuraciones. Los otros perfiles se eligen por máximo y mínimo historial de entrenamiento; el menor historial observado aún tiene 19 interacciones y no representa cold start extremo. La estabilidad entre semillas se registra en `profile_stability.csv`.

Configuración seleccionada: para un despliegue académico con prioridad al costo, popularidad como referencia por defecto. Está en Pareto y logra casi el mismo HR que el híbrido con menor costo. Para estudiar personalización y exposición, se selecciona entre los híbridos 20 factores, 12 épocas y alpha .75: mejora HR respecto de .25 a costa de cobertura. Es una elección exploratoria: no se usó validación independiente y por tanto no se afirma generalización del valor elegido.

Costo: popularidad 0.71 s y 0.16 MB; híbrido elegido 10.24 s y 3.04 MB. Es 14.3 veces el tiempo para una ganancia media de 0.164 puntos porcentuales de HR y 8.87 puntos de cobertura. Los tiempos suman entrenamiento MF y ranking de 610 usuarios; excluyen descarga, carga, TF-IDF compartido e I/O. El tamaño mide pickle del estado por método (ids, popularidad, contenido/MF cuando aplica), sin historial ni runtime. No se publican pickles ni datos. No se midieron energía ni CO2.

Pareto: se maximiza HR y cobertura y se minimizan segundos y bytes, usando medias entre semillas. `pareto.csv` marca dominancia estricta en al menos un objetivo y no peor en los demás. Diferencias pequeñas de tiempo no implican mejoras robustas. Se incluyen los deterministas una vez porque repetir semillas no cambia sus salidas.

Riesgo principal y mitigación: concentración popular y burbuja de filtro. Mantener baseline, medir diversidad por usuario, exposición y novedad; probar reranking diversificado y monitorear retroalimentación. No se pueden afirmar resultados por grupos sin demografía.

Limitaciones: una sola película retenida por usuario; todos los ratings cuentan como interacción relevante para HR principal. P@10 es HR/10 por diseño, no una medida independiente. También se informa HR entre los 363 eventos de rating >=4. Hay 23 ítems desconocidos en entrenamiento, sin exclusión del denominador. Hay 94 empates temporales y posible fuga entre usuarios. Próximo experimento: corte global estricto con disponibilidad del catálogo, validación separada, múltiples positivos y prueba final intacta. Las tres semillas no son tres muestras independientes de usuarios ni permiten afirmar significancia estadística.
