import customtkinter as ctk
from tkinter import ttk, messagebox
from database.connection import DatabaseManager

class PerformanceTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="ew")
        ctk.CTkLabel(header, text="Monitoreo de Rendimiento", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")
        ctk.CTkButton(header, text="Actualizar", width=100, command=self.load_data).pack(side="right")

        self.tabs_view = ctk.CTkTabview(self)
        self.tabs_view.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")
        tab_sessions = self.tabs_view.add("Sesiones Activas")
        tab_locks = self.tabs_view.add("Bloqueos de Objetos")

        cols_sess = ("sid", "serial", "user", "status", "machine", "program")
        self.tree_sess = ttk.Treeview(tab_sessions, columns=cols_sess, show="headings", height=15)
        for col, text in zip(cols_sess, ["SID", "Serial#", "Usuario", "Estado", "Máquina", "Programa"]):
            self.tree_sess.heading(col, text=text)
            self.tree_sess.column(col, anchor="center", width=120)
        
        scroll_s = ttk.Scrollbar(tab_sessions, orient="vertical", command=self.tree_sess.yview)
        self.tree_sess.configure(yscrollcommand=scroll_s.set)
        self.tree_sess.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scroll_s.pack(side="right", fill="y", pady=10)

        cols_lock = ("sid", "user", "object", "locked_mode")
        self.tree_locks = ttk.Treeview(tab_locks, columns=cols_lock, show="headings", height=15)
        for col, text in zip(cols_lock, ["SID", "Usuario", "Objeto Bloqueado", "Modo Bloqueo"]):
            self.tree_locks.heading(col, text=text)
            self.tree_locks.column(col, anchor="center", width=150)
            
        scroll_l = ttk.Scrollbar(tab_locks, orient="vertical", command=self.tree_locks.yview)
        self.tree_locks.configure(yscrollcommand=scroll_l.set)
        self.tree_locks.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scroll_l.pack(side="right", fill="y", pady=10)

        if self.db.is_connected():
            self.load_data()

    def get_cursor(self):
        conn = self.db.get_connection()
        if not conn:
            return None
        return conn.cursor()

    def load_data(self):
        cursor = self.get_cursor()
        if not cursor: return

        try:
            for i in self.tree_sess.get_children(): self.tree_sess.delete(i)
            for i in self.tree_locks.get_children(): self.tree_locks.delete(i)

            cursor.execute("""
                SELECT sid, serial#, username, status, machine, program 
                FROM v$session WHERE type != 'BACKGROUND' AND username IS NOT NULL
            """)
            for row in cursor.fetchall():
                self.tree_sess.insert("", "end", values=row)

            cursor.execute("""
                SELECT s.sid, s.username, o.object_name, l.locked_mode
                FROM v$locked_object l
                JOIN dba_objects o ON l.object_id = o.object_id
                JOIN v$session s ON l.session_id = s.sid
            """)
            for row in cursor.fetchall():
                self.tree_locks.insert("", "end", values=row)
                
        except Exception as e:
            messagebox.showerror("Error SQL", str(e))
        finally:
            cursor.close()