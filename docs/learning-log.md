# Registro de aprendizaje

Registrar decisiones, fundamentos y evidencia. Desde el 2026-11-20 se implementa
sin preguntas ni ejercicios obligatorios, por preferencia del usuario. Las
respuestas históricas se conservan; no confundir cambios con comprensión demostrada.

## Incremento 00 — Plan y método de trabajo

Fecha: 2026-11-19.

- Qué intentaba resolver: convertir el roadmap en incrementos pequeños y dejar
  instrucciones persistentes para trabajar con la IA de forma guiada.
- Qué creía que iba a pasar: pendiente de reflexión del usuario; este incremento
  fue autorizado como preparación documental.
- Qué cambió: roadmap original conservado en `ROADMAP.md`, secuencia de commits
  en `implementation-plan.md`, este registro e instrucciones en `../AGENTS.md`.
- Concepto presentado: el roadmap define alcance y destino; el plan lo convierte
  en cambios verificables; el registro conserva evidencia y aprendizaje.
- Verificación realizada: `cmp` confirmó que el roadmap es idéntico al original;
  el diff contiene únicamente los cuatro documentos previstos y
  `git diff --cached --check` pasó sin errores. No se ejecutó la aplicación
  ni se crearon pruebas de código para estos cambios documentales.
- Qué puedo explicar ahora: el usuario identifica el roadmap y el plan como
  herramientas para una implementación ordenada y documentada; el registro es
  personal y acompaña su formación como ingeniero de datos. Se explicó que el
  roadmap define alcance y etapas, y el plan los convierte en cambios verificables.
- Qué todavía me genera dudas: pendiente de respuesta del usuario.
- Pregunta de cierre: ¿qué diferencia ves entre el roadmap, el plan de commits
  y el registro de aprendizaje?
- Próximo incremento al cerrar esta etapa: 01, dejar de versionar `venv/`.

## Incremento 01 — Dejar de versionar el entorno virtual

Fecha: 2026-11-19.

- Qué intentaba resolver: quitar del versionado los 3.118 archivos del entorno
  virtual, conservando la instalación local.
- Qué creía que iba a pasar (usuario): los archivos seguirían en su computadora,
  Git dejaría de registrarlos y las versiones antiguas los conservarían.
- Aclaración conversada: el cambio aparecerá en la versión actual de GitHub
  cuando se suba el commit; los commits anteriores seguirán conteniendo `venv/`.
- Cambio realizado: agregar `venv/` a `.gitignore` y ejecutar
  `git rm -r --cached venv`. `--cached` retira los archivos del índice (la
  preparación del próximo commit) y conserva los archivos de trabajo.
- Concepto presentado: `.gitignore` evita incorporar archivos no seguidos;
  por sí solo no deja de seguir archivos que ya estaban versionados.
- Verificación: los 3.118 archivos locales conservaron su contenido (comparación
  de SHA-256 y destinos de enlaces antes/después); `git ls-files venv` quedó
  vacío; el commit anterior conserva las 3.118 rutas. `git check-ignore -v`
  confirmó las reglas de `venv/` y `.venv/`. La revisión del diff no detectó
  cambios de código y `git diff --cached --check` pasó sin errores.
- Qué puedo explicar ahora: la predicción del usuario distingue archivos locales,
  versionado actual e historial. La comprensión de `.gitignore` queda por revisar.
- Qué todavía me genera dudas: pendiente de respuesta del usuario.
- Pregunta de cierre: ¿por qué agregar `venv/` a `.gitignore` no era suficiente?
- Respuesta posterior del usuario: sin `--cached`, `git rm` habría borrado los
  archivos versionados de `venv/` también de la computadora.
- Próximo paso al cerrar esta etapa: incremento 02.

## Incremento 02 — Restringir el servidor legado a uso local

Fecha: 2026-11-19.

- Qué intentaba resolver: limitar el servidor Flask del prototipo al equipo del
  operador y desactivar las herramientas de debug durante esta transición.
- Qué creía que iba a pasar (usuario): inicialmente interpretó que pasar a
  `127.0.0.1` permitiría acceder también desde el celular.
