# Sorteos de Instagram — v1 local

Herramienta en construcción para operar sorteos de pequeñas cuentas y negocios
locales desde la computadora del operador.

## Estado actual

El paquete instalable `sorteos` está en `src/sorteos`, con pytest, Ruff y
comprobaciones locales. El incremento 05 agrega su automatización en GitHub
Actions. **Todavía no hay CLI, interfaz ni funciones de extracción o sorteo.**

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
activar el entorno: `uv run` elige su intérprete. El antiguo `venv/` es independiente.

`make test` ejecuta Ruff para detectar errores e imports desordenados, comprueba
el formato sin modificar archivos y ejecuta pytest. La prueba inicial importa el
paquete desde una carpeta temporal, con Python aislado de `PYTHONPATH` y del
directorio actual. Comprueba la instalación; no valida reglas de sorteos todavía.

Sin Make, los comandos equivalentes son:

```bash
uv sync --locked
uv run --locked ruff check src tests
uv run --locked ruff format --check src tests
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
