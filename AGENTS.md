# Trabajo guiado en sorteos v1

## Objetivo y alcance

Construir la v1 local del roadmap mientras el usuario aprende a explicar,
modificar y verificar el código. Consultar `docs/ROADMAP.md` y
`docs/implementation-plan.md` antes de implementar un incremento.
El roadmap describe un destino, no capacidades ya implementadas.

## Forma de trabajo

- Trabajar en español, con explicaciones claras y ejemplos concretos.
- Realizar un incremento acordado por vez, con un concepto principal por commit.
- Antes de actuar, anunciar archivos, comandos relevantes, propósito y efectos.
- Implementar directamente el incremento acordado, sin preguntas de predicción
  ni cuestionarios de cierre, según la preferencia del usuario del 2026-11-20.
- Explicar los conceptos nuevos y fundamentar cada decisión, su efecto y sus
  alternativas relevantes. Aclarar dudas cuando el usuario las plantee.
- Ejecutar las acciones ya autorizadas del incremento sin pedir permiso por
  cada comando rutinario. No avanzar automáticamente al siguiente incremento.
- Revisar el estado de Git y preservar cambios ajenos al incremento.
- Verificar el resultado con comprobaciones proporcionales al cambio; explicar
  qué prueban y sus límites. No crear pruebas artificiales para documentación.
- Explicar el diff y registrar evidencia en `docs/learning-log.md`.
- No atribuir al usuario comprensión, respuestas o ejercicios que no expresó.
- Crear el commit cuando esté autorizado; informar su hash, archivos y validación.
- Cerrar con el resultado, las verificaciones y el próximo paso pendiente.

## Criterios técnicos

- Mantener la lógica en el paquete central, separada de CLI y Streamlit.
- Usar datos sintéticos para pruebas y demos. No versionar tokens, contraseñas,
  claves, sesiones ni datos reales de participantes o comercios.
- Verificar documentación oficial vigente de Meta antes de implementar acceso:
  permisos, campos, cuotas y pasos del roadmap son hipótesis hasta comprobarlos.
- Documentar decisiones que afecten elegibilidad, identidad y reproducibilidad.
- No publicar, desplegar ni contactar a terceros como parte implícita de un commit.
