import customtkinter as ctk

class AuditTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        label = ctk.CTkLabel(
            self, 
            text="Auditoría del Sistema", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        label.pack(padx=20, pady=20, anchor="w")

        info = ctk.CTkLabel(
            self, 
            text="Módulo asignado al Integrante 3.\nConsultas y filtros sobre UNIFIED_AUDIT_TRAIL.",
            font=ctk.CTkFont(size=14)
        )
        info.pack(padx=20, pady=10, anchor="w")