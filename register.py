import hashlib
import mysql.connector
import pymysql as sql

from customtkinter import CTk as Tk
from customtkinter import CTkFrame as Frame
from customtkinter import CTkLabel as Label
from customtkinter import CTkEntry as Entry
from customtkinter import CTkFont as Font
from customtkinter import CTkButton as Button
from customtkinter import CTkComboBox as ComboBox

def abrir_login():
    root.destroy()  
    import login

    app = login.LoginWindow()
    app.mainloop()

def conectar_db():
    return sql.connect(
        host="localhost",
        user="root",
        password="",
        database="ayds"
    )


def recibir_preguntas():
    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM preguntas_recuperacion")
    response = cur.fetchall()

    preguntas = [pregunta for _, pregunta in response]
    conn.close()
    return preguntas


def register():
    usuario = user_entry.get().strip()
    contrasena = pass_entry.get().strip()
    contrasena2 = pass2_entry.get().strip()
    pregunta_recuperacion = rec_question.get().strip()
    id_recuperacion = recibir_preguntas().index(pregunta_recuperacion)
    respuesta = rec_answer.get().strip()
    
    if contrasena != contrasena2:
        resultado_label.configure(text="Las contraseñas no coinciden", text_color="orange")
        return

    # Validaciones básicas
    if not usuario or not contrasena:
        resultado_label.configure(text="Completa todos los campos", text_color="orange")
        return

    if len(contrasena) < 4:
        resultado_label.configure(text="Mínimo 4 caracteres", text_color="orange")
        return

    # Hash de contraseña
    contrasena_hash = hashlib.sha256(contrasena.encode()).hexdigest()

    conexion = None
    cursor = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()

        # Verificar si el usuario ya existe
        cursor.execute("SELECT id_usuario FROM usuarios WHERE usuario = %s", (usuario,))
        if cursor.fetchone():
            resultado_label.configure(text="El usuario ya existe", text_color="red")
            return

        # Insertar usuario 
        query = "INSERT INTO usuarios (usuario, contrasena_hash) VALUES (%s, %s)"
        cursor.execute(query, (usuario, contrasena_hash))
        conexion.commit()

        resultado_label.configure(text="Usuario registrado", text_color="green")
        # Limpiar campos
        user_entry.delete(0, "end")
        pass_entry.delete(0, "end")

        # Abrir login y cerrar registro
        abrir_login()

    except Exception as e:
        resultado_label.configure(text="Error al registrar", text_color="red")
        print(e)
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


# ================= UI =================

root = Tk()
root.geometry("400x420")
root.title("Login / Register")

main_frame = Frame(root)
main_frame.pack(expand=True)

login_label = Label(
    main_frame,
    text="Registro",
    font=Font(family="Calibri", size=24, weight="bold")
)
login_label.pack(pady=(20, 30))

user_entry = Entry(main_frame, placeholder_text="Usuario")
user_entry.pack(pady=10, padx=40)

pass_entry = Entry(main_frame, placeholder_text="Contraseña", show="*")
pass_entry.pack(pady=10, padx=40)

# Confirmar contraseña
pass2_entry = Entry(main_frame, placeholder_text="Conf Contraseña", show="*")
pass2_entry.pack(pady=10, padx=40)

# Seleccionar pregunta de recuperación con ComboBox
rec_question = ComboBox(main_frame, values=recibir_preguntas())
rec_question.pack(pady=10, padx=40)

# Ingresar respuesta (40 chars max) de recuperacion
rec_answer = Entry(main_frame, placeholder_text="Respuesta")
rec_answer.pack(pady=10, padx=40)

# Ingresar la boleta del estudiante
boleta = Entry(main_frame, placeholder_text="Boleta")
boleta.pack(pady=10, padx=40)

register_button = Button(main_frame, text="Registrarse", command=register)
register_button.pack(pady=20)

resultado_label = Label(main_frame, text="")
resultado_label.pack()

root.mainloop()