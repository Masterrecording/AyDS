from tkinter.messagebox import showerror, showinfo
import customtkinter as ctk
import pymysql as sql
import tkinter as tk
import json

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def conectar_db():
    cfg = json.loads(open('settings.json', 'r', encoding='utf-8').read())
    return sql.connect(host=cfg['host'], user=cfg['user'], password=cfg['password'], database=cfg['database'])


class AgregarMateriaView(ctk.CTk):
    def __init__(self, boleta: int, reload_function: function):
        super().__init__()
        self.reload_function = reload_function
        self.boleta = str(boleta)
        self.title("Añadir Nueva Materia")
        self.geometry("400x180")
        self.resizable(False, False)

        self.frame = ctk.CTkFrame(self, corner_radius=15)
        self.frame.pack(expand=True, fill="both", padx=5, pady=5)

        self.entry_nombre = ctk.CTkEntry(
            self.frame, 
            placeholder_text="Nombre de la materia", 
            width=300, 
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.entry_nombre.pack(pady=(30, 15))
        self.entry_nombre.bind('<Return>', self._guardar)
        
        self.btn_guardar = ctk.CTkButton(
            self.frame, 
            text="Guardar Materia", 
            width=30, 
            height=45, 
            command=self._guardar,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.btn_guardar.pack(pady=(10, 20))

    def _guardar(self, *args, **kwargs):
        nombre = self.entry_nombre.get().strip().lower().capitalize()
        if nombre == '': return showerror("Error", "Ingresa un nombre de materia válido!")
        
        try:
            conn = conectar_db()
            cur = conn.cursor()
            query = "SELECT * FROM materias WHERE usuario_boleta = %s"
            cur.execute(query, args=(self.boleta,))
            conn.commit()
            conn.close()
            
            semestre = self.get_semestre(self.boleta)
            if not semestre: return showerror("Error", "Completa la encuesta base antes de añadir una materia")
            
            materias = cur.fetchall()
            for materia in materias:
                if materia[2] == nombre: return showerror("Error", "Ya tienes esta materia registrada!")
            
            connection = conectar_db()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO materias (usuario_boleta, semestre, nombre) values (%s, %s, %s)",
                        args=(self.boleta, semestre, nombre))
            connection.commit()
            connection.close()
            showinfo("Éxito", f"Has guardado la materia {nombre} con éxito!!")
            self.entry_nombre.delete(0, tk.END)
            self.reload_function()
        except Exception as e:
            showerror("Error", f"Se ha producido un error, intenta más tarde\n{e}")

    def get_semestre(self, boleta):
            try:
                con = conectar_db()
                cur = con.cursor()
                cur.execute("select semestre from quiz_base where usuario_boleta = %s", args=(boleta,))
                response = cur.fetchone()
                con.close()
                return response[0]
            except Exception as e:
                print(f"Error al obtener el semestre (Vista: Añadir materia): {e}")

if __name__ == "__main__":
    app = AgregarMateriaView(0)
    app.mainloop()
