import customtkinter as ctk

# Configuración de apariencia
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def verify_password():
    password1 = entry_password.get()
    password2 = entry_confirm.get()

    if not password1 or not password2:
        mostrar_error("Por favor completa ambos campos.")
        return

    if len(password1) < 4:
        mostrar_error("La contraseña debe tener al menos 4 caracteres.")
        return

    if password1 != password2:
        mostrar_error("Las contraseñas no coinciden.")
        return

    mostrar_exito("Contraseña actualizada correctamente.")


def mostrar_error(mensaje):
    label_error.configure(text=mensaje, text_color="orange")


def mostrar_exito(mensaje):
    label_error.configure(text=mensaje, text_color="green")



# Ventana principal
app = ctk.CTk()
app.title("Actualizar Contraseña")
app.geometry("480x380")
app.resizable(False, False)

# Frame central
frame = ctk.CTkFrame(app, corner_radius=16)
frame.pack(expand=True, fill="both", padx=30, pady=30)

# Título
label_titulo = ctk.CTkLabel(
    frame,
    text="Actualizar Contraseña",
    font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
)
label_titulo.pack(pady=(28, 20))

# Entry contraseña nueva
entry_password = ctk.CTkEntry(
    frame,
    placeholder_text="Nueva contraseña",
    show="*",
    width=260,
    height=42,
    corner_radius=10,
    font=ctk.CTkFont(size=14),
)
entry_password.pack(pady=(0, 12))

# Entry confirmar contraseña
entry_confirm = ctk.CTkEntry(
    frame,
    placeholder_text="Confirmar contraseña",
    show="*",
    width=260,
    height=42,
    corner_radius=10,
    font=ctk.CTkFont(size=14),
)
entry_confirm.pack(pady=(0, 12))

# Label de error (oculto inicialmente)
label_error = ctk.CTkLabel(
    frame,
    text="",
    font=ctk.CTkFont(size=13),
    wraplength=240,
)
label_error.pack(pady=(0, 10))



# Botón confirmar
boton_confirmar = ctk.CTkButton(
    frame,
    text="Confirmar",
    width=260,
    height=42,
    corner_radius=10,
    font=ctk.CTkFont(size=14, weight="bold"),
    command=verify_password,
)
boton_confirmar.pack(pady=(4, 28))

app.mainloop()