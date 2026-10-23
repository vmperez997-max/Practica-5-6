# Declaración de uso de IA · LAB10

Se utilizó OpenAI Codex para diseñar y completar la implementación, depurar, entrenar AE/VAE, construir pruebas y app, ejecutar el notebook, revisar paneles, redactar documentación y producir el PDF. No se afirma revisión humana ya realizada ni defensa del estudiante completada.

## Prompts relevantes

El estudiante proporcionó las instrucciones de «U03.LAB10 · Autoencoder y VAE con Fashion-MNIST», el mandato de consolidación y la rúbrica del Ejercicio 06, y pidió: «Ahora este trabajo». En la sesión había indicado publicar las actividades en `https://github.com/vmperez997-max/Practica-5-6.git` y utilizar «Unidad 02. Ejercicio 03 - Victor_Perez» como base del PDF. Estas preferencias se conservaron para esta entrega.

## Acciones, verificaciones y correcciones

- La URL del ZIP docente respondió HTTP 403. Se declaró implementación propia siguiendo la guía, sin atribuirle identidad con el ZIP inaccesible.
- Se creó `generativos/` con entorno, dependencias y lock independientes; TensorFlow no se agregó al proyecto del recomendador.
- Se consultaron la fuente oficial de Fashion-MNIST y el tutorial oficial de VAE de TensorFlow. Se fijó commit de dataset, hashes, fecha y licencia.
- Se separó validación desde entrenamiento; prueba se usó después de restaurar los checkpoints elegidos por validación. No se escogieron imágenes por su calidad.
- Se registraron costo, errores, curvas, interpolación, muestras y vecinos sobre todos los ejemplos de fit. Se distinguió reconstrucción de la media y muestra posterior del VAE.
- Una ejecución inicial de pytest encontró restricciones del directorio temporal del entorno restringido. Las pruebas se volvieron a ejecutar desde el notebook con permisos de kernel local; se conservaron los resultados reales en `reports/tests.txt`.
- Se corrigieron títulos superpuestos del panel reconstruido, sin cambiar índices, muestras ni modelos; `scripts/refresh_panels.py` regenera el panel desde los checkpoints.
- La consola PowerShell envolvió un warning de compatibilidad interno de TensorFlow como NativeCommandError. El entrenamiento sí completó las 14 épocas y guardó modelos y métricas. Los eventos de épocas se conservan en `reports/training_log.txt`, sin el envoltorio de consola; no se modifican sus valores.
- Se comprobó recarga de modelos, flujo de gradientes y aplicación Streamlit. El notebook verifica hashes y recalcula métricas sobre las 10,000 imágenes de prueba.
- Se revisaron visualmente paneles e informe PDF. Se documentó la borrosidad, el error de reconstrucción del bolso y la diversidad limitada del AE con prior arbitrario.

Los números proceden de ejecuciones reales. La IA no demuestra privacidad, originalidad, equivalencia visual ni significancia estadística. La interpretación es exploratoria, con una semilla de entrenamiento y presupuestos distintos de épocas.

El estudiante es responsable de revisar fuentes, código, resultados y conclusiones; debe reproducir los comandos y poder explicar BCE, KL, reparametrización, particiones, vecinos y límites. No se atribuye al estudiante una revisión personal que todavía no ha confirmado.
