import customtkinter as ctk

class SecurityTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        label = ctk.CTkLabel(
            self, 
            text="Seguridad y Control de Acceso", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        label.pack(padx=20, pady=20, anchor="w")

        info = ctk.CTkLabel(
            self, 
            text="Módulo asignado al Integrante 2.\nAquí se gestionarán los usuarios, roles y privilegios de sistema.",
            font=ctk.CTkFont(size=14)
        )
        info.pack(padx=20, pady=10, anchor="w")