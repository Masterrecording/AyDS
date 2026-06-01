import customtkinter as ctk

# Configuración de apariencia
# ctk.set_appearance_mode("dark")
# ctk.set_default_color_theme("blue")

class UpdatePassWindow(ctk.CTk):
    def __init__(self, usuario, **kwargs):
        super().__init__(**kwargs)
        self.app = ctk.CTk()
        self.app.title("Actualizar Contraseña")
        self.app.geometry("480x380")
        self.app.resizable(False, False)
        self.usuario = usuario
    
    def verify_password(self):
        password1 = self.entry_password.get()
        password2 = self.entry_confirm.get()

        if not password1 or not password2: return self.label_error.configure(text="Porfavor completa ambos campos.", text_color="orange")
        if len(password1) < 4: return self.label_error.configure(text="PoLa contraseña debe tener al menos 4 caracteres.", text_color="orange")
        if password1 != password2: self.label_error.configure(text="Las contraseñas no coinciden.", text_color="orange")

        
        
        self.label_error.configure(text="Contraseña actualizada correctamente", text_color="green")

    def show(self):
        self.frame = ctk.CTkFrame(self.app, corner_radius=16)
        self.frame.pack(expand=True, fill="both", padx=30, pady=30)

        # Título
        self.label_titulo = ctk.CTkLabel(
            self.frame,
            text="Actualizar Contraseña",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
        )
        self.label_titulo.pack(pady=(28, 20))

        # Entry contraseña nueva
        self.entry_password = ctk.CTkEntry(
            self.frame,
            placeholder_text="Nueva contraseña",
            show="*",
            width=260,
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=14),
        )
        self.entry_password.pack(pady=(0, 12))

        # Entry confirmar contraseña
        self.entry_confirm = ctk.CTkEntry(
            self.frame,
            placeholder_text="Confirmar contraseña",
            show="*",
            width=260,
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=14),
        )
        self.entry_confirm.pack(pady=(0, 12))

        # Label de error (oculto inicialmente)
        self.label_error = ctk.CTkLabel(
            self.frame,
            text="",
            font=ctk.CTkFont(size=13),
            wraplength=240,
        )
        self.label_error.pack(pady=(0, 10))



        # Botón confirmar
        self.boton_confirmar = ctk.CTkButton(
            self.frame,
            text="Confirmar",
            width=260,
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.verify_password,
        )
        self.boton_confirmar.pack(pady=(4, 28))

        self.app.mainloop()