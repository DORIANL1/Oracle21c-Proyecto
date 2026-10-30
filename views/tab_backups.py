import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from database.connection import DatabaseManager
from views.ui_helpers import COLORS, show_operation_error


class BackupsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=COLORS["canvas"])
        self.db = DatabaseManager()
        # Diccionario {NOMBRE_DIRECTORIO: RUTA_FISICA}
        self.directories_map = {}
        self._was_connected = False

        # Configuración del layout principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Encabezado del módulo
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 5))

        title_label = ctk.CTkLabel(
            header_frame,
            text="Respaldos, Recuperación y Directorios (Oracle Data Pump)",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side="left")

        btn_refresh_all = ctk.CTkButton(
            header_frame,
            text="Sincronizar con Oracle",
            width=160,
            command=self.refresh_all_data
        )
        btn_refresh_all.pack(side="right")

        # Contenedor de las 3 sub-pestañas
        self.tabview = ctk.CTkTabview(self, fg_color=COLORS["surface"])
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.tab_dirs = self.tabview.add("1. Directorios de Oracle")
        self.tab_exp = self.tabview.add("2. Respaldos (expdp)")
        self.tab_imp = self.tabview.add("3. Recuperación (impdp)")

        self._setup_treeview_style()
        self._build_directories_tab()
        self._build_export_tab()
        self._build_import_tab()

        # Sincronizar automáticamente apenas detecte conexión activa
        self._auto_sync_loop()

    def _setup_treeview_style(self):
        ttk.Style(self).configure("Treeview", rowheight=28)

    def _auto_sync_loop(self):
        is_conn = self.db.is_connected()
        if is_conn and not self._was_connected:
            self.refresh_all_data()
        self._was_connected = is_conn
        self.after(1500, self._auto_sync_loop)

    def refresh_all_data(self):
        if not self.db.is_connected():
            return
        self.load_directories()
        self.load_schemas_helper()

    # 1. PESTAÑA DIRECTORIOS DE ORACLE (DBA_DIRECTORIES)
    def _build_directories_tab(self):
        self.tab_dirs.grid_rowconfigure(1, weight=1)
        self.tab_dirs.grid_columnconfigure(0, weight=1)

        form_frame = ctk.CTkFrame(self.tab_dirs, fg_color=COLORS["surface"])
        form_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        form_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(form_frame, text="Nombre Lógico:").grid(row=0, column=0, padx=10, pady=12, sticky="w")
        self.entry_dir_name = ctk.CTkEntry(form_frame, placeholder_text="Ej: DIR_RESPALDOS", width=180)
        self.entry_dir_name.grid(row=0, column=1, padx=5, pady=12, sticky="w")

        ctk.CTkLabel(form_frame, text="Ruta en Disco:").grid(row=0, column=2, padx=(15, 5), pady=12, sticky="w")
        self.entry_dir_path = ctk.CTkEntry(form_frame, placeholder_text="C:\\respaldos_oracle")
        self.entry_dir_path.grid(row=0, column=3, padx=5, pady=12, sticky="ew")

        btn_browse = ctk.CTkButton(
            form_frame,
            text="Explorar Carpeta...",
            width=130,
            fg_color="#4A5568",
            hover_color="#2D3748",
            command=self._browse_folder
        )
        btn_browse.grid(row=0, column=4, padx=5, pady=12)

        btn_create_dir = ctk.CTkButton(
            form_frame,
            text="Crear / Reemplazar Directorio",
            width=190,
            command=self.create_or_replace_directory
        )
        btn_create_dir.grid(row=0, column=5, padx=10, pady=12)

        table_container = ctk.CTkFrame(self.tab_dirs, fg_color=COLORS["surface"])
        table_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        columns = ("owner", "name", "path")
        self.tree_dirs = ttk.Treeview(table_container, columns=columns, show="headings")
        self.tree_dirs.heading("owner", text="PROPIETARIO")
        self.tree_dirs.heading("name", text="NOMBRE DEL DIRECTORIO (DBA_DIRECTORIES)")
        self.tree_dirs.heading("path", text="RUTA FÍSICA DEL SISTEMA DE ARCHIVOS")

        self.tree_dirs.column("owner", width=120, anchor="center")
        self.tree_dirs.column("name", width=260, anchor="w")
        self.tree_dirs.column("path", width=550, anchor="w")

        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree_dirs.yview)
        self.tree_dirs.configure(yscrollcommand=scrollbar.set)

        self.tree_dirs.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _browse_folder(self):
        folder = filedialog.askdirectory(title="Seleccionar carpeta para respaldos Data Pump")
        if folder:
            normalized = os.path.normpath(folder)
            self.entry_dir_path.delete(0, "end")
            self.entry_dir_path.insert(0, normalized)

    def load_directories(self):
        conn = self.db.get_connection()
        if not conn:
            return

        try:
            for item in self.tree_dirs.get_children():
                self.tree_dirs.delete(item)
            self.directories_map.clear()

            cursor = conn.cursor()
            cursor.execute("""
                SELECT owner, directory_name, directory_path
                FROM dba_directories
                ORDER BY directory_name
            """)
            rows = cursor.fetchall()
            cursor.close()

            for owner, name, path in rows:
                self.directories_map[name] = path
                self.tree_dirs.insert("", "end", values=(owner, name, path))

            dir_names = list(self.directories_map.keys())
            if dir_names:
                self.combo_exp_dir.configure(values=dir_names)
                self.combo_imp_dir.configure(values=dir_names)

                default_dir = "DATA_PUMP_DIR" if "DATA_PUMP_DIR" in dir_names else dir_names[0]
                self.combo_exp_dir.set(default_dir)
                self.combo_imp_dir.set(default_dir)
                self.load_dmp_files(default_dir)

        except Exception as e:
            show_operation_error(self, "consultar los directorios de Oracle", e)

    def create_or_replace_directory(self):
        if not self.db.is_connected():
            messagebox.showwarning("Sin conexión", "Conéctate primero a la base de datos.")
            return

        dir_name = self.entry_dir_name.get().strip().upper()
        dir_path = self.entry_dir_path.get().strip()

        if not dir_name or not dir_path:
            messagebox.showwarning("Campos incompletos", "Ingresa el nombre del directorio y su ruta física.")
            return

        if not dir_name.replace("_", "").isalnum():
            messagebox.showwarning("Nombre inválido", "El nombre solo debe contener letras, números y guiones bajos (_).")
            return

        try:
            os.makedirs(dir_path, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error de Sistema de Archivos", f"No se pudo crear la carpeta física:\n{e}")
            return

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            safe_path = dir_path.replace("'", "''")
            cursor.execute(f"CREATE OR REPLACE DIRECTORY {dir_name} AS '{safe_path}'")
            cursor.close()

            messagebox.showinfo(
                "Directorio Registrado",
                f"El directorio '{dir_name}' fue creado exitosamente en:\n{dir_path}"
            )
            self.load_directories()
            self.combo_exp_dir.set(dir_name)
            self.combo_imp_dir.set(dir_name)
            self.load_dmp_files(dir_name)

        except Exception as e:
            show_operation_error(self, "crear o reemplazar el directorio Oracle", e)

    
    # 2. SUB-PESTAÑA DE RESPALDOS (expdp)
    def _build_export_tab(self):
        self.tab_exp.grid_rowconfigure(2, weight=1)
        self.tab_exp.grid_columnconfigure(0, weight=1)

        form = ctk.CTkFrame(self.tab_exp, fg_color=COLORS["surface"])
        form.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(form, text="Directorio Oracle:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.combo_exp_dir = ctk.CTkComboBox(form, values=["DATA_PUMP_DIR"], width=230)
        self.combo_exp_dir.grid(row=0, column=1, padx=10, pady=8, sticky="w")

        ctk.CTkLabel(form, text="Nombre Archivo (.dmp):").grid(row=0, column=2, padx=10, pady=8, sticky="w")
        self.entry_exp_file = ctk.CTkEntry(form, placeholder_text="respaldo.dmp", width=230)
        self.entry_exp_file.insert(0, "respaldo_datos.dmp")
        self.entry_exp_file.grid(row=0, column=3, padx=10, pady=8, sticky="w")

        ctk.CTkLabel(form, text="Tipo de Respaldo:").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.var_exp_mode = ctk.StringVar(value="SCHEMAS")

        radio_frame = ctk.CTkFrame(form, fg_color="transparent")
        radio_frame.grid(row=1, column=1, columnspan=3, padx=5, pady=8, sticky="w")

        ctk.CTkRadioButton(
            radio_frame, text="Por Schemas (SCHEMAS)", variable=self.var_exp_mode,
            value="SCHEMAS", command=self._update_exp_mode_ui
        ).pack(side="left", padx=10)

        ctk.CTkRadioButton(
            radio_frame, text="Por Tablas (TABLES)", variable=self.var_exp_mode,
            value="TABLES", command=self._update_exp_mode_ui
        ).pack(side="left", padx=10)

        ctk.CTkRadioButton(
            radio_frame, text="Full (Base Completa)", variable=self.var_exp_mode,
            value="FULL", command=self._update_exp_mode_ui
        ).pack(side="left", padx=10)

        self.lbl_exp_target = ctk.CTkLabel(form, text="Esquema(s) a exportar:")
        self.lbl_exp_target.grid(row=2, column=0, padx=10, pady=8, sticky="w")

        self.entry_exp_target = ctk.CTkEntry(form, placeholder_text="Ej: DEMO_USER", width=230)
        self.entry_exp_target.grid(row=2, column=1, padx=10, pady=8, sticky="w")

        ctk.CTkLabel(form, text="Elegir esquema existente:").grid(row=2, column=2, padx=10, pady=8, sticky="w")
        self.combo_schema_helper = ctk.CTkComboBox(
            form, values=["(Cargar esquemas)"], width=230, command=self._on_pick_schema_exp
        )
        self.combo_schema_helper.grid(row=2, column=3, padx=10, pady=8, sticky="w")

        self.btn_run_expdp = ctk.CTkButton(
            form,
            text="Ejecutar Respaldo (expdp)",
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            width=200,
            command=self.run_expdp_backup
        )
        self.btn_run_expdp.grid(row=2, column=4, padx=15, pady=8)

        ctk.CTkLabel(
            self.tab_exp,
            text="Consola de Avance en Tiempo Real (expdp):",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=1, column=0, sticky="w", padx=12, pady=(2, 2))

        self.txt_exp_log = ctk.CTkTextbox(self.tab_exp, font=("Consolas", 12))
        self.txt_exp_log.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

    def _update_exp_mode_ui(self):
        mode = self.var_exp_mode.get()
        if mode == "FULL":
            self.lbl_exp_target.configure(text="Objetivo (No requerido):")
            self.entry_exp_target.configure(state="disabled")
        elif mode == "SCHEMAS":
            self.lbl_exp_target.configure(text="Esquema(s) a exportar:")
            self.entry_exp_target.configure(state="normal", placeholder_text="Ej: DEMO_USER")
        elif mode == "TABLES":
            self.lbl_exp_target.configure(text="Tabla(s) (ESQUEMA.TABLA):")
            self.entry_exp_target.configure(state="normal", placeholder_text="Ej: DEMO_USER.CLIENTES")

    def _on_pick_schema_exp(self, selected_schema):
        if selected_schema and not selected_schema.startswith("("):
            if self.var_exp_mode.get() == "TABLES":
                self.entry_exp_target.delete(0, "end")
                self.entry_exp_target.insert(0, f"{selected_schema}.NOMBRE_TABLA")
            else:
                self.entry_exp_target.delete(0, "end")
                self.entry_exp_target.insert(0, selected_schema)

    def load_schemas_helper(self):
        conn = self.db.get_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT username FROM dba_users
                WHERE oracle_maintained = 'N'
                ORDER BY username
            """)
            users = [r[0] for r in cursor.fetchall()]
            if not users:
                cursor.execute("SELECT username FROM dba_users ORDER BY username")
                users = [r[0] for r in cursor.fetchall()]
            cursor.close()

            if users:
                self.combo_schema_helper.configure(values=users)
                self.combo_schema_helper.set(users[0])
                self.combo_imp_schema_helper.configure(values=users)
                self.combo_imp_schema_helper.set(users[0])
        except Exception as e:
            show_operation_error(self, "cargar la lista de esquemas", e)

    def run_expdp_backup(self):
        if not self.db.is_connected():
            messagebox.showwarning("Sin conexión", "Conéctate primero a Oracle 21c XE.")
            return

        directory = self.combo_exp_dir.get().strip()
        dumpfile = self.entry_exp_file.get().strip()
        mode = self.var_exp_mode.get()
        target = self.entry_exp_target.get().strip()

        if not dumpfile:
            messagebox.showwarning("Archivo requerido", "Especifica un nombre para el archivo .dmp.")
            return
        if not dumpfile.lower().endswith(".dmp"):
            dumpfile += ".dmp"

        logfile = dumpfile[:-4] + "_exp.log"
        userid = self._build_datapump_userid()

        cmd = [
            "expdp",
            userid,
            f"DIRECTORY={directory}",
            f"DUMPFILE={dumpfile}",
            f"LOGFILE={logfile}",
            "REUSE_DUMPFILES=Y"
        ]

        if mode == "FULL":
            cmd.append("FULL=Y")
        elif mode == "SCHEMAS":
            if not target:
                messagebox.showwarning("Esquema requerido", "Indica el nombre del esquema a respaldar.")
                return
            cmd.append(f"SCHEMAS={target}")
        elif mode == "TABLES":
            if not target:
                messagebox.showwarning("Tabla requerida", "Indica la tabla a respaldar (ej: ESQUEMA.TABLA).")
                return
            cmd.append(f"TABLES={target}")

        self._execute_datapump_process(cmd, self.txt_exp_log, self.btn_run_expdp)

    # 3. SUB-PESTAÑA DE RECUPERACIÓN (impdp)
    def _build_import_tab(self):
        self.tab_imp.grid_rowconfigure(2, weight=1)
        self.tab_imp.grid_columnconfigure(0, weight=1)

        form = ctk.CTkFrame(self.tab_imp, fg_color=COLORS["surface"])
        form.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(form, text="Directorio Oracle:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.combo_imp_dir = ctk.CTkComboBox(
            form,
            values=["DATA_PUMP_DIR"],
            width=230,
            command=self.load_dmp_files
        )
        self.combo_imp_dir.grid(row=0, column=1, padx=10, pady=8, sticky="w")

        ctk.CTkLabel(form, text="Archivo .dmp a restaurar:").grid(row=0, column=2, padx=10, pady=8, sticky="w")
        self.combo_imp_dmp = ctk.CTkComboBox(form, values=["(Sin archivos .dmp)"], width=230)
        self.combo_imp_dmp.grid(row=0, column=3, padx=10, pady=8, sticky="w")

        btn_scan_dmp = ctk.CTkButton(
            form,
            text="Refrescar .dmp",
            width=140,
            fg_color="#4A5568",
            hover_color="#2D3748",
            command=lambda: self.load_dmp_files(self.combo_imp_dir.get())
        )
        btn_scan_dmp.grid(row=0, column=4, padx=15, pady=8)

        ctk.CTkLabel(form, text="Modo de Recuperación:").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.var_imp_mode = ctk.StringVar(value="SCHEMAS")

        radio_imp_frame = ctk.CTkFrame(form, fg_color="transparent")
        radio_imp_frame.grid(row=1, column=1, columnspan=3, padx=5, pady=8, sticky="w")

        ctk.CTkRadioButton(
            radio_imp_frame, text="Por Schemas (SCHEMAS)", variable=self.var_imp_mode,
            value="SCHEMAS", command=self._update_imp_mode_ui
        ).pack(side="left", padx=10)

        ctk.CTkRadioButton(
            radio_imp_frame, text="Por Tablas (TABLES)", variable=self.var_imp_mode,
            value="TABLES", command=self._update_imp_mode_ui
        ).pack(side="left", padx=10)

        ctk.CTkRadioButton(
            radio_imp_frame, text="Full (Todo el archivo .dmp)", variable=self.var_imp_mode,
            value="FULL", command=self._update_imp_mode_ui
        ).pack(side="left", padx=10)

        self.lbl_imp_target = ctk.CTkLabel(form, text="Esquema(s) a restaurar:")
        self.lbl_imp_target.grid(row=2, column=0, padx=10, pady=8, sticky="w")

        self.entry_imp_target = ctk.CTkEntry(form, placeholder_text="Ej: DEMO_USER", width=230)
        self.entry_imp_target.grid(row=2, column=1, padx=10, pady=8, sticky="w")

        ctk.CTkLabel(form, text="Elegir esquema existente:").grid(row=2, column=2, padx=10, pady=8, sticky="w")
        self.combo_imp_schema_helper = ctk.CTkComboBox(
            form, values=["(Cargar esquemas)"], width=230, command=self._on_pick_schema_imp
        )
        self.combo_imp_schema_helper.grid(row=2, column=3, padx=10, pady=8, sticky="w")

        self.btn_run_impdp = ctk.CTkButton(
            form,
            text="Iniciar Recuperación (impdp)",
            fg_color="#D97706",
            hover_color="#B45309",
            width=200,
            command=self.run_impdp_recovery
        )
        self.btn_run_impdp.grid(row=2, column=4, padx=15, pady=8)

        ctk.CTkLabel(
            self.tab_imp,
            text="Consola de Avance en Tiempo Real (impdp):",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=1, column=0, sticky="w", padx=12, pady=(2, 2))

        self.txt_imp_log = ctk.CTkTextbox(self.tab_imp, font=("Consolas", 12))
        self.txt_imp_log.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

    def _update_imp_mode_ui(self):
        mode = self.var_imp_mode.get()
        if mode == "FULL":
            self.lbl_imp_target.configure(text="Objetivo (No requerido):")
            self.entry_imp_target.configure(state="disabled")
        elif mode == "SCHEMAS":
            self.lbl_imp_target.configure(text="Esquema(s) a restaurar:")
            self.entry_imp_target.configure(state="normal", placeholder_text="Ej: DEMO_USER")
        elif mode == "TABLES":
            self.lbl_imp_target.configure(text="Tabla(s) (ESQUEMA.TABLA):")
            self.entry_imp_target.configure(state="normal", placeholder_text="Ej: DEMO_USER.CLIENTES")

    def _on_pick_schema_imp(self, selected_schema):
        if selected_schema and not selected_schema.startswith("("):
            if self.var_imp_mode.get() == "TABLES":
                self.entry_imp_target.delete(0, "end")
                self.entry_imp_target.insert(0, f"{selected_schema}.NOMBRE_TABLA")
            else:
                self.entry_imp_target.delete(0, "end")
                self.entry_imp_target.insert(0, selected_schema)

    def load_dmp_files(self, dir_name):
        folder_path = self.directories_map.get(dir_name)
        if not folder_path or not os.path.isdir(folder_path):
            msg = "(Carpeta no accesible en disco)"
            self.combo_imp_dmp.configure(values=[msg])
            self.combo_imp_dmp.set(msg)
            return

        try:
            dmp_files = sorted([
                f for f in os.listdir(folder_path)
                if f.lower().endswith(".dmp")
            ])
            if dmp_files:
                self.combo_imp_dmp.configure(values=dmp_files)
                self.combo_imp_dmp.set(dmp_files[0])
            else:
                msg = "(Sin archivos .dmp en carpeta)"
                self.combo_imp_dmp.configure(values=[msg])
                self.combo_imp_dmp.set(msg)
        except Exception:
            msg = "(Error leyendo carpeta)"
            self.combo_imp_dmp.configure(values=[msg])
            self.combo_imp_dmp.set(msg)

    def run_impdp_recovery(self):
        if not self.db.is_connected():
            messagebox.showwarning("Sin conexión", "Conéctate primero a Oracle 21c XE.")
            return

        directory = self.combo_imp_dir.get().strip()
        dumpfile = self.combo_imp_dmp.get().strip()
        mode = self.var_imp_mode.get()
        target = self.entry_imp_target.get().strip()

        if not dumpfile or dumpfile.startswith("("):
            messagebox.showwarning("Archivo .dmp inválido", "Selecciona un archivo .dmp válido de la lista.")
            return

        logfile = dumpfile[:-4] + "_imp.log"
        userid = self._build_datapump_userid()

        cmd = [
            "impdp",
            userid,
            f"DIRECTORY={directory}",
            f"DUMPFILE={dumpfile}",
            f"LOGFILE={logfile}",
            "TABLE_EXISTS_ACTION=REPLACE"
        ]

        if mode == "FULL":
            cmd.append("FULL=Y")
        elif mode == "SCHEMAS":
            if not target:
                messagebox.showwarning("Esquema requerido", "Indica el esquema que deseas recuperar.")
                return
            cmd.append(f"SCHEMAS={target}")
        elif mode == "TABLES":
            if not target:
                messagebox.showwarning("Tabla requerida", "Indica la tabla que deseas recuperar (ESQUEMA.TABLA).")
                return
            cmd.append(f"TABLES={target}")

        self._execute_datapump_process(cmd, self.txt_imp_log, self.btn_run_impdp)

   # MOTOR DE EJECUCIÓN ASÍNCRONA
    def _build_datapump_userid(self):
        app = self.winfo_toplevel()
        password = app.entry_pass.get().strip() if hasattr(app, "entry_pass") else ""
        user = self.db.user or "SYS"
        dsn = f"{self.db.host}:{self.db.port}/{self.db.service_name}"

        if self.db.role == "SYSDBA" or user.upper() == "SYS":
            return f"'{user}/{password}@{dsn} AS SYSDBA'"
        return f"{user}/{password}@{dsn}"

    def _execute_datapump_process(self, cmd, log_textbox, action_button):
        action_button.configure(state="disabled")
        log_textbox.delete("1.0", "end")

        safe_cmd_display = " ".join([cmd[0], '"<CREDENCIALES_ACTIVAS>"'] + cmd[2:])
        log_textbox.insert("end", f"> Ejecutando: {safe_cmd_display}\n")
        log_textbox.insert("end", "=" * 80 + "\n\n")

        def worker():
            try:
                creation_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="cp850" if os.name == "nt" else "utf-8",
                    errors="replace",
                    bufsize=1,
                    creationflags=creation_flags
                )

                for line in iter(process.stdout.readline, ""):
                    self.after(0, self._append_log_line, log_textbox, line)

                process.stdout.close()
                return_code = process.wait()

                if return_code == 0:
                    status_msg = "\n" + "=" * 80 + "\n[PROCESO DATA PUMP COMPLETADO EXITOSAMENTE - Código 0]\n"
                else:
                    status_msg = "\n" + "=" * 80 + f"\n[PROCESO FINALIZADO CON ADVERTENCIAS O ERRORES - Código {return_code}]\n"

                self.after(0, self._append_log_line, log_textbox, status_msg)
                self.after(0, lambda: self.load_dmp_files(self.combo_imp_dir.get()))

            except FileNotFoundError:
                err = (
                    "\n[ERROR CRÍTICO]: No se encontró el ejecutable 'expdp' / 'impdp'.\n"
                    "Verifica que la carpeta 'bin' de tu instalación de Oracle 21c XE esté en el PATH de Windows.\n"
                )
                self.after(0, self._append_log_line, log_textbox, err)
            except Exception as e:
                self.after(0, self._append_log_line, log_textbox, f"\n[ERROR INESPERADO]: {e}\n")
            finally:
                self.after(0, lambda: action_button.configure(state="normal"))

        threading.Thread(target=worker, daemon=True).start()

    @staticmethod
    def _append_log_line(textbox, text):
        textbox.insert("end", text)
        textbox.see("end")