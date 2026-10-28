import customtkinter as ctk

class PerformanceTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        label = ctk.CTkLabel(
            self, 
            text="Monitoreo de Rendimiento (Performance)", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        label.pack(padx=20, pady=20, anchor="w")

        info = ctk.CTkLabel(
            self, 
            text="Módulo asignado al Integrante 3.\nInspección de V$SESSION y bloqueos en V$LOCKED_OBJECT.",
            font=ctk.CTkFont(size=14)
        )
        info.pack(padx=20, pady=10, anchor="w")