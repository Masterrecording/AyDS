import pymysql as sql
import json
from datetime import datetime

from tkinter import messagebox
from customtkinter import CTk as Tk
from customtkinter import CTkFrame as Frame
from customtkinter import CTkLabel as Label
from customtkinter import CTkEntry as Entry
from customtkinter import CTkOptionMenu as OptionMenu
from customtkinter import CTkButton as Button
from customtkinter import CTkFont as Font
from customtkinter import CTkScrollableFrame as ScrollableFrame
import customtkinter as ctk
from tkinter.messagebox import showerror, askokcancel

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

class VistaPrincipalEstudiante(Ventana):
    def __init__(self, master, boleta=None, **kwargs):
        super().__init__(master, **kwargs)
        self.boleta = boleta
        self.build()

    def build(self):
        for widget in self.winfo_children():
            widget.destroy()

        scroll = ScrollableFrame(self)
        scroll.pack(expand=True, fill='both', padx=15, pady=15)

        self._mostrar_info_estudiante(scroll)
        self._mostrar_grafica_estres(scroll)
        self._mostrar_pendientes(scroll)
        self._mostrar_boton_agregar(scroll)

    def _mostrar_info_estudiante(self, parent):
        try:
            conn = conectar_db()
            cur = conn.cursor()
            
            cur.execute('SELECT nombre FROM usuario WHERE boleta = %s', (self.boleta,))
            nombre_result = cur.fetchone()
            nombre = nombre_result[0] if nombre_result else "Usuario"

            cur.execute('''
                SELECT semestre
                FROM quiz_base
                WHERE usuario_boleta = %s
            ''', (self.boleta,))
            semestre_result = cur.fetchone()
            semestre = semestre_result[0] if semestre_result else "N/A"
            
            cur.close()
            conn.close()
        except Exception as e:
            nombre = "Usuario"
            semestre = "N/A"
            print(e)

        header_frame = Frame(parent)
        header_frame.pack(fill='x', pady=(0, 20))

        Label(header_frame, text=nombre, font=Font(family='Calibri', size=28, weight='bold')).pack(anchor='w')
        Label(header_frame, text=f"Boleta {self.boleta} - Semestre {semestre}", font=Font(size=14), fg_color='gray').pack(anchor='w')

    def _mostrar_grafica_estres(self, parent):
        estres_frame = Frame(parent)
        estres_frame.pack(fill='x', pady=(0, 20))

        Label(estres_frame, text='Estrés Semanal', font=Font(size=14, weight='bold')).pack(anchor='w', pady=(0, 10))

        estres_valor = self._calcular_estres_semanal()
        
        color_mapa = self._obtener_color_estres(estres_valor)
        
        barra_contenedor = Frame(estres_frame, fg_color='gray20', corner_radius=5, height=30)
        barra_contenedor.pack(fill='x', padx=0)

        porcentaje = max(0, min(estres_valor / 100, 1.0))
        barra_relleno = Frame(barra_contenedor, fg_color=color_mapa, corner_radius=5)
        if porcentaje > 0:
            barra_relleno.place(relx=0, rely=0, relwidth=porcentaje, relheight=1)

        Label(estres_frame, text=f'{estres_valor:.1f}%', font=Font(size=12, weight='bold')).pack(anchor='w', pady=(5, 0))

    def _calcular_estres_semanal(self):
        try:
            conn = conectar_db()
            cur = conn.cursor()

            hoy = datetime.now().date()
            hace_7_dias = datetime(hoy.year, hoy.month, hoy.day-7)

            cur.execute(
                '''
                SELECT COALESCE(AVG(prioridad), 0)
                FROM actividades
                WHERE usuario_boleta = %s AND DATE(fecha_entrega) BETWEEN %s AND %s
                ''',
                (self.boleta, hace_7_dias, hoy)
            )
            valor = cur.fetchone()[0] or 0

            cur.close()
            conn.close()

            promedio = valor / 5.0 * 100
            return min(promedio, 100)
        except Exception as e:
            print(e)
            return 0

    def _obtener_color_estres(self, valor):
        if valor < 20:
            return '#00ff00'
        elif valor < 40:
            return '#88ff00'
        elif valor < 60:
            return '#ffff00'
        elif valor < 80:
            return '#ff8800'
        else:
            return '#ff0000'

    def _mostrar_pendientes(self, parent):
        Label(parent, text='Pendientes', font=Font(size=14, weight='bold')).pack(anchor='w', pady=(20, 10))

        try:
            conn = conectar_db()
            cur = conn.cursor()
            
            cur.execute('''
                SELECT p.id_act, p.nombre, m.nombre, p.fecha_entrega, p.estado, p.semestre
                FROM actividades AS p
                JOIN materias m ON p.materias_idmaterias = m.idmaterias
                WHERE p.usuario_boleta = %s AND p.estado != %s
                ORDER BY p.fecha_entrega ASC
            ''', (self.boleta, 'completada'))
            pendientes = cur.fetchall()
            
            cur.close()
            conn.close()
        except Exception as e:
            pendientes = []
            print(e)

        if not pendientes:
            Label(parent, text='No hay pendientes registrados', font=Font(size=12,), text_color='gray').pack(pady=10)
            return

        for pid, nombre, materia, fecha_entrega, estado, semestre in pendientes:
            if semestre == self.resolve_semestre():
                self._crear_tarjeta_pendiente(parent, pid, nombre, materia, fecha_entrega, estado)

    def resolve_semestre(self):
        try:
            boleta = self.boleta
            con = conectar_db()
            cur = con.cursor()
            cur.execute("select semestre from quiz_base where usuario_boleta = %s", args=(str(boleta),))
            semestre = cur.fetchone()[0]
            con.commit()
            con.close()

            return semestre
            
        except Exception as e:
            print(f"Ocurrió un error al obtener el semestre para la lista de pendientes: {e}")

    def _crear_tarjeta_pendiente(self, parent, pid, nombre, materia, fecha_entrega, estado):
        hoy = datetime.now().date()
        if isinstance(fecha_entrega, datetime):
            fecha_entrega = fecha_entrega.date()
        dias_restantes = (fecha_entrega - hoy).days
        
        color = self._obtener_color_pendiente(dias_restantes, estado)

        tarjeta = Frame(parent, fg_color=color, corner_radius=8)
        tarjeta.pack(fill='x', pady=5, padx=5)

        contenido = Frame(tarjeta, fg_color=color)
        contenido.pack(fill='both', expand=True, padx=12, pady=10)

        info_frame = Frame(contenido, fg_color=color)
        info_frame.pack(side='left', fill='both', expand=True)

        Label(info_frame, text=nombre, font=Font(size=12, weight='bold'), fg_color=color).pack(anchor='w')
        Label(info_frame, text=f'{materia} • {dias_restantes} días', font=Font(size=10,), fg_color=color).pack(anchor='w')

        botones_frame = Frame(contenido, fg_color=color)
        botones_frame.pack(side='right')

        Button(botones_frame, text='✓', width=8, fg_color='green', hover_color='darkgreen',
               command=lambda: self._marcar_completada(pid)).pack(side='left', padx=3)
        Button(botones_frame, text='✎', width=8, fg_color='blue', hover_color='darkblue',
               command=lambda: self._editar_pendiente(pid)).pack(side='left', padx=3)

    def _obtener_color_pendiente(self, dias_restantes, estado):
        if estado == 'completada':
            return '#003300'
        elif dias_restantes <= 0:
            return '#cc0000'
        elif dias_restantes <= 1:
            return '#ff6600'
        elif dias_restantes <= 3:
            return '#ffff00'
        elif dias_restantes <= 7:
            return '#ccff00'
        else:
            return '#00cc00'

    def _marcar_completada(self, pid):
        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute('UPDATE actividades SET estado = %s WHERE id_act = %s', ('completada', pid))
            conn.commit()
            cur.close()
            conn.close()
            self.build()
        except Exception as e:
            print(e)
            messagebox.showerror("Error", f"Error al actualizar: {e}")

    def _editar_pendiente(self, pid):
        messagebox.showinfo("Editar", "Funcionalidad en desarrollo")

    def _mostrar_boton_agregar(self, parent):
        Button(parent, text='+ Agregar Pendiente', command=self._abrir_agregar_tareas,
               height=40, font=Font(size=14, weight='bold')).pack(fill='x', pady=(20, 0))

    def _abrir_agregar_tareas(self):
        ventana = Tk()
        ventana.geometry("500x600")
        ventana.title("Crear Pendiente")
        
        from App.add_task import AddTaskView
        view = AddTaskView(ventana, self.gestor, boleta=self.boleta, callback=self.build)
        view.pack(expand=True, fill='both')
        ventana.mainloop()
