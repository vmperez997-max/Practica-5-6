# Declaración de herramientas de IA

Se utilizó OpenAI Codex para inspeccionar y ampliar el proyecto base, corregir código, ejecutar experimentos, preparar pruebas, notebook, tarjetas e informe y publicar en el repositorio solicitado. No se atribuye a la IA una validación humana ni una defensa realizada por el estudiante.

## Prompt relevante

El estudiante proporcionó las instrucciones completas de LAB08, LAB09 y Ejercicio 05: auditoría MovieLens, popularidad, contenido, factorización, híbrido, tres perfiles, tres semillas, Pareto, pruebas, notebook ejecutado, PDF breve y publicación en `https://github.com/vmperez997-max/Practica-5-6.git`.

La solicitud final fue: «Al final de todo lo quiero en Git hub» con dicho enlace. No se utilizaron prompts adicionales del estudiante para alterar resultados.

## Verificaciones y correcciones realizadas

- Se reutilizó la carpeta base ya presente; se creó un único entorno Python 3.12 con uv.
- Se verificó el README oficial de GroupLens y se registraron hash y fecha de descarga.
- Se amplió la validación de datos y se corrigió el corte para usuarios de un evento y empates reproducibles.
- Se reemplazó la preselección colaborativa de 100 candidatos del híbrido por puntuación sobre todo el catálogo sin vistos. Así alpha=0 puede representar contenido sin el filtro colaborativo previo.
- Se mantuvieron los ítems desconocidos en la evaluación y se corrigió el denominador de HitRate para que listas ausentes cuenten como fallos.
- Se agregó un baseline suavizado consistente y una política explícita para usuarios nuevos.
- Se ejecutaron pruebas del código y de la interfaz con tres películas; se verificó el notebook sin celdas con error y se revisó el PDF renderizado.
- Se corrigieron caracteres dañados por la codificación de la consola durante la preparación de la interfaz.
- Se distinguieron ratings, ranking de interacciones y ranking de positivos; se documentaron fuga temporal entre usuarios, empates y selección exploratoria.

No se inventaron métricas ni bibliografía. Los resultados proceden de `scripts/run_experiments.py` ejecutado por el notebook. Los tiempos dependen del equipo y de la carga. La medición es de tiempo y tamaño, no de energía ni emisiones.

## Responsabilidad del estudiante

Antes de entregar, el estudiante debe revisar el código y las salidas, confirmar autoría y datos de identificación, reproducir los comandos y poder explicar TF-IDF, SGD, exclusión de vistos, cold start, métricas y límites del corte. Esta declaración no afirma que esa revisión personal ya se realizó.
