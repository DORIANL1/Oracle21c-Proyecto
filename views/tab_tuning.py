import customtkinter as ctk

class TuningTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        label = ctk.CTkLabel(
            self, 
            text="Tuning y Optimización de Consultas", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        label.pack(padx=20, pady=20, anchor="w")

        info = ctk.CTkLabel(
            self, 
            text="Módulo asignado al Integrante 3.\nAquí se procesará EXPLAIN PLAN, DBMS_STATS y gestión de índices.",
            font=ctk.CTkFont(size=14)
        )
        info.pack(padx=20, pady=10, anchor="w")