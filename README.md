# Sorteos de Instagram — v1 local

Herramienta en construcción para operar sorteos de pequeñas cuentas y negocios
locales desde la computadora del operador.

## Estado actual

Completado el incremento 03: se retiraron el extractor anterior, la interfaz Flask
y sus dependencias. **Todavía no hay una aplicación ejecutable ni instrucciones
de instalación para la nueva v1.** El siguiente incremento crea el paquete Python
`src/sorteos` y las herramientas de comprobación local.

El prototipo solicitaba contraseñas de Instagram. La nueva arquitectura prevé
fuentes autorizadas, acceso mediante token y un modo archivo con datos sintéticos.
La disponibilidad y los requisitos del acceso real se verificarán antes de
implementar esa integración.

## Alcance previsto

- Operación local asistida, sin hosting, cuentas de usuario ni pagos.
- Núcleo Python compartido por CLI y Streamlit, con SQLite para persistencia.
- Extracción reanudable, reglas de participación y revisión con registro.
- Sorteo reproducible, acta verificable y exportación de resultados.

Estas capacidades son objetivos del roadmap, no funciones ya disponibles.

## Documentación

- [Roadmap original](docs/ROADMAP.md): alcance y etapas de la v1.
- [Plan de implementación](docs/implementation-plan.md): commits y criterios de cierre.
- [Registro de aprendizaje](docs/learning-log.md): decisiones y evidencia.
- [Instrucciones para la IA](AGENTS.md): método de colaboración.

## Historial del prototipo

El último commit que contiene el prototipo es `d49aeb7`. Se puede consultar sin
restaurarlo ni modificar la carpeta de trabajo:

```bash
git show d49aeb7:extraerComentariosReels.py
git show d49aeb7:version_web/app.py
```

La retirada no desinstala paquetes del entorno virtual local ni elimina archivos
locales ignorados o no versionados. Los entornos virtuales, credenciales y datos
reales no deben incorporarse al repositorio.
