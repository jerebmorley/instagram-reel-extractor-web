# Roadmap de la primera versión (v1): sorteos para pequeñas cuentas y negocios locales

Fecha: 2026-11-18. Recorta `product-roadmap-v3.md` a lo que se puede construir y usar **sin** hosting, dominio, pagos ni verificación de empresa.

## 1. Alcance de la v1

**Para quién:** negocios locales y cuentas chicas. Volumen esperado: decenas a pocos miles de comentarios por publicación; el caso máximo conocido es un reel de 10.000.

**Modelo de uso: operado y local.** Vos corrés la herramienta en tu computadora para uno o pocos comercios conocidos, con su consentimiento. No hay servidor público, no hay cuentas de usuario, no hay cobros.

**Interpretación de "comercios oficiales":** la entiendo como verificación de empresa y App Review de Meta, que quedan **fuera** de la v1. Si te referías a otra cosa, avisame y lo ajusto.

### Entra (v1)

- Conectar la cuenta del comercio con **token generado desde el panel de Meta** (sin flujo OAuth propio).
- Listar publicaciones (posts, carruseles y reels) y elegir una o varias.
- Extraer comentarios y respuestas, con progreso, reanudación y snapshot con hash.
- Reglas: comentar, arrobar a N personas distintas, ventana de fechas, sin auto-arrobas ni arroba al comercio, una entrada por participante, lista negra.
- Motivos de descarte, alertas de sospecha y revisión manual con registro.
- Sorteo determinista y verificable, con ganadores y suplentes, y acta.
- Verificación de **seguir la cuenta** solo en finalistas.
- Reporte de campaña mínimo y exportación a CSV.
- Modo archivo (JSON/CSV) y datos sintéticos para pruebas y demos.

### No entra (queda para después)

Stories, hashtags, benchmark, tableros de crecimiento y NLP (módulos M2 y M3), OAuth propio, multiusuario, hosting, dominio, pagos, App Review, contacto automático con ganadores.

Las métricas siguen en el plan, pero **después** de la v1 (ver sección 8).

## 2. Cómo se conecta una cuenta sin hosting ni dominio

El OAuth de Instagram necesita una URL de retorno con HTTPS; en local se resuelve con un túnel, lo que suma piezas. Para la v1 se evita con el flujo de **tester**:

1. El comercio tiene una cuenta **profesional** (Business o Creator; las personales no sirven con este tipo de API).
2. Vos lo agregás como **Instagram Tester** en tu app de Meta (modo desarrollo).
3. El comercio acepta la invitación desde Instagram (Configuración, Apps y sitios web, Invitaciones de prueba).
4. En el panel de Meta, "API setup with Instagram login", se genera el token. **El dueño debe autenticarse él mismo** en la ventana de Instagram (en persona o por videollamada): vos nunca escribís ni ves su contraseña.
5. Pegás el token en la herramienta, que lo valida, lo guarda **cifrado** y anota su vencimiento (los tokens de larga duración duran hasta 60 días y hay que refrescarlos; verificá el procedimiento vigente).
6. Revocación: el comercio puede quitar el acceso cuando quiera desde la misma sección de Instagram.

**Transparencia con el comercio:** el permiso de comentarios se llama "manage" y técnicamente permite también responder y borrar. La herramienta **solo lee**; esto debe decirse por escrito en el consentimiento.

## 3. Alternativas de arquitectura para la v1

| Opción | Pro | Contra |
|---|---|---|
| **A. Librería central + CLI + Streamlit + SQLite, todo local** | Lo más rápido para llegar a algo usable; sin servidores ni contenedores obligatorios; la lógica queda separada de la interfaz | Streamlit no es multiusuario; la interfaz se reescribe cuando haya hosting |
| B. FastAPI + HTMX + SQLite o Postgres local | Más cerca de lo que será el producto público | Más código de interfaz y de sesiones que la v1 no necesita |

**Criterio:** A. Para no rehacer trabajo, **toda la lógica vive en una librería** (`core`) que la CLI, Streamlit y, más adelante, FastAPI reutilizan. Cambia la interfaz, no el motor.

### Decisiones de diseño

