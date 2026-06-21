import json
from datetime import datetime, date
from tkinter import messagebox
from tkinter.messagebox import showerror, askokcancel

from customtkinter import CTk as Tk
from customtkinter import CTkFrame as Frame
from customtkinter import CTkLabel as Label
from customtkinter import CTkEntry as Entry
from customtkinter import CTkOptionMenu as OptionMenu
from customtkinter import CTkButton as Button
from customtkinter import CTkFont as Font
from customtkinter import CTkScrollableFrame as ScrollableFrame
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


from App.utils import conectar_db, get_semestre, get_rol
from App.estres import (
    calcular_estres,
    registrar_historial,
    obtener_historial,
    generar_recomendaciones,
)

class Ventana(Frame):
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

        self._estres_valor, self._estres_nivel = registrar_historial(self.boleta)

        self._mostrar_info_estudiante(scroll)
        self._mostrar_estres(scroll)
        self._mostrar_grafica(scroll)
        self._mostrar_recomendaciones(scroll)
        self._mostrar_pendientes(scroll)
        self._mostrar_boton_agregar(scroll)

    def _mostrar_info_estudiante(self, parent):
        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute('SELECT nombre FROM usuario WHERE boleta = %s', (self.boleta,))
            row = cur.fetchone()
            nombre = row[0] if row else 'Usuario'
            cur.close()
            conn.close()
        except Exception as e:
            nombre = 'Usuario'
            print(e)

        semestre = get_semestre(self.boleta) or 'N/A'

        header_frame = Frame(parent)
        header_frame.pack(fill='x', pady=(0, 20))

        Label(header_frame, text=nombre,
              font=Font(family='Calibri', size=28, weight='bold')).pack(anchor='w')
        Label(header_frame,
              text=f'Boleta {self.boleta} - Semestre {semestre}',
              font=Font(size=14), fg_color='gray').pack(anchor='w')

    def _mostrar_estres(self, parent):
        estres_frame = Frame(parent)
        estres_frame.pack(fill='x', pady=(0, 10))

        valor = self._estres_valor
        nivel = self._estres_nivel
        color = self._color_estres(valor)

        Label(estres_frame, text='Nivel de Estrés Actual',
              font=Font(size=14, weight='bold')).pack(anchor='w', pady=(0, 6))

        barra_cont = Frame(estres_frame, fg_color='gray20', corner_radius=5, height=30)
        barra_cont.pack(fill='x')

        porc = max(0, min(valor / 100, 1.0))
        if porc > 0:
            Frame(barra_cont, fg_color=color, corner_radius=5).place(
                relx=0, rely=0, relwidth=porc, relheight=1)

        Label(estres_frame,
              text=f'{valor}/100 — {nivel}',
              font=Font(size=12, weight='bold'),
              text_color=color).pack(anchor='w', pady=(4, 0))

    def _mostrar_grafica(self, parent):
        grafica_frame = Frame(parent)
        grafica_frame.pack(fill='x', pady=(0, 20))

        Label(grafica_frame, text='Historial de Estrés (últimos 30 días)',
              font=Font(size=13, weight='bold')).pack(anchor='w', pady=(0, 6))

        historial = obtener_historial(self.boleta, dias=30)

        if not historial:
            Label(grafica_frame,
                  text='Sin historial todavía. Los datos aparecerán con el uso.',
                  text_color='gray', font=Font(size=11)).pack(anchor='w')
            return

        fechas = [str(f) for f, _ in historial]
        valores = [v for _, v in historial]
        
        if self._estres_valor > 0:
            hoy_str = str(date.today())
            if not fechas or fechas[-1] != hoy_str:
                fechas.append(hoy_str)
                valores.append(self._estres_valor)

        fig = Figure(figsize=(6, 2.2), dpi=90, facecolor='#2b2b2b')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#2b2b2b')

        ax.plot(fechas, valores, color='#3d8ef0', linewidth=2, marker='o',
                markersize=5, markerfacecolor='white')
        ax.fill_between(range(len(valores)), valores, alpha=0.15, color='#3d8ef0')

        ax.axhline(75, color='#ff2222', linewidth=0.8, linestyle='--', alpha=0.6)
        ax.axhline(50, color='#ff8800', linewidth=0.8, linestyle='--', alpha=0.6)
        ax.axhline(25, color='#ffff00', linewidth=0.8, linestyle='--', alpha=0.6)

        ax.set_ylim(0, 100)
        ax.set_xlim(-0.3, len(fechas) - 0.7)
        ax.set_xticks(range(len(fechas)))
        ax.set_xticklabels(
            [f[-5:] for f in fechas],  # solo MM-DD
            rotation=45, ha='right', fontsize=7, color='#cccccc'
        )
        ax.tick_params(axis='y', colors='#cccccc', labelsize=8)
        ax.spines[:].set_color('#444444')
        ax.yaxis.label.set_color('#cccccc')
        ax.set_ylabel('Estrés', color='#cccccc', fontsize=9)
        fig.tight_layout(pad=0.5)

        canvas = FigureCanvasTkAgg(fig, master=grafica_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='x')

    def _mostrar_recomendaciones(self, parent):
        recs = generar_recomendaciones(self.boleta)

        rec_frame = Frame(parent, fg_color='gray20', corner_radius=8)
        rec_frame.pack(fill='x', pady=(0, 20))

        Label(rec_frame, text='Recomendaciones',
              font=Font(size=13, weight='bold')).pack(anchor='w', padx=12, pady=(10, 4))

        for rec in recs:
            Label(rec_frame, text=rec, font=Font(size=11),
                  wraplength=680, justify='left',
                  fg_color='gray20').pack(anchor='w', padx=14, pady=2)

        Label(rec_frame, text='').pack(pady=4)

    def _mostrar_pendientes(self, parent):
        Label(parent, text='Pendientes',
              font=Font(size=14, weight='bold')).pack(anchor='w', pady=(20, 10))

        semestre = get_semestre(self.boleta)

        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute(
                '''SELECT p.id_act, p.nombre, m.nombre, p.fecha_entrega, p.estado, p.semestre, p.tipo_actividad
                   FROM actividades AS p
                   JOIN materias m ON p.materias_idmaterias = m.idmaterias
                   WHERE p.usuario_boleta = %s AND p.estado != %s
                   ORDER BY p.fecha_entrega ASC''',
                (self.boleta, 'completada')
            )
            pendientes = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            pendientes = []
            print(e)

        pendientes_semestre = [p for p in pendientes if p[5] == semestre]

        if not pendientes_semestre:
            Label(parent,
                  text='No hay pendientes registrados para el semestre actual.',
                  font=Font(size=12), text_color='gray').pack(pady=10)
            return

        for pid, nombre, materia, fecha_entrega, estado, _, tipo in pendientes_semestre:
            self._crear_tarjeta_pendiente(parent, pid, nombre, materia, fecha_entrega, estado, tipo)

    def _crear_tarjeta_pendiente(self, parent, pid, nombre, materia, fecha_entrega, estado, tipo):
        hoy = date.today()
        if isinstance(fecha_entrega, datetime):
            fecha_entrega = fecha_entrega.date()
        dias_restantes = (fecha_entrega - hoy).days

        color = self._color_pendiente(dias_restantes, estado)

        tarjeta = Frame(parent, fg_color=color, corner_radius=8)
        tarjeta.pack(fill='x', pady=5, padx=5)

        contenido = Frame(tarjeta, fg_color=color)
        contenido.pack(fill='both', expand=True, padx=12, pady=10)

        info_frame = Frame(contenido, fg_color=color)
        info_frame.pack(side='left', fill='both', expand=True)

        tipo_txt = f'[{tipo}] ' if tipo else ''
        Label(info_frame, text=f'{tipo_txt}{nombre}',
              font=Font(size=12, weight='bold'), fg_color=color).pack(anchor='w')
        Label(info_frame,
              text=f'{materia} • {dias_restantes} días',
              font=Font(size=10), fg_color=color).pack(anchor='w')

        botones_frame = Frame(contenido, fg_color=color)
        botones_frame.pack(side='right')

        Button(botones_frame, text='✓', width=8,
               fg_color='green', hover_color='darkgreen',
               command=lambda p=pid: self._marcar_completada(p)
               ).pack(side='left', padx=3)
        Button(botones_frame, text='✎', width=8,
               fg_color='blue', hover_color='darkblue',
               command=lambda p=pid: self._editar_pendiente(p)
               ).pack(side='left', padx=3)

    def _marcar_completada(self, pid):
        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute('UPDATE actividades SET estado = %s WHERE id_act = %s',
                        ('completada', pid))
            conn.commit()
            cur.close()
            conn.close()
            self.build()
        except Exception as e:
            print(e)
            messagebox.showerror('Error', f'Error al actualizar: {e}')

    def _editar_pendiente(self, pid):
        from App.edit_task import EditTaskView
        ventana = Tk()
        ventana.geometry('500x520')
        ventana.title('Editar Pendiente')
        EditTaskView(ventana, boleta=self.boleta, id_act=pid,
                     callback=self.build).pack(expand=True, fill='both')
        ventana.mainloop()

    def _mostrar_boton_agregar(self, parent):
        Button(parent, text='+ Agregar Pendiente',
               command=self._abrir_agregar_tareas,
               height=40, font=Font(size=14, weight='bold')
               ).pack(fill='x', pady=(20, 0))

    def _abrir_agregar_tareas(self):
        ventana = Tk()
        ventana.geometry('500x600')
        ventana.title('Crear Pendiente')
        from App.add_task import AddTaskView
        AddTaskView(ventana, self.gestor, boleta=self.boleta,
                    callback=self.build).pack(expand=True, fill='both')
        ventana.mainloop()

    # ── Helpers de color ──────────────────────────────────────

    def _color_estres(self, valor):
        if valor < 25:  return '#00cc44'
        if valor < 50:  return '#ffff00'
        if valor < 75:  return '#ff8800'
        return '#ff2222'

    def _color_pendiente(self, dias_restantes, estado):
        if estado == 'completada':  return '#003300'
        if dias_restantes <= 0:     return '#cc0000'
        if dias_restantes <= 1:     return '#ff6600'
        if dias_restantes <= 3:     return '#ffff00'
        if dias_restantes <= 7:     return '#ccff00'
        return '#00cc00'

