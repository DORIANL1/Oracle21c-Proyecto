import customtkinter as ctk
from tkinter import ttk, messagebox
from database.connection import DatabaseManager

class AuditTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")
        ctk.CTkLabel(header, text="Auditoría del Sistema", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")

        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        ctk.CTkLabel(filter_frame, text="Usuario:").pack(side="left", padx=10, pady=10)
        self.entry_user = ctk.CTkEntry(filter_frame, placeholder_text="Ej. SYS")
        self.entry_user.pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(filter_frame, text="Buscar", command=self.load_audit).pack(side="left", padx=20, pady=10)

        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=2, column=0, padx=20, pady=5, sticky="nsew")
        
        cols = ("time", "user", "action", "object", "sql")
        self.tree_audit = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)
        for col, text in zip(cols, ["Fecha/Hora", "Usuario", "Acción", "Objeto", "Comando SQL"]):
            self.tree_audit.heading(col, text=text)
            self.tree_audit.column(col, anchor="center", width=120)
        self.tree_audit.column("sql", anchor="w", width=300)

        scroll_a = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_audit.yview)
        self.tree_audit.configure(yscrollcommand=scroll_a.set)
        self.tree_audit.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scroll_a.pack(side="right", fill="y", pady=10)

        if self.db.is_connected():
            self.load_audit()

    def load_audit(self):
        conn = self.db.get_connection()
        if not conn: return
        cursor = conn.cursor()

        user_filter = self.entry_user.get().strip().upper()
        try:
            for i in self.tree_audit.get_children(): self.tree_audit.delete(i)
            
            query = """
                SELECT TO_CHAR(event_timestamp, 'YYYY-MM-DD HH24:MI'), dbusername, action_name, object_name, sql_text 
                FROM unified_audit_trail 
            """
            if user_filter:
                query += f" WHERE dbusername = '{user_filter}' "
                
            query += " ORDER BY event_timestamp DESC FETCH FIRST 100 ROWS ONLY"
            
            cursor.execute(query)
            for row in cursor.fetchall():
                self.tree_audit.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Error SQL", str(e))
        finally:
            cursor.close()