- Aclaración conversada: `0.0.0.0` escucha en todas las interfaces IPv4, lo que
  permite acceso desde la red si el firewall lo admite; `127.0.0.1` es la
  dirección de loopback del propio dispositivo y limita el acceso directo al
  equipo local. `localhost` en el celular se refiere al propio celular.
- Qué puedo explicar ahora: tras la explicación, el usuario identificó
  correctamente `0.0.0.0` como la opción para escuchar desde otros dispositivos.
- Qué cambió: `app.run` usa `debug=False` y `host="127.0.0.1"`; el README
  documenta el acceso local, el reinicio manual y el alcance del arranque directo.
- Cómo lo comprobé: compilación en memoria de `app.py` sin errores de sintaxis;
  ejecución aislada del bloque principal con un sustituto de `app.run`, que
  confirmó host, debug, puerto e hilos esperados. `git diff --check` pasó sin
  errores. No se inició un servidor real ni se escribió el archivo de estado.
- Límites: no se prueba extracción ni autenticación con Instagram. Este cambio
  configura `python app.py`, no otros lanzadores ni despliegues existentes.
- Qué todavía me genera dudas: pendiente de respuesta del usuario.
- Pregunta de cierre: con debug desactivado, ¿qué harías después de modificar
  el código para que el servidor que ya está ejecutándose use esos cambios?
- Aclaración posterior: el usuario propuso hacer push para cargar los cambios;
  se explicó que push actualiza GitHub y que el servidor local se reinicia con
  `Ctrl+C` y `python app.py`. El commit 02 fue subido a main.
- Próximo paso al cerrar esta etapa: incremento 03.

## Incremento 03 — Retirar el prototipo anterior

Fecha: 2026-11-20.

- Objetivo: retirar los flujos que solicitan contraseñas antes de construir el
  núcleo local basado en fuentes autorizadas.
- Decisión: eliminar el extractor y los archivos versionados de `version_web`,
  incluidos interfaz, estado de ejemplo y configuración de despliegue; todos
  pertenecían al flujo anterior y mantenerlos dejaría puntos de entrada obsoletos.
- Dependencias: retirar ambos `requirements.txt`; Flask, instaloader y requests
  solo eran utilizados por el prototipo. Las dependencias del nuevo núcleo se
  declararán cuando se necesiten, sin desinstalar el entorno local existente.
- Documentación: reemplazar las instrucciones obsoletas del README por el estado
  real de transición y referencias al plan. El commit `d49aeb7` conserva el
  prototipo para consulta sin restaurarlo en la carpeta de trabajo.
- Método: actualizar AGENTS.md y el plan para implementar directamente, sin
  cuestionarios, manteniendo fundamentos y verificaciones. Se conserva el
  roadmap original como documento de origen.
- Verificación: se comprobaron los 13 retiros previstos y la ausencia de código
  Python, JavaScript y HTML versionado restante; los enlaces locales del README
  resuelven a archivos existentes. `git cat-file -e` confirmó que el extractor y
  la app anterior siguen en `d49aeb7`; `venv/` permanece local.
  `git diff --check` pasó sin errores. No se ejecutó la aplicación ni se
  agregaron pruebas artificiales para esta retirada y sus documentos.
- Límite: no hay aplicación ejecutable en este punto. Retirar archivos locales
  no elimina despliegues remotos existentes ni archivos ignorados del operador.
- Próximo paso: incremento 04, paquete Python y herramientas locales.

## Incremento 04 — Paquete Python y herramientas locales

Fecha: 2026-11-20.

- Objetivo: disponer de una base instalable y un comando único de comprobación
  antes de implementar reglas o acceso a datos.
- Estructura: `src/sorteos` separa el paquete del repositorio; la distribución
  se llama `sorteos-ig` y se importa como `sorteos`. Se usa versión de desarrollo
  `0.1.0.dev0` porque todavía no existe la funcionalidad de la v1.
- Configuración: `pyproject.toml` centraliza metadatos, Hatchling como constructor,
  pytest y Ruff. Se conserva Python >=3.10 como mínimo declarado. No hay
  dependencias de ejecución; pytest y Ruff pertenecen al grupo de desarrollo.
