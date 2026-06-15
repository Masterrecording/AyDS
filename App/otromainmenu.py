import pymysql as sql
import json
from datetime import datetime, timedelta
from tkinter import messagebox

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

class VistaPrincipalEstudiante(Frame):
    def __init__(self, master, gestor, usuario_id=None, **kwargs):
        super().__init__(master, **kwargs)
        self.gestor = gestor
        self.usuario_id = usuario_id
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
            
            cur.execute('SELECT nombre FROM usuario WHERE idusuario = %s', (self.usuario_id,))
            nombre_result = cur.fetchone()
            nombre = nombre_result[0] if nombre_result else "Usuario"
            
            cur.execute('''
                SELECT c.nombre 
                FROM datos_usuario_perm d
                JOIN carreras c ON d.carreras_idcarreras = c.idcarreras
                WHERE d.usuario_idusuario = %s
            ''', (self.usuario_id,))
            carrera_result = cur.fetchone()
            carrera = carrera_result[0] if carrera_result else "No especificada"
            
            cur.execute('''
                SELECT semestre
                FROM quiz_base
                WHERE usuario_idusuario = %s
            ''', (self.usuario_id,))
            semestre_result = cur.fetchone()
            semestre = semestre_result[0] if semestre_result else "N/A"
            
            cur.close()
            conn.close()
        except Exception as e:
            nombre = "Usuario"
            carrera = "No especificada"
            semestre = "N/A"
            print(e)

        header_frame = Frame(parent)
        header_frame.pack(fill='x', pady=(0, 20))

        Label(header_frame, text=nombre, font=Font(family='Calibri', size=28, weight='bold')).pack(anchor='w')
        Label(header_frame, text=f"{carrera} - Semestre {semestre}", font=Font(size=14), fg_color='gray').pack(anchor='w')

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
            hace_7_dias = hoy - timedelta(days=7)

            valores = []
            
            for tabla in ['act_examen', 'act_proyecto', 'act_tarea']:
                try:
                    cur.execute(
                        f'SELECT COALESCE(AVG(genera_estres), 0) FROM {tabla} WHERE usuario_idusuario = %s AND DATE(fecha) BETWEEN %s AND %s',
                        (self.usuario_id, hace_7_dias, hoy)
                    )
                except Exception as e:
                    print(e)
                val = cur.fetchone()[0]
                valores.append(val if val else 0)

            cur.close()
            conn.close()

            promedio = (sum(valores) / len(valores) if valores else 0) / 5.0 * 100
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
                SELECT p.id_act, p.nombre, m.nombre, p.fecha_entrega, p.estado
                FROM actividades AS p
                JOIN materias m ON p.materias_idmaterias = m.idmaterias
                WHERE p.usuario_idusuario = %s AND p.estado != %s
                ORDER BY p.fecha_entrega ASC
            ''', (self.usuario_id, 'completada'))
            pendientes = cur.fetchall()
            
            cur.close()
            conn.close()
        except Exception as e:
            pendientes = []
            print(e)

        if not pendientes:
            Label(parent, text='No hay pendientes registrados', font=Font(size=12,), text_color='gray').pack(pady=10)
            return

        for pid, nombre, materia, fecha_entrega, estado in pendientes:
            self._crear_tarjeta_pendiente(parent, pid, nombre, materia, fecha_entrega, estado)

    def _crear_tarjeta_pendiente(self, parent, pid, nombre, materia, fecha_entrega, estado):
        hoy = datetime.now().date()
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
        view = AddTaskView(ventana, self.gestor, usuario_id=self.usuario_id, callback=self.build)
        view.pack(expand=True, fill='both')
        ventana.mainloop()

if __name__ == "__main__":
    root = Tk()
    VistaPrincipalEstudiante(root, None, usuario_id=1)
    root.mainloop()