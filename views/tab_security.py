import customtkinter as ctk
from tkinter import ttk, messagebox
from database.connection import DatabaseManager

class SecurityTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="ew")

        title = ctk.CTkLabel(
            header_frame, 
            text="Seguridad y Gestión de Usuarios", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(side="left")

        btn_refresh = ctk.CTkButton(
            header_frame, 
            text="Actualizar", 
            width=100, 
            command=self.load_users
        )
        btn_refresh.pack(side="right")

        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")

        cols = ("username", "status", "default_ts", "temp_ts", "created")
        self.tree_users = ttk.Treeview(table_frame, columns=cols, show="headings", height=10)
        self.tree_users.heading("username", text="Usuario")
        self.tree_users.heading("status", text="Estado de Cuenta")
        self.tree_users.heading("default_ts", text="Default Tablespace")
        self.tree_users.heading("temp_ts", text="Temporary Tablespace")
        self.tree_users.heading("created", text="Fecha Creación")

        for c in cols:
            self.tree_users.column(c, anchor="center", width=140)

        scroll_u = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_users.yview)
        self.tree_users.configure(yscrollcommand=scroll_u.set)
        self.tree_users.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scroll_u.pack(side="right", fill="y", pady=10)

        actions_frame = ctk.CTkFrame(self)
        actions_frame.grid(row=2, column=0, padx=20, pady=(5, 15), sticky="ew")

        btn_create_user = ctk.CTkButton(actions_frame, text="Crear Usuario", command=self.open_create_user_dialog)
        btn_create_user.pack(side="left", padx=10, pady=10)

        btn_roles = ctk.CTkButton(actions_frame, text="Asignar / Revocar Roles", command=self.open_roles_dialog)
        btn_roles.pack(side="left", padx=10, pady=10)

        btn_privs = ctk.CTkButton(actions_frame, text="Asignar / Revocar Privilegios", command=self.open_privs_dialog)
        btn_privs.pack(side="left", padx=10, pady=10)

        if self.db.is_connected():
            self.load_users()

    def get_cursor(self):
        conn = self.db.get_connection()
        if not conn:
            messagebox.showerror("Error", "No hay conexión activa a Oracle.")
            return None
        return conn.cursor()

    def load_users(self):
        cursor = self.get_cursor()
        if not cursor:
            return

        try:
            for item in self.tree_users.get_children():
                self.tree_users.delete(item)

            query = """
                SELECT username, account_status, default_tablespace, temporary_tablespace, 
                       TO_CHAR(created, 'YYYY-MM-DD HH24:MI') 
                FROM dba_users 
                ORDER BY username
            """
            cursor.execute(query)
            for row in cursor.fetchall():
                self.tree_users.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error SQL", f"No se pudo cargar la lista de usuarios:\n{str(e)}")
        finally:
            cursor.close()

    def get_tablespaces_list(self):
        cursor = self.get_cursor()
        if not cursor:
            return ["USERS"]
        try:
            cursor.execute("SELECT tablespace_name FROM dba_tablespaces ORDER BY tablespace_name")
            return [r[0] for r in cursor.fetchall()]
        except Exception:
            return ["USERS"]
        finally:
            cursor.close()

    def get_users_list(self):
        cursor = self.get_cursor()
        if not cursor:
            return []
        try:
            cursor.execute("SELECT username FROM dba_users ORDER BY username")
            return [r[0] for r in cursor.fetchall()]
        except Exception:
            return []
        finally:
            cursor.close()

    # --- Acciones DDL de Seguridad ---

    def open_create_user_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Crear Usuario")
        dialog.geometry("460x420")
        dialog.resizable(False, False)
        dialog.attributes("-topmost", True)

        container = ctk.CTkFrame(dialog)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(container, text="Crear Nuevo Usuario", font=ctk.CTkFont(size=17, weight="bold")).pack(pady=(5, 10))

        entry_user = ctk.CTkEntry(container, placeholder_text="Nombre de Usuario (ej. PROY_USER)")
        entry_user.pack(fill="x", padx=15, pady=6)

        entry_pwd = ctk.CTkEntry(container, placeholder_text="Contraseña", show="*")
        entry_pwd.pack(fill="x", padx=15, pady=6)

        ts_list = self.get_tablespaces_list()
        ctk.CTkLabel(container, text="Default Tablespace:", font=ctk.CTkFont(size=12)).pack(padx=15, anchor="w")
        cb_ts = ctk.CTkComboBox(container, values=ts_list)
        cb_ts.pack(fill="x", padx=15, pady=6)

        entry_quota = ctk.CTkEntry(container, placeholder_text="Cuota en MB (vacío para UNLIMITED)")
        entry_quota.pack(fill="x", padx=15, pady=6)

        def ejecutar():
            username = entry_user.get().strip().upper()
            pwd = entry_pwd.get().strip()
            ts = cb_ts.get().strip()
            quota = entry_quota.get().strip()

            if not username or not pwd or not ts:
                messagebox.showwarning("Atención", "Usuario, contraseña y tablespace son obligatorios.", parent=dialog)
                return

            quota_clause = f"QUOTA {quota}M ON {ts}" if quota else f"QUOTA UNLIMITED ON {ts}"
            sql = f"CREATE USER {username} IDENTIFIED BY \"{pwd}\" DEFAULT TABLESPACE {ts} {quota_clause}"

            cursor = self.get_cursor()
            if not cursor:
                return
            try:
                try:
                    cursor.execute('ALTER SESSION SET "_ORACLE_SCRIPT" = TRUE')
                except Exception:
                    pass

                cursor.execute(sql)
                cursor.execute(f"GRANT CREATE SESSION TO {username}")
                messagebox.showinfo("Éxito", f"Usuario '{username}' creado exitosamente.", parent=dialog)
                dialog.destroy()
                self.load_users()
            except Exception as e:
                messagebox.showerror("Error al crear usuario", str(e), parent=dialog)
            finally:
                cursor.close()

        ctk.CTkButton(container, text="Crear Usuario", command=ejecutar).pack(pady=(12, 5))

    def open_roles_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Gestión de Roles")
        dialog.geometry("460x320")
        dialog.resizable(False, False)
        dialog.attributes("-topmost", True)

        container = ctk.CTkFrame(dialog)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(container, text="Asignar / Revocar Roles", font=ctk.CTkFont(size=17, weight="bold")).pack(pady=(5, 10))

        users = self.get_users_list()
        cb_users = ctk.CTkComboBox(container, values=users if users else [""])
        cb_users.pack(fill="x", padx=15, pady=6)

        cursor = self.get_cursor()
        roles = ["CONNECT", "RESOURCE", "DBA"]
        if cursor:
            try:
                cursor.execute("SELECT role FROM dba_roles ORDER BY role")
                roles = [r[0] for r in cursor.fetchall()]
            except Exception:
                pass
            finally:
                cursor.close()

        cb_roles = ctk.CTkComboBox(container, values=roles)
        cb_roles.pack(fill="x", padx=15, pady=6)

        def ejecutar(accion):
            user = cb_users.get().strip().upper()
            role = cb_roles.get().strip().upper()

            if not user or not role:
                messagebox.showwarning("Atención", "Seleccione usuario y rol.", parent=dialog)
                return

            sql = f"{accion} {role} TO {user}" if accion == "GRANT" else f"{accion} {role} FROM {user}"
            cur = self.get_cursor()
            if not cur:
                return
            try:
                try:
                    cur.execute('ALTER SESSION SET "_ORACLE_SCRIPT" = TRUE')
                except Exception:
                    pass
                cur.execute(sql)
                messagebox.showinfo("Éxito", f"{accion} del rol '{role}' sobre '{user}' completado.", parent=dialog)
            except Exception as e:
                messagebox.showerror("Error de Permisos", str(e), parent=dialog)
            finally:
                cur.close()

        btn_box = ctk.CTkFrame(container, fg_color="transparent")
        btn_box.pack(pady=15)

        ctk.CTkButton(btn_box, text="GRANT Rol", command=lambda: ejecutar("GRANT"), width=120).pack(side="left", padx=10)
        ctk.CTkButton(btn_box, text="REVOKE Rol", command=lambda: ejecutar("REVOKE"), width=120, fg_color="#C0392B", hover_color="#962D22").pack(side="left", padx=10)

    def open_privs_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Gestión de Privilegios")
        dialog.geometry("480x320")
        dialog.resizable(False, False)
        dialog.attributes("-topmost", True)

        container = ctk.CTkFrame(dialog)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(container, text="Asignar / Revocar Privilegios", font=ctk.CTkFont(size=17, weight="bold")).pack(pady=(5, 10))

        users = self.get_users_list()
        cb_users = ctk.CTkComboBox(container, values=users if users else [""])
        cb_users.pack(fill="x", padx=15, pady=6)

        cursor = self.get_cursor()
        privs = ["CREATE SESSION", "CREATE TABLE", "CREATE VIEW", "CREATE PROCEDURE", "UNLIMITED TABLESPACE"]
        if cursor:
            try:
                cursor.execute("SELECT name FROM system_privilege_map ORDER BY name")
                privs = [r[0] for r in cursor.fetchall()]
            except Exception:
                pass
            finally:
                cursor.close()

        cb_privs = ctk.CTkComboBox(container, values=privs)
        cb_privs.pack(fill="x", padx=15, pady=6)

        def ejecutar(accion):
            user = cb_users.get().strip().upper()
            priv = cb_privs.get().strip().upper()

            if not user or not priv:
                messagebox.showwarning("Atención", "Seleccione usuario y privilegio.", parent=dialog)
                return

            sql = f"{accion} {priv} TO {user}" if accion == "GRANT" else f"{accion} {priv} FROM {user}"
            cur = self.get_cursor()
            if not cur:
                return
            try:
                try:
                    cur.execute('ALTER SESSION SET "_ORACLE_SCRIPT" = TRUE')
                except Exception:
                    pass
                cur.execute(sql)
                messagebox.showinfo("Éxito", f"{accion} de '{priv}' a '{user}' completado.", parent=dialog)
            except Exception as e:
                messagebox.showerror("Error de Privilegio", str(e), parent=dialog)
            finally:
                cur.close()

        btn_box = ctk.CTkFrame(container, fg_color="transparent")
        btn_box.pack(pady=15)

        ctk.CTkButton(btn_box, text="GRANT Privilegio", command=lambda: ejecutar("GRANT"), width=130).pack(side="left", padx=10)
        ctk.CTkButton(btn_box, text="REVOKE Privilegio", command=lambda: ejecutar("REVOKE"), width=130, fg_color="#C0392B", hover_color="#962D22").pack(side="left", padx=10)