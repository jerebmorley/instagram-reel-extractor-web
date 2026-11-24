# ADR 002 · Operación local asistida

Aceptada el 2026-11-24 para la v1.

Un operador acompaña a pocos comercios desde una computadora. El titular autorizará el acceso desde el panel de Meta con su propia cuenta. El token generado en el panel es el mecanismo previsto, sujeto a una prueba de acceso con la cuenta elegida.

La CLI y Streamlit compartirán el núcleo Python. SQLite guardará el estado de los trabajos y las decisiones de revisión. Los snapshots JSONL con hash permitirán verificar el conjunto usado en cada sorteo. Una extracción en un proceso separado podrá continuar aunque Streamlit vuelva a ejecutar la pantalla.

El operador será responsable de la disponibilidad del equipo, la retención de los datos y la renovación de las credenciales. La persistencia del token requerirá cifrado con la clave separada del repositorio. El paso 10 cubre esa implementación.

Se posponen el servicio web, OAuth propio y Postgres porque implican administrar sesiones, infraestructura y acceso concurrente. Revisar esta decisión cuando varios operadores deban compartir campañas o se requiera acceso remoto.
