import tkinter.messagebox as messagebox
import customtkinter as ctk
from database.connection import DatabaseManager
from views.tab_tablespaces import TablespacesTab
from views.tab_security import SecurityTab
from views.tab_tuning import TuningTab
from views.tab_performance import PerformanceTab
from views.tab_audit import AuditTab
from views.tab_backups import BackupsTab

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AdminApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Oracle21c-Proyecto - Database Administration Tool (EIF-402)")
        self.geometry("1100x680")
        self.minsize(950, 600)

        self.db = DatabaseManager()

        # Configuración del grid principal (1 fila, 2 columnas)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.setup_sidebar()
        self.setup_main_area()
        self.setup_status_bar()

        # Iniciar en la pantalla de conexión
        self.show_view("connection")

    def setup_sidebar(self):
        """Barra lateral fija de navegación."""
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Oracle 21c XE\nAdmin Tool", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 20))

        # Botones de navegación
        self.btn_nav_conn = ctk.CTkButton(self.sidebar_frame, text="Conexión", command=lambda: self.show_view("connection"))
        self.btn_nav_conn.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        self.btn_nav_tbs = ctk.CTkButton(self.sidebar_frame, text="Tablespaces", command=lambda: self.show_view("tablespaces"), state="disabled")
        self.btn_nav_tbs.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.btn_nav_sec = ctk.CTkButton(self.sidebar_frame, text="Seguridad", command=lambda: self.show_view("security"), state="disabled")
        self.btn_nav_sec.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        self.btn_nav_tun = ctk.CTkButton(self.sidebar_frame, text="Tuning SQL", command=lambda: self.show_view("tuning"), state="disabled")
        self.btn_nav_tun.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

        self.btn_nav_perf = ctk.CTkButton(self.sidebar_frame, text="Performance", command=lambda: self.show_view("performance"), state="disabled")
        self.btn_nav_perf.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        self.btn_nav_aud = ctk.CTkButton(self.sidebar_frame, text="Auditoría", command=lambda: self.show_view("audit"), state="disabled")
        self.btn_nav_aud.grid(row=6, column=0, padx=20, pady=5, sticky="ew")

        self.btn_nav_bkp = ctk.CTkButton(self.sidebar_frame, text="Respaldos", command=lambda: self.show_view("backups"), state="disabled")
        self.btn_nav_bkp.grid(row=7, column=0, padx=20, pady=5, sticky="ew")

        # Control de desconexión
        self.btn_disconnect = ctk.CTkButton(
            self.sidebar_frame, 
            text="Desconectar", 
            fg_color="#D32F2F", 
            hover_color="#9A0007", 
            command=self.handle_disconnect,
            state="disabled"
        )
        self.btn_disconnect.grid(row=9, column=0, padx=20, pady=20, sticky="ew")

    def setup_main_area(self):
        """Área central de contenido dinámico."""
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Diccionario de vistas
        self.views = {
            "connection": self.create_connection_view(),
            "tablespaces": TablespacesTab(self.main_container),
            "security": SecurityTab(self.main_container),
            "tuning": TuningTab(self.main_container),
            "performance": PerformanceTab(self.main_container),
            "audit": AuditTab(self.main_container),
            "backups": BackupsTab(self.main_container)
        }

    def create_connection_view(self):
        """Formulario de credenciales de conexión."""
        frame = ctk.CTkFrame(self.main_container)
        
        card = ctk.CTkFrame(frame, width=450)
        card.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(card, text="Iniciar Conexión a Oracle 21c XE", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(padx=30, pady=(25, 20))

        # Host y Puerto
        self.entry_host = ctk.CTkEntry(card, placeholder_text="Host", width=320)
        self.entry_host.insert(0, "localhost")
        self.entry_host.pack(padx=30, pady=6)

        self.entry_port = ctk.CTkEntry(card, placeholder_text="Puerto", width=320)
        self.entry_port.insert(0, "1521")
        self.entry_port.pack(padx=30, pady=6)

        # Servicio (PDB)
        self.entry_service = ctk.CTkEntry(card, placeholder_text="Servicio / PDB", width=320)
        self.entry_service.insert(0, "XEPDB1")
        self.entry_service.pack(padx=30, pady=6)

        # Usuario y Password
        self.entry_user = ctk.CTkEntry(card, placeholder_text="Usuario (ej. SYS o SYSTEM)", width=320)
        self.entry_user.insert(0, "SYS")
        self.entry_user.pack(padx=30, pady=6)

        self.entry_pass = ctk.CTkEntry(card, placeholder_text="Contraseña", show="*", width=320)
        self.entry_pass.pack(padx=30, pady=6)

        # Checkbox SYSDBA
        self.check_sysdba = ctk.CTkCheckBox(card, text="Conectar como SYSDBA")
        self.check_sysdba.select()  # Seleccionado por defecto para SYS
        self.check_sysdba.pack(padx=30, pady=12)

        # Botón de Conectar
        self.btn_connect = ctk.CTkButton(card, text="Conectar a la Base de Datos", width=320, command=self.handle_connect)
        self.btn_connect.pack(padx=30, pady=(10, 25))

        return frame

    def setup_status_bar(self):
        """Barra de estado inferior horizontal."""
        self.status_bar = ctk.CTkFrame(self, height=28, corner_radius=0)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.status_label = ctk.CTkLabel(
            self.status_bar, 
            text="Estado: Desconectado", 
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=15, pady=2)

    def show_view(self, view_name):
        """Muestra la vista seleccionada ocultando las demás."""
        for v in self.views.values():
            v.grid_forget()
        self.views[view_name].grid(row=0, column=0, sticky="nsew")

    def handle_connect(self):
        """Gestiona el intento de conexión y habilita los módulos si es exitoso."""
        host = self.entry_host.get().strip()
        port = self.entry_port.get().strip()
        service = self.entry_service.get().strip()
        user = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        is_sysdba = bool(self.check_sysdba.get())

        if not all([host, port, service, user, password]):
            messagebox.showwarning("Campos vacíos", "Por favor completa todos los campos de conexión.")
            return

        self.btn_connect.configure(text="Conectando...", state="disabled")
        self.update()

        success, message = self.db.connect(host, port, service, user, password, is_sysdba)

        self.btn_connect.configure(text="Conectar a la Base de Datos", state="normal")

        if success:
            messagebox.showinfo("Éxito", message)
            self.status_label.configure(
                text=f"Estado: Conectado a {service} | Usuario: {self.db.user} ({self.db.role}) | Host: {host}:{port}"
            )
            self.set_module_buttons_state("normal")
            self.btn_disconnect.configure(state="normal")
            self.show_view("tablespaces")
        else:
            messagebox.showerror("Error de Conexión", message)
            self.status_label.configure(text="Estado: Error de conexión")

    def handle_disconnect(self):
        """Cierra la sesión y bloquea la navegación de módulos."""
        self.db.disconnect()
        self.set_module_buttons_state("disabled")
        self.btn_disconnect.configure(state="disabled")
        self.status_label.configure(text="Estado: Desconectado")
        self.show_view("connection")
        messagebox.showinfo("Desconexión", "Sesión cerrada correctamente.")

    def set_module_buttons_state(self, state):
        """Habilita o deshabilita los botones de los módulos."""
        self.btn_nav_tbs.configure(state=state)
        self.btn_nav_sec.configure(state=state)
        self.btn_nav_tun.configure(state=state)
        self.btn_nav_perf.configure(state=state)
        self.btn_nav_aud.configure(state=state)
        self.btn_nav_bkp.configure(state=state)


if __name__ == "__main__":
    app = AdminApp()
    app.mainloop()