- Instalación: uv crea `.venv` y fija las dependencias resueltas en `uv.lock`.
  `--locked` evita actualizar silenciosamente ese archivo. Los requisitos del
  constructor se resuelven aparte en el entorno de construcción aislado.
- Comprobaciones: `make test` ejecuta lint, comprobación de formato sin edición
  y pytest. Se incluyen reglas para imports ordenados. No se crean módulos
  vacíos de negocio ni pruebas de funcionalidades aún inexistentes.
- Prueba inicial: ejecuta Python con `-I` desde una carpeta temporal para importar
  `sorteos` y leer sus metadatos instalados sin depender del directorio actual
  ni de `PYTHONPATH`. Detecta errores de instalación y descubrimiento del paquete.
- Evidencia: `make install test` creó un entorno nuevo y pasó con Python 3.14.3,
  pytest 9.2.0 y Ruff 0.17.6: lint correcto, dos archivos con formato correcto y
  una prueba aprobada. `uv build --wheel --offline` creó el wheel; instalado sin
  dependencias en otro entorno temporal limpio, se importó fuera del repositorio.
- Documentación: README con requisitos, comandos y referencias oficiales;
  `.gitignore` excluye cachés, artefactos de construcción y metadatos generados.
- Límites: la prueba valida empaquetado, no extracción ni sorteos. Otras versiones
  de Python no se ejecutaron en este incremento; se evaluarán en CI.
- Próximo paso: incremento 05, automatizar las comprobaciones en CI.

## Incremento 05 — Integración continua

Fecha: 2026-11-20.

- Objetivo: repetir automáticamente las comprobaciones locales en GitHub y
  comprobar la compatibilidad declarada en varias versiones de Python.
- Workflow: `.github/workflows/ci.yml` se activa con push a main, pull requests
  hacia main y ejecución manual. Ejecuta `make install` y `make test`, evitando
  mantener comandos distintos en la computadora del operador y en CI.
- Matriz: Python 3.10 a 3.14 sobre Ubuntu 24.04, con entornos separados y
  `fail-fast: false` para observar cada resultado aunque falle otra versión.
- Reproducibilidad: uv 0.11.2, dependencias del lock y acciones fijadas por SHA;
  los SHA se verificaron contra los tags oficiales de checkout y setup-uv.
- Operación: permisos de lectura, sin credenciales de Instagram ni despliegues.
  Se cancelan ejecuciones anteriores de la misma referencia y se limita cada
  trabajo a diez minutos. Se omite caché para comprobar instalaciones nuevas.
- Verificación local: `make install test` pasó en Python 3.14.3; lint, formato y
  la prueba de instalación siguen correctos. `git diff --check` pasó sin errores.
