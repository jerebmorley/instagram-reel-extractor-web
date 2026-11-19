# Plan de implementación y aprendizaje

Fecha: 2026-11-19.

## Cómo usar este plan

Cada fila propone un commit con un objetivo verificable. Si resulta grande para
entender su diff, dividirla antes de implementar. Las diez semanas del roadmap
son orientativas: el avance depende de la evidencia y del aprendizaje.

Ciclo: concepto → predicción del usuario → aviso de acciones → implementación →
verificación → lectura del diff → learning-log y commit → pausa de aprendizaje.

Las predicciones se responden antes del cambio técnico; las preguntas de cierre,
después. Una respuesta breve o incompleta sirve. El usuario puede optar por omitir
el ejercicio. La IA no debe inventar sus respuestas ni su comprensión.

## Estado inicial observado

- Extractor con `instaloader` y autenticación mediante contraseña.
- Interfaz Flask en `version_web`, con debug activo y escucha en todas las interfaces.
- 3.118 archivos de `venv/` versionados; `.gitignore` solo contempla `.venv/`.
- Árbol de trabajo limpio antes del incremento 00.

## Secuencia de commits

### Etapa 0: ordenar el proyecto

| ID | Commit propuesto | Aprendizaje y criterio de cierre |
|---|---|---|
| 00 | `docs: registrar alcance v1 y método de aprendizaje` | Roadmap, plan, registro e instrucciones para IA disponibles; revisión documental. |
| 01 | `chore: dejar de versionar el entorno virtual` | Distinguir carpeta, índice e historial. `venv/` permanece local y sale del índice. |
| 02 | `fix: restringir el servidor legado a uso local` | Desactivar debug y escuchar en localhost mientras exista el prototipo. |
| 03 | `refactor: retirar el extractor legado y su interfaz` | Retirar flujos con contraseña, `instaloader` y `version_web`; actualizar dependencias y README. |
| 04 | `build: crear el paquete sorteos y herramientas locales` | Crear `src/sorteos`, configuración, pytest, Ruff y `make test`; comprobar instalación e importación en entorno limpio. |
| 05 | `ci: ejecutar comprobaciones en cada cambio` | Automatizar las comprobaciones locales y verificar su ejecución en CI. |
| 06 | `docs: registrar decisiones de arquitectura v1` | ADR sobre fuentes autorizadas y operación local asistida. |

El incremento 03 deja temporalmente el proyecto sin la funcionalidad anterior.
El prototipo se conserva en el historial de Git; no se mantendrán dos sistemas.

### Etapa 1: comprobar acceso real

| ID | Commit propuesto | Aprendizaje y criterio de cierre |
|---|---|---|
| 07 | `docs: documentar preparación de la cuenta de prueba` | Consultar documentación oficial vigente y registrar matriz de capacidades esperadas. El usuario autentica y opera el panel. |
| 08 | `feat: consultar el perfil con un token local` | Peticiones HTTP, autenticación y errores; ninguna credencial en código, Git ni logs. |
| 09 | `feat: consultar una publicación y sus comentarios` | Observar campos reales de comentarios y respuestas; registrar conclusiones sin datos personales. |
| 10 | `feat: guardar credenciales cifradas localmente` | Separar clave y datos; probar guardado, lectura y errores con credenciales ficticias. |

Permisos, tamaños de página, campos, cuotas y vencimientos del roadmap requieren
verificación. Si falla el acceso real, continuar con archivos y fixtures, dejando
la integración explícitamente pendiente.

### Etapa 2: núcleo sin red

| ID | Commit propuesto | Aprendizaje y criterio de cierre |
|---|---|---|
| 11 | `feat: definir el contrato de comentario` | IDs, autor, publicación, fecha y respuestas; probar datos válidos e incompletos. |
| 12 | `feat: detectar y normalizar menciones` | Tabla de casos: puntuación, mayúsculas, repetidos, correos, URLs y caracteres parecidos. |
| 13 | `feat: evaluar fechas y exclusiones` | Funciones puras; probar límites temporales, lista negra y motivos de descarte. |
| 14 | `feat: evaluar menciones requeridas` | Contar personas distintas y excluir autoarrobas y al comercio. |
| 15 | `feat: consolidar una entrada por participante` | Separar comentario válido y participante habilitado; probar comentarios múltiples. |
| 16 | `test: generar campañas sintéticas reproducibles` | Crear ruido y casos límite; medir 10.000 comentarios y comprobar resultados idénticos. |

Antes del 15, definir identidad, admisión de respuestas y si las menciones se
cuentan por comentario o se acumulan. No resolver estas reglas de manera implícita.

### Etapa 3: fuentes, persistencia y reanudación

