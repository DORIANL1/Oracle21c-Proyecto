import customtkinter as ctk
from tkinter import ttk, messagebox
from database.connection import DatabaseManager

class TablespacesTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Encabezado
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="ew")

        title = ctk.CTkLabel(
            header_frame, 
            text="Administración de Tablespaces", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(side="left")

        btn_refresh = ctk.CTkButton(
            header_frame, 
            text="Actualizar", 
            width=100, 
            command=self.load_data
        )
        btn_refresh.pack(side="right")

        # Pestañas Resumen y Datafiles
        self.tabs_view = ctk.CTkTabview(self)
        self.tabs_view.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")

        tab_resumen = self.tabs_view.add("Resumen de Tablespaces")
        tab_datafiles = self.tabs_view.add("Detalle de Datafiles")

        # Estilo para Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=26)
        style.configure("Treeview.Heading", background="#1f1f1f", foreground="white", relief="flat")
        style.map("Treeview", background=[("selected", "#1f538d")])

        # Tabla Resumen
        cols_resumen = ("tablespace", "total", "usado", "libre", "pct_usado", "pct_libre")
        self.tree_resumen = ttk.Treeview(tab_resumen, columns=cols_resumen, show="headings", height=10)
        self.tree_resumen.heading("tablespace", text="Tablespace")
        self.tree_resumen.heading("total", text="Total (MB)")
        self.tree_resumen.heading("usado", text="Usado (MB)")
        self.tree_resumen.heading("libre", text="Libre (MB)")
        self.tree_resumen.heading("pct_usado", text="% Ocupado")
        self.tree_resumen.heading("pct_libre", text="% Libre")

        for col in cols_resumen:
            self.tree_resumen.column(col, anchor="center", width=120)

        scroll_r = ttk.Scrollbar(tab_resumen, orient="vertical", command=self.tree_resumen.yview)
        self.tree_resumen.configure(yscrollcommand=scroll_r.set)
        self.tree_resumen.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scroll_r.pack(side="right", fill="y", pady=10)

        # Tabla Datafiles
        cols_df = ("tablespace", "file_name", "size_mb", "status", "autoext")
        self.tree_df = ttk.Treeview(tab_datafiles, columns=cols_df, show="headings", height=10)
        self.tree_df.heading("tablespace", text="Tablespace")
        self.tree_df.heading("file_name", text="Ruta de Archivo")
        self.tree_df.heading("size_mb", text="Tamaño (MB)")
        self.tree_df.heading("status", text="Estado")
        self.tree_df.heading("autoext", text="Autoextensible")

        self.tree_df.column("tablespace", anchor="center", width=120)
        self.tree_df.column("file_name", anchor="w", width=380)
        self.tree_df.column("size_mb", anchor="center", width=100)
        self.tree_df.column("status", anchor="center", width=90)
        self.tree_df.column("autoext", anchor="center", width=100)

        scroll_df = ttk.Scrollbar(tab_datafiles, orient="vertical", command=self.tree_df.yview)
        self.tree_df.configure(yscrollcommand=scroll_df.set)
        self.tree_df.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scroll_df.pack(side="right", fill="y", pady=10)

        # Barra de Operaciones
        actions_frame = ctk.CTkFrame(self)
        actions_frame.grid(row=2, column=0, padx=20, pady=(5, 15), sticky="ew")

        btn_create = ctk.CTkButton(actions_frame, text="Crear Tablespace", command=self.open_create_dialog)
        btn_create.pack(side="left", padx=10, pady=10)

        btn_add_df = ctk.CTkButton(actions_frame, text="Agregar Datafile", command=self.open_add_datafile_dialog)
        btn_add_df.pack(side="left", padx=10, pady=10)

        btn_resize_df = ctk.CTkButton(actions_frame, text="Redimensionar Datafile", command=self.open_resize_dialog)
        btn_resize_df.pack(side="left", padx=10, pady=10)

        if self.db.is_connected():
            self.load_data()

    def get_cursor(self):
        conn = self.db.get_connection()
        if not conn:
            messagebox.showerror("Error", "No hay conexión activa a Oracle.")
            return None
        return conn.cursor()

    def load_data(self):
        cursor = self.get_cursor()
        if not cursor:
            return

        try:
            for item in self.tree_resumen.get_children():
                self.tree_resumen.delete(item)
            for item in self.tree_df.get_children():
                self.tree_df.delete(item)

            query_resumen = """
                SELECT tablespace_name,
                       ROUND(SUM(mbtotal) / 1024 / 1024, 2) AS mbtotal,
                       ROUND(SUM(mbtotal - mblibre) / 1024 / 1024, 2) AS mbusado,
                       ROUND(SUM(mblibre) / 1024 / 1024, 2) AS mblibre,
                       ROUND(((SUM(mbtotal - mblibre) / 1024 / 1024) * 100) / NULLIF(SUM(mbtotal) / 1024 / 1024, 0), 2) AS porc_ocu,
                       ROUND(((SUM(mblibre) / 1024 / 1024) * 100) / NULLIF(SUM(mbtotal) / 1024 / 1024, 0), 2) AS porc_libre
                FROM (
                    SELECT tablespace_name, bytes AS mbtotal, 0 AS mblibre FROM dba_data_files
                    UNION ALL
                    SELECT tablespace_name, 0 AS mbtotal, bytes AS mblibre FROM dba_free_space
                )
                GROUP BY tablespace_name
                ORDER BY tablespace_name
            """
            cursor.execute(query_resumen)
            for row in cursor.fetchall():
                ts, tot, usd, lib, p_usd, p_lib = row
                self.tree_resumen.insert("", "end", values=(
                    ts, 
                    f"{tot:.2f}" if tot is not None else "0.00", 
                    f"{usd:.2f}" if usd is not None else "0.00", 
                    f"{lib:.2f}" if lib is not None else "0.00", 
                    f"{p_usd:.2f}%" if p_usd is not None else "0%", 
                    f"{p_lib:.2f}%" if p_lib is not None else "0%"
                ))

            query_df = """
                SELECT tablespace_name, file_name, ROUND(bytes / 1024 / 1024, 2), status, autoextensible 
                FROM dba_data_files 
                ORDER BY tablespace_name, file_name
            """
            cursor.execute(query_df)
            for row in cursor.fetchall():
                self.tree_df.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Error SQL", f"Fallo al consultar tablespaces:\n{str(e)}")
        finally:
            cursor.close()

    def get_tablespaces_list(self):
        cursor = self.get_cursor()
        if not cursor:
            return []
        try:
            cursor.execute("SELECT tablespace_name FROM dba_tablespaces ORDER BY tablespace_name")
            return [r[0] for r in cursor.fetchall()]
        except Exception:
            return []
        finally:
            cursor.close()

    def get_datafiles_list(self):
        cursor = self.get_cursor()
        if not cursor:
            return []
        try:
            cursor.execute("SELECT file_name FROM dba_data_files ORDER BY file_name")
            return [r[0] for r in cursor.fetchall()]
        except Exception:
            return []
        finally:
            cursor.close()

    # --- Acciones DDL ---

    def open_create_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Crear Tablespace")
        dialog.geometry("460x420")
        dialog.resizable(False, False)
        dialog.attributes("-topmost", True)

        container = ctk.CTkFrame(dialog)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            container, 
            text="Crear Nuevo Tablespace", 
            font=ctk.CTkFont(size=17, weight="bold")
        ).pack(pady=(5, 10))

        entry_name = ctk.CTkEntry(container, placeholder_text="Nombre Tablespace (ej. DATOS_TBS)")
        entry_name.pack(fill="x", padx=15, pady=6)

        entry_file = ctk.CTkEntry(container, placeholder_text="Nombre de archivo (ej. DATOS01.DBF)")
        entry_file.pack(fill="x", padx=15, pady=6)

        entry_size = ctk.CTkEntry(container, placeholder_text="Tamaño Inicial en MB (ej. 10)")
        entry_size.pack(fill="x", padx=15, pady=6)

        chk_auto = ctk.CTkCheckBox(container, text="Habilitar AUTOEXTEND ON")
        chk_auto.pack(padx=15, pady=6, anchor="w")

        entry_next = ctk.CTkEntry(container, placeholder_text="Incremento NEXT en MB (ej. 5)")
        entry_next.pack(fill="x", padx=15, pady=6)

        def ejecutar():
            t_name = entry_name.get().strip().upper()
            d_file = entry_file.get().strip()
            s_size = entry_size.get().strip()

            if not t_name or not d_file or not s_size:
                messagebox.showwarning("Atención", "Complete los campos obligatorios.", parent=dialog)
                return

            sql = f"CREATE TABLESPACE {t_name} DATAFILE '{d_file}' SIZE {s_size}M"
            if chk_auto.get() == 1:
                next_mb = entry_next.get().strip() or "5"
                sql += f" AUTOEXTEND ON NEXT {next_mb}M MAXSIZE UNLIMITED"

            cursor = self.get_cursor()
            if not cursor:
                return
            try:
                cursor.execute(sql)
                messagebox.showinfo("Éxito", f"Tablespace '{t_name}' creado exitosamente.", parent=dialog)
                dialog.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error de Oracle", str(e), parent=dialog)
            finally:
                cursor.close()

        ctk.CTkButton(container, text="Crear Tablespace", command=ejecutar).pack(pady=(12, 5))

    def open_add_datafile_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Agregar Datafile")
        dialog.geometry("460x320")
        dialog.resizable(False, False)
        dialog.attributes("-topmost", True)

        container = ctk.CTkFrame(dialog)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            container, 
            text="Agregar Datafile a Tablespace Existente", 
            font=ctk.CTkFont(size=17, weight="bold")
        ).pack(pady=(5, 10))

        ts_list = self.get_tablespaces_list()
        cb_ts = ctk.CTkComboBox(container, values=ts_list if ts_list else [""])
        cb_ts.pack(fill="x", padx=15, pady=6)

        entry_file = ctk.CTkEntry(container, placeholder_text="Nombre de archivo (ej. DATOS02.DBF)")
        entry_file.pack(fill="x", padx=15, pady=6)

        entry_size = ctk.CTkEntry(container, placeholder_text="Tamaño en MB (ej. 20)")
        entry_size.pack(fill="x", padx=15, pady=6)

        def ejecutar():
            t_name = cb_ts.get().strip().upper()
            d_file = entry_file.get().strip()
            s_size = entry_size.get().strip()

            if not t_name or not d_file or not s_size:
                messagebox.showwarning("Atención", "Todos los campos son obligatorios.", parent=dialog)
                return

            sql = f"ALTER TABLESPACE {t_name} ADD DATAFILE '{d_file}' SIZE {s_size}M"

            cursor = self.get_cursor()
            if not cursor:
                return
            try:
                cursor.execute(sql)
                messagebox.showinfo("Éxito", f"Datafile agregado a {t_name}.", parent=dialog)
                dialog.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error de Oracle", str(e), parent=dialog)
            finally:
                cursor.close()

        ctk.CTkButton(container, text="Agregar Datafile", command=ejecutar).pack(pady=(12, 5))

    def open_resize_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Redimensionar Datafile")
        dialog.geometry("500x300")
        dialog.resizable(False, False)
        dialog.attributes("-topmost", True)

        container = ctk.CTkFrame(dialog)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            container, 
            text="Redimensionar Datafile (RESIZE)", 
            font=ctk.CTkFont(size=17, weight="bold")
        ).pack(pady=(5, 10))

        df_list = self.get_datafiles_list()
        cb_df = ctk.CTkComboBox(container, values=df_list if df_list else [""])
        cb_df.pack(fill="x", padx=15, pady=6)

        entry_size = ctk.CTkEntry(container, placeholder_text="Nuevo tamaño en MB (ej. 30)")
        entry_size.pack(fill="x", padx=15, pady=6)

        def ejecutar():
            d_file = cb_df.get().strip()
            s_size = entry_size.get().strip()

            if not d_file or not s_size:
                messagebox.showwarning("Atención", "Complete todos los campos.", parent=dialog)
                return

            sql = f"ALTER DATABASE DATAFILE '{d_file}' RESIZE {s_size}M"

            cursor = self.get_cursor()
            if not cursor:
                return
            try:
                cursor.execute(sql)
                messagebox.showinfo("Éxito", "Datafile redimensionado exitosamente.", parent=dialog)
                dialog.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error de Oracle", str(e), parent=dialog)
            finally:
                cursor.close()

        ctk.CTkButton(container, text="Redimensionar", command=ejecutar).pack(pady=(12, 5))