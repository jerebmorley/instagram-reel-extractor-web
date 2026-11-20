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
