# Declaración de IA · Unidad 04

OpenAI Codex apoyó inspección y corrección del proyecto base local, implementación, pruebas, ejecución, preparación de evidencias, documentación, PDF y Git. No se atribuyen a la IA autoridad institucional, aprobación jurídica ni valoración personal del estudiante.

## Prompts y valores

El estudiante proporcionó las guías LAB11–13 y las rúbricas E07/E08; se conservaron sus instrucciones anteriores de publicar en `vmperez997-max/Practica-5-6` y usar su documento de Unidad 02 como formato del PDF. Ante la pregunta sobre el daño a priorizar respondió literalmente: **«No omitir zonas que necesitan revisión humana»**. Esta prioridad orienta recall y la comparación de umbral.

Los umbrales originales de la base se conservaron. Soporte30/10, costo30s, retención30/90/180, checklist de traspaso y puntuaciones cualitativas de riesgos se documentan como **propuestas académicas** para revisión del estudiante, no como preferencias confirmadas de afectados ni probabilidades medidas. Ningún expediente sustituye la revisión personal requerida por la rúbrica. La decisión técnica REVIEW es resultado de controles y no una aprobación de uso real.

## Verificaciones y correcciones

- Se usó la base U04 disponible localmente; los diez tests originales pasaron antes de completar el trabajo. No se recreó el dataset ni se inventó semilla de generación.
- Se detectó age_band como predictor pese a estar declarada sensible y se excluyó junto con protected_group.
- Se añadieron validación de nulos, tipos/rangos, unicidad, categorías, allowlist y partición estricta sin romper fechas empatadas.
- Se corrigieron dos scripts originales con cadenas multilínea inválidas (LAB11 y simulacro) y el sobrescrito del registro de decisión al reejecutar LAB11.
- Se separó validación temporal para elegir umbral/modelo antes de prueba; se compararon Dummy, logística, árbol y mitigación de umbral, sin usar prueba para elegir.
- Se agregaron conteos por clase, soporte, intervalos Wilson y desconocidos como NaN/null; no se ocultan grupos pequeños ni se convierten denominadores cero en brechas cero.
- Se amplió RACI a exactamente un A, se hicieron efectivas puertas de privacidad/soporte/costo y se registró REVIEW por falta de evidencia interseccional suficiente.
- Se ejecutó un simulacro con alarma inyectada y rollback verificable que bloquea carga del modelo y probabilidad. No se enviaron mensajes externos ni se simularon firmas reales.
- Se revisaron hashes de dataset, política y modelos; se preservaron bytes originales CRLF del CSV en Git para reproducir sus hashes en otros sistemas.
- Las primeras pruebas del entorno restringido mostraron un aviso de limpieza de temporales. La ejecución final se realiza con permisos de temporales y conserva resultados reales.
- Se revisan los PDF renderizados y las referencias institucionales. No se inventan cifras, bibliografía, decisiones humanas ni comunicaciones.

El estudiante debe revisar las propuestas de valor, supuestos, umbrales, riesgos y conclusiones, reproducir el trabajo y poder defender cada elemento. No se afirma que haya realizado esa revisión completa ni que las instituciones ficticias hayan aceptado responsabilidades.
