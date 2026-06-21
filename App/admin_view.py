from datetime import datetime

from customtkinter import CTkFrame as Frame
from customtkinter import CTkLabel as Label
from customtkinter import CTkFont as Font
from customtkinter import CTkScrollableFrame as ScrollableFrame
from customtkinter import CTkButton as Button
import customtkinter as ctk

from App.utils import conectar_db
from App.estres import calcular_estres, obtener_historial


class VistaAdmin(Frame):
    """
    Vista exclusiva para administradores.
    Muestra usuarios, información general, estadísticas y estrés.
    """

    def __init__(self, master, gestor, boleta=None, **kwargs):
        super().__init__(master, **kwargs)
        self.gestor = gestor
        self.boleta = boleta
        self._usuario_seleccionado = None
        self.build()

    def show(self):
        self.pack(expand=True, fill='both')

    def close(self):
        self.pack_forget()
        self.destroy()

    def build(self):
        for w in self.winfo_children():
            w.destroy()

        Label(self, text='Panel de Administración',
              font=Font(family='Calibri', size=20, weight='bold')).pack(pady=(12, 4))
        Label(self, text='Vista exclusiva para administradores',
              font=Font(size=11), text_color='gray').pack(pady=(0, 10))

        # Layout: tabla izquierda + detalle derecha
        contenedor = Frame(self)
        contenedor.pack(expand=True, fill='both', padx=12, pady=6)

        # Panel izquierdo — lista de usuarios
        izq = Frame(contenedor, width=260)
        izq.pack(side='left', fill='y', padx=(0, 8))
        izq.pack_propagate(False)

        Label(izq, text='Usuarios registrados',
              font=Font(size=13, weight='bold')).pack(pady=(6, 4))

        self._lista_frame = ScrollableFrame(izq)
        self._lista_frame.pack(expand=True, fill='both')

        # Panel derecho — detalle del usuario seleccionado
        der = Frame(contenedor)
        der.pack(side='left', expand=True, fill='both')

        self._detalle_frame = ScrollableFrame(der)
        self._detalle_frame.pack(expand=True, fill='both')

        self._cargar_lista_usuarios()
        self._mostrar_estadisticas_generales()

    # ─────────────────────────────────────────────────────────
    # Lista de usuarios
    # ─────────────────────────────────────────────────────────

    def _cargar_lista_usuarios(self):
        for w in self._lista_frame.winfo_children():
            w.destroy()

        try:
            conn = conectar_db()
            cur = conn.cursor()
            cur.execute(
                """SELECT u.boleta, u.nombre, r.nombre AS rol
                   FROM usuario u
                   JOIN roles r ON u.roles_idroles = r.idroles
                   ORDER BY r.nombre DESC, u.nombre ASC"""
            )
            usuarios = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            print(e)
            usuarios = []

        for boleta, nombre, rol in usuarios:
            fila = Frame(self._lista_frame, fg_color='gray20', corner_radius=6)
            fila.pack(fill='x', pady=3, padx=4)

            color_rol = '#3d8ef0' if rol == 'Administrador' else '#555555'
            Label(fila, text=rol, font=Font(size=9),
                  fg_color=color_rol, corner_radius=4,
                  text_color='white', width=90).pack(anchor='w', padx=6, pady=(5, 0))
            Label(fila, text=nombre, font=Font(size=11, weight='bold'),
                  fg_color='gray20').pack(anchor='w', padx=6)
            Label(fila, text=f'Boleta: {boleta}', font=Font(size=9),
                  text_color='gray', fg_color='gray20').pack(anchor='w', padx=6, pady=(0, 4))

            Button(fila, text='Ver detalle', height=26,
                   command=lambda b=boleta: self._mostrar_detalle_usuario(b)
                   ).pack(padx=6, pady=(0, 6), anchor='w')

    # ─────────────────────────────────────────────────────────
    # Detalle de usuario seleccionado
    # ─────────────────────────────────────────────────────────

    def _mostrar_detalle_usuario(self, boleta):
        for w in self._detalle_frame.winfo_children():
            w.destroy()

        try:
            conn = conectar_db()
            cur = conn.cursor()

            # Info usuario
            cur.execute(
                """SELECT u.nombre, u.boleta, r.nombre
                   FROM usuario u JOIN roles r ON u.roles_idroles = r.idroles
                   WHERE u.boleta = %s""",
                (boleta,)
            )
            info = cur.fetchone()

            # Quiz base
            cur.execute(
                """SELECT grupo, carrera, universidad, sit_acad, semestre,
                          propenso_estres, carga_carrera, tiempo_hobbies,
                          estres_examenes, estres_tareas, estres_proyectos
                   FROM quiz_base WHERE usuario_boleta = %s""",
                (boleta,)
            )
            quiz = cur.fetchone()

            # Conteo actividades
            cur.execute(
                """SELECT estado, COUNT(*) FROM actividades
                   WHERE usuario_boleta = %s GROUP BY estado""",
                (boleta,)
            )
            act_resumen = cur.fetchall()

            # Materias
            cur.execute(
                "SELECT nombre, dificultad FROM materias WHERE usuario_boleta = %s",
                (boleta,)
            )
            materias = cur.fetchall()

            cur.close()
            conn.close()
        except Exception as e:
            print(e)
            Label(self._detalle_frame, text=f'Error: {e}', text_color='red').pack(pady=10)
            return

        if not info:
            Label(self._detalle_frame, text='Usuario no encontrado.',
                  text_color='orange').pack(pady=10)
            return

        nombre, boleta_d, rol = info

        # ── Encabezado ───────────────────────────────────────
        Label(self._detalle_frame, text=nombre,
              font=Font(family='Calibri', size=18, weight='bold')).pack(anchor='w', pady=(8, 0), padx=10)
        Label(self._detalle_frame, text=f'Boleta: {boleta_d}  •  Rol: {rol}',
              font=Font(size=11), text_color='gray').pack(anchor='w', padx=10)

        sep = Frame(self._detalle_frame, height=2, fg_color='gray40')
        sep.pack(fill='x', padx=10, pady=8)

        # ── Estrés actual ────────────────────────────────────
        valor_estres, nivel = calcular_estres(boleta)

        est_frame = Frame(self._detalle_frame, fg_color='gray20', corner_radius=8)
        est_frame.pack(fill='x', padx=10, pady=4)

        Label(est_frame, text='Estrés actual',
              font=Font(size=12, weight='bold')).pack(anchor='w', padx=10, pady=(8, 2))

        color = self._color_estres(valor_estres)
        barra_cont = Frame(est_frame, fg_color='gray30', corner_radius=5, height=22)
        barra_cont.pack(fill='x', padx=10, pady=(0, 4))
        barra_cont.pack_propagate(False)
        porc = max(0, min(valor_estres / 100, 1.0))
        if porc > 0:
            Frame(barra_cont, fg_color=color, corner_radius=5).place(
                relx=0, rely=0, relwidth=porc, relheight=1)

        Label(est_frame, text=f'{valor_estres}/100 — {nivel}',
              font=Font(size=11), text_color=color).pack(anchor='w', padx=10, pady=(0, 8))

        # ── Historial de estrés (últimos 7 registros) ────────
        historial = obtener_historial(boleta, dias=30)
        if historial:
            Label(self._detalle_frame, text='Historial de estrés (últimos 30 días)',
                  font=Font(size=11, weight='bold')).pack(anchor='w', padx=10, pady=(8, 2))
            hist_scroll = ScrollableFrame(self._detalle_frame, height=90)
            hist_scroll.pack(fill='x', padx=10, pady=(0, 6))
            for fecha, est in reversed(historial[-10:]):
                col = self._color_estres(est)
                fila_h = Frame(hist_scroll, fg_color='gray20', corner_radius=4)
                fila_h.pack(fill='x', pady=1)
                Label(fila_h, text=str(fecha), font=Font(size=10),
                      fg_color='gray20', width=90).pack(side='left', padx=6)
                Label(fila_h, text=f'{est}/100', font=Font(size=10, weight='bold'),
                      text_color=col, fg_color='gray20').pack(side='left')

        # ── Quiz base ────────────────────────────────────────
        if quiz:
            (grupo, carrera, univ, sit_acad, semestre,
             propenso, carga, hobbies, ex_exam, ex_tar, ex_proy) = quiz

            Label(self._detalle_frame, text='Datos académicos',
                  font=Font(size=11, weight='bold')).pack(anchor='w', padx=10, pady=(8, 2))

            datos_acad = Frame(self._detalle_frame, fg_color='gray20', corner_radius=8)
            datos_acad.pack(fill='x', padx=10, pady=4)

            _fila_dato(datos_acad, 'Carrera',          carrera)
            _fila_dato(datos_acad, 'Universidad',      univ)
            _fila_dato(datos_acad, 'Grupo',            grupo)
            _fila_dato(datos_acad, 'Semestre',         str(semestre))
            _fila_dato(datos_acad, 'Situación acad.',  sit_acad)
            _fila_dato(datos_acad, 'Propensión estrés', f'{propenso}/5')
            _fila_dato(datos_acad, 'Carga carrera',    f'{carga}/5')
            tiempo_txt = {1: 'Menos de 1h', 2: '1-2h', 3: 'Más de 2h'}.get(int(hobbies), str(hobbies))
            _fila_dato(datos_acad, 'Tiempo hobbies',   tiempo_txt)
            _fila_dato(datos_acad, 'Estrés exámenes',  f'{ex_exam}/5')
            _fila_dato(datos_acad, 'Estrés tareas',    f'{ex_tar}/5')
            _fila_dato(datos_acad, 'Estrés proyectos', f'{ex_proy}/5')
        else:
            Label(self._detalle_frame,
                  text='Este usuario aún no ha completado la encuesta base.',
                  text_color='orange', font=Font(size=11)).pack(anchor='w', padx=10, pady=8)

        # ── Materias ─────────────────────────────────────────
        if materias:
            Label(self._detalle_frame, text='Materias',
                  font=Font(size=11, weight='bold')).pack(anchor='w', padx=10, pady=(8, 2))
            mat_frame = Frame(self._detalle_frame, fg_color='gray20', corner_radius=8)
            mat_frame.pack(fill='x', padx=10, pady=4)
            for mat_nombre, dif in materias:
                _fila_dato(mat_frame, mat_nombre, f'Dificultad {dif}/5')

        # ── Resumen de actividades ───────────────────────────
        if act_resumen:
            Label(self._detalle_frame, text='Actividades',
                  font=Font(size=11, weight='bold')).pack(anchor='w', padx=10, pady=(8, 2))
            act_frame = Frame(self._detalle_frame, fg_color='gray20', corner_radius=8)
            act_frame.pack(fill='x', padx=10, pady=(4, 12))
            for estado, cnt in act_resumen:
                _fila_dato(act_frame, estado.capitalize(), str(cnt))

    # ─────────────────────────────────────────────────────────
    # Estadísticas generales (panel inicial del detalle)
    # ─────────────────────────────────────────────────────────

    def _mostrar_estadisticas_generales(self):
        for w in self._detalle_frame.winfo_children():
            w.destroy()

        Label(self._detalle_frame, text='Estadísticas generales',
              font=Font(size=14, weight='bold')).pack(pady=(10, 6), padx=10, anchor='w')

        try:
            conn = conectar_db()
            cur = conn.cursor()

            cur.execute("SELECT COUNT(*) FROM usuario WHERE roles_idroles = 1")
            total_alumnos = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM usuario")
            total_usuarios = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM quiz_base WHERE aplicado = TRUE")
            con_encuesta = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM actividades WHERE estado = 'pendiente'")
            act_pendientes = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM actividades WHERE estado = 'completada'")
            act_completadas = cur.fetchone()[0]

            cur.execute(
                "SELECT COUNT(*) FROM actividades WHERE estado != 'completada' AND fecha_entrega < NOW()"
            )
            act_vencidas = cur.fetchone()[0]

            cur.close()
            conn.close()
        except Exception as e:
            print(e)
            Label(self._detalle_frame, text='Error al cargar estadísticas.',
                  text_color='red').pack(pady=10)
            return

        stats_frame = Frame(self._detalle_frame, fg_color='gray20', corner_radius=8)
        stats_frame.pack(fill='x', padx=10, pady=4)

        _fila_dato(stats_frame, 'Total usuarios',       str(total_usuarios))
        _fila_dato(stats_frame, 'Alumnos',              str(total_alumnos))
        _fila_dato(stats_frame, 'Con encuesta base',    str(con_encuesta))
        _fila_dato(stats_frame, 'Act. pendientes',      str(act_pendientes))
        _fila_dato(stats_frame, 'Act. completadas',     str(act_completadas))
        _fila_dato(stats_frame, 'Act. vencidas',        str(act_vencidas))

        Label(self._detalle_frame,
              text='Selecciona un usuario de la lista para ver su detalle.',
              font=Font(size=11), text_color='gray').pack(pady=(16, 4), padx=10)

    def _color_estres(self, valor):
        if valor < 25:  return '#00cc44'
        if valor < 50:  return '#ffff00'
        if valor < 75:  return '#ff8800'
        return '#ff2222'


# ─────────────────────────────────────────────────────────────
# Helper de fila clave-valor reutilizable
# ─────────────────────────────────────────────────────────────

def _fila_dato(parent, clave, valor):
    fila = Frame(parent, fg_color='transparent')
    fila.pack(fill='x', padx=8, pady=2)
    Label(fila, text=clave + ':', font=Font(size=10),
          text_color='gray', width=130, anchor='w',
          fg_color='transparent').pack(side='left')
    Label(fila, text=valor, font=Font(size=10, weight='bold'),
          anchor='w', fg_color='transparent').pack(side='left')
