
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

PREGUNTAS = [
    "¿En donde naciste?",
    "¿Nombre de tu personaje favorito?",
    "¿Nombre de tu primera mascota?",
    "¿Nombre de tu mejor amigo?",
    "¿Comida favorita?",
]


class RecoverPasswordApp(ctk.CTk):

    BG       = "#1c1c1c"
    CARD     = "#2b2b2b"
    ENTRY    = "#3a3a3a"
    BTN      = "#3d8ef0"
    BTN_HOV  = "#2e7de0"
    TXT      = "#e0e0e0"
    PH       = "#888888"

    def __init__(self):
        super().__init__()
        self.title("Recuperacion de ContraseÃ±a")
        self.geometry("380x360")
        self.resizable(False, False)
        self.configure(fg_color=self.BG)
        self._build_ui()

    def _build_ui(self):

        # â”€â”€ Tarjeta central â”€â”€
        card = ctk.CTkFrame(
            self,
            fg_color=self.CARD,
            corner_radius=14,
        )
        card.pack(padx=28, pady=30, fill="both", expand=True)

        # Titulo
        ctk.CTkLabel(
            card,
            text="Recuperacion de ContraseÃ±a",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=self.TXT,
        ).pack(pady=(28, 24))

        # â”€â”€ Campos â”€â”€
        frame = ctk.CTkFrame(card, fg_color="transparent")
        frame.pack(padx=24, fill="x")

        # Dropdown pregunta
        self.combo_pregunta = ctk.CTkOptionMenu(
            frame,
            values=PREGUNTAS,
            dynamic_resizing=False,
            height=42,
            corner_radius=8,
            fg_color=self.ENTRY,
            button_color=self.ENTRY,
            button_hover_color="#4a4a4a",
            text_color=self.PH,
            font=ctk.CTkFont(size=13),
        )
        self.combo_pregunta.pack(fill="x", pady=(0, 10))
        self.combo_pregunta.set("Pregunta de seguridad")

        # Respuesta
        self.entry_respuesta = ctk.CTkEntry(
            frame,
            placeholder_text="Respuesta",
            placeholder_text_color=self.PH,
            fg_color=self.ENTRY,
            border_color=self.ENTRY,
            text_color=self.TXT,
            height=42,
            corner_radius=8,
            font=ctk.CTkFont(size=13),
        )
        self.entry_respuesta.pack(fill="x", pady=(0, 0))

        # â”€â”€ Boton Recuperar â”€â”€
        ctk.CTkButton(
            card,
            text="Recuperar",
            fg_color=self.BTN,
            hover_color=self.BTN_HOV,
            text_color="white",
            height=44,
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: None,
        ).pack(padx=24, pady=24, fill="x")


if __name__ == "__main__":
    app = RecoverPasswordApp()
    app.mainloop()
    