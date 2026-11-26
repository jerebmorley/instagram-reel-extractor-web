# Sorteos de Instagram — v1 local

Herramienta en construcción para operar sorteos de pequeñas cuentas y negocios
locales desde la computadora del operador.

## Preparar una campaña desde el navegador

Desde la raíz del proyecto, ejecutá `make ui` y abrí la dirección local indicada
en la terminal. La interfaz escucha en `127.0.0.1`. En **Campaña de prueba**,
seleccioná publicaciones, ajustá las reglas y pulsá **Aplicar configuración**.
La vista previa evalúa los comentarios sintéticos con el motor de la CLI.

En **Cuenta autorizada**, indicá la versión de API de tu panel y pulsá **Cargar
cuenta**. Se usa la credencial del entorno o de la cuenta cifrada local. Elegí
una o varias publicaciones entre las primeras diez devueltas por Meta. Las
fechas comprenden días completos en UTC. Al aplicar las reglas podés descargar
el borrador JSON con la cuenta, las publicaciones, la identidad y las reglas.
Pulsá **Iniciar extracción** y después **Actualizar progreso** para ver el estado
y los registros leídos por publicación. El subproceso continúa si se cierra la
pestaña. Al aplicar la misma configuración desde el mismo proyecto se recupera
el trabajo bajo `exports/interfaz/`. **Continuar extracción** retoma las páginas
pendientes tras una interrupción. Cada ejecución para una cuenta real comparte
el presupuesto de consultas entre las publicaciones elegidas.

Al finalizar, elegí **Descartados**, **Con alerta** o **Todos**. La alerta señala
texto idéntico repetido por una cuenta en varios comentarios. Revisá el contexto
antes de decidir. Para aplicar una excepción seleccioná un participante, indicá
la decisión y escribí el motivo. El historial conserva las correcciones y su hora
UTC. **Descargar revisiones vigentes** genera el JSON que acepta
`congelar --revisiones`, con la decisión más reciente por identidad.
La revisión corresponde al snapshot combinado de esa configuración.

## Estado actual

La CLI local permite comprobar el perfil autorizado y tomar muestras de publicaciones, comentarios y respuestas. La guía de cuenta de prueba
detalla los comandos y la evidencia pendiente de obtener con Meta.

## Alcance previsto

- Operación local asistida, sin hosting, cuentas de usuario ni pagos.
- Núcleo Python compartido por CLI y Streamlit, con SQLite para persistencia.
- Extracción reanudable, reglas de participación y revisión con registro.
- Sorteo reproducible, acta verificable y exportación de resultados.

Estas capacidades son objetivos del roadmap, no funciones ya disponibles.

## Preparar el entorno de desarrollo

