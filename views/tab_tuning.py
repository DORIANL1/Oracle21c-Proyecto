import customtkinter as ctk
from tkinter import messagebox
from database.connection import DatabaseManager

class TuningTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="ew")
        ctk.CTkLabel(header, text="Tuning y Optimización de Consultas", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")

        plan_frame = ctk.CTkFrame(self)
        plan_frame.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")
        plan_frame.grid_columnconfigure(0, weight=1)
        plan_frame.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(plan_frame, text="Ingrese consulta SELECT para analizar:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.txt_query = ctk.CTkTextbox(plan_frame, height=80)
        self.txt_query.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        ctk.CTkButton(plan_frame, text="Analizar (EXPLAIN PLAN)", command=self.ejecutar_explain).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.txt_result = ctk.CTkTextbox(plan_frame, font=ctk.CTkFont(family="Courier", size=12))
        self.txt_result.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")

        actions_frame = ctk.CTkFrame(self)
        actions_frame.grid(row=2, column=0, padx=20, pady=(5, 15), sticky="ew")
        
        ctk.CTkButton(actions_frame, text="Recolectar Estadísticas (DBMS_STATS)", command=self.open_stats_dialog).pack(side="left", padx=10, pady=10)
        ctk.CTkButton(actions_frame, text="Gestionar Índices", command=self.open_index_dialog).pack(side="left", padx=10, pady=10)

    def get_cursor(self):
        conn = self.db.get_connection()
        if not conn:
            messagebox.showerror("Error", "No hay conexión activa a Oracle.")
            return None
        return conn.cursor()

    def ejecutar_explain(self):
        query = self.txt_query.get("1.0", "end-1c").strip().rstrip(';')
        if not query:
            messagebox.showwarning("Atención", "Ingrese una consulta SQL.")
            return

        cursor = self.get_cursor()
        if not cursor:
            return

        try:
            cursor.execute(f"EXPLAIN PLAN FOR {query}")
            cursor.execute("SELECT PLAN_TABLE_OUTPUT FROM TABLE(DBMS_XPLAN.DISPLAY())")
            
            self.txt_result.delete("1.0", "end")
            for row in cursor.fetchall():
                self.txt_result.insert("end", row[0] + "\n")
        except Exception as e:
            messagebox.showerror("Error SQL", str(e))
        finally:
            cursor.close()

    def open_stats_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Recolectar Estadísticas")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.attributes("-topmost", True)

        container = ctk.CTkFrame(dialog)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(container, text="DBMS_STATS", font=ctk.CTkFont(size=17, weight="bold")).pack(pady=(5, 10))

        entry_schema = ctk.CTkEntry(container, placeholder_text="Esquema (ej. HR)")
        entry_schema.pack(fill="x", padx=15, pady=6)

        entry_table = ctk.CTkEntry(container, placeholder_text="Tabla (ej. EMPLOYEES)")
        entry_table.pack(fill="x", padx=15, pady=6)

        def ejecutar():
            schema = entry_schema.get().strip().upper()
            table = entry_table.get().strip().upper()

            if not schema or not table:
                messagebox.showwarning("Atención", "Complete esquema y tabla.", parent=dialog)
                return

            cursor = self.get_cursor()
            if not cursor:
                return
            try:
                cursor.callproc('DBMS_STATS.GATHER_TABLE_STATS', [schema, table])
                messagebox.showinfo("Éxito", f"Estadísticas recolectadas para {schema}.{table}.", parent=dialog)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error de Oracle", str(e), parent=dialog)
            finally:
                cursor.close()

        ctk.CTkButton(container, text="Recolectar", command=ejecutar).pack(pady=(12, 5))

    def open_index_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Gestionar Índices")
        dialog.geometry("450x350")
        dialog.resizable(False, False)
        dialog.attributes("-topmost", True)

        container = ctk.CTkFrame(dialog)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(container, text="Crear / Eliminar Índice", font=ctk.CTkFont(size=17, weight="bold")).pack(pady=(5, 10))

        entry_idx = ctk.CTkEntry(container, placeholder_text="Nombre del Índice (ej. IDX_EMP_ID)")
        entry_idx.pack(fill="x", padx=15, pady=6)

        entry_table = ctk.CTkEntry(container, placeholder_text="Tabla (ej. EMPLOYEES)")
        entry_table.pack(fill="x", padx=15, pady=6)

        entry_col = ctk.CTkEntry(container, placeholder_text="Columna (ej. EMPLOYEE_ID)")
        entry_col.pack(fill="x", padx=15, pady=6)

        def ejecutar(accion):
            idx = entry_idx.get().strip().upper()
            tabla = entry_table.get().strip().upper()
            columna = entry_col.get().strip().upper()

            if not idx:
                messagebox.showwarning("Atención", "El nombre del índice es obligatorio.", parent=dialog)
                return
            
            if accion == "CREATE" and (not tabla or not columna):
                messagebox.showwarning("Atención", "Tabla y columna son obligatorias para crear.", parent=dialog)
                return

            sql = f"CREATE INDEX {idx} ON {tabla}({columna})" if accion == "CREATE" else f"DROP INDEX {idx}"

            cursor = self.get_cursor()
            if not cursor:
                return
            try:
                cursor.execute(sql)
                messagebox.showinfo("Éxito", f"Índice {'creado' if accion == 'CREATE' else 'eliminado'} exitosamente.", parent=dialog)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error de Oracle", str(e), parent=dialog)
            finally:
                cursor.close()

        btn_box = ctk.CTkFrame(container, fg_color="transparent")
        btn_box.pack(pady=15)

        ctk.CTkButton(btn_box, text="Crear Índice", command=lambda: ejecutar("CREATE"), width=120).pack(side="left", padx=10)
        ctk.CTkButton(btn_box, text="Eliminar Índice", command=lambda: ejecutar("DROP"), width=120, fg_color="#C0392B", hover_color="#962D22").pack(side="left", padx=10)