class VentanaBase(Ventana):
    def __init__(self, master, gestor, boleta=None, **kwargs):
        super().__init__(master, gestor, **kwargs)
        self.boleta  = boleta
        self.semestre = None
        self._build_form()
        if self.boleta:
            self.cargar()

    def _build_form(self):
        Label(self, text='Datos iniciales (encuesta base)',
              font=Font(family='Calibri', size=16, weight='bold')).pack(pady=8)

        frame = ScrollableFrame(self)
        frame.pack(expand=True, fill='both', padx=8, pady=8)

        self.entries = {}

        texto_libre = [
            ('grupo',       'Grupo'),
            ('carrera',     'Nombre de tu carrera'),
            ('universidad', 'Universidad'),
            ('sit_acad',    'Situación académica (excelente / buena / regular / mala)'),
        ]
        for key, label in texto_libre:
            Label(frame, text=label).pack(anchor='w', padx=6, pady=(6, 0))
            e = Entry(frame)
            e.pack(fill='x', padx=6, pady=(0, 6))
            self.entries[key] = e

        Label(frame, text='Semestre').pack(anchor='w', padx=6, pady=(6, 0))
        e_sem = OptionMenu(frame, values=[str(i) for i in range(1, 11)])
        e_sem.pack(fill='x', padx=6, pady=(0, 6))
        self.entries['semestre'] = e_sem

        escalas = [
            ('propenso_estres',  '¿Qué tan fácil te estresas? (1=nada, 5=mucho)'),
            ('carga_carrera',    '¿Qué tan pesada consideras la carga de tu carrera? (1=liviana, 5=muy pesada)'),
            ('estres_examenes',  '¿Qué tanto te estresan los exámenes? (1=nada, 5=mucho)'),
            ('estres_tareas',    '¿Qué tanto te estresan las tareas? (1=nada, 5=mucho)'),
            ('estres_proyectos', '¿Qué tanto te estresan los proyectos? (1=nada, 5=mucho)'),
        ]
        for key, label in escalas:
            Label(frame, text=label).pack(anchor='w', padx=6, pady=(6, 0))
            e = OptionMenu(frame, values=[str(i) for i in range(1, 6)])
            e.pack(fill='x', padx=6, pady=(0, 6))
            self.entries[key] = e

        Label(frame, text='¿Cuánto tiempo le dedicas a tus hobbies al día?'
              ).pack(anchor='w', padx=6, pady=(6, 0))
        self._hobbies_map = {
            'Menos de 1 hora': 1,
            'Entre 1 y 2 horas': 2,
            'Más de 2 horas': 3,
        }
        self._hobbies_inv = {v: k for k, v in self._hobbies_map.items()}
        e_hob = OptionMenu(frame, values=list(self._hobbies_map.keys()))
        e_hob.set('Entre 1 y 2 horas')
        e_hob.pack(fill='x', padx=6, pady=(0, 6))
        self.entries['tiempo_hobbies'] = e_hob

        self._init_materias(frame)

        btn_frame = Frame(self)
        btn_frame.pack(pady=(20, 10))
        Button(btn_frame, text='Guardar',
               command=self.guardar).pack(pady=6, side='left', padx=5)
        Button(btn_frame, text='Añadir Materia',
               command=self.añadir_materia).pack(pady=6, side='left', padx=5)

        self.status = Label(self, text='')
        self.status.pack()

    def _init_materias(self, frame):
        self.resolve_semestre_silencioso()
        self.resolve_materias()

        Label(frame, text='Materias del semestre actual',
              font=Font(size=11, weight='bold')).pack(anchor='w', padx=6, pady=(10, 2))

        self.frame_materias = ctk.CTkScrollableFrame(frame, height=90)
        self.frame_materias.pack(fill='x', expand=False, padx=6, pady=0)
        self.actualizar_materias()

    def resolve_semestre_silencioso(self):
        self.semestre = get_semestre(self.boleta)

    def resolve_semestre(self):
        self.semestre = get_semestre(self.boleta)
        if not self.semestre:
            showerror('Aviso', 'Completa primero la encuesta base para continuar.')

    def resolve_materias(self):
        self.resolve_semestre_silencioso()
        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute(
                'SELECT nombre FROM materias WHERE usuario_boleta = %s AND semestre = %s',
                (self.boleta, self.semestre)
            )
            rows = cur.fetchall()
            cur.close()
            conn.close()
            self.materias = [r[0] for r in rows] if rows else ['No hay materias...']
        except Exception as e:
            print(f'[VentanaBase] Error al cargar materias: {e}')
            self.materias = ['No hay materias...']

    def actualizar_materias(self):
        self.resolve_materias()
        for w in self.frame_materias.winfo_children():
            w.destroy()
        for materia in self.materias:
            fila = ctk.CTkFrame(self.frame_materias)
            fila.pack(fill='x', pady=2)
            ctk.CTkLabel(fila, text=materia, anchor='w'
                         ).pack(side='left', fill='x', expand=True, padx=(10, 5), pady=5)
            if materia != 'No hay materias...':
                ctk.CTkButton(
                    fila, text='✕', width=35,
                    fg_color='red', hover_color='#B00000',
                    command=lambda m=materia: self.eliminar_materia(m)
                ).pack(side='right', padx=5, pady=5)

    def eliminar_materia(self, nombre):
        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute(
                'DELETE FROM materias WHERE usuario_boleta = %s AND nombre = %s',
                (str(self.boleta), nombre)
            )
            conn.commit()
            conn.close()
            self.actualizar_materias()
        except Exception as e:
            if 'Cannot delete or update a parent row' in str(e):
                showerror('ERROR', 'No puedes eliminar una materia que tiene pendientes.')
            print(f'[VentanaBase] Error al eliminar materia: {e}')

    def añadir_materia(self):
        from App import menumateria
        menumateria.AgregarMateriaView(
            boleta=self.boleta,
            reload_function=self.actualizar_materias
        ).mainloop()

    def cargar(self):
        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute(
                '''SELECT grupo, carrera, universidad, sit_acad, semestre,
                          propenso_estres, carga_carrera, tiempo_hobbies,
                          estres_examenes, estres_tareas, estres_proyectos
                   FROM quiz_base WHERE usuario_boleta = %s''',
                (self.boleta,)
            )
            row = cur.fetchone()
            cur.close()
            conn.close()

            if row:
                (grupo, carrera, univ, sit_acad, semestre,
                 propenso, carga, hobbies, ex_exam, ex_tar, ex_proy) = row

                claves_texto = ['grupo', 'carrera', 'universidad', 'sit_acad']
                valores_texto = [grupo, carrera, univ, sit_acad]
                for k, v in zip(claves_texto, valores_texto):
                    self.entries[k].delete(0, 'end')
                    self.entries[k].insert(0, str(v) if v else '')

                # OptionMenus de escala
                for k, v in [('semestre', semestre),
                              ('propenso_estres', propenso),
                              ('carga_carrera', carga),
                              ('estres_examenes', ex_exam),
                              ('estres_tareas', ex_tar),
                              ('estres_proyectos', ex_proy)]:
                    self.entries[k].set(str(v) if v else '3')

                hobbies_txt = self._hobbies_inv.get(int(hobbies), 'Entre 1 y 2 horas')
                self.entries['tiempo_hobbies'].set(hobbies_txt)

                self.status.configure(text='Datos cargados.', text_color='green')
            else:
                self.status.configure(text='No existen datos previos.', text_color='orange')
        except Exception as e:
            print(e)
            self.status.configure(text='Error al cargar.', text_color='orange')

    def guardar(self):
        if not self.boleta:
            self.status.configure(text='Usuario no definido.', text_color='orange')
            return

        grupo = self.entries['grupo'].get().strip()
        carrera = self.entries['carrera'].get().strip()
        universidad = self.entries['universidad'].get().strip()
        sit_acad = self.entries['sit_acad'].get().strip()
        semestre = self.entries['semestre'].get().strip()
        propenso = self.entries['propenso_estres'].get().strip()
        carga = self.entries['carga_carrera'].get().strip()
        hobbies_txt = self.entries['tiempo_hobbies'].get().strip()
        ex_exam = self.entries['estres_examenes'].get().strip()
        ex_tar = self.entries['estres_tareas'].get().strip()
        ex_proy = self.entries['estres_proyectos'].get().strip()

        if not all([grupo, carrera, universidad, sit_acad, semestre,
                    propenso, carga, ex_exam, ex_tar, ex_proy]):
            self.status.configure(text='Completa todos los campos antes de guardar.',
                                  text_color='orange')
            return

        hobbies = self._hobbies_map.get(hobbies_txt, 2)

        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute(
                'SELECT usuario_boleta FROM quiz_base WHERE usuario_boleta = %s',
                (self.boleta,)
            )
            existe = cur.fetchone()

            if existe:
                cur.execute(
                    '''UPDATE quiz_base
                       SET grupo=%s, carrera=%s, universidad=%s, sit_acad=%s, semestre=%s,
                           propenso_estres=%s, carga_carrera=%s, tiempo_hobbies=%s,
                           estres_examenes=%s, estres_tareas=%s, estres_proyectos=%s,
                           aplicado=TRUE, fecha_aplicacion=%s
                       WHERE usuario_boleta=%s''',
                    (grupo, carrera, universidad, sit_acad, semestre,
                     propenso, carga, hobbies, ex_exam, ex_tar, ex_proy,
                     datetime.now().date(), str(self.boleta))
                )
            else:
                cur.execute(
                    '''INSERT INTO quiz_base
                       (usuario_boleta, grupo, carrera, universidad, sit_acad, semestre,
                        propenso_estres, carga_carrera, tiempo_hobbies,
                        estres_examenes, estres_tareas, estres_proyectos,
                        aplicado, fecha_aplicacion)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,TRUE,%s)''',
                    (str(self.boleta), grupo, carrera, universidad, sit_acad, semestre,
                     propenso, carga, hobbies, ex_exam, ex_tar, ex_proy,
                     datetime.now().date())
                )

            conn.commit()
            cur.close()
            conn.close()

            self.actualizar_materias()
            if 'inicio' in self.gestor.windows:
                self.gestor.windows['inicio'].build()

            self.status.configure(text='Guardado exitoso.', text_color='green')
        except Exception as e:
            print(e)
            self.status.configure(text='Error al guardar.', text_color='orange')