| ID | Commit propuesto | Aprendizaje y criterio de cierre |
|---|---|---|
| 17 | `feat: cargar comentarios desde fixtures y archivos` | Contrato común, JSON/CSV y validación con errores comprensibles. |
| 18 | `feat: producir snapshots canónicos con sha256` | Orden y serialización estables; mismas entradas producen los mismos bytes y hash. |
| 19 | `feat: persistir trabajos en SQLite` | Tablas, transacciones y WAL; guardar progreso y estados. |
| 20 | `feat: paginar comentarios y respuestas de Graph` | Implementar paginación según comportamiento verificado de la API. |
| 21 | `feat: limitar reintentos y consumo de API` | Simular errores transitorios y límites; los reintentos deben terminar. |
| 22 | `feat: reanudar extracciones interrumpidas` | Persistir datos y cursor consistentemente, sin pérdidas ni duplicados. |
| 23 | `test: verificar recuperación de una extracción completa` | Interrumpir 10.000 comentarios sintéticos y obtener el mismo snapshot que sin interrupción. |

La igualdad de hashes se exige sobre una fuente sintética estable. En una fuente
real pueden agregarse o borrarse comentarios durante la extracción; registrar esa
limitación y no prometer una captura atómica de Instagram.

### Etapa 4: sorteo verificable

| ID | Commit propuesto | Aprendizaje y criterio de cierre |
|---|---|---|
| 24 | `feat: congelar participantes reglas y revisiones` | Guardar elegibles, reglas y decisiones manuales con motivos. |
| 25 | `feat: registrar el compromiso de la semilla` | Compromiso y revelación; registrar evidencia de publicación previa, sin publicar automáticamente. |
| 26 | `feat: seleccionar ganadores y suplentes` | Ranking determinista con entrada bien definida y desempate estable; independiente del orden inicial. |
| 27 | `feat: generar acta y verificar el resultado` | Acta HTML imprimible y datos/versiones suficientes; `verify` reproduce resultados y detecta alteraciones. |

Reproducibilidad no demuestra por sí sola imparcialidad: fijar reglas y evitar
cambios silenciosos de participantes o semilla.

### Etapa 5: interfaz local

| ID | Commit propuesto | Aprendizaje y criterio de cierre |
|---|---|---|
| 28 | `feat: crear un flujo Streamlit con datos sintéticos` | Separar presentación y lógica; entender reejecuciones. |
| 29 | `feat: configurar cuenta publicaciones y reglas` | Formularios, validación, estados vacíos y errores. |
| 30 | `feat: ejecutar extracciones en un subproceso` | Progreso persistido; reejecutar la interfaz no duplica el trabajo. |
| 31 | `feat: revisar descartes y alertas con registro` | Distinguir sospecha y exclusión; registrar cada excepción. |
| 32 | `feat: completar sorteo acta e historial` | Recorrer el flujo completo desde la interfaz. |
| 33 | `fix: resolver problemas observados en pruebas de uso` | Observar a dos personas; corregir dificultades concretas y comprobar el flujo sin ayuda. |

### Etapa 6: finalistas y reporte

| ID | Commit propuesto | Aprendizaje y criterio de cierre |
|---|---|---|
| 34 | `feat: registrar verificación manual de finalistas` | Estado, fecha y motivo; aplicar suplencias según reglas previamente definidas. |
| 35 | `feat: generar resumen y exportación CSV` | Entradas, participantes, descartes y cuentas más mencionadas contra fixtures conocidos. |
| 36 | `feat: informar cobertura y límites de extracción` | Distinguir cobertura desconocida, discrepancia y coincidencia de conteos; coincidir no garantiza integridad. |

Cruce con export de seguidores y curva temporal son opcionales, después del flujo
principal. Recortar según el orden del roadmap si falta tiempo.

### Etapa 7: piloto y cierre

| ID | Commit propuesto | Aprendizaje y criterio de cierre |
|---|---|---|
| 37 | `docs: preparar consentimiento y guía del piloto` | Alcance, token, retención y bases; verificar requisitos aplicables antes del sorteo real. |
| 38 | `feat: aplicar limpieza por retención` | Vista previa de borrado y comprobaciones con datos ficticios. |
| 39 | `docs: registrar retrospectiva anonimizada del piloto` | Registrar evidencia del recorrido real y mejoras sin versionar datos personales. |
| 40 | `docs: publicar instrucciones de instalación y demo` | Otra persona instala y completa demo sintética desde README; incluir demostración visual. |

## Preguntas de cierre de cada incremento

1. ¿Qué problema resolvimos?
2. ¿Por qué elegimos esta solución?
3. ¿Qué evidencia tenemos de que funciona?
4. ¿Qué todavía no resuelve?

Alternar explicaciones con ejercicios pequeños del usuario: agregar un caso de
prueba, interpretar un error o modificar una regla.

## Relación con el roadmap original

`ROADMAP.md` conserva el texto entregado por el usuario. Este plan adapta la
ejecución al repositorio observado: usamos `AGENTS.md` como instrucciones de IA
en lugar del `CLAUDE.md` sugerido allí. Las referencias externas y afirmaciones
de API o normativa del original no se verificaron en el incremento documental 00.
