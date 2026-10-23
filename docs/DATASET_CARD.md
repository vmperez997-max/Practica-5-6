# Dataset Card · MovieLens Latest Small

Fuente: GroupLens Research, University of Minnesota. URL de descarga: https://files.grouplens.org/datasets/movielens/ml-latest-small.zip

La descarga usada está fechada en `reports/download_manifest.json`, con SHA-256 del ZIP: `696d65a3dfceac7c45750ad32df2c259311949efec81f0f144fdfb91ebc9e436`. El manifiesto se actualiza al descargar; la auditoría registra además hashes de cada CSV. Si cambia el hash, no se garantiza reproducir los resultados publicados.

## Universo observado

100,836 valoraciones, 610 usuarios anónimos, 9,742 películas y 9,724 películas valoradas. Densidad: 1.6968% del producto usuario-catálogo. Interacciones entre 1996-03-29 y 2018-09-24 UTC. La documentación oficial fecha la generación en 2018-09-26. Es una edición de desarrollo, no un benchmark archivado para resultados científicos compartidos.

Los usuarios incluidos valoraron al menos 20 películas. No hay demografía; no se pueden evaluar diferencias por sexo, edad u otros grupos. Ausencia de rating no equivale a rechazo. Las valoraciones reflejan elección de consumo y decisión de valorar, con sesgo de autoselección.

## Diccionario y validaciones

`ratings.csv`: userId, movieId, rating (0.5 a 5, pasos de 0.5), timestamp (segundos Unix UTC). `movies.csv`: movieId, title, genres (separados por `|`). `tags.csv` y `links.csv` se descargan, pero no se utilizan para entrenar.

Se comprueban columnas, ausencia de nulos, unicidad de movieId, unicidad usuario-película, claves foráneas, rango y pasos de rating y timestamps numéricos no negativos. `reports/audit.json` contiene cantidades, distribución y hashes. No se modifican los archivos originales.

## Partición

Último evento de cada usuario con al menos dos eventos para prueba; el resto para entrenamiento. Usuarios con un solo evento permanecen en entrenamiento. Orden determinista: usuario, timestamp, movieId. Hay 100,226 filas de entrenamiento y 610 de prueba; 23 ítems de prueba no tienen ratings de entrenamiento. Se mantienen los 610 usuarios en el denominador y se aplica media global a ítems desconocidos para RMSE.

En 94 usuarios hay empate entre timestamp final de entrenamiento y prueba: movieId desempata, pero no reconstruye el orden real. Este leave-one-out por usuario admite interacciones de otros usuarios posteriores al evento objetivo: no es una simulación global estricta del pasado. Se declara esta limitación; un siguiente experimento debe usar corte global, validación y test independientes y disponibilidad temporal de ítems.

## Licencia y referencia

Condiciones oficiales: https://files.grouplens.org/datasets/movielens/ml-latest-small-README.html

Uso de investigación con reconocimiento a GroupLens, sin afirmar respaldo institucional. El uso comercial requiere autorización previa. El README permite redistribución bajo sus condiciones, pero **esta entrega no redistribuye MovieLens**, conforme al mandato académico. Solo se publican código, hashes, métricas agregadas y rankings derivados de ejemplo; no se publican las valoraciones ni copias del catálogo.

Harper, F. Maxwell, y Joseph A. Konstan (2015). *The MovieLens Datasets: History and Context*. ACM Transactions on Interactive Intelligent Systems, 5(4), artículo 19. https://doi.org/10.1145/2827872
