import pymysql as sql
import json
from datetime import datetime

from customtkinter import CTk as Tk
from customtkinter import CTkFrame as Frame
from customtkinter import CTkLabel as Label
from customtkinter import CTkEntry as Entry
from customtkinter import CTkOptionMenu as OptionMenu
from customtkinter import CTkButton as Button
from customtkinter import CTkFont as Font
from customtkinter import CTkScrollableFrame as ScrollableFrame


def conectar_db():
    cfg = json.loads(open('settings.json', 'r', encoding='utf-8').read())
    return sql.connect(host=cfg['host'], user=cfg['user'], password=cfg['password'], database=cfg['database'])


class Ventana(Frame):
    """Clase base para ventanas. Cada ventana debe implementar show() y close()."""
    def __init__(self, master, gestor, **kwargs):
        super().__init__(master, **kwargs)
        self.gestor = gestor

    def show(self):
        self.pack(expand=True, fill='both')

    def close(self):
        self.pack_forget()
        self.destroy()


class VentanaBase(Ventana):
    """Formulario simplificado que mapea a la tabla quiz_base del script SQL."""
    def __init__(self, master, gestor, usuario_id=None, **kwargs):
        super().__init__(master, gestor, **kwargs)
        self.usuario_id = usuario_id
        Label(self, text='Datos iniciales (quiz_base)', font=Font(family='Calibri', size=16, weight='bold')).pack(pady=8)

        campos = [
            ('grupo', 'Grupo'),
            ('sit_acad', 'Situación académica'),
            ('num_materias', 'Número de materias'),
            ('semestre', 'Semestre'),
            ('str_tolerancia', 'Tolerancia (texto)'),
            ('perse_carga', 'Perseverancia/carga (num)'),
            ('pers_anim_general', 'Percepción anímica (texto)'),
            ('motivacion_acad', 'Motivación académica (texto)')
        ]
        self.entries = {}
        frame = ScrollableFrame(self)
        frame.pack(expand=True, fill='both', padx=8, pady=8)
        for key, label in campos:
            Label(frame, text=label).pack(anchor='w', padx=6, pady=(6, 0))
            e = Entry(frame)
            e.pack(fill='x', padx=6, pady=(0, 6))
            self.entries[key] = e

        Button(self, text='Guardar', command=self.guardar).pack(pady=6)
        self.status = Label(self, text='')
        self.status.pack()

        if self.usuario_id:
            self.cargar()

    def cargar(self):
        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute('SELECT grupo,sit_acad,num_materias,semestre,str_tolerancia,perse_carga,pers_anim_general,motivacion_acad FROM quiz_base WHERE usuario_idusuario=%s', (self.usuario_id,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if row:
                for k, v in zip(self.entries.keys(), row):
                    self.entries[k].delete(0, 'end')
                    self.entries[k].insert(0, str(v) if v is not None else '')
                self.status.configure(text='Datos cargados.')
            else:
                self.status.configure(text='No existen datos previos.')
        except Exception as e:
            print(e)
            self.status.configure(text='Error al cargar.')

    def guardar(self):
        if not self.usuario_id:
            self.status.configure(text='Usuario no definido.')
            return
        vals = {k: self.entries[k].get().strip() or None for k in self.entries}
        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute('SELECT usuario_idusuario FROM quiz_base WHERE usuario_idusuario=%s', (self.usuario_id,))
            exists = cur.fetchone()
            if exists:
                cur.execute('''UPDATE quiz_base SET grupo=%s,sit_acad=%s,num_materias=%s,semestre=%s,str_tolerancia=%s,perse_carga=%s,pers_anim_general=%s,motivacion_acad=%s WHERE usuario_idusuario=%s''',
                            (vals['grupo'], vals['sit_acad'], vals['num_materias'], vals['semestre'], vals['str_tolerancia'], vals['perse_carga'], vals['pers_anim_general'], vals['motivacion_acad'], self.usuario_id))
            else:
                cur.execute('''INSERT INTO quiz_base (usuario_idusuario,grupo,sit_acad,num_materias,semestre,str_tolerancia,perse_carga,pers_anim_general,motivacion_acad,docente_iddocente,gruopo_relacion) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NULL,NULL)''',
                            (self.usuario_id, vals['grupo'], vals['sit_acad'], vals['num_materias'], vals['semestre'], vals['str_tolerancia'], vals['perse_carga'], vals['pers_anim_general'], vals['motivacion_acad']))
            conn.commit()
            cur.close()
            conn.close()
            self.status.configure(text='Guardado exitoso.')
        except Exception as e:
            print(e)
            self.status.configure(text='Error al guardar.')


class VentanaSeguimiento(Ventana):
    """Ventana para registrar aplicaciones de seguimiento (quiz_seguimiento y Quiz_base_estado)."""
    def __init__(self, master, gestor, usuario_id=None, **kwargs):
        super().__init__(master, gestor, **kwargs)
        self.usuario_id = usuario_id
        Label(self, text='Seguimiento (quiz_seguimiento)', font=Font(family='Calibri', size=16, weight='bold')).pack(pady=8)
        Label(self, text='Registrar aplicación (marca la fecha de hoy)').pack(pady=(0,6))
        Button(self, text='Registrar aplicación hoy', command=self.registrar).pack(pady=6)
        self.status = Label(self, text='')
        self.status.pack()

    def registrar(self):
        if not self.usuario_id:
            self.status.configure(text='Usuario no definido.')
            return
        hoy = datetime.now().date()
        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute('SELECT usuario_idusuario FROM quiz_seguimiento WHERE usuario_idusuario=%s', (self.usuario_id,))
            if cur.fetchone():
                cur.execute('UPDATE quiz_seguimiento SET ultima_aplicacion=%s WHERE usuario_idusuario=%s', (hoy, self.usuario_id))
            else:
                cur.execute('INSERT INTO quiz_seguimiento (usuario_idusuario,ultima_aplicacion) VALUES (%s,%s)', (self.usuario_id, hoy))
            # marcar quiz_base_estado.aplicada = 1 y fecha
            cur.execute('SELECT usuario_idusuario FROM Quiz_base_estado WHERE usuario_idusuario=%s', (self.usuario_id,))
            if cur.fetchone():
                cur.execute('UPDATE Quiz_base_estado SET aplicada=1, fecha_aplicacion=%s WHERE usuario_idusuario=%s', (hoy, self.usuario_id))
            else:
                # Quiz_base_estado expects aplicada and fecha_aplicacion; insert with aplicada=1
                try:
                    cur.execute('INSERT INTO Quiz_base_estado (usuario_idusuario,aplicada,fecha_aplicacion) VALUES (%s,1,%s)', (self.usuario_id, hoy))
                except Exception:
                    # In case schema differs, ignore optional update
                    pass
            conn.commit()
            cur.close()
            conn.close()
            self.status.configure(text='Aplicación registrada.')
        except Exception as e:
            print(e)
            self.status.configure(text='Error al registrar.')


class VentanaActividades(Ventana):
    """Formulario para crear actividades en tablas act_*.
       Simplificado: varios campos y mapeo según tipo.
    """
    def __init__(self, master, gestor, usuario_id=None, **kwargs):
        super().__init__(master, gestor, **kwargs)
        self.usuario_id = usuario_id
        Label(self, text='Registrar actividad', font=Font(family='Calibri', size=16, weight='bold')).pack(pady=8)
        Label(self, text='Tipo').pack(anchor='w', padx=8)
        tipos = ['act_examen', 'act_proyecto', 'act_equipo', 'act_tarea']
        self.tipo = OptionMenu(self, values=tipos)
        self.tipo.set(tipos[0])
        self.tipo.pack(fill='x', padx=8, pady=(0,6))

        Label(self, text='ID materia (num)').pack(anchor='w', padx=8)
        self.id_materia = Entry(self)
        self.id_materia.pack(fill='x', padx=8, pady=(0,6))

        Label(self, text='Tiempo estimado (min)').pack(anchor='w', padx=8)
        self.tiempo_estimado = Entry(self)
        self.tiempo_estimado.pack(fill='x', padx=8, pady=(0,6))

        Label(self, text='Genera estrés (1-5)').pack(anchor='w', padx=8)
        self.genera_estres = OptionMenu(self, values=['1','2','3','4','5'])
        self.genera_estres.set('3')
        self.genera_estres.pack(fill='x', padx=8, pady=(0,6))

        Button(self, text='Registrar', command=self.registrar).pack(pady=8)
        self.status = Label(self, text='')
        self.status.pack()

    def registrar(self):
        if not self.usuario_id:
            self.status.configure(text='Usuario no definido.')
            return
        try:
            mid = int(self.id_materia.get())
            tiempo = int(self.tiempo_estimado.get() or 0)
            genera = int(self.genera_estres.get())
        except Exception:
            self.status.configure(text='Valores inválidos.')
            return
        tipo = self.tipo.get()
        fecha = datetime.now()
        try:
            conn = conectar_db()
            cur = conn.cursor()
            if tipo == 'act_examen':
                cur.execute('INSERT INTO act_examen (usuario_idusuario,materias_idmaterias,fecha,tiempo_estimado,temas_dificiles,genera_estres) VALUES (%s,%s,%s,%s,%s,%s)',
                            (self.usuario_id, mid, fecha, tiempo, 3, genera))
            elif tipo == 'act_proyecto':
                cur.execute('INSERT INTO act_proyecto (usuario_idusuario,materias_idmaterias,fecha,tiempo_estimado,complejo,en_equipo,genera_estres) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                            (self.usuario_id, mid, fecha, tiempo, 3, 0, genera))
            elif tipo == 'act_equipo':
                cur.execute('INSERT INTO act_equipo (usuario_idusuario,materias_idmaterias,fecha,comodo_equipo,funcionamiento) VALUES (%s,%s,%s,%s,%s)',
                            (self.usuario_id, mid, fecha, 3, 3))
            elif tipo == 'act_tarea':
                cur.execute('INSERT INTO act_tarea (usuario_idusuario,materias_idmaterias,fecha,tiempo_estimado,compleja,instrucciones_claras) VALUES (%s,%s,%s,%s,%s,%s)',
                            (self.usuario_id, mid, fecha, tiempo, 3, 1))
            conn.commit()
            cur.close()
            conn.close()
            self.status.configure(text='Actividad registrada.')
        except Exception as e:
            print(e)
            self.status.configure(text='Error al registrar.')


class GestorVentanas:
    """Gestor que mantiene y muestra ventanas (frames)."""
    def __init__(self, master, usuario=None):
        self.master = master
        self.usuario = usuario
        self.usuario_id = None
        self._resolve_usuario_id()

        self.container = Frame(master)
        self.container.pack(expand=True, fill='both')

        self.windows = {}
        self._build_nav()
        self._create_windows()

    def _resolve_usuario_id(self):
        if not self.usuario:
            return
        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute('SELECT idusuario FROM usuario WHERE nombre=%s OR boleta=%s', (self.usuario, self.usuario))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if row:
                self.usuario_id = row[0]
        except Exception as e:
            print(e)

    def _build_nav(self):
        nav = Frame(self.master)
        nav.pack(pady=6, fill='x')
        Button(nav, text='Base', command=lambda: self.show('base')).pack(side='left', padx=6)
        Button(nav, text='Seguimiento', command=lambda: self.show('seguimiento')).pack(side='left', padx=6)
        Button(nav, text='Actividades', command=lambda: self.show('actividades')).pack(side='left', padx=6)

    def _create_windows(self):
        self.windows['base'] = VentanaBase(self.container, self, usuario_id=self.usuario_id)
        self.windows['seguimiento'] = VentanaSeguimiento(self.container, self, usuario_id=self.usuario_id)
        self.windows['actividades'] = VentanaActividades(self.container, self, usuario_id=self.usuario_id)

    def show(self, name):
        for w in self.windows.values():
            w.pack_forget()
        win = self.windows.get(name)
        if win:
            win.show()


if __name__ == '__main__':
    app = Tk()
    app.geometry('800x650')
    app.title('AyDS - Encuestas (refactor)')
    gestor = GestorVentanas(app, usuario=None)
    app.mainloop()