- **Almacenamiento:** SQLite (modo WAL) para metadatos, evaluaciones y actas; los snapshots son archivos JSONL inmutables con `sha256` en disco. Se migra a Postgres cuando haya más de un operador o hosting.
- **Extracción:** proceso aparte (subproceso) que escribe el progreso y el cursor en SQLite. Streamlit vuelve a ejecutar el script en cada interacción, así que un hilo dentro de la interfaz podría perderse.
- **Token:** cifrado con `cryptography` (Fernet) y la clave en el llavero del sistema o en una variable de entorno; nunca en el repositorio ni en logs.
- **Pruebas sin Instagram:** `FixtureSource` y un mini servidor falso que imita paginación de 50, expansión de respuestas y errores.

## 4. Estructura del repositorio

```
sorteos-ig/
├── CLAUDE.md
├── docs/ (ROADMAP.md, adr/, learning-log.md, bases-y-condiciones-plantilla.md)
├── src/sorteos/
│   ├── models.py        # contrato del comentario
│   ├── mentions.py      # parser de arrobas
│   ├── rules.py         # motor de reglas y motivos
│   ├── sources/         # graph.py, file.py, fixture.py
│   ├── snapshot.py      # JSONL + sha256
│   ├── jobs.py          # extracción reanudable
│   ├── draw.py          # sorteo determinista
│   ├── report.py        # acta y reporte
│   └── store.py         # SQLite
├── app/                 # Streamlit
├── cli.py
├── data/ (fixtures sintéticos versionados; datos reales ignorados)
└── tests/
```

## 5. Plan por semanas (≈10 semanas a 6–8 h/semana)

Cada incremento es un commit chico con el ciclo de trabajo con IA: concepto, predicción, plan, implementación, vos corrés el criterio, entendés el diff, learning-log.

### Semana 1 · V0 Higiene
- Sacar `venv/` del índice, `debug=False`, quitar `--password`, retirar `version_web` y el extractor con instaloader; estructura `src/`, CI con ruff y pytest, `CLAUDE.md`.
- ADR-001: solo fuentes autorizadas. ADR-002: v1 local y asistido, token por panel de Meta.
- **Hecho cuando:** `make test` pasa en una máquina limpia y no queda código que pida contraseñas de Instagram.

### Semana 2 · V1 Acceso real
- Crear la app de Meta en modo desarrollo, pasar tu cuenta (o una de prueba) a profesional, invitación de tester, token.
- Script que lea perfil, una media y sus comentarios. Registrar en una matriz **qué devuelve realmente**: si aparece `username` en comentarios y en respuestas, tamaño de página, headers de uso, cuota por hora.
- **Hecho cuando:** extraés los comentarios de un post de tu cuenta con un comando.
- *Predicción previa:* ¿qué campos creés que vienen en los comentarios y cuáles no?

### Semana 3 · V2 Núcleo sin red
- Modelo del comentario, parser de arrobas (puntuación final, mayúsculas, varias, correos, URLs, Unicode parecido a letras), motor de reglas con motivos, generador de datos sintéticos con ruido (spam, auto-arrobas, duplicados, ráfagas).
- **Hecho cuando:** los tests de tabla pasan y 10.000 comentarios sintéticos se evalúan en un tiempo medido y documentado; mismas entradas dan salidas idénticas.

### Semana 4 · V3 Fuentes y snapshot
- `GraphSource` (páginas de 50, expansión de respuestas, reintentos con tope, presupuesto de cuota), `FileSource`, `FixtureSource`; snapshot JSONL con hash; trabajo reanudable por cursor.
- **Hecho cuando:** una extracción sintética de 10.000 comentarios interrumpida a la mitad se reanuda y produce el **mismo hash** que una sin interrupciones (test).

### Semana 5 · V4 Sorteo y acta
- Selección determinista (`sha256(semilla + id)` ordenado), ganadores y suplentes, compromiso previo de la semilla, acta en HTML (imprimible a PDF) y comando `verify` que reproduce el resultado.
- **Hecho cuando:** un tercero verifica un acta con un solo comando.
- Nota: el compromiso de la semilla solo vale si se hace **público antes del cierre** (por ejemplo en una historia o comentario fijado); la herramienta lo registra pero no lo publica.

