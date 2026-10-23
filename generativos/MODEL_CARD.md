# Model Card · AE y VAE · Fashion-MNIST

**Autor de la entrega:** Victor Manuel Perez Padilla, matrícula 100801946. INF-8239, UASD. Guía docente: Edwin Ramón José Nolasco. Fecha: 23 de octubre de 2026.

## Propósito y procedencia

Demostración académica de reconstrucción, generación, espacio latente y costo. No es un generador comercial ni una herramienta para decisiones sobre personas. El enlace al ZIP docente devolvió HTTP 403 y no estaba disponible localmente; este código es una **implementación propia conforme a la guía**, no una copia verificada del proyecto base. TensorFlow está en `generativos/.venv`, con pyproject y lock independientes del recomendador.

## Datos y licencia

Fashion-MNIST, Zalando Research: 60,000 imágenes oficiales de entrenamiento y 10,000 de prueba, escala de grises 28×28 y 10 etiquetas de ropa. Licencia MIT; el aviso original se conserva en `docs/FASHION_MNIST_LICENSE.txt`. Fuentes: [repositorio oficial](https://github.com/zalandoresearch/fashion-mnist), [Xiao, Rasul y Vollgraf, 2017](https://arxiv.org/abs/1708.07747).

`reports/download_manifest.json` fija el commit de origen `b2617bb6d3ffa2e429640350f613e3291e10b141`, URLs, fechas UTC, tamaños y SHA-256 de los cuatro archivos comprimidos. La caché verifica hashes al cargar. No se publica la descarga completa ni MovieLens. Los paneles contienen ejemplos de Fashion-MNIST bajo su licencia.

Preprocesamiento: uint8 → float32 / 255; no binarización ni aumento. Partición estratificada de los 60,000: 50,000 fit y 10,000 validación, semilla 42. La prueba oficial permanece separada hasta seleccionar checkpoints por validación. Hash del orden de índices en `runtime.json`; índices locales en `data/split_indices.npz`. Las etiquetas se usan para estratificar y analizar errores, no para condicionar ni entrenar la reconstrucción. Se preservan las diez clases; no se filtran imágenes por calidad.

## Arquitectura, entrenamiento y selección

AE: Flatten(784) → Dense 256 ReLU → Dense 128 ReLU → latente 2 → Dense 128 ReLU → Dense 256 ReLU → Dense 784 sigmoid → 28×28×1. 469,010 parámetros. VAE: misma capacidad salvo dos cabezas de tamaño 2 para media y logvar; 469,268 parámetros. `z = mean + exp(0.5*logvar)*epsilon`, epsilon ~ N(0,I), manteniendo gradientes. El prior es normal estándar, no una afirmación de ajuste perfecto del posterior agregado.

AE minimiza BCE sumada en 784 píxeles y promediada por batch. VAE suma `beta*KL`, beta=1, donde KL=-0.5*sum(1+logvar-mean²-exp(logvar)). Adam .001, batch 256, 6 épocas AE y 8 VAE, semilla 42 y operaciones deterministas solicitadas. Se restaura el menor loss de validación (época 6 AE y 8 VAE). Para validación VAE se usa ruido stateless fijo por batch, evitando cambiar el ruido entre épocas.

La dimensionalidad 2 es una restricción educativa para visualizar directamente el latente; limita fidelidad. El presupuesto de épocas es distinto: la comparación describe estas configuraciones y no aísla causalmente la arquitectura. Una sola semilla de entrenamiento, sin búsqueda de hiperparámetros ni intervalo estadístico. Mismo equipo y preprocesamiento para ambos. No se afirma reproducción bit a bit entre versiones o hardware.

## Resultados ejecutados

| Método | MSE prueba | BCE/píxel | Épocas | Tiempo fit (s) | Parámetros | Modelo (MB) |
|---|---:|---:|---:|---:|---:|---:|
| Imagen media de fit | 0.086641 | 0.491094 | 0 | No medido | 784 | 0.0031* |
| AE | 0.028717 | 0.327269 | 6 | 7.70 | 469,010 | 1.922 |
| VAE, decodificar media | 0.030226 | 0.331847 | 8 | 9.94 | 469,268 | 1.926 |

Fuente: `reports/metrics.csv`. *Baseline: bytes de 784 float32, sin contenedor; AE/VAE: bytes reales `.keras`, sin optimizador. Tiempo incluye fit, validación, trazado inicial y restauración del mejor checkpoint; excluye descarga, carga, figuras y serialización. Inferencia de 10,000: AE 0.246 s y VAE media 0.243 s. El VAE incluye encoder y decoder. Decoder para app: 962,840 bytes. Son tiempos locales, no energía ni CO2; no se midió pico de RAM.

VAE KL medio de prueba: 6.0725 nats. Evaluación determinista usa `decoder(mean)`; una muestra posterior fija adicional obtiene MSE 0.030705 y BCE/píxel 0.333181. Son convenciones diferentes de reconstrucción, declaradas separadamente. BCE es un criterio sobre intensidades continuas normalizadas, no evidencia de que los píxeles sean observaciones Bernoulli binarias reales.

## Fidelidad, diversidad y espacio latente

`reconstructions.png` muestra 16 índices uniformes sin reemplazo (semilla 2026), originales y ambos modelos, sin selección manual. AE conserva mejor MSE, pero ambos borran detalles: estampado de camiseta #263, vestido #3702 y sandalias #3547/#9049. VAE convierte el bolso #797 en una forma semejante a prenda superior. La clase Bag tiene mayor MSE (AE .03760; VAE .05003); Sneaker, el menor (AE .01943; VAE .01938). Error por clase no es precisión de clasificación ni evaluación de grupos humanos.

`samples_vae.png`: primeras 16 de 256 muestras normales, semilla 2026. Hay formas de prendas superiores, pantalones y calzado, con bordes borrosos y salidas ambiguas. `samples_ae.png` usa exactamente los mismos puntos del prior: su AE no fue regularizado para esa distribución y produce imágenes muy oscuras y similares. Esa comparación muestra la falta de calibración de ese prior; no demuestra que cualquier estrategia de generación con AE fracase.

Diversidad: MSE medio entre pares distintos de 256 imágenes es .08777 en VAE y .00628 en AE con prior arbitrario; referencia de los 16 originales, .21547. Desviación media por píxel VAE .19015, AE .04816. No son medidas perceptuales ni una prueba de cobertura de las diez clases; tamaños muestrales de referencia difieren. No se calculó FID ni una métrica de realismo validada en este dominio.

Interpolación: AE entre las codificaciones de los dos primeros ejemplos del panel (bolso y abrigo); VAE entre los primeros dos puntos del prior, sin escoger extremos por estética. Las transiciones son graduales en píxeles, aunque pueden cruzar formas ambiguas. `latent_space.png` utiliza 2,000 ejemplos de prueba uniformes y etiquetas solo como color. VAE concentra coordenadas más cerca del prior; el AE muestra escalas mucho mayores. Cuadrícula VAE [-2,2]² en `latent_grid.png`. Ningún eje tiene significado semántico garantizado.

No se observa colapso total a una única imagen: varianza de medias posteriores por dimensión ~1.58 y 1.57, KL>0 y muestras diferentes. No implica ausencia de colapso parcial, categorías poco cubiertas o una distribución posterior agregada exactamente normal; la varianza posterior media ~.0045/.0063 es pequeña.

## Vecinos y posible memorización

Cada una de 256 muestras VAE se compara con los **50,000 ejemplos de fit completos** usando MSE de píxeles (sin validación). MSE al vecino: media .01021, mínimo .00248; los 16 originales de prueba tienen media .02284 a sus vecinos. No se detectaron distancias cero. Las muestras suavizadas pueden aproximarse a prototipos; un MSE más pequeño no demuestra copia. Un vecino parecido tampoco la demuestra, y no detectar igualdad no garantiza privacidad ni originalidad.

`nearest_neighbors.png` compara las primeras 16 muestras y vecinos; CSV registra índices originales y clases del vecino. Estas clases son una señal indirecta, no etiquetas verificadas de las imágenes sintéticas: Shirt aparece 53 veces frente a Coat 6 y Dress 8 de 256. No se entrenó clasificador para certificar diversidad semántica. No se hizo membership inference, búsqueda exhaustiva de duplicados aproximados ni auditoría formal de privacidad.

## Diferencias conceptuales

| Enfoque | Objetivo | Límite |
|---|---|---|
| AE | Comprimir y reconstruir | Prior arbitrario no garantiza salidas plausibles |
| VAE | Reconstrucción y regularización probabilística | Puede generar promedios borrosos o cubrir pocas formas |
| GAN | Competencia generador/discriminador | Puede colapsar y su evaluación es difícil; no se entrenó aquí |
| Transfer learning | Reutilizar representaciones preentrenadas | No es por sí solo generativo ni evita validar el dominio; no se ejecutó aquí |

## Pruebas, artefactos y uso previsto

Pruebas: parser IDX, etiquetas, normalización, partición reproducible sin intersección, reparametrización y gradientes, KL normal estándar, rangos/formas, serialización AE/VAE/decoder, diversidad nula y Streamlit con cambios de semilla y coordenadas. El notebook recarga hashes de modelos, recalcula MSE en toda la prueba y ejecuta los tests; entrenamiento repetible mediante `RETRAIN=True` o script CLI.

`models/manifest.json` identifica los seis `.keras`. La app carga solo `models/decoder.keras` mediante ruta relativa y realiza inferencia; no entrena ni descarga datos por visita. Decoder sin capas personalizadas; VAE completo requiere registrar `Sampling`, implementado en `inf8239_lab10.models`. No se requiere GPU. El extra GPU está destinado a WSL2/Linux configurado; no se probó esa ruta ni un despliegue en nube.

Decisión: AE para reconstrucción didáctica, VAE para explorar muestreo y regularización. No usar estas imágenes como catálogo comercial, prueba de originalidad o garantía de privacidad. Siguiente experimento: más dimensiones y arquitectura convolucional, comparación a igual presupuesto, varias semillas y validación perceptual/diversidad apropiada, manteniendo una nueva prueba final intacta al ajustar configuraciones. No optimizar más después de mirar esta prueba y seguir llamándola independiente.

## Referencias

- Xiao, H., Rasul, K. y Vollgraf, R. (2017). *Fashion-MNIST: a Novel Image Dataset for Benchmarking Machine Learning Algorithms*. https://arxiv.org/abs/1708.07747
- Kingma, D. P. y Welling, M. (2013). *Auto-Encoding Variational Bayes*. https://arxiv.org/abs/1312.6114
- TensorFlow. *Convolutional Variational Autoencoder* (referencia conceptual; este trabajo usa arquitectura densa y Fashion-MNIST). https://www.tensorflow.org/tutorials/generative/cvae
