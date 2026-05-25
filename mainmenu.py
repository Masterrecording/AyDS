import mysql.connector
import tkinter as tk

from customtkinter import CTk as Tk
from customtkinter import CTkFrame as Frame
from customtkinter import CTkLabel as Label
from customtkinter import CTkEntry as Entry
from customtkinter import CTkOptionMenu as OptionMenu
from customtkinter import CTkButton as Button
from customtkinter import CTkFont as Font
from customtkinter import CTkScrollableFrame as ScrollableFrame


def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="monitoreo_estudiantil"
    )


class MainMenu(Frame):
    """Panel principal que muestra y edita encuesta_base, registro de seguimiento y actividades."""
    def __init__(self, master, usuario=None, **kwargs):
        super().__init__(master, **kwargs)
        self.usuario = usuario
        self.id_usuario = None

        self.title = Label(self, text="Encuestas - Usuario: %s" % (self.usuario or "(no definido)"), font=Font(family="Calibri", size=18, weight="bold"))
        self.title.pack(pady=(8, 8))

        
        if self.usuario:
            try:
                conexion = conectar_db()
                cursor = conexion.cursor()
                cursor.execute("SELECT id_usuario FROM usuarios WHERE usuario = %s", (self.usuario,))
                row = cursor.fetchone()
                cursor.close()
                conexion.close()
                if row:
                    self.id_usuario = row[0]
                else:
                    self.title.configure(text=f"Usuario '{self.usuario}' no encontrado.")
            except Exception as e:
                print(e)
                self.title.configure(text="Error conectando a la BD")

        
        nav = Frame(self)
        nav.pack(pady=(4, 6), fill="x")
        Button(nav, text="Base (registro inicial)", command=self.show_base).pack(side="left", padx=6)
        Button(nav, text="Seguimiento", command=self.show_seguimiento).pack(side="left", padx=6)
        Button(nav, text="Actividades", command=self.show_actividades).pack(side="left", padx=6)

        
        self.container = Frame(self)
        self.container.pack(expand=True, fill="both", padx=10, pady=10)

        self.base_frame = Frame(self.container)
        self.seguimiento_frame = Frame(self.container)
        self.actividades_frame = Frame(self.container)

        self._build_base_frame()
        self._build_seguimiento_frame()
        self._build_actividades_frame()

        self.show_base()

    def _build_base_frame(self):
        f = self.base_frame
        Label(f, text="Encuesta base (datos iniciales)").pack(pady=(4, 6))

        
        self.scrollable = ScrollableFrame(f)
        self.scrollable.pack(expand=True, fill="both")

        parent = self.scrollable
        self.eb_entries = {}
        campos = [
            ("boleta", "Boleta"),
            ("nombre", "Nombre completo"),
            ("id_carrera", "ID Carrera (num)"),
            ("semestre_cursado", "Semestre"),
            ("grupo", "Grupo"),
            ("situacion_escolar", "Situación escolar (Regular/Irregular/Baja temporal/Dictaminado/Otro)"),
            ("num_materias", "Número de materias"),
            ("id_unidad", "ID Unidad académica"),
            ("percepcion_animica", "Percepción anímica (1-5)"),
            ("motivacion_academica", "Motivación académica (1-5)"),
            ("tolerancia_estres", "Tolerancia al estrés (1-5)"),
            ("horas_hobbies", "¿Cuántas horas a la semana le dedicas a tus hobbies?")
        ]
        for key, label in campos:
            Label(parent, text=label).pack(anchor="w", padx=6, pady=(6, 0))
            e = Entry(parent)
            e.pack(fill="x", pady=(0, 6), padx=6)
            self.eb_entries[key] = e

        Button(parent, text="Guardar encuesta base", command=self.guardar_encuesta_base).pack(pady=8)
        self.base_status = Label(parent, text="")
        self.base_status.pack()

    def mostrar_encuesta_base(self):
        if not self.id_usuario:
            self.base_status.configure(text="Usuario no definido.")
            return
        try:
            conexion = conectar_db()
            cursor = conexion.cursor()
            cursor.execute("SELECT boleta,nombre,id_carrera,semestre_cursado,grupo,situacion_escolar,num_materias,id_unidad,percepcion_animica,motivacion_academica,tolerancia_estres,horas_hobbies FROM encuesta_base WHERE id_usuario=%s", (self.id_usuario,))
            row = cursor.fetchone()
            cursor.close()
            conexion.close()
            if row:
                keys = ["boleta","nombre","id_carrera","semestre_cursado","grupo","situacion_escolar","num_materias","id_unidad","percepcion_animica","motivacion_academica","tolerancia_estres","horas_hobbies"]
                for k,v in zip(keys, row):
                    self.eb_entries[k].delete(0, 'end')
                    self.eb_entries[k].insert(0, str(v) if v is not None else "")
                self.base_status.configure(text="Encuesta base cargada.")
            else:
                self.base_status.configure(text="No hay encuesta base registrada. Complete el formulario.")
        except Exception as e:
            print(e)
            self.base_status.configure(text="Error al leer la BD.")

    def guardar_encuesta_base(self):
        if not self.id_usuario:
            self.base_status.configure(text="Usuario no definido.")
            return
        data = {k: self.eb_entries[k].get().strip() for k in self.eb_entries}
        try:
            conexion = conectar_db()
            cursor = conexion.cursor()
            # Verificar existencia
            cursor.execute("SELECT id_encuesta_base FROM encuesta_base WHERE id_usuario=%s", (self.id_usuario,))
            row = cursor.fetchone()
            if row:
                # UPDATE
                query = ("UPDATE encuesta_base SET boleta=%s,nombre=%s,id_carrera=%s,semestre_cursado=%s,grupo=%s,situacion_escolar=%s,num_materias=%s,id_unidad=%s,percepcion_animica=%s,motivacion_academica=%s,tolerancia_estres=%s,horas_hobbies=%s WHERE id_usuario=%s")
                params = (data['boleta'], data['nombre'], data['id_carrera'] or None, data['semestre_cursado'] or None, data['grupo'], data['situacion_escolar'], data['num_materias'] or None, data['id_unidad'] or None, data['percepcion_animica'] or None, data['motivacion_academica'] or None, data['tolerancia_estres'] or None, data['horas_hobbies'] or None, self.id_usuario)
                cursor.execute(query, params)
                conexion.commit()
                self.base_status.configure(text="Encuesta base actualizada.")
            else:
                # INSERT
                query = ("INSERT INTO encuesta_base (id_usuario,boleta,nombre,id_carrera,semestre_cursado,grupo,situacion_escolar,num_materias,id_unidad,percepcion_animica,motivacion_academica,tolerancia_estres,horas_hobbies) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
                params = (self.id_usuario, data['boleta'], data['nombre'], data['id_carrera'] or None, data['semestre_cursado'] or None, data['grupo'], data['situacion_escolar'], data['num_materias'] or None, data['id_unidad'] or None, data['percepcion_animica'] or None, data['motivacion_academica'] or None, data['tolerancia_estres'] or None, data['horas_hobbies'] or None)
                cursor.execute(query, params)
                conexion.commit()
                self.base_status.configure(text="Encuesta base registrada.")
            cursor.close()
            conexion.close()
        except Exception as e:
            print(e)
            self.base_status.configure(text="Error al guardar.")

    def _build_seguimiento_frame(self):
        f = self.seguimiento_frame
        Label(f, text="Encuesta de seguimiento (frecuente)").pack(pady=(4,6))
        self.seg_options = {}
        choices = ["1","2","3","4","5"]
        for key,label_text in [("estado_animico","Estado anímico (1-5):"),("nivel_motivacional","Nivel motivacional (1-5):"),("estres_semanal_calc","Estrés semanal (1-5):")]:
            Label(f, text=label_text).pack(anchor="w")
            opt = OptionMenu(f, values=choices)
            opt.set("3")
            opt.pack(fill="x", pady=(0,6))
            self.seg_options[key]=opt
        Button(f, text="Guardar seguimiento", command=self.guardar_seguimiento).pack(pady=6)
        self.seg_status = Label(f,text="")
        self.seg_status.pack()

    def guardar_seguimiento(self):
        if not self.id_usuario:
            self.seg_status.configure(text="Usuario no definido.")
            return
        try:
            vals = [int(self.seg_options[k].get()) for k in self.seg_options]
            conexion = conectar_db()
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO encuesta_seguimiento (id_usuario,estado_animico,nivel_motivacional,estres_semanal_calc) VALUES (%s,%s,%s,%s)", (self.id_usuario, vals[0], vals[1], vals[2]))
            conexion.commit()
            cursor.close()
            conexion.close()
            self.seg_status.configure(text="Registro de seguimiento guardado.")
        except Exception as e:
            print(e)
            self.seg_status.configure(text="Error al guardar seguimiento.")

    
    def _build_actividades_frame(self):
        f = self.actividades_frame
        Label(f, text="Registrar actividad (Examen/Proyecto/TrabajoEquipo/TrabajoCLase/Tarea)").pack(pady=(4,6))
        Label(f, text="Tipo de actividad:").pack(anchor="w")
        tipos = ['Examen','Proyecto','TrabajoEquipo','TrabajoCLase','Tarea']
        self.tipo_act = OptionMenu(f, values=tipos)
        self.tipo_act.set(tipos[0])
        self.tipo_act.pack(fill="x", pady=(0,6))

        Label(f, text="ID Materia (num):").pack(anchor="w")
        self.act_id_materia = Entry(f)
        self.act_id_materia.pack(fill="x", pady=(0,6))

        Label(f, text="Tiempo real horas (0-24):").pack(anchor="w")
        self.act_tiempo_real = Entry(f)
        self.act_tiempo_real.pack(fill="x", pady=(0,6))

        Label(f, text="Estrés real (1-5):").pack(anchor="w")
        self.act_estres_real = Entry(f)
        self.act_estres_real.pack(fill="x", pady=(0,6))

        # Campos específicos que se mostrarán según tipo
        self.specific_frame = Frame(f)
        self.specific_frame.pack(fill="x", pady=(6,6))
        self.specific_entries = {}

        Button(f, text="Registrar actividad", command=self.guardar_actividad).pack(pady=6)
        self.act_status = Label(f, text="")
        self.act_status.pack()

    def guardar_actividad(self):
        if not self.id_usuario:
            self.act_status.configure(text="Usuario no definido.")
            return
        tipo = self.tipo_act.get()
        try:
            id_materia = int(self.act_id_materia.get())
            tiempo_real = float(self.act_tiempo_real.get())
            estres_real = int(self.act_estres_real.get())
        except Exception:
            self.act_status.configure(text="Valores inválidos en campos básicos.")
            return
        try:
            conexion = conectar_db()
            cursor = conexion.cursor()
            
            cursor.execute("INSERT INTO actividades (id_usuario,id_materia,tipo_actividad,tiempo_real_horas,estres_real) VALUES (%s,%s,%s,%s,%s)", (self.id_usuario, id_materia, tipo, tiempo_real, estres_real))
            id_actividad = cursor.lastrowid

            
            if tipo == 'Examen':
                
                if 'tiempo_esperado_hrs' in self.specific_entries:
                    tiempo_esp = float(self.specific_entries['tiempo_esperado_hrs'].get() or 1)
                else:
                    tiempo_esp = 1.0
                if 'dificultad_esperada' in self.specific_entries:
                    dificultad = int(self.specific_entries['dificultad_esperada'].get() or 3)
                else:
                    dificultad = 3
                if 'estres_esperado' in self.specific_entries:
                    estres_esp = int(self.specific_entries['estres_esperado'].get() or 3)
                else:
                    estres_esp = 3
                cursor.execute("INSERT INTO examenes (id_actividad,tiempo_esperado_hrs,dificultad_esperada,estres_esperado) VALUES (%s,%s,%s,%s)", (id_actividad, tiempo_esp, dificultad, estres_esp))

            elif tipo == 'Proyecto':
                if 'tiempo_esperado_hrs' in self.specific_entries:
                    tiempo_esp = float(self.specific_entries['tiempo_esperado_hrs'].get() or 1)
                else:
                    tiempo_esp = 1.0
                if 'dificultad_esperada' in self.specific_entries:
                    dificultad = int(self.specific_entries['dificultad_esperada'].get() or 3)
                else:
                    dificultad = 3
                if 'trabajo_en_equipo' in self.specific_entries:
                    trabajo_equipo = int(self.specific_entries['trabajo_en_equipo'].get() or 0)
                else:
                    trabajo_equipo = 0
                if 'estres_esperado' in self.specific_entries:
                    estres_esp = int(self.specific_entries['estres_esperado'].get() or 3)
                else:
                    estres_esp = 3
                cursor.execute("INSERT INTO proyectos (id_actividad,tiempo_esperado_hrs,dificultad_esperada,trabajo_en_equipo,estres_esperado) VALUES (%s,%s,%s,%s,%s)", (id_actividad, tiempo_esp, dificultad, trabajo_equipo, estres_esp))

            elif tipo == 'TrabajoEquipo':
                if 'funcionalidad_aporte_hrs' in self.specific_entries:
                    funcionalidad_aporte = float(self.specific_entries['funcionalidad_aporte_hrs'].get() or 0)
                else:
                    funcionalidad_aporte = 0.0
                if 'comodidad_equipo' in self.specific_entries:
                    comodidad = int(self.specific_entries['comodidad_equipo'].get() or 3)
                else:
                    comodidad = 3
                if 'funcionalidad_equipo' in self.specific_entries:
                    funcionalidad = int(self.specific_entries['funcionalidad_equipo'].get() or 3)
                else:
                    funcionalidad = 3
                cursor.execute("INSERT INTO trabajos_equipo (id_actividad,funcionalidad_aporte_hrs,comodidad_equipo,funcionalidad_equipo) VALUES (%s,%s,%s,%s)", (id_actividad, funcionalidad_aporte, comodidad, funcionalidad))

            elif tipo == 'TrabajoCLase':
                if 'tiempo_esperado_hrs' in self.specific_entries:
                    tiempo_esp = float(self.specific_entries['tiempo_esperado_hrs'].get() or 0)
                else:
                    tiempo_esp = 0.0
                if 'dificultad_esperada' in self.specific_entries:
                    dificultad = int(self.specific_entries['dificultad_esperada'].get() or 3)
                else:
                    dificultad = 3
                cursor.execute("INSERT INTO trabajos_clase (id_actividad,tiempo_esperado_hrs,dificultad_esperada) VALUES (%s,%s,%s)", (id_actividad, tiempo_esp, dificultad))

            elif tipo == 'Tarea':
                if 'tiempo_esperado_hrs' in self.specific_entries:
                    tiempo_esp = float(self.specific_entries['tiempo_esperado_hrs'].get() or 0)
                else:
                    tiempo_esp = 0.0
                if 'estres_esperado' in self.specific_entries:
                    estres_esp = int(self.specific_entries['estres_esperado'].get() or 3)
                else:
                    estres_esp = 3
                if 'claridad_tema' in self.specific_entries:
                    claridad = int(self.specific_entries['claridad_tema'].get() or 3)
                else:
                    claridad = 3
                cursor.execute("INSERT INTO tareas (id_actividad,tiempo_esperado_hrs,estres_esperado,claridad_tema) VALUES (%s,%s,%s,%s)", (id_actividad, tiempo_esp, estres_esp, claridad))

            conexion.commit()
            cursor.close()
            conexion.close()
            self.act_status.configure(text="Actividad registrada.")
        except Exception as e:
            print(e)
            self.act_status.configure(text="Error al registrar actividad.")

    
    def _on_mousewheel(self, event):
        
        try:
            delta = int(-1 * (event.delta / 120))
        except Exception:
            if getattr(event, 'num', None) == 4:
                delta = -1
            elif getattr(event, 'num', None) == 5:
                delta = 1
            else:
                delta = 0
        try:
            self.base_canvas.yview_scroll(delta, "units")
        except Exception:
            pass

    def clear_container(self):
        for w in self.container.winfo_children():
            w.pack_forget()

    def show_base(self):
        self.clear_container()
        self.base_frame.pack(expand=True, fill="both")
        self.mostrar_encuesta_base()

    def show_seguimiento(self):
        self.clear_container()
        self.seguimiento_frame.pack(expand=True, fill="both")

    def show_actividades(self):
        self.clear_container()
        self.actividades_frame.pack(expand=True, fill="both")


if __name__ == "__main__":
    app = Tk()
    app.geometry("700x600")
    app.title("Menu - Encuestas")
    main_menu = MainMenu(app, usuario=None)
    main_menu.pack(expand=True, fill="both")
    app.mainloop()
