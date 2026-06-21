import pymysql as sql
from datetime import datetime

from customtkinter import CTk as Tk
from customtkinter import CTkFrame as Frame
from customtkinter import CTkLabel as Label
from customtkinter import CTkEntry as Entry
from customtkinter import CTkButton as Button
from customtkinter import CTkFont as Font
from customtkinter import CTkOptionMenu as OptionMenu
from tkinter.messagebox import showerror, showinfo

from App.utils import conectar_db, get_semestre

TIPOS_ACTIVIDAD = ['Tarea', 'Examen', 'Proyecto', 'Práctica', 'Investigación', 'Otro']
PRIORIDAD_MAP   = {'Baja': 1, 'Media': 2, 'Alta': 3, 'Muy Alta': 4, 'Urgente': 5}
PRIORIDAD_INV   = {v: k for k, v in PRIORIDAD_MAP.items()}
ESTADOS         = ['pendiente', 'en progreso', 'completada']


class EditTaskView(Frame):
    """
    Vista para editar una actividad existente.
    Se puede usar embebida en un Frame o en una ventana Tk secundaria.
    """

    def __init__(self, master, boleta, id_act, callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.boleta   = boleta
        self.id_act   = id_act
        self.callback = callback
        self._materias_dict = {}

        Label(self, text='Editar Pendiente',
              font=Font(family='Calibri', size=16, weight='bold')).pack(pady=8)

        # ── Nombre ───────────────────────────────────────────
        Label(self, text='Nombre del pendiente').pack(anchor='w', padx=8)
        self.nombre_entry = Entry(self)
        self.nombre_entry.pack(fill='x', padx=8, pady=(0, 6))

        # ── Tipo de actividad ────────────────────────────────
        Label(self, text='Tipo de actividad').pack(anchor='w', padx=8)
        self.tipo_menu = OptionMenu(self, values=TIPOS_ACTIVIDAD)
        self.tipo_menu.pack(fill='x', padx=8, pady=(0, 6))

        # ── Materia ──────────────────────────────────────────
        Label(self, text='Materia').pack(anchor='w', padx=8)
        self.materia_menu = OptionMenu(self, values=self._cargar_materias())
        self.materia_menu.pack(fill='x', padx=8, pady=(0, 6))

        # ── Fecha ────────────────────────────────────────────
        Label(self, text='Fecha de entrega (DD-MM-YYYY)').pack(anchor='w', padx=8)
        self.fecha_entry = Entry(self)
        self.fecha_entry.pack(fill='x', padx=8, pady=(0, 6))

        # ── Prioridad ────────────────────────────────────────
        Label(self, text='Prioridad').pack(anchor='w', padx=8)
        self.prioridad_menu = OptionMenu(self, values=list(PRIORIDAD_MAP.keys()))
        self.prioridad_menu.set('Alta')
        self.prioridad_menu.pack(fill='x', padx=8, pady=(0, 6))

        # ── Estado ───────────────────────────────────────────
        Label(self, text='Estado').pack(anchor='w', padx=8)
        self.estado_menu = OptionMenu(self, values=ESTADOS)
        self.estado_menu.set('pendiente')
        self.estado_menu.pack(fill='x', padx=8, pady=(0, 6))

        # ── Botones ──────────────────────────────────────────
        btn_frame = Frame(self)
        btn_frame.pack(pady=8)
        Button(btn_frame, text='Guardar cambios',
               command=self._guardar).pack(side='left', padx=5)
        Button(btn_frame, text='Cancelar', fg_color='gray', hover_color='darkgray',
               command=self._cancelar).pack(side='left', padx=5)

        self.status = Label(self, text='')
        self.status.pack()

        # Cargar datos actuales de la actividad
        self._cargar_datos()

    # ─────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────

    def _cargar_materias(self):
        semestre = get_semestre(self.boleta)
        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute(
                'SELECT idmaterias, nombre FROM materias WHERE usuario_boleta = %s AND semestre = %s',
                (self.boleta, semestre)
            )
            rows = cur.fetchall()
            cur.close()
            conn.close()
            self._materias_dict = {nombre: mid for mid, nombre in rows}
            return [nombre for _, nombre in rows] or ['Sin materias']
        except Exception as e:
            print(e)
            return ['Error al cargar']

    def _cargar_datos(self):
        """Rellena el formulario con los datos actuales de la actividad."""
        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute(
                """SELECT a.nombre, a.tipo_actividad, a.fecha_entrega,
                          a.prioridad, a.estado, m.nombre AS materia
                   FROM actividades a
                   JOIN materias m ON a.materias_idmaterias = m.idmaterias
                   WHERE a.id_act = %s AND a.usuario_boleta = %s""",
                (self.id_act, self.boleta)
            )
            row = cur.fetchone()
            cur.close()
            conn.close()

            if not row:
                self.status.configure(text='Actividad no encontrada.', text_color='red')
                return

            nombre, tipo, fecha_entrega, prioridad, estado, materia = row

            self.nombre_entry.insert(0, nombre or '')

            if tipo in TIPOS_ACTIVIDAD:
                self.tipo_menu.set(tipo)

            if materia in self._materias_dict:
                self.materia_menu.set(materia)

            if isinstance(fecha_entrega, datetime):
                fecha_entrega = fecha_entrega.date()
            self.fecha_entry.insert(0, fecha_entrega.strftime('%d-%m-%Y'))

            prioridad_texto = PRIORIDAD_INV.get(int(prioridad), 'Alta')
            self.prioridad_menu.set(prioridad_texto)

            if estado in ESTADOS:
                self.estado_menu.set(estado)

        except Exception as e:
            print(e)
            self.status.configure(text='Error al cargar datos.', text_color='red')

    # ─────────────────────────────────────────────────────────
    # Acciones
    # ─────────────────────────────────────────────────────────

    def _guardar(self):
        nombre        = self.nombre_entry.get().strip()
        tipo          = self.tipo_menu.get()
        materia_nom   = self.materia_menu.get().strip()
        fecha_str     = self.fecha_entry.get().strip()
        prioridad_txt = self.prioridad_menu.get()
        estado        = self.estado_menu.get()

        if not nombre or not fecha_str:
            self.status.configure(text='Nombre y fecha son obligatorios.', text_color='orange')
            return

        try:
            fecha = datetime.strptime(fecha_str, '%d-%m-%Y').date()
        except ValueError:
            self.status.configure(text='Fecha inválida. Usa DD-MM-YYYY.', text_color='orange')
            return

        prioridad  = PRIORIDAD_MAP.get(prioridad_txt, 3)
        materia_id = self._materias_dict.get(materia_nom)

        if not materia_id:
            self.status.configure(text='Selecciona una materia válida.', text_color='orange')
            return

        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute(
                """UPDATE actividades
                   SET nombre = %s, tipo_actividad = %s, materias_idmaterias = %s,
                       fecha_entrega = %s, prioridad = %s, estado = %s
                   WHERE id_act = %s AND usuario_boleta = %s""",
                (nombre, tipo, materia_id, fecha, prioridad, estado,
                 self.id_act, self.boleta)
            )
            conn.commit()
            cur.close()
            conn.close()
            self.status.configure(text='Guardado correctamente.', text_color='green')
            if self.callback:
                self.callback()
        except Exception as e:
            print(e)
            self.status.configure(text='Error al guardar.', text_color='red')

    def _cancelar(self):
        """Cierra la ventana si es secundaria, o limpia el frame."""
        top = self.winfo_toplevel()
        if isinstance(top, Tk):
            top.destroy()


# ─────────────────────────────────────────────────────────────
# Prueba independiente
# ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app = Tk()
    app.geometry('500x520')
    app.title('Editar Pendiente')
    EditTaskView(app, boleta='2025670127', id_act=1).pack(expand=True, fill='both')
    app.mainloop()
