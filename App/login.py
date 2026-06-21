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

    def show(self):
        self.main_frame = Frame(self)
        self.main_frame.pack(expand=True)

        self.login_label = Label(
            self.main_frame,
            text="Inicia Sesion",
            font=Font(family="Calibri", size=24, weight="bold")
        )
        self.login_label.pack(pady=(20, 30))

        self.boleta_entry = Entry(self.main_frame, placeholder_text="Boleta")
        self.boleta_entry.pack(pady=10, padx=40)

        self.pass_entry = Entry(self.main_frame, placeholder_text="Contraseña", show="*")
        self.pass_entry.pack(pady=10, padx=40)
        self.pass_entry.bind("<Return>", lambda event: self.login())  # Permite presionar Enter para iniciar sesión

        self.register_button = Button(self.main_frame, text="Registrarse", command=self.abrir_register, fg_color="gray", hover_color="darkgray")
        self.register_button.pack(pady=5)

        self.forgotten_pass = Button(self.main_frame, text="Olvide mi contraseña", command=self.abrir_olvide_mi_contraseña, fg_color="gray", hover_color="darkgray")
        self.forgotten_pass.pack(pady=5)

        self.login_button = Button(self.main_frame, text="Entrar", command=self.login)
        self.login_button.pack(pady=20)

        self.resultado_label = Label(self.main_frame, text="")
        self.resultado_label.pack()
        self.mainloop()
        
    def abrir_olvide_mi_contraseña(self):
        self.destroy() 
        from App.recover_password import RecoverPasswordWindow
        RecoverPasswordWindow().show()

    def abrir_register(self):
        self.withdraw()
        from App.register import RegisterWindow
        RegisterWindow().show()

    def abrir_menu(self, boleta):
        self.destroy()
        from App.mainmenu import GestorVentanas

        self.app = Tk()
        self.app.geometry('800x750')
        self.app.title('AyDS')
        self.gestor = GestorVentanas(self.app, boleta=boleta)
        self.gestor.show('inicio')
        self.app.mainloop()


    def conectar_db(self):
        DATABASE = json.loads(open('settings.json', 'r', encoding='utf-8').read())
        
        return sql.connect(
            host=DATABASE["host"],
            user=DATABASE["user"],
            password=DATABASE["password"],
            database=DATABASE["database"]
        )

    def login(self):
        boleta = self.boleta_entry.get().strip()
        contrasena = self.pass_entry.get()

        
        contrasena_hash = hashlib.sha256(contrasena.encode()).hexdigest()

        try:
            conexion = self.conectar_db()
            cursor = conexion.cursor()

            query = "SELECT contrasena FROM usuario WHERE boleta = %s"
            cursor.execute(query, (boleta,))
            resultado = cursor.fetchone()

            if resultado:
                contrasena_db = resultado[0]


                if contrasena_hash == contrasena_db:
                    self.resultado_label.configure(text="Login exitoso", text_color="green")
                    self.abrir_menu(boleta)
                else:
                    self.resultado_label.configure(text="Contraseña incorrecta", text_color="red")
            else:
                self.resultado_label.configure(text="No existe un usuario con esa boleta", text_color="red")

            cursor.close()
            conexion.close()

        except Exception as e:
            self.resultado_label.configure(text="Error de conexion", text_color="red")
            print(e)

if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()
