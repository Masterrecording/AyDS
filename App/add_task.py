from datetime import datetime

from customtkinter import CTk as Tk
from customtkinter import CTkFrame as Frame
from customtkinter import CTkLabel as Label
from customtkinter import CTkEntry as Entry
from customtkinter import CTkButton as Button
from customtkinter import CTkFont as Font
from customtkinter import CTkOptionMenu as OptionMenu
from tkinter.messagebox import showerror

from App.utils import conectar_db, get_semestre

TIPOS_ACTIVIDAD = ['Tarea', 'Examen', 'Proyecto', 'Práctica', 'Investigación', 'Otro']
PRIORIDAD_MAP   = {'Baja': 1, 'Media': 2, 'Alta': 3, 'Muy Alta': 4, 'Urgente': 5}


class AddTaskView(Frame):
    def __init__(self, master, gestor, boleta=None, usuario_id=None, callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.gestor   = gestor
        self.boleta   = boleta or usuario_id
        self.callback = callback

        Label(self, text='Crear Pendiente',
              font=Font(family='Calibri', size=16, weight='bold')).pack(pady=8)

        Label(self, text='Nombre del pendiente').pack(anchor='w', padx=8)
        self.nombre_entry = Entry(self)
        self.nombre_entry.pack(fill='x', padx=8, pady=(0, 6))

        Label(self, text='Tipo de actividad').pack(anchor='w', padx=8)
        self.tipo_menu = OptionMenu(self, values=TIPOS_ACTIVIDAD)
        self.tipo_menu.set('Tarea')
        self.tipo_menu.pack(fill='x', padx=8, pady=(0, 6))

        Label(self, text='Materia').pack(anchor='w', padx=8)
        self.materia_menu = OptionMenu(self, values=self._cargar_materias())
        self.materia_menu.pack(fill='x', padx=8, pady=(0, 6))

        Label(self, text='Fecha de entrega (DD-MM-YYYY)').pack(anchor='w', padx=8)
        self.fecha_entry = Entry(self)
        self.fecha_entry.pack(fill='x', padx=8, pady=(0, 6))

        Label(self, text='Prioridad').pack(anchor='w', padx=8)
        self.prioridad_menu = OptionMenu(self, values=list(PRIORIDAD_MAP.keys()))
        self.prioridad_menu.set('Alta')
        self.prioridad_menu.pack(fill='x', padx=8, pady=(0, 6))

        Button(self, text='Guardar Pendiente', command=self._guardar).pack(pady=8)

        self.status = Label(self, text='')
        self.status.pack()

    def _cargar_materias(self):
        self.materias_dict = {}
        semestre = get_semestre(self.boleta)
        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute(
                'SELECT idmaterias, nombre FROM materias WHERE usuario_boleta = %s AND semestre = %s',
                (self.boleta, semestre)
            )
            materias = cur.fetchall()
            cur.close()
            conn.close()
            self.materias_dict = {nombre: mid for mid, nombre in materias}
            return [nombre for _, nombre in materias] or ['Sin materias']
        except Exception as e:
            print(e)
            return ['Error al cargar']

    def _guardar(self):
        if not self.boleta:
            self.status.configure(text='Usuario no definido.')
            return

        semestre = get_semestre(self.boleta)
        if not semestre:
            return showerror('Error', 'Debes completar la encuesta base antes de añadir pendientes.')

        nombre       = self.nombre_entry.get().strip()
        tipo         = self.tipo_menu.get()
        materia_nom  = self.materia_menu.get().strip()
        fecha_str    = self.fecha_entry.get().strip()
        prio_texto   = self.prioridad_menu.get()

        if not nombre or not materia_nom or not fecha_str:
            self.status.configure(text='Completa todos los campos requeridos.',
                                  text_color='orange')
            return

        try:
            fecha = datetime.strptime(fecha_str, '%d-%m-%Y').date()
        except ValueError:
            self.status.configure(text='Fecha inválida. Usa DD-MM-YYYY.', text_color='orange')
            return

        prioridad  = PRIORIDAD_MAP.get(prio_texto, 3)
        materia_id = self.materias_dict.get(materia_nom)
        if not materia_id:
            self.status.configure(text='Materia inválida.', text_color='orange')
            return

        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute(
                '''INSERT INTO actividades
                   (usuario_boleta, materias_idmaterias, nombre, tipo_actividad,
                    fecha_entrega, semestre, prioridad)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                (self.boleta, materia_id, nombre, tipo, fecha, str(semestre), prioridad)
            )
            conn.commit()
            cur.close()
            conn.close()

            self.status.configure(text='Pendiente creado exitosamente.', text_color='green')
            self.nombre_entry.delete(0, 'end')
            self.fecha_entry.delete(0, 'end')
            self.tipo_menu.set('Tarea')

            if self.callback:
                self.callback()
        except Exception as e:
            print(e)
            self.status.configure(text='Error al guardar pendiente.', text_color='red')


if __name__ == '__main__':
    app = Tk()
    app.geometry('400x520')
    app.title('Crear Pendiente')
    AddTaskView(app, None, boleta='2025670127').pack(expand=True, fill='both')
    app.mainloop()
