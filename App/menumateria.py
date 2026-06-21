from tkinter.messagebox import showerror, showinfo
import customtkinter as ctk
import tkinter as tk

from App.utils import conectar_db, get_semestre

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AgregarMateriaView(ctk.CTk):
    def __init__(self, boleta, reload_function):
        super().__init__()
        self.reload_function = reload_function
        self.boleta = str(boleta)
        self.title("Añadir Nueva Materia")
        self.geometry("400x260")
        self.resizable(False, False)

        frame = ctk.CTkFrame(self, corner_radius=15)
        frame.pack(expand=True, fill="both", padx=5, pady=5)

        self.entry_nombre = ctk.CTkEntry(
            frame,
            placeholder_text="Nombre de la materia",
            width=300, height=40,
            font=ctk.CTkFont(size=14)
        )
        self.entry_nombre.pack(pady=(24, 10))
        self.entry_nombre.bind('<Return>', self._guardar)

        # Dificultad 1-5
        ctk.CTkLabel(
            frame,
            text="Dificultad de la materia (1=fácil, 5=muy difícil)",
            font=ctk.CTkFont(size=12)
        ).pack()
        self.dificultad_menu = ctk.CTkOptionMenu(
            frame,
            values=[str(i) for i in range(1, 6)],
            width=200, height=36
        )
        self.dificultad_menu.set("3")
        self.dificultad_menu.pack(pady=(4, 14))

        ctk.CTkButton(
            frame,
            text="Guardar Materia",
            width=30, height=45,
            command=self._guardar,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(0, 16))

    def _guardar(self, *args, **kwargs):
        nombre = self.entry_nombre.get().strip().lower().capitalize()
        if not nombre:
            return showerror("Error", "Ingresa un nombre de materia válido.")

        semestre = get_semestre(self.boleta)
        if not semestre:
            return showerror("Error", "Completa la encuesta base antes de añadir una materia.")

        dificultad = int(self.dificultad_menu.get())

        try:
            conn = conectar_db()
            cur = conn.cursor()

            # Verificar duplicado
            cur.execute(
                "SELECT nombre FROM materias WHERE usuario_boleta = %s AND nombre = %s AND semestre = %s",
                (self.boleta, nombre, semestre)
            )
            if cur.fetchone():
                conn.close()
                return showerror("Error", "Ya tienes esta materia registrada en este semestre.")

            cur.execute(
                "INSERT INTO materias (usuario_boleta, semestre, nombre, dificultad) VALUES (%s, %s, %s, %s)",
                (self.boleta, semestre, nombre, dificultad)
            )
            conn.commit()
            conn.close()

            showinfo("Éxito", f"Materia '{nombre}' guardada con éxito.")
            self.entry_nombre.delete(0, tk.END)
            self.dificultad_menu.set("3")
            self.reload_function()
        except Exception as e:
            showerror("Error", f"Se produjo un error: {e}")


if __name__ == "__main__":
    app = AgregarMateriaView(boleta='0', reload_function=lambda: None)
    app.mainloop()
