# Instagram Reel Comment Extractor

Este proyecto permite iniciar sesión en Instagram, pegar la URL de un reel y exportar los comentarios a un archivo CSV. El flujo está pensado como una app de consola guiada (fase 1), con una estructura lista para evolucionar hacia una interfaz web más adelante.

## Requisitos

- Python 3.10 o superior
- Acceso a Instagram con una cuenta real
- Navegador web habilitado para la sesión del cliente (la autenticación se realiza mediante `instaloader` en modo cliente)

## Instalación

1. Cloná el repositorio o descargá este proyecto.
2. Creá un entorno virtual y activalo:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Instalá las dependencias:

```bash
pip install -r requirements.txt
```

## Uso

### Modo interactivo

Ejecutá:

```bash
python extraerComentariosReels.py
```

El programa te pedirá:

1. Usuario de Instagram
2. Contraseña
3. URL del reel
4. Confirmación del destino del CSV

Luego comienzan los pasos:

- iniciar sesión y guardar la sesión local
- validar la URL del reel
- extraer los comentarios con la API GraphQL de Instagram
- guardar cada comentario con el formato:
  - id
  - username
  - text
  - created_at
  - likes_count

### Modo no interactivo

También podés suministrar parámetros directamente:

```bash
python extraerComentariosReels.py --username tu_usuario --password tu_contrasena --reel-url "https://www.instagram.com/reel/XXXXXXXXXXX/"
```

Opcionalmente podés definir la ruta de salida:

```bash
python extraerComentariosReels.py --username tu_usuario --password tu_contrasena --reel-url "https://www.instagram.com/reel/XXXXXXXXXXX/" --output exports/comentarios.csv
```

## Estructura esperada

Los archivos generados se guardan en la carpeta `exports`:

```text
exports/
└── comentarios_Dct0o7mpcsk.csv
```

## Importante

- El programa guarda la sesión localmente para evitar repetir el login en ejecuciones futuras.
- Instagram puede bloquear o limitar peticiones por uso intensivo o rate limiting.
- Este proyecto está orientado a casos legales y de uso responsable, con fines de análisis de contenido del que tenés acceso autorizado.
- Respetá los términos de servicio y la privacidad de la cuenta.

## Siguientes pasos

La próxima evolución sugerida es convertir esta lógica en una página web con:

- pantalla de login guiada
- campo para pegar el enlace del reel
- resumen de la extracción paso a paso
- vista del archivo CSV descargado
- historial de ejecuciones

## Troubleshooting

- Si la sesión falla: elimina la sesión guardada y vuelve a iniciar sesión.
- Si la URL no es válida: asegurate de usar una URL del tipo `https://www.instagram.com/reel/XXXXXXXXXXX/`.
- Si Instagram devuelve error 429: espera unos segundos y vuelve a intentar.
