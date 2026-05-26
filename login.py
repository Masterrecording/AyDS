import pymysql as sql
import hashlib
import json

from customtkinter import CTk as Tk
from customtkinter import CTkFrame as Frame
from customtkinter import CTkLabel as Label
from customtkinter import CTkEntry as Entry
from customtkinter import CTkFont as Font
from customtkinter import CTkButton as Button

class LoginWindow(Tk):
    def __init__(self):
        super().__init__()
        self.geometry("400x400")
        self.title("Login")

        self.main_frame = Frame(self)
        self.main_frame.pack(expand=True)

        self.login_label = Label(
            self.main_frame,
            text="Inicia Sesion",
            font=Font(family="Calibri", size=24, weight="bold")
        )
        self.login_label.pack(pady=(20, 30))

        self.user_entry = Entry(self.main_frame, placeholder_text="Usuario")
        self.user_entry.pack(pady=10, padx=40)

        self.pass_entry = Entry(self.main_frame, placeholder_text="Contraseña", show="*")
        self.pass_entry.pack(pady=10, padx=40)
        self.pass_entry.bind("<Return>", lambda event: self.login())  # Permite presionar Enter para iniciar sesión

        self.login_button = Button(self.main_frame, text="Entrar", command=self.login)
        self.login_button.pack(pady=20)

        self.resultado_label = Label(self.main_frame, text="")
        self.resultado_label.pack()

    def abrir_menu(self, usuario):
        self.destroy()
        from mainmenu import MainMenu

        menu_window = Tk()
        menu_window.geometry("700x600")
        main_menu = MainMenu(menu_window, usuario=usuario)
        main_menu.pack(expand=True, fill="both")
        menu_window.mainloop()



    def conectar_db(self):
        DATABASE = json.loads(open('settings.json', 'r', encoding='utf-8').read())
        
        return sql.connect(
            host=DATABASE["host"],
            user=DATABASE["user"],
            password=DATABASE["password"],
            database=DATABASE["database"]
        )

    def login(self):
        usuario = self.user_entry.get().strip()
        contrasena = self.pass_entry.get()

        
        contrasena_hash = hashlib.sha256(contrasena.encode()).hexdigest()

        try:
            conexion = self.conectar_db()
            cursor = conexion.cursor()

            query = "SELECT contraseña FROM usuario WHERE nombre = %s"
            cursor.execute(query, (usuario,))
            resultado = cursor.fetchone()

            if resultado:
                contrasena_db = resultado[0]


                if contrasena_hash == contrasena_db:
                    self.resultado_label.configure(text="Login exitoso", text_color="green")
                    self.abrir_menu(usuario)
                else:
                    self.resultado_label.configure(text="Contraseña incorrecta", text_color="red")
            else:
                self.resultado_label.configure(text="Usuario no existe", text_color="red")

            cursor.close()
            conexion.close()

        except Exception as e:
            self.resultado_label.configure(text="Error de conexion", text_color="red")
            print(e)

if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()