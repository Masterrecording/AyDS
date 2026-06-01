import hashlib
import pymysql as sql
import json

from customtkinter import CTk as Tk
from customtkinter import CTkFrame as Frame
from customtkinter import CTkLabel as Label
from customtkinter import CTkEntry as Entry
from customtkinter import CTkFont as Font
from customtkinter import CTkButton as Button
from customtkinter import CTkComboBox as ComboBox


class RegisterWindow(Tk):
    def __init__(self, fg_color = None, **kwargs):
        super().__init__(fg_color, **kwargs)
        self.geometry("400x710")
        self.title("Login / Register")
    

    def conectar_db(self):
        DATABASE = json.loads(open('settings.json', 'r', encoding='utf-8').read())
        return sql.connect(
            host=DATABASE["host"],
            user=DATABASE["user"],
            password=DATABASE["password"],
            database=DATABASE["database"]
        )
        
    def abrir_login(self):
        self.destroy()  
        from App.login import LoginWindow

        LoginWindow().show()

    def recibir_preguntas(self):
        conn = self.conectar_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM preguntas_recuperacion")
        response = cur.fetchall()

        preguntas = [pregunta for _, pregunta in response]
        conn.close()
        return preguntas

    def register(self):
        usuario = self.user_entry.get().strip().lower()
        contrasena = self.pass_entry.get().strip()
        contrasena2 = self.pass2_entry.get().strip()
        pregunta_recuperacion = self.rec_question.get().strip()
        respuesta = self.rec_answer.get().strip().lower()
        id_boleta = self.boleta.get().strip()
        
        if not id_boleta: return self.resultado_label.configure("Ingresa una boleta válida", text_color="orange")
        
        if pregunta_recuperacion == "Recuperacion": return self.resultado_label.configure(text="Pregunta de recuperación inválida",
                                                                                    text_color="orange")
        else: id_recuperacion = self.recibir_preguntas().index(pregunta_recuperacion)+1
        
        if not respuesta: return self.resultado_label.configure(text="Respuesta de recupración inválida",
                                                        text_color="orange")
        
        if contrasena != contrasena2:
            self.resultado_label.configure(text="Las contraseñas no coinciden", text_color="orange")
            return

        # Validaciones básicas
        if not usuario or not contrasena:
            self.resultado_label.configure(text="Completa todos los campos", text_color="orange")
            return

        if len(contrasena) < 4:
            self.resultado_label.configure(text="Mínimo 4 caracteres", text_color="orange")
            return

        # Hash de contraseña
        contrasena_hash = hashlib.sha256(contrasena.encode()).hexdigest()

        conexion = None
        cursor = None
        try:
            conexion = self.conectar_db()
            cursor = conexion.cursor()

            # Verificar si el usuario ya existe
            cursor.execute("SELECT idusuario FROM usuario WHERE nombre = %s", (usuario,))
            if cursor.fetchone():
                self.resultado_label.configure(text="El usuario ya existe", text_color="red")
                return
            print(id_recuperacion)

            # Insertar usuario 
            query = "INSERT INTO usuario (nombre, boleta, contraseña, res_recu, idrecuperacion, roles_idroles) VALUES ( %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (usuario, id_boleta, contrasena_hash, respuesta, id_recuperacion, "1"))
            conexion.commit()

            self.resultado_label.configure(text="Usuario registrado", text_color="green")
            # Limpiar campos
            self.user_entry.delete(0, "end")
            self.pass_entry.delete(0, "end")

            # Abrir login y cerrar registro
            self.abrir_login()

        except Exception as e:
            self.resultado_label.configure(text="Error al registrar", text_color="red")
            print(e)
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def show(self):
        self.main_frame = Frame(self)
        self.main_frame.pack(expand=True)

        self.login_label = Label(
            self.main_frame,
            text="Registro",
            font=Font(family="Calibri", size=24, weight="bold")
        )
        self.login_label.pack(pady=(20, 30))

        self.user_entry = Entry(self.main_frame, placeholder_text="Usuario")
        self.user_entry.pack(pady=10, padx=40)

        self.pass_entry = Entry(self.main_frame, placeholder_text="Contraseña", show="*")
        self.pass_entry.pack(pady=10, padx=40)

        # Confirmar contraseña
        self.pass2_entry = Entry(self.main_frame, placeholder_text="Conf Contraseña", show="*")
        self.pass2_entry.pack(pady=10, padx=40)

        # Seleccionar pregunta de recuperación con ComboBox
        self.rec_question = ComboBox(self.main_frame, values=self.recibir_preguntas())
        self.rec_question.set("Recuperacion")
        self.rec_question.pack(pady=10, padx=40)

        # Ingresar respuesta (40 chars max) de recuperacion
        self.rec_answer = Entry(self.main_frame, placeholder_text="Respuesta")
        self.rec_answer.pack(pady=10, padx=40)

        # Ingresar la boleta del estudiante
        self.boleta = Entry(self.main_frame, placeholder_text="Boleta")
        self.boleta.pack(pady=10, padx=40)

        self.login_button = Button(self.main_frame, text="Iniciar Sesión", command=self.abrir_login)
        self.login_button.pack(pady=20)

        self.register_button = Button(self.main_frame, text="Registrarse", command=self.register)
        self.register_button.pack(pady=20)

        self.resultado_label = Label(self.main_frame, text="")
        self.resultado_label.pack()

        self.mainloop()