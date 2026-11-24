# ADR 001 · Fuentes autorizadas

Aceptada el 2026-11-24 para la v1.

El operador necesita explicar de dónde salieron las participaciones de un sorteo. Para campañas reales se admitirán la API oficial con acceso concedido por el titular y archivos JSON/CSV que el titular esté autorizado a facilitar. Para pruebas y demos se usarán datos sintéticos.

El núcleo recibirá el mismo contrato de comentario desde cada fuente. La procedencia deberá quedar asociada al snapshot de campaña para que otro operador pueda reconstruir qué conjunto se evaluó. Los datos reales se mantendrán fuera de Git.

Se descartó recuperar el extractor con contraseña y sesiones de Instagram. Ese mecanismo obligaba a confiar credenciales al operador. Si el permiso de API falta o se revoca, la extracción se detendrá y el modo archivo podrá usarse con una fuente autorizada identificada por separado. Cambiar de fuente para una campaña exige registrar su procedencia.
