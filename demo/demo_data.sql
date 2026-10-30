-- Datos ficticios para la demostración de Oracle 21c XE Admin Tool.
-- Ejecute el archivo como SYSTEM en la PDB XEPDB1 (por ejemplo, con SQL Developer: F5).
-- La cuenta SYSTEM requiere privilegios administrativos para crear el usuario y sus objetos.
-- Ejecutar una sola vez. Si DEMO_APP ya existe, revise el esquema antes de recrearlo.

WHENEVER SQLERROR EXIT SQL.SQLCODE
SET ECHO ON
SET FEEDBACK ON
SET SERVEROUTPUT ON

PROMPT === Preparando el esquema de demostracion DEMO_APP ===

CREATE USER DEMO_APP
  IDENTIFIED BY "DemoApp_2026"
  DEFAULT TABLESPACE USERS
  TEMPORARY TABLESPACE TEMP
  QUOTA UNLIMITED ON USERS;

GRANT CREATE SESSION, CREATE TABLE TO DEMO_APP;

CREATE TABLE DEMO_APP.DEMO_CLIENTES (
  cliente_id NUMBER(4) CONSTRAINT PK_DEMO_CLIENTES PRIMARY KEY,
  nombre     VARCHAR2(80) NOT NULL,
  correo     VARCHAR2(120) NOT NULL,
  ciudad     VARCHAR2(60) NOT NULL,
  creado_el  DATE DEFAULT SYSDATE NOT NULL,
  CONSTRAINT UQ_DEMO_CLIENTES_CORREO UNIQUE (correo)
);

CREATE TABLE DEMO_APP.DEMO_PEDIDOS (
  pedido_id  NUMBER(4) CONSTRAINT PK_DEMO_PEDIDOS PRIMARY KEY,
  cliente_id NUMBER(4) NOT NULL,
  fecha      DATE NOT NULL,
  estado     VARCHAR2(20) NOT NULL,
  total      NUMBER(9, 2) NOT NULL,
  CONSTRAINT FK_DEMO_PEDIDOS_CLIENTE
    FOREIGN KEY (cliente_id)
    REFERENCES DEMO_APP.DEMO_CLIENTES (cliente_id),
  CONSTRAINT CK_DEMO_PEDIDOS_TOTAL CHECK (total > 0)
);

INSERT INTO DEMO_APP.DEMO_CLIENTES (cliente_id, nombre, correo, ciudad)
VALUES (1, 'Ana Torres', 'ana.torres@example.test', 'Heredia');

INSERT INTO DEMO_APP.DEMO_CLIENTES (cliente_id, nombre, correo, ciudad)
VALUES (2, 'Luis Mora', 'luis.mora@example.test', 'Alajuela');

INSERT INTO DEMO_APP.DEMO_CLIENTES (cliente_id, nombre, correo, ciudad)
VALUES (3, 'Sofia Rojas', 'sofia.rojas@example.test', 'San Jose');

INSERT INTO DEMO_APP.DEMO_PEDIDOS (pedido_id, cliente_id, fecha, estado, total)
VALUES (101, 1, DATE '2026-10-20', 'ENTREGADO', 18500.00);

INSERT INTO DEMO_APP.DEMO_PEDIDOS (pedido_id, cliente_id, fecha, estado, total)
VALUES (102, 2, DATE '2026-10-22', 'EN PROCESO', 9200.50);

INSERT INTO DEMO_APP.DEMO_PEDIDOS (pedido_id, cliente_id, fecha, estado, total)
VALUES (103, 1, DATE '2026-10-25', 'PENDIENTE', 12750.00);

INSERT INTO DEMO_APP.DEMO_PEDIDOS (pedido_id, cliente_id, fecha, estado, total)
VALUES (104, 3, DATE '2026-10-27', 'ENTREGADO', 6400.00);

COMMIT;

PROMPT === Verificacion de datos de demostracion ===
SELECT COUNT(*) AS TOTAL_CLIENTES FROM DEMO_APP.DEMO_CLIENTES;
SELECT COUNT(*) AS TOTAL_PEDIDOS FROM DEMO_APP.DEMO_PEDIDOS;
SELECT c.nombre, p.pedido_id, p.estado, p.total
FROM DEMO_APP.DEMO_CLIENTES c
JOIN DEMO_APP.DEMO_PEDIDOS p ON p.cliente_id = c.cliente_id
ORDER BY p.pedido_id;

PROMPT === Para la demostracion, despues de exportar, ejecute manualmente: ===
PROMPT DROP TABLE DEMO_APP.DEMO_PEDIDOS PURGE;
PROMPT No ejecute DROP antes de generar y verificar el archivo .dmp.