- Verificación remota: el commit `e4c8d11` pasó en las cinco versiones de Python.
  Se confirmaron los pasos de instalación y comprobación en cada trabajo de la
  [primera ejecución de CI](https://github.com/jerebmorley/instagram-reel-extractor-web/actions/runs/44822820974).
  La evidencia se registra en un commit documental posterior para conservar
  intacto el commit ya verificado por GitHub Actions.
- Límites: CI valida las comprobaciones existentes; no valida funcionalidades
  de negocio aún no implementadas y no configura protecciones de rama.
- Próximo paso: incremento 06, decisiones de arquitectura (ADR).

## Plantilla para el siguiente incremento

```markdown
## Incremento NN — Título

Fecha:

- Objetivo:
- Decisiones y fundamentos:
- Cambios realizados:
- Verificación y evidencia:
- Límites:
- Próximo paso:
```

## Incremento 06 — Decisiones de arquitectura (2026-11-24)

Los ADR registran por qué la procedencia de cada conjunto de comentarios debe conservarse y por qué la v1 se operará localmente. Se contrastaron ambas decisiones con las secciones 1 a 3 del roadmap y el alcance del paso 06. Son criterios para revisar futuras implementaciones.

## Incremento 07 — Preparación de la cuenta de prueba (2026-11-24)

La guía reúne el procedimiento del titular y la matriz que completaremos con lecturas reales. Contrastamos la modalidad Instagram Login, el host y los permisos con las referencias oficiales de Meta enlazadas en la guía. Revisamos los enlaces internos del README y el diff de documentación. La configuración en el panel, el vencimiento del token y todas las mediciones siguen pendientes de la prueba con una cuenta autorizada.

## Incremento 08 — Perfil autorizado (2026-11-24)

La CLI recibe la versión explícita y toma el token del entorno. El cliente usa HTTPS al host fijo y envía la credencial en la cabecera. Solo muestra id y username para que el operador compruebe la identidad. Ruff y tres pruebas pasaron con respuestas simuladas, incluida una denegación HTTP. La lectura con la cuenta de prueba sigue pendiente.

## Incremento 09 — Muestra de publicaciones y comentarios (2026-11-24)

Se incorporaron dos comandos de diagnóstico al cliente de solo lectura. La lista de publicaciones permite elegir el ID y el informe conserva la relación raíz-respuestas mediante agrupación. Los campos presentes y los indicadores de continuación permiten revisar datos faltantes y cobertura parcial sin guardar textos. Ruff, formato y cinco pruebas pasaron en Python 3.14.3, incluidas una página vacía y una raíz con campos ausentes y otra página disponible. Se comprobó la ayuda de la CLI. Falta contrastar la muestra con la publicación real del titular.

## Incremento 10 — Cuenta activa cifrada (2026-11-24)

La CLI valida el perfil antes de guardar una credencial. El archivo se reemplaza de forma atómica con permisos privados y la clave se proporciona por separado desde el entorno. La fecha de corte opcional permite rechazar una credencial vencida. Con datos sintéticos verificamos la lectura con la clave correcta, el rechazo con otra clave y la conservación del archivo al rechazar un reemplazo vencido. Pasaron Ruff y seis pruebas locales.

## Incremento 11 — Contrato del comentario (2026-11-24)

Comment conserva el texto original, los identificadores de comentario y publicación y el instante normalizado a UTC. parent_id enlaza una respuesta con su comentario. El identificador y el nombre del autor pueden faltar independientemente. Esto permite representar la observación antes de aplicar reglas de elegibilidad. Los adaptadores de fuentes se implementarán en sus propios incrementos. Ruff y 14 pruebas pasaron con Python 3.14.3, incluidos el cambio de día al convertir a UTC, autor ausente, fecha ambigua y autorreferencia.

## Incremento 12 — Menciones (2026-11-24)

El parser local admite nombres ASCII de hasta 30 caracteres con puntos internos, letras, números y guion bajo. Quita la puntuación final, compara en minúsculas y conserva la primera aparición de cada cuenta. Son convenciones de campaña para interpretar texto, sin verificar si la cuenta existe. Pasaron cinco casos de tabla con duplicados, correos, URLs, puntuación, longitud y caracteres Unicode parecidos.

## Incremento 13 — Fechas y exclusiones (2026-11-24)

La ventana incluye los instantes de apertura y cierre, expresados con zona horaria. La lista de exclusión contiene nombres de autores normalizados. Ante un nombre ausente o inválido, una lista activa produce autor_no_verificable. La función devuelve todos los motivos aplicables en orden estable. Siete pruebas comprobaron los extremos, instantes adyacentes, motivos simultáneos y ventanas inválidas.

## Incremento 14 — Menciones requeridas (2026-11-24)

El mínimo se evalúa sobre las cuentas distintas de un comentario. Las menciones al propio autor y al comercio aportan cero. Las demás pueden cumplir el mínimo aunque estén acompañadas por menciones excluidas. Si falta la identidad verificable del autor, la regla activa devuelve autor_no_verificable. El mínimo cero desactiva el requisito. Ejemplo con mínimo dos: Ana cumple con «@Ana @Tienda @Luis @Sol» por Luis y Sol. La agrupación entre comentarios y la política de participantes quedan para el paso 15. Pasaron Ruff, formato y las 33 pruebas locales en Python 3.14.3.

## Incremento 15 — Una entrada por participante

Se elige la clave de identidad para toda la campaña antes de evaluar. El ID de autor conserva la identidad ante cambios de nombre. Para fuentes que solo aportan nombres se puede elegir username normalizado; en ese modo un cambio de nombre podría dividir a una persona. Una clave ausente queda registrada como identidad_no_disponible.

Se admiten raíces. Cada comentario debe cumplir por sí solo el mínimo de menciones. Entre todos los comentarios válidos del mismo participante, incluso en publicaciones distintas, concede entrada el primero por fecha UTC, publicación e ID. Las decisiones conservan la referencia del comentario y sus motivos. La repetición idéntica de una fila se absorbe; dos versiones diferentes para la misma referencia requieren resolución.

Cuatro pruebas verificaron desempate y cambio de nombre, reglas por comentario, respuestas, políticas de identidad y duplicados contradictorios.

## Incremento 16 — Campaña reproducible

El generador usa un reloj de referencia fijo y una semilla local. La muestra incluye ráfagas, participantes repetidos, autoarrobas, menciones duplicadas, URLs, exclusiones, fechas fuera de ventana, identidad ausente y respuestas. Con Python 3.14.3 y semilla 16, la primera evaluación de 10.000 comentarios produjo 1.988 entradas en 0,093 segundos en el equipo local. Una segunda generación produjo los mismos comentarios y la evaluación inversa reprodujo todas las decisiones. El tiempo mide solo la consolidación en memoria y varía según el equipo. Ruff, formato y las 38 pruebas pasaron. El README incluye el comando para repetir la medición.

## Incremento 17 — Fuentes locales

FileSource y FixtureSource se recorren como secuencias de Comment. Los identificadores se mantienen como cadenas para conservar ceros iniciales. En CSV las celdas opcionales vacías representan ausencia. La validación identifica el registro que incumple el contrato. Cinco pruebas comprobaron equivalencia entre formatos, zonas horarias, texto multilínea, reproducibilidad y rechazo de entradas incompletas.

## Incremento 18 — Snapshot canónico

La CLI ordena por publicación e ID, normaliza los instantes a UTC y escribe un objeto JSON por línea. El hash identifica los bytes del conjunto único. La publicación por enlace de archivo evita sobreescribir un destino concurrente. Si el destino ya existe se comprueba su hash. Se verificaron reordenamiento, duplicados, conflictos y alteración del archivo. Pasaron Ruff y 45 pruebas en Python 3.14.3. La CLI procesó 10.000 comentarios sintéticos con semilla 16 y produjo SHA-256 `5be2a7f17559b2e79a57b71c3c9fbc13f7f8e9dea2e2aded5e45097ea39b4692`. El resumen de origen se emite por consola para conservarlo junto al registro de campaña.

## Incremento 19 — Trabajos SQLite

El comando snapshot registra el origen, el estado y el avance cada cien registros en trabajos.sqlite3 dentro del destino. El cierre guarda el total leído, el total único y el hash en una transacción. La prueba reabrió la base, comprobó WAL y distinguió un trabajo completo de otro interrumpido. Un cierre abrupto del proceso puede dejar el estado activo; la recuperación corresponde al paso 22.

## Incremento 20 — Recorrido de Graph

GraphSource transforma cada raíz y respuesta al contrato Comment. Solicita hasta 50 registros por página, reconstruye cada petición con el cursor after y conserva el padre de cada respuesta. Dos pruebas sintéticas recorrieron páginas vacías con continuación y detectaron un ciclo de cursores. El tamaño efectivo y los campos devueltos siguen pendientes de medición con la cuenta autorizada. [Paginación según Meta](https://developers.facebook.com/docs/graph-api/results/)

## Incremento 21 — Presupuesto y reintentos

Cada petición GET descuenta un intento del presupuesto compartido por el cliente. Los errores de conexión y los HTTP 500, 502, 503 y 504 sin Retry-After admiten hasta tres intentos totales. Un 429 o una indicación Retry-After en esos errores HTTP detiene la operación. Es una política local conservadora; el presupuesto no mide la cuota disponible en Meta. Las pruebas simulan agotamiento, recuperación, error permanente y límite de uso. Ruff, formato y 52 pruebas pasaron con Python 3.14.3. La CLI completó un trabajo de 101 registros sintéticos con hash. Sigue pendiente validar una publicación real y reanudar trabajos desde un cursor persistido.
