import customtkinter as ctk

class BackupsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        label = ctk.CTkLabel(
            self, 
            text="Respaldos y Recuperación (Oracle Data Pump)", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        label.pack(padx=20, pady=20, anchor="w")

        info = ctk.CTkLabel(
            self, 
            text="Módulo asignado al Integrante 4.\nEjecución de expdp / impdp, salida en tiempo real y DBA_DIRECTORIES.",
            font=ctk.CTkFont(size=14)
        )
        info.pack(padx=20, pady=10, anchor="w")