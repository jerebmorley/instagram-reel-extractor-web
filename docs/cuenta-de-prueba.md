# Preparar una cuenta de prueba

Guía del operador para los incrementos 07 a 09. Revisión documental del 2026-11-24.

1. Elegí una cuenta profesional Business o Creator que controles y una publicación propia con un comentario raíz y una respuesta. Si pertenece a un comercio, obtené antes su consentimiento escrito para la lectura de los datos de prueba.
2. En el panel de tu app de Meta, seleccioná la configuración de Instagram API con Instagram Login. El host de este flujo es `graph.instagram.com`. Registrá la versión de API elegida en el panel para poder repetir la prueba. [Documentación de Meta](https://developers.facebook.com/docs/instagram/platform/instagram-api/changelog/)
3. En la configuración de prueba, vinculá la cuenta profesional y revisá los roles que pide el panel. Si hay una invitación de tester, el titular debe aceptarla con su propia cuenta. Confirmá que figura activa antes de generar el token. Los nombres de las pantallas y el acceso efectivo quedan por confirmar en la app. [Colección oficial de Meta](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api?entity=request-23987686-44282184-4e45-416a-97df-37f581b8679b)
4. El titular inicia sesión en Instagram desde el flujo del panel. Revisen el alcance básico del perfil (`instagram_business_basic`) y el de comentarios (`instagram_business_manage_comments`). Explicale que el permiso de gestión admite operaciones más amplias que las lecturas previstas. Si el panel exige acceso adicional, registrá el requisito y revisalo antes de concederlo.
5. Cuando el panel ofrezca generar el token para esa cuenta, guardalo en un gestor de secretos local. Anotá aparte el vencimiento si se muestra. Mantené el valor fuera del chat, capturas, comandos, logs y archivos del repositorio. Si falta la opción, registrá el paso y el mensaje sin datos identificadores. La prueba puede retomarse después con el titular.

## Matriz para las primeras lecturas

Al completar cada fila anotá fecha, versión de API y resultado observado. Para errores guardá el código y una descripción anonimizada. Una celda pendiente indica que todavía falta la medición.

| Paso | Capacidad | Evidencia que registrar | Observado |
|---|---|---|---|
| 08 | Leer el perfil | Estado HTTP y presencia de identificador en el perfil esperado | Pendiente |
| 09 | Listar publicaciones | Tipo de publicación de prueba y si aparece al listar | Pendiente |
| 09 | Leer comentarios raíz | Presencia de id, texto, fecha y autor, incluidos campos ausentes | Pendiente |
| 09 | Leer respuestas | Relación con el comentario raíz y disponibilidad de username | Pendiente |
| 09 | Paginar | Cantidad solicitada y recibida, presencia de cursor siguiente | Pendiente |
| 09 | Observar consumo | Nombres y unidades de cabeceras de uso disponibles. Registrar cuota horaria solo si existe un valor explícito | Pendiente |

Para cerrar el 08 se necesita una lectura autenticada del perfil. Para el 09 se compara la publicación preparada con los comentarios y respuestas devueltos. Si la identidad del autor falta, se documenta antes de decidir cómo contará esa participación.

## Ejecutar la prueba de perfil

En Bash, desde la raíz, ingresá la versión de tu panel y pegá el token en la entrada oculta. El titular puede comparar el usuario devuelto con su cuenta. Conservá en la matriz solo la fecha, versión y resultado de esa comparación.

```bash
read -rp 'Versión API (vN.N): ' VERSION_API
read -rsp 'Token: ' INSTAGRAM_ACCESS_TOKEN && echo
export INSTAGRAM_ACCESS_TOKEN
uv run --locked python -m sorteos --version-api "$VERSION_API" perfil
unset INSTAGRAM_ACCESS_TOKEN
```
