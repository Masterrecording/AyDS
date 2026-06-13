import customtkinter as ctk
import pymysql as sql
import json
from tkinter.messagebox import showinfo, showerror

DATABASE = json.loads(open('settings.json', 'r', encoding='utf-8').read())

class RecoverPasswordWindow(ctk.CTk):
    def __init__(self,):
        super().__init__()
        self.BG = "#1c1c1c"
        self.CARD = "#2b2b2b"
        self.ENTRY = "#3a3a3a"
        self.BTN = "#3d8ef0"
        self.BTN_HOV = "#2e7de0"
        self.TXT = "#e0e0e0"
        self.PH = "#888888"
        self.title("Recuperacion de Contraseña")
        self.geometry("380x400")
        self.resizable(False, False)
        self.configure(fg_color=self.BG)
        self.PREGUNTAS = self.recibir_preguntas()

    def conectar_db(self):
        return sql.connect(
            host=DATABASE["host"],
            user=DATABASE["user"],
            password=DATABASE["password"],
            database=DATABASE["database"]
        )

    def recibir_preguntas(self):
        conn = self.conectar_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM preguntas_recuperacion")
        response = cur.fetchall()

        preguntas = [pregunta for _, pregunta in response]
        conn.close()
        return preguntas

    def actualizar_contraseña(self, usuario):
        from App.updatepass import UpdatePassWindow
        self.destroy()
        UpdatePassWindow(usuario).show()

    def recuperar(self, *args, **kwargs):
        usuario = self.entry_usuario.get().strip().lower()
        pregunta = self.combo_pregunta.get()
        respuesta = self.entry_respuesta.get().strip().lower()
        
        if not usuario: return showerror("Error", "Ingresa un usuario válido")
        if pregunta == "Pregunta de seguridad": return showerror("Error", "Selecciona tu pregunta de recuperación")
        if not respuesta: return showerror("Error", "Ingresa una respuesta válida")
        try:
            conn = self.conectar_db()
            cur = conn.cursor()
            cur.execute("SELECT * from usuario where nombre = %s", args=(usuario,))
            response = list(cur.fetchall()[0])
            if self.PREGUNTAS.index(pregunta)+1 == response[5] and response[4] == respuesta:
                showinfo("Éxito", "Hemos detectado tu cuenta y validado tu pregunta de recuperación")
                self.actualizar_contraseña(usuario)
            else: showerror("Error", "Los datos que has ingresado son incorrectos o el usuario no existe.")
        except IndexError as e:
            showerror("Error", "Los datos que has ingresado son incorrectos o el usuario no existe.")
        

    def show(self):
        card = ctk.CTkFrame(self, fg_color=self.CARD, corner_radius=14)
        card.pack(padx=28, pady=30, fill="both", expand=True)

        ctk.CTkLabel(card, text="Recuperacion de Contraseña", font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"), text_color=self.TXT,).pack(pady=(28, 24))

        frame = ctk.CTkFrame(card, fg_color="transparent")
        frame.pack(padx=24, fill="x")

        self.entry_usuario = ctk.CTkEntry(frame, placeholder_text="Usuario", placeholder_text_color=self.PH, fg_color=self.ENTRY, border_color=self.ENTRY, text_color=self.TXT, height=42, corner_radius=8, font=ctk.CTkFont(size=13))
        self.entry_usuario.pack(fill="x", pady=(0,30))
        self.entry_usuario.bind('<Return>', self.recuperar)

        self.combo_pregunta = ctk.CTkOptionMenu(frame, values=self.PREGUNTAS, dynamic_resizing=False, height=42, corner_radius=8, fg_color=self.ENTRY, button_color=self.ENTRY, button_hover_color="#4a4a4a", text_color=self.PH, font=ctk.CTkFont(size=13),)
        self.combo_pregunta.pack(fill="x", pady=(0, 10))
        self.combo_pregunta.set("Pregunta de seguridad")

        self.entry_respuesta = ctk.CTkEntry(frame, placeholder_text="Respuesta", placeholder_text_color=self.PH, fg_color=self.ENTRY, border_color=self.ENTRY, text_color=self.TXT, height=42, corner_radius=8, font=ctk.CTkFont(size=13))
        self.entry_respuesta.pack(fill="x", pady=(0, 0))
        self.entry_respuesta.bind('<Return>', self.recuperar)

        self.send_button = ctk.CTkButton(card, text="Recuperar", fg_color=self.BTN, hover_color=self.BTN_HOV, text_color="white", height=44, corner_radius=8, font=ctk.CTkFont(size=14, weight="bold"), command=self.recuperar,)
        self.send_button.pack(padx=24, pady=24, fill="x")
        self.mainloop()


if __name__ == "__main__":
    RecoverPasswordWindow().show()