### Semanas 6–7 · V5 Interfaz
- Asistente en Streamlit: cuenta, publicación(es), reglas con plantilla, extracción con progreso, revisión de descartados y alertas con registro de excepciones, sorteo, acta, historial.
- Redacción pensada para alguien no técnico; mensajes de error útiles; estados vacíos. Prueba de uso con dos personas pensando en voz alta (aprovechá lo del trabajo de usabilidad).
- **Hecho cuando:** una persona no técnica completa un sorteo de prueba sin ayuda.

### Semana 8 · V6 Finalistas y reporte
- Verificación de seguir la cuenta en finalistas: lista de control manual y, opcionalmente, cruce con el JSON de seguidores del export del dueño; el acta declara la fecha de corte.
- Reporte: entradas, participantes únicos, válidas y descartadas por motivo, cuentas más arrobadas, curva temporal, **cobertura** (`comments_count` incluye respuestas, se concilia con lo extraído), exportación a CSV.
- **Hecho cuando:** el reporte es correcto sobre fixtures y la cobertura distingue un faltante de un conteo exacto.

### Semana 9 · V7 Piloto real
- Sorteo real con el comercio de tu amigo: consentimiento por escrito (incluye alcance del token y retención), bases y condiciones con la liberación a Instagram, acta final.
- **Hecho cuando:** hay un sorteo real auditado de punta a punta y una retrospectiva escrita.

### Semana 10 · V8 Cierre
- README con demo sobre datos sintéticos, GIF, ADRs, empaquetado simple (`uv run` o similar), comando de limpieza por retención.
- **Hecho cuando:** otra persona instala y corre el demo siguiendo el README.

**Si falta tiempo, se recorta en este orden:** PDF directo, cruce con export de followers, curva temporal, múltiples publicaciones por campaña.

## 6. Cumplimiento mínimo (orientativo, no es asesoramiento legal)

- Plantilla de bases y condiciones con la liberación a Instagram y aclaración de que no la patrocina ni administra; no pedir etiquetados inexactos.
- Aviso de que el comercio debe consultar la normativa de sorteos de su provincia (algunas lotería provinciales exigen autorización para sorteos en redes).
- Datos mínimos, almacenados solo en tu equipo, con retención corta (por ejemplo 90 días) y comando de borrado.
- Consentimiento escrito del comercio antes de generar el token.
- Nada real en el repositorio público ni en la demo.

## 7. Riesgos de la v1

| Riesgo | Mitigación |
|---|---|
| El campo `username` falta en algunas respuestas (hay reportes de desarrolladores) | Se mide en la semana 2; si falta, la regla de participante usa solo comentarios raíz |
| Token vencido durante una campaña | Mostrar vencimiento y alertar con anticipación; guía de refresco |
| Invitación de tester friccionada para el comercio | Guía ilustrada y sesión acompañada |
| Falta de un post con 10.000 comentarios para probar | Servidor falso con paginación y límites; prueba real solo con tamaños chicos |
| Confianza del comercio al compartir un token | Consentimiento, revocación explícita, solo lectura, datos locales |
| Normativa de sorteos | Aviso visible y plantilla; el comercio decide y verifica |
| Alcance | Recortes definidos; M2 y M3 fuera |

## 8. Después de la v1

Condiciones para pasar a la etapa siguiente: al menos 3 sorteos reales en 2 comercios, y feedback de uso.

| Etapa | Qué suma |
|---|---|
| v1.5 | Tableros locales por cuenta: crecimiento diario, rendimiento de publicaciones, comentarios y sentimiento (M2) |
| v2 | Web con login propio y OAuth, Postgres y hosting; evaluar App Review y verificación de empresa |
| v2+ | Stories, benchmark y hashtags (M3) |

## 9. Primer paso

Incremento V0. Antes de ejecutar `git rm -r --cached venv`, escribí tu predicción: ¿qué pasa con los archivos de `venv/` en tu carpeta y qué pasa con el historial? Después compartime el resultado y armamos el prompt para Claude Code.

## 10. Referencias

- Crear una app de Meta para la plataforma de Instagram: https://developers.facebook.com/documentation/development/create-an-app/other-app-types/instagram-apis
- Business Login for Instagram: https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-instagram-login/business-login
- Comentarios de una media: https://developers.facebook.com/documentation/instagram-platform/instagram-graph-api/reference/ig-media/comments