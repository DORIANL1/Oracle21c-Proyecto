from tkinter import messagebox, ttk

COLORS = {
    "canvas": "#0B1220",
    "surface": "#111D2D",
    "surface_elevated": "#172538",
    "border": "#24364D",
    "text": "#F4F7FB",
    "muted": "#91A1B5",
    "accent": "#E34B5F",
    "blue": "#4C9AFF",
}


def configure_treeview_style(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(
        "Treeview",
        background="#101A29",
        foreground="#DCE5F0",
        fieldbackground="#101A29",
        rowheight=30,
        borderwidth=0,
        font=("Segoe UI", 10),
    )
    style.configure(
        "Treeview.Heading",
        background="#1A2A3F",
        foreground="#ffffff",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
    )
    style.map(
        "Treeview",
        background=[("selected", "#244E78")],
        foreground=[("selected", "#ffffff")],
    )


def show_operation_error(parent, operation, error):
    detail = str(error).strip() or "Oracle no proporcionó información adicional."
    upper_detail = detail.upper()

    if "ORA-01031" in upper_detail:
        explanation = "La cuenta conectada no tiene los privilegios necesarios."
    elif "ORA-00942" in upper_detail:
        explanation = "El objeto no existe o la cuenta no tiene permiso para consultarlo."
    elif "ORA-00904" in upper_detail:
        explanation = "La consulta usa una columna o un nombre que Oracle no reconoce."
    elif "ORA-12154" in upper_detail or "ORA-12514" in upper_detail:
        explanation = "No se pudo localizar el servicio Oracle indicado. Revisa host, puerto y servicio."
    else:
        explanation = "Revisa la conexión y los permisos de la cuenta antes de volver a intentarlo."

    messagebox.showerror(
        "No se pudo completar la operación",
        f"No fue posible {operation}.\n{explanation}\n\nDetalle técnico:\n{detail}",
        parent=parent,
    )
