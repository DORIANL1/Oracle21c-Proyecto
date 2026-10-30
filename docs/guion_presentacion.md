# Guion de presentación y demostración

**Duración estimada:** 6–8 minutos  
**Base de datos:** Oracle 21c XE, PDB `XEPDB1`  
**Esquema de prueba:** `DEMO_APP`

## Preparación antes del laboratorio

1. Inicie Oracle XE y confirme que `XEPDB1` está abierta.
2. Ejecute [`demo_data.sql`](../demo/demo_data.sql) una sola vez como `SYSTEM` en `XEPDB1` (en SQL Developer, use **Run Script / F5**).
3. En Windows, prepare una carpeta de respaldo local, por ejemplo `C:\oracle21c\backups`. Asegúrese de que la cuenta del servicio Oracle pueda leer y escribir en ella. La ruta debe ser accesible también desde la aplicación.
4. Verifique que `expdp` e `impdp` se encuentran en `PATH` abriendo una terminal y ejecutando `where expdp` y `where impdp`.
5. Abra la aplicación con `python main.py`. Conecte como `SYSTEM`, deje **desactivado** «Conectar como SYSDBA» y use host `localhost`, puerto `1521` y servicio `XEPDB1`.
6. En **Respaldos → Directorios de Oracle**, registre el nombre lógico `DEMO_PUMP_DIR` con la carpeta preparada. Sincronice y confirme que aparece en la lista.
7. Prepare SQL Developer para validar el estado antes y después. No ejecute la eliminación hasta confirmar que la exportación terminó correctamente.

## Guion hablado y acciones

### 1. Apertura — 30 segundos

> «Esta herramienta de escritorio reúne módulos para administrar almacenamiento, usuarios, rendimiento, auditoría y Data Pump en Oracle 21c XE. Iniciaré sesión en la PDB de laboratorio y demostraré el ciclo de respaldo y recuperación con datos ficticios.»

**Acción:** muestre brevemente la conexión y la barra lateral habilitada.

### 2. Recorrido de módulos — 1 minuto

> «Al entrar a cada módulo se consultan los datos actuales. Tablespaces muestra capacidad y datafiles; Seguridad permite consultar usuarios y administrar permisos; Tuning presenta planes estimados y herramientas de índices; Performance consulta sesiones y bloqueos; Auditoría filtra los eventos disponibles.»

**Acción:** abra Tablespaces, Seguridad y Performance. Muestre Auditoría solo si hay eventos disponibles. No ejecute cambios administrativos ajenos a la demo.

### 3. Confirmar esquema — 30 segundos

En SQL Developer, ejecute y muestre los resultados:

```sql
SELECT COUNT(*) FROM DEMO_APP.DEMO_CLIENTES;
SELECT COUNT(*) FROM DEMO_APP.DEMO_PEDIDOS;
```

Resultados esperados: **3 clientes** y **4 pedidos**.

### 4. Exportar el esquema — 1–2 minutos

**Acción:** en **Respaldos → Respaldos (expdp)**:

1. Seleccione `DEMO_PUMP_DIR`.
2. Use un nombre nuevo, por ejemplo `demo_app_lab.dmp`.
3. Seleccione **Por Schemas (SCHEMAS)** e indique `DEMO_APP`.
4. Ejecute el respaldo y espere el mensaje de finalización exitosa. Compruebe que el `.dmp` se creó en la carpeta del servidor.

> «El archivo contiene el esquema de prueba y sus dos tablas pobladas. No continúo si Data Pump reporta error o si el archivo no aparece.»

### 5. Simular pérdida de una tabla — 30 segundos

Con el respaldo ya verificado, ejecute en SQL Developer como `SYSTEM`:

```sql
DROP TABLE DEMO_APP.DEMO_PEDIDOS PURGE;
```

Compruebe que la tabla ya no está disponible:

```sql
SELECT COUNT(*) FROM DEMO_APP.DEMO_PEDIDOS;
```

El error de tabla inexistente es esperado en este punto.

### 6. Recuperar y validar — 1–2 minutos

**Acción:** en **Respaldos → Recuperación (impdp)**:

1. Seleccione `DEMO_PUMP_DIR` y pulse **Refrescar .dmp**.
2. Elija `demo_app_lab.dmp`.
3. Seleccione **Por Schemas (SCHEMAS)** y escriba `DEMO_APP`.
4. Inicie la recuperación y espere a que la consola indique que terminó.

En SQL Developer, vuelva a ejecutar:

```sql
SELECT COUNT(*) FROM DEMO_APP.DEMO_CLIENTES;
SELECT COUNT(*) FROM DEMO_APP.DEMO_PEDIDOS;
```

Resultados esperados: **3** y **4**. Opcionalmente, muestre los pedidos:

```sql
SELECT pedido_id, cliente_id, estado, total
FROM DEMO_APP.DEMO_PEDIDOS
ORDER BY pedido_id;
```

### 7. Cierre — 30 segundos

> «La prueba confirma que el esquema ficticio se exportó, se eliminó una tabla de forma intencional y se recuperó desde el archivo Data Pump. En un entorno real, se deben verificar permisos, destino y respaldo antes de importar.»

## Plan de contingencia

- **No aparece el ejecutable:** no iniciar la demo de Data Pump; verificar `PATH` y Oracle Client antes de la evaluación.
- **Error de permisos o DIRECTORY:** confirmar usuario `SYSTEM`, objeto `DEMO_PUMP_DIR` y permisos de lectura/escritura sobre la carpeta para el servicio Oracle.
- **No aparece el `.dmp`:** confirmar que la ruta del servidor coincide con la ruta visible desde la aplicación y pulsar **Refrescar .dmp**.
- **La importación falla:** no seguir borrando objetos; conservar el log y explicar el error al evaluador. No usar credenciales de producción.

## Seguridad de la demostración

La contraseña ficticia definida en el SQL de muestra es solo para laboratorio. No la reutilice. La importación de la aplicación utiliza `TABLE_EXISTS_ACTION=REPLACE`, por lo que siempre se debe verificar el archivo y el esquema de destino antes de iniciar.