Requisitos: Python 3.10 o posterior, [uv](https://docs.astral.sh/uv/getting-started/installation/)
y Make. Desde la raíz del repositorio:

```bash
make install
make test
```

`make install` ejecuta `uv sync --locked`: crea el entorno `.venv`, instala el
paquete en modo editable y las herramientas de desarrollo usando `uv.lock`.
La primera instalación necesita acceso al índice de paquetes. No hace falta
activar el entorno: `uv run` elige su intérprete.

`make test` ejecuta Ruff para detectar errores e imports desordenados, comprueba
el formato sin modificar archivos y ejecuta pytest. La prueba inicial importa el
paquete desde una carpeta temporal, con Python aislado de `PYTHONPATH` y del
directorio actual. Comprueba la instalación; no valida reglas de sorteos todavía.

Sin Make, los comandos equivalentes son:

```bash
uv sync --locked
uv run --locked ruff check src tests scripts app
uv run --locked ruff format --check src tests scripts app
uv run --locked pytest
```

La configuración está en `pyproject.toml`; `uv.lock` registra las versiones
resueltas. Al cambiar dependencias, regenerá el lock con `uv lock` y revisá su diff.
El nombre de distribución es `sorteos-ig`, y el nombre usado en Python es `sorteos`:

```bash
uv run --locked python -c "import sorteos; print(sorteos.__file__)"
```

Referencias de configuración: [empaquetado Python](https://packaging.python.org/en/latest/tutorials/packaging-projects/),
[prácticas de pytest](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
y [configuración de Ruff](https://docs.astral.sh/ruff/configuration/).

## Integración continua (CI)

[El workflow de CI](.github/workflows/ci.yml) ejecuta `make install` y `make test`
en Ubuntu 24.04 para Python 3.10, 3.11, 3.12, 3.13 y 3.14. Se activa al subir
commits a `main`, al abrir o actualizar un pull request hacia `main`, o manualmente
desde [GitHub Actions](https://github.com/jerebmorley/instagram-reel-extractor-web/actions/workflows/ci.yml).

Cada versión usa un entorno separado. Un fallo no cancela las otras versiones,
para mostrar todos los problemas de compatibilidad. Una ejecución nueva en la
misma rama reemplaza la anterior; cada trabajo tiene un límite de diez minutos.

CI usa los mismos comandos que el desarrollo local y el lock existente; fija uv
en 0.11.2 y las acciones externas por su commit. Solo requiere permisos de lectura
del repositorio. No necesita credenciales de Instagram ni publica la aplicación.
No se configura caché inicialmente: el entorno pequeño permite comprobar la
instalación desde cero en cada ejecución.

Un resultado verde indica que pasaron las comprobaciones actuales de estilo e
instalación. No garantiza funcionalidades futuras ni bloquea por sí solo un push
a `main`; las protecciones de rama se configuran por separado.

Referencia: [integración oficial de uv con GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/).

## Documentación

- [ADR 001 · Fuentes autorizadas](docs/adr/001-fuentes-autorizadas.md)
- [ADR 002 · Operación local asistida](docs/adr/002-operacion-local.md)
- [Preparación de la cuenta de prueba y matriz de capacidades](docs/cuenta-de-prueba.md)

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

El entorno local del proyecto se gestiona en `.venv/`. Los entornos virtuales, credenciales y datos
reales no deben incorporarse al repositorio.

## Evaluar una campaña de ejemplo

Desde la raíz, ejecutá `uv run --locked python scripts/medir_campana.py`. Genera
10.000 comentarios ficticios con semilla 16, evalúa una entrada por participante
en tres publicaciones y muestra el tiempo de la primera evaluación. Después
regenera los datos y comprueba que la evaluación en orden inverso produce las
mismas decisiones. La medición excluye la generación y el acceso a Instagram.

## Crear un snapshot local

```bash
uv run --locked python -m sorteos snapshot --sinteticos 10000 --semilla 16
uv run --locked python -m sorteos snapshot --archivo campaña.csv
```

Para importar JSON usá una lista de objetos. Para CSV usá cabecera, comas y
codificación UTF-8. Ambos requieren `id`, `media_id`, `text` y `created_at`
(fecha ISO con zona horaria). Los identificadores JSON son cadenas.
`author_id`, `username` y `parent_id` son opcionales. Ejemplo JSON sintético:

```json
[{"id":"01","media_id":"m1","text":"@amiga","created_at":"2026-01-01T00:00:00Z"}]
```

El comando muestra el origen, la cantidad de comentarios únicos, la ruta y el
SHA-256. Conservá ese resumen con la campaña. Por defecto escribe en
`exports/snapshots/`, ignorado por Git. Podés elegir otra carpeta con `--destino`.
El JSONL contiene los datos originales del comentario y representa los instantes
en UTC. Se ordena por publicación e ID y absorbe repeticiones idénticas.
Para comprobar el contenido, compará `sha256sum RUTA_DEL_JSONL` con el hash
registrado. La aplicación reutiliza archivos idénticos y rechaza conflictos.

## Extraer una publicación autorizada

Con la versión y la credencial configuradas según la guía de cuenta de prueba:

```bash
uv run --locked python -m sorteos --version-api "$VERSION_API" snapshot --publicacion "$MEDIA_ID" --max-peticiones 500
```

Cada página de comentarios y cada consulta de respuestas consume presupuesto,
incluso si vuelve vacía. El límite de 500 intentos es local y configurable.
Un fallo transitorio admite dos reintentos con pausas de uno y dos segundos.
Un 429 detiene el trabajo. El JSONL final se publica al concluir la lectura.

En el destino del snapshot, la tabla `jobs` de `trabajos.sqlite3` conserva el
origen, estado, registros leídos, cantidad única y SHA-256. Para revisar el
progreso desde otra terminal con la utilidad SQLite:

```bash
sqlite3 -readonly exports/snapshots/trabajos.sqlite3 'SELECT id,status,processed,unique_count FROM jobs ORDER BY id DESC;'
```

Los trabajos nuevos guardan cada página de Graph o lote de cien filas locales
junto a su punto de continuación. Para retomar, repetí el comando con el mismo
origen y destino y agregá `--reanudar ID` (el ID figura en la consulta anterior).

```bash
uv run --locked python -m sorteos snapshot --sinteticos 10000 --semilla 16 --reanudar 1
```

En archivos y fixtures se vuelve a leer y verificar el prefijo ya confirmado.
En Graph se retoma la página de raíces o respuestas pendiente; la cuenta debe
seguir autorizada y el cursor debe continuar vigente. Un nuevo proceso dispone
de su propio presupuesto de peticiones. Cambios en Instagram durante la pausa
pueden alterar el conjunto observado. Los trabajos anteriores a este incremento
carecen de datos parciales para reanudar. En Linux el bloqueo por trabajo se
libera cuando termina el proceso, incluso tras un cierre abrupto.

## Preparar el sorteo

Usá una base SQLite privada por campaña, bajo `exports/`. Antes del cierre,
generá el compromiso y publicá el SHA-256 junto con la identificación de la
campaña y su cierre. La semilla permanece en la base local. Sustituí las
variables por la fecha y referencia reales. Las fechas requieren zona horaria.

```bash
uv run --locked python -m sorteos comprometer exports/campana.db --cierre "$CIERRE"
uv run --locked python -m sorteos registrar-publicacion exports/campana.db --referencia "$REFERENCIA" --publicado "$PUBLICADO"
```

La referencia y la fecha son declaraciones del operador. Conservá la publicación
original para que un tercero pueda comprobar el contenido y la fecha.

Al cerrar, usá un snapshot de la campaña y un archivo JSON de reglas como este.
Ajustá el intervalo a tus bases. El cierre debe coincidir con el del compromiso.

```json
{"starts_at":"2026-11-01T00:00:00-03:00","ends_at":"2026-11-30T18:00:00-03:00","required_mentions":2,"business_username":"tienda","excluded_usernames":[]}
```

```bash
uv run --locked python -m sorteos congelar exports/campana.db "$SNAPSHOT" reglas.json
uv run --locked python -m sorteos revelar exports/campana.db
```

El padrón usa ID de autor por defecto. Para una fuente identificada por nombres
seleccioná `--identidad username`. Podés agregar `--revisiones archivo.json`
con una lista de decisiones por identidad observada, por ejemplo
`[{"participante":"demo_1","decision":"excluir","motivo":"Renuncia registrada"}]`.
Una inclusión manual usa `incluir` y requiere motivo aunque el participante
haya quedado descartado automáticamente. El padrón guarda ambas decisiones.
Conservá el SHA-256 que imprime la CLI para identificar esa versión.

Tras el cierre y el registro de la publicación, `revelar` muestra la semilla
hexadecimal. Su compromiso es SHA-256 de los 32 bytes obtenidos al decodificar
ese hexadecimal. Compartí la revelación cuando corresponda y mantené la base
SQLite local, ya que contiene el padrón y la semilla en claro.

## Sortear y verificar el acta

Al ejecutar el sorteo, indicá las cantidades de ganadores y suplentes acordadas en las bases. La selección usa el padrón congelado y la semilla revelada. El ejemplo selecciona un ganador y dos suplentes.

```bash
uv run --locked python -m sorteos sortear exports/campana.db exports/acta.html --ganadores 1 --suplentes 2
uv run --locked python -m sorteos verify exports/acta.html
```

Abrí el HTML en un navegador para imprimirlo o guardarlo como PDF. Conservá el HTML original para verificarlo. Incluye las identidades elegibles, el orden de finalistas y la semilla revelada. Considerá ese alcance al compartir el archivo.

El algoritmo v1 ordena cada identidad por SHA-256 de la concatenación de la semilla (32 bytes) y el identificador UTF-8 exacto. En caso de empate usa los bytes del identificador en orden ascendente. Asigna primero los ganadores y después los suplentes. La base conserva el resultado y permite volver a exportarlo con los mismos cupos.

Un tercero con esta versión de la herramienta puede ejecutar `verify` sobre el archivo recibido. El comando comprueba el compromiso, la cronología declarada, el ranking y el HTML visible. Para autenticar la copia, agregá `--sha256 HUELLA` con el valor que imprimió el organizador y que conservaste por un canal independiente. Contrastá el compromiso y la fecha con su publicación original. La auditoría de la elegibilidad requiere además el padrón congelado y el snapshot identificados en el acta.

## Finalizar una campaña desde Streamlit

En **Campaña de prueba**, aplicá la configuración inicial y pulsá **Preparar compromiso de prueba**. La demo usa datos de enero de 2026 y una referencia pública ficticia que se identifica como tal en el acta.

Para una **Cuenta autorizada**, generá el compromiso antes del cierre, publicá la huella y registrá la referencia y el instante real de publicación. Tras el cierre, extraé la publicación completa y revisá los participantes. **Congelar padrón** fija las últimas decisiones manuales. Elegí los cupos y pulsá **Realizar sorteo**. El resultado y el acta quedan en la carpeta de la campaña. **Ver historial de sorteos** permite recuperar el HTML y su huella en otra sesión desde el mismo proyecto.

La preparación del paso 33 está en el [guion de prueba de uso](docs/prueba-de-uso.md).

### Verificación de finalistas y reporte

Si las bases exigen seguir la cuenta, marcá esa condición antes de realizar el
sorteo. En el resultado, registrá la fecha de corte con zona horaria, el estado
y el motivo de cada control manual. Al confirmar se ocupan los cupos según
el orden original. Si se agotan los suplentes, el anexo indica las vacantes.
Guardá el anexo JSON junto con el acta HTML. La huella del HTML permite
identificar el sorteo al que corresponde el anexo.

El reporte CSV muestra entradas antes y después de la revisión, motivos de
descarte, menciones y comentarios por día UTC. Un comentario puede tener varios
motivos. Cada cuenta mencionada cuenta una vez por comentario. La diferencia
de cobertura se calcula como extraídos menos referencia, incluyendo respuestas.
Un valor negativo señala un faltante respecto del conteo observado. Sin referencia
guardada, la cobertura figura como desconocida. La igualdad de cantidades por sí
sola no prueba que se hayan recuperado exactamente los mismos comentarios.
