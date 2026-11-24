# Sorteos de Instagram — v1 local

Herramienta en construcción para operar sorteos de pequeñas cuentas y negocios
locales desde la computadora del operador.

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
uv run --locked ruff check src tests scripts
uv run --locked ruff format --check src tests scripts
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
