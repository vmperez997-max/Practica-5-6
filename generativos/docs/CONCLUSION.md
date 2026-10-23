# Cierre interpretativo · LAB10

Resultado de reconstrucción: AE logra MSE 0.028717, VAE con media posterior 0.030226; ambos mejoran el baseline .086641. AE pierde estampados y detalles; VAE confunde el bolso #797 con una prenda superior. Bag es la clase de mayor MSE; no se interpreta como error de clasificación.

Resultado de generación: VAE produce prendas superiores, pantalones y calzado con bordes borrosos y formas ambiguas. El AE con el mismo prior N(0,I) produce imágenes oscuras y poco variadas; ese prior no está calibrado para su latente. No se concluye que todas las estrategias generativas AE fallen.

Evidencia de diversidad: MSE medio entre pares VAE 0.08777, AE-prior 0.00628; los 16 originales dan 0.21547. Son distancias de píxel, no realismo ni diversidad semántica certificados, con referencia de distinto tamaño. Las clases de vecinos son diagnósticos indirectos y desbalanceados.

Comportamiento del latente: interpolaciones graduales en píxeles, con formas intermedias ambiguas. El VAE contiene medias en escala más cercana al prior; los ejes no tienen significado garantizado. KL de prueba 6.0725 nats; no se observa colapso total a una única salida, pero no se descarta cobertura parcial. AE usa coordenadas de escala mayor.

Costo computacional: CPU, AE 7.70 s / 6 épocas y VAE 9.94 s / 8 épocas, incluyendo validación y trazado. No es una comparación a igual presupuesto. Tamaños .keras 1.922 y 1.926 MB. No se midieron energía ni pico de RAM. Inferencia 10,000: 0.246 s AE y 0.243 s VAE, en este equipo.

Riesgo o limitación: una semilla, latente de solo 2 dimensiones, intensidades de baja resolución, métrica no perceptual y vecinos sin auditoría formal de privacidad. Los 256 outputs tienen MSE medio a fit 0.01021 y mínimo 0.00248, sin distancia cero detectada; no demuestra originalidad ni ausencia de memorización. El dato puede ser semejante por ser un prototipo suavizado.

Decisión sobre uso previsto: AE para enseñar reconstrucción y VAE para muestreo probabilístico. No usar como catálogo comercial ni afirmar privacidad o novedad. Siguiente paso: mayor latente y redes convolucionales, igual presupuesto, varias semillas, métricas perceptuales y de diversidad adecuadas; otra prueba independiente al ajustar configuraciones. GAN y transferencia solo se comparan conceptualmente, sin entrenamiento en esta entrega.