class VentanaBase(Ventana):
    """Formulario simplificado que mapea a la tabla quiz_base del script SQL."""
    def __init__(self, master, gestor, boleta=None, **kwargs):
        super().__init__(master, gestor, **kwargs)
        self.boleta = boleta
        Label(self, text='Datos iniciales (quiz_base)', font=Font(family='Calibri', size=16, weight='bold')).pack(pady=8)

        campos = [
            ('grupo', 'Grupo', 0),
            ('carrera', 'Nombre de tu carrera', 0),
            ('universidad', 'Nombre de la universidad en la que estudias', 0),
            ('sit_acad', 'Situación académica', 0),
            ('semestre', 'Semestre', 10),
            ('propenso_estres', 'Del 1 al 5 ¿Qué tan fácil te estresas?', 5)
        ]

        
        
        self.entries = {}
        frame = ScrollableFrame(self)
        frame.pack(expand=True, fill='both', padx=8, pady=8)
        for key, label, number in campos:
            if number == 0:
                Label(frame, text=label).pack(anchor='w', padx=6, pady=(6, 0))
                e = Entry(frame)
                e.pack(fill='x', padx=6, pady=(0, 6))
                self.entries[key] = e
            else:
                Label(frame, text=label).pack(anchor='w', padx=6, pady=(6, 0))
                values = [str(i) for i in range(1, number + 1)]
                e = OptionMenu(frame, values=values)
                e.pack(fill='x', padx=6, pady=(0, 6))
                self.entries[key] = e
                
                
        self.resolve_materias()
        self.crear_vista_materias()
                
                
        self.button_frame = Frame(self)
        self.button_frame.pack(pady=(20,10))
        
        Button(self.button_frame, text='Guardar', command=self.guardar).pack(pady=6, side='left', padx=5)
        Button(self.button_frame, text="Añadir Materia", command=self.añadir_materia).pack(pady=6, side='left', padx=5)
        self.status = Label(self, text='')
        self.status.pack()
        

        if self.boleta:
            self.cargar()
        
    def eliminar_materia(self, nombre:str, *args, **kwargs):
        try:
            conn = conectar_db()
            cur = conn.cursor()
            
            query = "DELETE FROM materias WHERE usuario_boleta = %s  AND nombre = %s;"
            cur.execute(query=query, args=(str(self.boleta), nombre))
            conn.commit()
            conn.close()
            
            self.actualizar_materias()
            
            print(f"Se ha eliminado la materia: {nombre}\nDel usuario con boleta: {self.boleta}")
            
        except Exception as e:
            if "Cannot delete or update a parent row:" in str(e):
                showerror("ERROR", "No puedes eliminar una materia de la cuál tienes pendientes")
            print(f"Error al eliminar materia: {e}")
    
    def añadir_materia(self, *args, **kwargs):
        from App import menumateria
        menumateria.AgregarMateriaView(boleta=self.boleta, reload_function=self.actualizar_materias).mainloop()
    
    def resolve_semestre(self):
        try:
            
            con = conectar_db()
            cur = con.cursor()
            cur.execute("select semestre from quiz_base where usuario_boleta=%s", args=(str(self.boleta),))
            semestre = cur.fetchone()[0]
            
            if not semestre: return showerror("Bienvenido, antes que nada completa la encuesta base para poder continuar")
            print(f"Semestre de el usuario {self.boleta} es: ")
            print(semestre)
            
            self.semestre = semestre
            
        except Exception as e:
            print(f"Se ha producido un error al obtener el semestre actual: {e}")
    
    def resolve_materias(self):
        try:
            self.resolve_semestre()
            conn = conectar_db()
            cur = conn.cursor()
            query = "Select nombre from materias where usuario_boleta = %s AND semestre = %s"
            cur.execute(query=query, args=(self.boleta, self.semestre))
            response = cur.fetchall()
            print(f"Respuesta de la bd ante las materias: {response}\n boleta: {self.boleta}\nsemestre: {self.semestre}")
            if not response: 
                self.materias = [("No hay materias...")]
                return
            self.materias = []
            for materia in response:
                self.materias.append(materia[0])
                
        except Exception as e:
            print(f"Se ha producido un error al cargar las materias: {e}")
            self.materias = [("No hay materias...")]
    
    def crear_vista_materias(self):

        self.frame_materias = ctk.CTkScrollableFrame(self, height=30)
        self.frame_materias.pack(fill="x", expand=False, padx=10, pady=0)

        self.actualizar_materias()


    def actualizar_materias(self):
        self.resolve_materias()
        
        # Limpiar filas actuales
        for widget in self.frame_materias.winfo_children():
            widget.destroy()

        # Crear filas nuevas
        for materia in self.materias:

            fila = ctk.CTkFrame(self.frame_materias)
            fila.pack(fill="x", pady=2)

            ctk.CTkLabel(
                fila,
                text=materia,
                anchor="w"
            ).pack(
                side="left",
                fill="x",
                expand=True,
                padx=(10, 5),
                pady=5
            )

            
            if materia != "No hay materias...":
                ctk.CTkButton(
                    fila,
                    text="✕",
                    width=35,
                    fg_color="red",
                    hover_color="#B00000",
                    command=lambda m=materia: self.eliminar_materia(m)
                ).pack(
                    side="right",
                    padx=5,
                    pady=5
                )

    def cargar(self):
        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute('SELECT grupo, carrera, universidad, sit_acad, semestre, propenso_estres FROM quiz_base WHERE usuario_boleta=%s', (self.boleta,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if row:
                for k, v in zip(self.entries.keys(), row):
                    if hasattr(self.entries[k], 'set'):
                        self.entries[k].set(str(v) if v is not None else '')
                    else:
                        self.entries[k].delete(0, 'end')
                        self.entries[k].insert(0, str(v) if v is not None else '')
                self.status.configure(text='Datos cargados.', text_color = 'green')
            else:
                self.status.configure(text='No existen datos previos.', text_color='orange')
        except Exception as e:
            print(e)
            self.status.configure(text='Error al cargar.', text_color='orange')

    def guardar(self):
        print(self.boleta)
        if not self.boleta:
            self.status.configure(text='Usuario no definido.', text_color='orange')
            return
        vals = {k: self.entries[k].get().strip() or None for k in self.entries}
        
        for value in vals.values():
            print(value)
            if value == None:
                return self.status.configure(text="Completa todos los campos antes de guardar", text_color="orange")
        
        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute('SELECT usuario_boleta FROM quiz_base WHERE usuario_boleta=%s', (self.boleta,))
            exists = cur.fetchone()
            if exists:
                cur.execute(
                    '''UPDATE quiz_base SET grupo=%s, carrera=%s, universidad=%s, sit_acad=%s, semestre=%s, propenso_estres=%s, aplicado=TRUE, fecha_aplicacion=%s WHERE usuario_boleta=%s''',
                    (vals['grupo'], vals['carrera'], vals['universidad'], vals['sit_acad'], vals['semestre'], vals['propenso_estres'], datetime.now().date(), str(self.boleta))
                )
            else:
                print("qpdolol")
                cur.execute(
                    '''INSERT INTO quiz_base (usuario_boleta, grupo, carrera, universidad, sit_acad, semestre, propenso_estres, aplicado, fecha_aplicacion) VALUES (%s,%s,%s,%s,%s,%s,%s,TRUE,%s)''',
                    (str(self.boleta), vals['grupo'], vals['carrera'], vals['universidad'], vals['sit_acad'], vals['semestre'], vals['propenso_estres'], datetime.now().date())
                )
            conn.commit()
            cur.close()
            conn.close()
            self.actualizar_materias()
            self.gestor.windows['inicio'].build()
            self.status.configure(text='Guardado exitoso.', text_color='green')
        except Exception as e:
            print(e)
            self.status.configure(text='Error al guardar.', text_color='orange')
            
        


class GestorVentanas:
    """Gestor que mantiene y muestra ventanas (frames)."""
    def __init__(self, master, boleta = None):
        self.master = master
        self.boleta = boleta
        self.nombre = self._resolve_nombre()

        self.container = Frame(master)
        self.container.pack(expand=True, fill='both')

        self.windows = {}
        self._create_windows()
        self._build_nav()

    def _resolve_nombre(self):
        if not self.boleta:
            return None
        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute('SELECT nombre FROM usuario WHERE boleta=%s', (self.boleta,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if row:
                return row[0]
        except Exception as e:
            print(e)
        return None

    def _build_nav(self):
        nav = Frame(self.master)
        nav.pack(pady=6, fill='x')
        Button(nav, text='Inicio', command=lambda: self.show('inicio')).pack(side='left', padx=6)
        Button(nav, text='Datos base', command=lambda: self.show('base')).pack(side='left', padx=6)

    def _create_windows(self):
        self.windows['inicio'] = VistaPrincipalEstudiante(gestor=self, master=self.container, boleta=self.boleta)
        self.windows['base'] = VentanaBase(gestor=self, master=self.container, boleta=self.boleta)

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
    gestor = GestorVentanas(app, boleta='0')
    gestor.show('inicio')
    app.mainloop()
