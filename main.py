import tkinter.messagebox as messagebox
import customtkinter as ctk
from database.connection import DatabaseManager
from views.ui_helpers import configure_treeview_style
from views.tab_tablespaces import TablespacesTab
from views.tab_security import SecurityTab
from views.tab_tuning import TuningTab
from views.tab_performance import PerformanceTab
from views.tab_audit import AuditTab
from views.tab_backups import BackupsTab

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "canvas": "#0B1220",
    "sidebar": "#0D1625",
    "surface": "#111D2D",
    "surface_elevated": "#172538",
    "border": "#24364D",
    "text": "#F4F7FB",
    "muted": "#91A1B5",
    "accent": "#E34B5F",
    "accent_hover": "#C9384C",
    "blue": "#4C9AFF",
}


class AdminApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Oracle21c-Proyecto - Database Administration Tool (EIF-402)")
        self.geometry("1160x740")
        self.minsize(1050, 650)
        self.configure(fg_color=COLORS["canvas"])

        self.db = DatabaseManager()
        self.active_view = "connection"

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
        self.sidebar_frame = ctk.CTkFrame(
            self,
            width=232,
            corner_radius=0,
            fg_color=COLORS["sidebar"],
            border_width=0,
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        self.sidebar_frame.grid_rowconfigure(9, weight=1)

        brand = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=22, pady=(25, 30))
        brand.grid_columnconfigure(1, weight=1)

        brand_mark = ctk.CTkFrame(
            brand,
            width=42,
            height=42,
            corner_radius=12,
            fg_color=COLORS["accent"],
        )
        brand_mark.grid(row=0, column=0, rowspan=2, padx=(0, 12))
        brand_mark.grid_propagate(False)
        ctk.CTkLabel(
            brand_mark,
            text="O",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color="#FFFFFF",
        ).place(relx=0.5, rely=0.48, anchor="center")

        ctk.CTkLabel(
            brand,
            text="ORACLE 21c XE",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=1, sticky="sw")
        ctk.CTkLabel(
            brand,
            text="DATABASE ADMIN",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=COLORS["muted"],
            anchor="w",
        ).grid(row=1, column=1, sticky="nw", pady=(2, 0))

        ctk.CTkLabel(
            self.sidebar_frame,
            text="ESPACIO DE TRABAJO",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color="#65768D",
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 9))

        nav_items = (
            ("connection", "Conexión", "btn_nav_conn"),
            ("tablespaces", "Tablespaces", "btn_nav_tbs"),
            ("security", "Seguridad", "btn_nav_sec"),
            ("tuning", "Tuning SQL", "btn_nav_tun"),
            ("performance", "Performance", "btn_nav_perf"),
            ("audit", "Auditoría", "btn_nav_aud"),
            ("backups", "Respaldos", "btn_nav_bkp"),
        )
        self.navigation_buttons = {}
        for row, (view_name, label, attribute) in enumerate(nav_items, start=2):
            button = ctk.CTkButton(
                self.sidebar_frame,
                text=label,
                anchor="w",
                height=42,
                corner_radius=9,
                fg_color="transparent",
                hover_color=COLORS["surface_elevated"],
                text_color=COLORS["muted"],
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                command=lambda name=view_name: self.show_view(name),
                state="normal" if view_name == "connection" else "disabled",
            )
            button.grid(row=row, column=0, padx=14, pady=3, sticky="ew")
            setattr(self, attribute, button)
            self.navigation_buttons[view_name] = button

        ctk.CTkFrame(
            self.sidebar_frame,
            height=1,
            fg_color=COLORS["border"],
        ).grid(row=9, column=0, sticky="ew", padx=20, pady=(10, 12))

        self.sidebar_connection = ctk.CTkLabel(
            self.sidebar_frame,
            text="●  SIN CONEXIÓN",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#8998AA",
            anchor="w",
        )
        self.sidebar_connection.grid(row=10, column=0, sticky="ew", padx=22, pady=(0, 8))

        self.btn_disconnect = ctk.CTkButton(
            self.sidebar_frame,
            text="Desconectar sesión",
            height=38,
            corner_radius=9,
            fg_color="#321E2A",
            hover_color="#482331",
            text_color="#F49AA5",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.handle_disconnect,
            state="disabled"
        )
        self.btn_disconnect.grid(row=11, column=0, padx=16, pady=(0, 20), sticky="ew")

    def setup_main_area(self):
        """Área central de contenido dinámico."""
        configure_treeview_style(self)

        self.main_container = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=COLORS["canvas"],
        )
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=(0, 0), pady=0)
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
        frame = ctk.CTkFrame(
            self.main_container,
            fg_color=COLORS["canvas"],
        )
        card = ctk.CTkFrame(
            frame,
            fg_color=COLORS["surface"],
            corner_radius=20,
            border_width=1,
            border_color=COLORS["border"],
        )
        card.place(relx=0.5, rely=0.49, anchor="center")
        card.grid_columnconfigure(0, minsize=285)
        card.grid_columnconfigure(1, minsize=410)

        hero = ctk.CTkFrame(card, fg_color="transparent")
        hero.grid(row=0, column=0, sticky="nsew", padx=(30, 20), pady=32)

        ctk.CTkLabel(
            hero,
            text="DATABASE\nOPERATIONS",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=COLORS["blue"],
            justify="left",
        ).pack(anchor="w", pady=(0, 18))
        ctk.CTkLabel(
            hero,
            text="Administra tu\nbase de datos\ncon claridad.",
            font=ctk.CTkFont(family="Segoe UI", size=27, weight="bold"),
            text_color=COLORS["text"],
            justify="left",
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            hero,
            text="Una consola central para Oracle 21c XE: almacenamiento, seguridad, rendimiento y recuperación.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["muted"],
            justify="left",
            wraplength=250,
        ).pack(anchor="w", pady=(14, 24))

        for label in ("ALMACENAMIENTO", "CONTROL DE ACCESO", "DATA PUMP"):
            item = ctk.CTkFrame(
                hero,
                fg_color=COLORS["surface_elevated"],
                corner_radius=7,
            )
            item.pack(anchor="w", fill="x", pady=4)
            ctk.CTkLabel(
                item,
                text=f"  {label}",
                font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
                text_color="#B7C5D6",
                anchor="w",
                height=27,
            ).pack(fill="x", padx=8)

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.grid(row=0, column=1, sticky="nsew", padx=(18, 30), pady=30)
        form.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            form,
            text="Iniciar sesión",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        ctk.CTkLabel(
            form,
            text="Introduce las credenciales de tu instancia.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS["muted"],
            anchor="w",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 17))

        self.entry_host = self._connection_field(form, "HOST", "localhost", 2, 0)
        self.entry_port = self._connection_field(form, "PUERTO", "1521", 2, 1)
        self.entry_service = self._connection_field(form, "SERVICIO / PDB", "XEPDB1", 4, 0, 2)
        self.entry_user = self._connection_field(form, "USUARIO", "SYS", 6, 0, 2)
        self.entry_pass = self._connection_field(
            form,
            "CONTRASEÑA",
            "Contraseña de Oracle",
            8,
            0,
            2,
            show="*",
        )

        self.check_sysdba = ctk.CTkCheckBox(card, text="Conectar como SYSDBA")
        self.check_sysdba.configure(
            text="Conectar con privilegios SYSDBA",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#C5D0DE",
        )
        self.check_sysdba.select()
        self.check_sysdba.grid(row=1, column=1, sticky="w", padx=18, pady=(0, 8))

        self.btn_connect = ctk.CTkButton(
            form,
            text="Conectar a Oracle",
            height=43,
            corner_radius=9,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self.handle_connect,
        )
        self.btn_connect.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        return frame

    @staticmethod
    def _connection_field(parent, label, placeholder, row, column, columnspan=1, show=None):
        wrapper = ctk.CTkFrame(parent, fg_color="transparent")
        wrapper.grid(
            row=row,
            column=column,
            columnspan=columnspan,
            sticky="ew",
            padx=(0, 8) if column == 0 and columnspan == 1 else (0, 0),
            pady=(0, 11),
        )
        wrapper.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            wrapper,
            text=label,
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color="#A7B6C8",
            anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))
        entry = ctk.CTkEntry(
            wrapper,
            placeholder_text=placeholder,
            height=38,
            corner_radius=8,
            fg_color="#0C1522",
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            placeholder_text_color="#718198",
            show=show,
        )
        entry.grid(row=1, column=0, sticky="ew")
        if label == "HOST":
            entry.insert(0, "localhost")
        elif label == "PUERTO":
            entry.insert(0, "1521")
        elif label == "SERVICIO / PDB":
            entry.insert(0, "XEPDB1")
        elif label == "USUARIO":
            entry.insert(0, "SYS")
        return entry

    def setup_status_bar(self):
        """Barra de estado inferior horizontal."""
        self.status_bar = ctk.CTkFrame(
            self,
            height=34,
            corner_radius=0,
            fg_color="#080E18",
        )
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="●  Desconectado",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=COLORS["muted"],
        )
        self.status_label.pack(side="left", padx=18, pady=2)
        ctk.CTkLabel(
            self.status_bar,
            text="ORACLE 21c XE  ·  ADMIN CONSOLE",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color="#63748A",
        ).pack(side="right", padx=18, pady=2)

    def show_view(self, view_name):
        """Muestra la vista seleccionada ocultando las demás."""
        for v in self.views.values():
            v.grid_forget()
        self.views[view_name].grid(row=0, column=0, sticky="nsew")
        self.active_view = view_name
        for name, button in self.navigation_buttons.items():
            if name == view_name:
                button.configure(
                    fg_color="#1B2B40",
                    text_color=COLORS["text"],
                )
            else:
                button.configure(
                    fg_color="transparent",
                    text_color=COLORS["muted"],
                )
        if view_name != "connection" and self.db.is_connected():
            refresh = {
                "tablespaces": self.views["tablespaces"].load_data,
                "security": self.views["security"].load_users,
                "performance": self.views["performance"].load_data,
                "audit": self.views["audit"].load_audit,
                "backups": self.views["backups"].refresh_all_data,
            }.get(view_name)
            if refresh:
                refresh()

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
                text=f"●  Conectado  ·  {self.db.user} ({self.db.role})  ·  {host}:{port}/{service}",
                text_color="#6DD6A5",
            )
            self.sidebar_connection.configure(
                text=f"●  CONECTADO · {self.db.user}",
                text_color="#6DD6A5",
            )
            self.set_module_buttons_state("normal")
            self.btn_disconnect.configure(state="normal")
            self.show_view("tablespaces")
        else:
            messagebox.showerror("Error de Conexión", message)
            self.status_label.configure(
                text="●  Error de conexión",
                text_color="#F28C98",
            )

    def handle_disconnect(self):
        """Cierra la sesión y bloquea la navegación de módulos."""
        self.db.disconnect()
        self.set_module_buttons_state("disabled")
        self.btn_disconnect.configure(state="disabled")
        self.status_label.configure(
            text="●  Desconectado",
            text_color=COLORS["muted"],
        )
        self.sidebar_connection.configure(
            text="●  SIN CONEXIÓN",
            text_color="#8998AA",
        )
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
        for name, button in self.navigation_buttons.items():
            if name != "connection":
                button.configure(
                    text_color=COLORS["muted"] if state == "normal" else "#59677A"
                )


if __name__ == "__main__":
    app = AdminApp()
    app.mainloop()