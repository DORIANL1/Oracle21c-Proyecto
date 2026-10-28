import oracledb

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.connection = None
            cls._instance.host = None
            cls._instance.port = None
            cls._instance.service_name = None
            cls._instance.user = None
            cls._instance.role = None
            
            # Intentar inicializar modo Thick automáticamente con las librerías de Oracle local
            try:
                oracledb.init_oracle_client()
            except Exception:
                # Si falla o no encuentra el path del cliente pesado, se mantiene en modo Thin
                pass

        return cls._instance

    def connect(self, host, port, service_name, user, password, as_sysdba=False):
        """Establece la conexión con Oracle 21c XE."""
        try:
            self.disconnect()
            
            # Construcción explícita de DSN
            dsn = f"{host}:{port}/{service_name}"
            mode = oracledb.SYSDBA if as_sysdba else oracledb.DEFAULT_AUTH

            self.connection = oracledb.connect(
                user=user,
                password=password,
                dsn=dsn,
                mode=mode
            )

            self.host = host
            self.port = port
            self.service_name = service_name
            self.user = user.upper()
            self.role = "SYSDBA" if as_sysdba else "NORMAL"
            return True, "Conexión establecida exitosamente."
        except oracledb.Error as e:
            error_obj, = e.args
            return False, f"Error ORA-{error_obj.code}: {error_obj.message}"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"

    def disconnect(self):
        """Cierra la conexión actual si está abierta."""
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
            finally:
                self.connection = None
                self.user = None
                self.role = None

    def is_connected(self):
        """Verifica si existe una conexión activa."""
        if self.connection is None:
            return False
        try:
            self.connection.ping()
            return True
        except Exception:
            self.connection = None
            return False

    def get_connection(self):
        return self.connection