class GestorVentanas:
    def __init__(self, master, boleta=None):
        self.master = master
        self.boleta = boleta
        self.rol    = get_rol(boleta)

        self.container = Frame(master)
        self.container.pack(expand=True, fill='both')

        self.windows = {}
        self._create_windows()
        self._build_nav()

    def _create_windows(self):
        self.windows['inicio'] = VistaPrincipalEstudiante(
            gestor=self, master=self.container, boleta=self.boleta)
        self.windows['base'] = VentanaBase(
            gestor=self, master=self.container, boleta=self.boleta)

        if self.rol == 'Administrador':
            from App.admin_view import VistaAdmin
            self.windows['admin'] = VistaAdmin(
                gestor=self, master=self.container, boleta=self.boleta)

    def _build_nav(self):
        nav = Frame(self.master)
        nav.pack(pady=6, fill='x')
        Button(nav, text='Inicio',
               command=lambda: self.show('inicio')).pack(side='left', padx=6)
        Button(nav, text='Encuesta base',
               command=lambda: self.show('base')).pack(side='left', padx=6)
        if self.rol == 'Administrador':
            Button(nav, text='⚙ Admin', fg_color='#3d5a8a', hover_color='#2e4a7a',
                   command=lambda: self.show('admin')).pack(side='left', padx=6)

    def show(self, name):
        for w in self.windows.values():
            w.pack_forget()
        win = self.windows.get(name)
        if win:
            win.show()


if __name__ == '__main__':
    app = Tk()
    app.geometry('800x750')
    app.title('AyDS')
    gestor = GestorVentanas(app, boleta='2025670127')
    gestor.show('inicio')
    app.mainloop()
