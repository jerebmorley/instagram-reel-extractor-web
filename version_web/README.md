# Versión web del extractor de comentarios

Esta carpeta contiene una versión web mejorada del proceso que ya quedó funcionando en consola. El flujo actual incluye:

1. inicio de sesión en Instagram
2. validación de la URL del reel
3. extracción de comentarios con progreso visual
4. generación de archivo CSV
5. descarga y historial de exportaciones

## Requisitos

- Python 3.10+
- pip

## Instalación

```bash
cd "/home/jeremias/Descargas/para manu/version_web"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecución local

```bash
python app.py
```

Luego abrí tu navegador en:

```text
http://localhost:5000
```

## Preparación para Vercel

La estructura ya fue adaptada para un despliegue serverless:

- `api/index.py` es el punto de entrada de Vercel
- `vercel.json` redirige todas las rutas a la función serverless
- el proyecto mantiene el mismo flujo Flask localmente

### Configuración en Vercel

1. En Vercel, crea un proyecto nuevo.
2. Seleccioná la carpeta `version_web` como root directory.
3. Dejá que Vercel detecte el proyecto Python.
4. Confirma que use `requirements.txt` del directorio raíz.
5. Hacé deploy.

### Importante

- En Vercel, la app se ejecuta como función serverless; por eso no es una app Flask “normal” y se necesita este wrapper.
- Instagram puede bloquear o limitar peticiones con rate limiting, así que conviene mantener un uso responsable y autorizado.

## Cómo funciona

- El formulario solicita usuario, contraseña y URL del reel.
- La app autentica con `instaloader` y guarda la sesión localmente.
- Durante la extracción, la interfaz muestra estados por etapas y un indicador de progreso.
- Al finalizar, genera un CSV dentro de la carpeta `exports/` y ofrece descarga directa.
- Mantiene un historial reciente de las exportaciones realizadas.
