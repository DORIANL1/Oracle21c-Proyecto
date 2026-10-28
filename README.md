#Oracle 21c XE - Database Administration Tool

Aplicación de escritorio integral desarrollada en **Python** con **CustomTkinter** para la administración, optimización, auditoría y ejecución de respaldos/restauraciones sobre **Oracle Database 21c XE**.

Proyecto Final para el curso **EIF-402 Administración de Bases de Datos**  
Universidad Nacional de Costa Rica (UNA) — Sede Interuniversitaria de Alajuela  
Fecha de Entrega / Evaluación: 4 de noviembre de 2026 (Semana 15)

---



La aplicación ofrece una interfaz gráfica moderna con modo oscuro nativo, diseñada para gestionar aspectos críticos de la base de datos Oracle 21c XE a través de un panel modular:

* **Gestión de Almacenamiento (Tablespaces):** Monitoreo visual de capacidad, archivos de datos (`.dbf`) y redimensionamiento dinámico.
* **Seguridad y Control de Acceso:** Administración de usuarios, asignación de roles, privilegios de sistema y cuotas.
* **Tuning y Optimización de Consultas:** Análisis de planes de ejecución (`EXPLAIN PLAN`), recolección de estadísticas (`DBMS_STATS`) y gestión de índices.
* **Monitoreo de Rendimiento (Performance):** Inspección en tiempo real de sesiones activas y bloqueos de objetos.
* **Auditoría del Sistema:** Consulta y filtrado de eventos registrados en la auditoría unificada.
* **Respaldos y Recuperación (Data Pump):** Exportación e importación (`expdp` / `impdp`) por esquema, tablas o base de datos completa, con registro de logs en tiempo real y gestión de `DBA_DIRECTORIES`.

---

##Requisitos del Sistema y Prerrequisitos

Para la correcta ejecución de la herramienta se requiere:

1. **Oracle Database 21c XE** instalado y en ejecución en el entorno local (`localhost:1521/XEPDB1`).
2. **Python 3.10** o superior.
3. Usuario con privilegios de administración (`SYSDBA` o `SYSTEM`) en Oracle.

---

##Instalación de Dependencias

Clonar el repositorio e instala las librerías necesarias ejecutando los siguientes comandos en tu terminal:

# bash

## 1. Clonar el repositorio
git clone [https://github.com/TU_USUARIO/oracle21c-admin-tool.git](https://github.com/TU_USUARIO/oracle21c-admin-tool.git)
cd oracle21c-admin-tool

Nota sobre oracledb: Se utiliza el controlador oficial de Oracle para Python en modo Thin o Thick según la configuración del cliente local. IMPORTANTE

-----

Guía de Ejecución
Para iniciar la aplicación gráfica:

Bash
python main.py
Al abrir la herramienta, completa los credenciales de conexión en la pantalla de inicio de sesión:

Host: localhost

Puerto: 1521

Servicio / SID: XEPDB1

Usuario: SYS (o SYSTEM)

Rol: Seleccionar SYSDBA (si se conecta con SYS)







