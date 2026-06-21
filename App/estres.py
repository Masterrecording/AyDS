"""
estres.py — Cálculo determinista de estrés (1-100) y registro de historial.

Fuentes de datos:
  - quiz_base : propenso_estres, sit_acad, semestre, carga_carrera,
                tiempo_hobbies, estres_examenes, estres_tareas, estres_proyectos
  - materias  : dificultad (sólo semestre actual)
  - actividades: pendientes, vencidas, próximas, completadas (sólo semestre actual)

Sin ML, sin IA, sin cron jobs. Puro SQL + aritmética.
"""

from datetime import datetime, date, timedelta
from App.utils import conectar_db, get_semestre


# ─────────────────────────────────────────────────────────────
# PESOS del modelo (suman ~100 puntos posibles antes de escalar)
# ─────────────────────────────────────────────────────────────
PESO_PROPENSO      = 20   # predisposición personal
PESO_SIT_ACAD      = 10   # situación académica
PESO_CARGA_CARRERA = 10   # percepción de carga de la carrera
PESO_ESTRES_EXAM   = 8    # estrés ante exámenes
PESO_ESTRES_TAREAS = 7    # estrés ante tareas
PESO_ESTRES_PROY   = 7    # estrés ante proyectos
PESO_DIFICULTAD    = 10   # dificultad promedio de materias
PESO_ACTIVIDADES   = 28   # carga de actividades pendientes/vencidas
PESO_HOBBIES       = -10  # hobbies REDUCEN estrés (negativo)


# ─────────────────────────────────────────────────────────────
# Helpers de mapeo
# ─────────────────────────────────────────────────────────────

def _puntaje_propenso(valor):
    """
    Convierte propenso_estres (1-5) a puntaje normalizado 0-1.
    3 = neutro (0.5), 1 = mínimo (0.0), 5 = máximo (1.0).
    """
    return (int(valor) - 1) / 4.0


def _puntaje_sit_acad(sit_acad):
    """
    Mapea situación académica a factor 0-1.
    Valores esperados (texto libre): regular, buena, excelente, mala, etc.
    """
    sit = str(sit_acad).strip().lower()
    mapa = {
        'excelente': 0.0,
        'buena':     0.1,
        'bueno':     0.1,
        'bien':      0.1,
        'regular':   0.5,
        'mala':      0.8,
        'malo':      0.8,
        'mal':       0.8,
        'crítica':   1.0,
        'critica':   1.0,
        'reprobando':1.0,
    }
    # Buscar coincidencia parcial
    for k, v in mapa.items():
        if k in sit:
            return v
    return 0.5  # neutro si no se reconoce


def _puntaje_hobbies(tiempo_hobbies):
    """
    1 = menos de 1h  → poca reducción
    2 = 1-2h         → reducción media
    3 = más de 2h    → mayor reducción
    Devuelve factor 0-1 (se multiplicará por PESO_HOBBIES negativo).
    """
    mapa = {1: 0.3, 2: 0.6, 3: 1.0}
    return mapa.get(int(tiempo_hobbies), 0.5)


def _puntaje_escala_1_5(valor):
    """Normaliza valor 1-5 a rango 0-1."""
    return (int(valor) - 1) / 4.0


# ─────────────────────────────────────────────────────────────
# Cálculo principal
# ─────────────────────────────────────────────────────────────

def calcular_estres(boleta):
    """
    Calcula el nivel de estrés del usuario (1-100).
    Retorna (valor_int, nivel_texto) o (0, 'Sin datos') si no hay quiz_base.
    """
    semestre = get_semestre(boleta)
    if semestre is None:
        return 0, 'Sin datos'

    try:
        conn = conectar_db()
        cur = conn.cursor()

        # ── 1. Datos de quiz_base ────────────────────────────
        cur.execute(
            """SELECT propenso_estres, sit_acad, carga_carrera,
                      tiempo_hobbies, estres_examenes, estres_tareas, estres_proyectos
               FROM quiz_base
               WHERE usuario_boleta = %s""",
            (str(boleta),)
        )
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            return 0, 'Sin datos'

        (propenso, sit_acad, carga_carrera,
         tiempo_hobbies, estres_exam, estres_tareas, estres_proy) = row

        # ── 2. Dificultad promedio de materias (semestre actual) ─
        cur.execute(
            "SELECT AVG(dificultad) FROM materias WHERE usuario_boleta = %s AND semestre = %s",
            (str(boleta), semestre)
        )
        dif_row = cur.fetchone()
        dif_promedio = float(dif_row[0]) if dif_row and dif_row[0] else 3.0

        # ── 3. Análisis de actividades (semestre actual) ─────
        hoy = date.today()
        proximos_dias = hoy + timedelta(days=3)

        cur.execute(
            """SELECT estado, fecha_entrega
               FROM actividades
               WHERE usuario_boleta = %s AND semestre = %s""",
            (str(boleta), semestre)
        )
        actividades = cur.fetchall()

        cur.close()
        conn.close()

        total_act    = len(actividades)
        vencidas     = 0
        proximas     = 0   # entrega en los próximos 3 días
        pendientes   = 0
        completadas  = 0

        for estado, fecha_entrega in actividades:
            fe = fecha_entrega.date() if isinstance(fecha_entrega, datetime) else fecha_entrega
            if estado == 'completada':
                completadas += 1
            else:
                pendientes += 1
                if fe < hoy:
                    vencidas += 1
                elif fe <= proximos_dias:
                    proximas += 1

        # Factor actividades: vencidas pesan doble, proximas pesan 1.5
        puntos_act = 0.0
        if total_act > 0:
            carga_bruta = (vencidas * 2 + proximas * 1.5 + (pendientes - vencidas - proximas))
            # Normalizar: máximo teórico = total_act * 2
            puntos_act = min(carga_bruta / (total_act * 2), 1.0)
        # Si no hay actividades aún, carga neutral (0.3)
        else:
            puntos_act = 0.3

        # ── 4. Suma ponderada ────────────────────────────────
        score = 0.0
        score += _puntaje_propenso(propenso)       * PESO_PROPENSO
        score += _puntaje_sit_acad(sit_acad)        * PESO_SIT_ACAD
        score += _puntaje_escala_1_5(carga_carrera) * PESO_CARGA_CARRERA
        score += _puntaje_escala_1_5(estres_exam)   * PESO_ESTRES_EXAM
        score += _puntaje_escala_1_5(estres_tareas) * PESO_ESTRES_TAREAS
        score += _puntaje_escala_1_5(estres_proy)   * PESO_ESTRES_PROY
        score += _puntaje_escala_1_5(dif_promedio)  * PESO_DIFICULTAD
        score += puntos_act                          * PESO_ACTIVIDADES
        score += _puntaje_hobbies(tiempo_hobbies)   * PESO_HOBBIES  # negativo

        # ── 5. Escalar a 1-100 ───────────────────────────────
        # Máximo teórico de la suma positiva sin hobbies:
        max_pos = (PESO_PROPENSO + PESO_SIT_ACAD + PESO_CARGA_CARRERA +
                   PESO_ESTRES_EXAM + PESO_ESTRES_TAREAS + PESO_ESTRES_PROY +
                   PESO_DIFICULTAD + PESO_ACTIVIDADES)
        min_pos = PESO_HOBBIES  # peor caso de reducción (negativo)

        valor = ((score - min_pos) / (max_pos - min_pos)) * 99 + 1
        valor = int(max(1, min(100, round(valor))))

        return valor, _nivel_texto(valor)

    except Exception as e:
        print(f"[estres] Error al calcular estrés para {boleta}: {e}")
        return 0, 'Error'


def _nivel_texto(valor):
    """Convierte valor numérico a nivel textual."""
    if valor <= 25:
        return 'Bajo'
    elif valor <= 50:
        return 'Moderado'
    elif valor <= 75:
        return 'Alto'
    else:
        return 'Crítico'


# ─────────────────────────────────────────────────────────────
# Historial
# ─────────────────────────────────────────────────────────────

def registrar_historial(boleta):
    """
    Calcula el estrés actual y lo inserta en historial_estres
    sólo si no existe un registro para el día de hoy.
    Se llama desde eventos normales de UI (login, carga de inicio, etc.).
    Retorna (valor, nivel_texto).
    """
    valor, nivel = calcular_estres(boleta)
    if valor == 0:
        return valor, nivel

    try:
        conn = conectar_db()
        cur = conn.cursor()
        hoy = date.today()

        # Un solo registro por día
        cur.execute(
            "SELECT id FROM historial_estres WHERE usuario_boleta = %s AND fecha = %s",
            (str(boleta), hoy)
        )
        if cur.fetchone():
            # Ya existe — actualizar con el valor más reciente
            cur.execute(
                "UPDATE historial_estres SET estres = %s WHERE usuario_boleta = %s AND fecha = %s",
                (valor, str(boleta), hoy)
            )
        else:
            cur.execute(
                "INSERT INTO historial_estres (usuario_boleta, fecha, estres) VALUES (%s, %s, %s)",
                (str(boleta), hoy, valor)
            )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[estres] Error al registrar historial para {boleta}: {e}")

    return valor, nivel


def obtener_historial(boleta, dias=30):
    """
    Devuelve lista de (fecha, estres) de los últimos `dias` días.
    Ordenado por fecha ASC para la gráfica.
    """
    try:
        conn = conectar_db()
        cur = conn.cursor()
        desde = date.today() - timedelta(days=dias)
        cur.execute(
            """SELECT fecha, estres
               FROM historial_estres
               WHERE usuario_boleta = %s AND fecha >= %s
               ORDER BY fecha ASC""",
            (str(boleta), desde)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"[estres] Error al obtener historial para {boleta}: {e}")
        return []


def generar_recomendaciones(boleta):
    """
    Genera lista de recomendaciones dinámicas basadas en datos reales.
    Retorna lista de strings.
    """
    semestre = get_semestre(boleta)
    if semestre is None:
        return ["Completa la encuesta base para obtener recomendaciones personalizadas."]

    recomendaciones = []

    try:
        conn = conectar_db()
        cur = conn.cursor()

        # Datos quiz_base
        cur.execute(
            """SELECT propenso_estres, sit_acad, carga_carrera,
                      tiempo_hobbies, estres_examenes, estres_tareas, estres_proyectos
               FROM quiz_base WHERE usuario_boleta = %s""",
            (str(boleta),)
        )
        row = cur.fetchone()
        if not row:
            conn.close()
            return ["Completa la encuesta base para obtener recomendaciones personalizadas."]

        (propenso, sit_acad, carga_carrera,
         tiempo_hobbies, estres_exam, estres_tareas, estres_proy) = row

        # Actividades
        hoy = date.today()
        proximos = hoy + timedelta(days=3)
        cur.execute(
            """SELECT estado, fecha_entrega, tipo_actividad
               FROM actividades
               WHERE usuario_boleta = %s AND semestre = %s""",
            (str(boleta), semestre)
        )
        acts = cur.fetchall()
        cur.close()
        conn.close()

        vencidas  = [a for a in acts if a[0] != 'completada' and
                     (a[1].date() if isinstance(a[1], datetime) else a[1]) < hoy]
        proximas  = [a for a in acts if a[0] != 'completada' and
                     hoy <= (a[1].date() if isinstance(a[1], datetime) else a[1]) <= proximos]
        pendientes_total = [a for a in acts if a[0] != 'completada']

        valor_estres, nivel = calcular_estres(boleta)

        # ── Recomendaciones por estrés general ──────────────
        if valor_estres >= 75:
            recomendaciones.append("⚠️ Tu nivel de estrés es crítico. Considera hablar con un tutor o psicólogo escolar.")
            recomendaciones.append("🛑 Prioriza dormir al menos 7 horas; el descanso reduce el impacto del estrés cognitivo.")
        elif valor_estres >= 50:
            recomendaciones.append("📋 Tu estrés es elevado. Organiza tus pendientes por urgencia y trabaja en bloques de 25 minutos (técnica Pomodoro).")
        elif valor_estres >= 25:
            recomendaciones.append("✅ Tu nivel de estrés es moderado. Mantén tu rutina de estudio y reserva tiempo para descansar.")
        else:
            recomendaciones.append("🌿 Tu nivel de estrés es bajo. ¡Buen trabajo manteniendo el equilibrio!")

        # ── Actividades vencidas ─────────────────────────────
        if len(vencidas) >= 3:
            recomendaciones.append(f"🔴 Tienes {len(vencidas)} actividades vencidas. Contacta a tus profesores para negociar entregas.")
        elif len(vencidas) > 0:
            recomendaciones.append(f"⏰ Tienes {len(vencidas)} actividad(es) vencida(s). Resuélvelas lo antes posible.")

        # ── Entregas próximas ────────────────────────────────
        if len(proximas) >= 3:
            recomendaciones.append(f"📅 Tienes {len(proximas)} entregas en los próximos 3 días. Organiza tu tiempo hoy.")
        elif len(proximas) > 0:
            tipos = set(a[2] for a in proximas if a[2])
            recomendaciones.append(f"📌 Próximas entregas: {', '.join(tipos) if tipos else 'actividades'}. Empieza con la más compleja.")

        # ── Carga de carrera ─────────────────────────────────
        if int(carga_carrera) >= 4:
            recomendaciones.append("📚 Percibes tu carrera como muy pesada. Divide el material en partes pequeñas y estudia con anticipación.")

        # ── Hobbies ──────────────────────────────────────────
        if int(tiempo_hobbies) == 1:
            recomendaciones.append("🎮 Dedicas poco tiempo a tus hobbies. Aunque sea 30 minutos al día de actividad que disfrutes reduce el estrés significativamente.")
        elif int(tiempo_hobbies) == 3:
            recomendaciones.append("🎯 Tienes buen tiempo para hobbies. Asegúrate de que no desplace tiempo de estudio necesario.")

        # ── Situación académica ───────────────────────────────
        sit = str(sit_acad).strip().lower()
        if any(k in sit for k in ('mal', 'mala', 'reprobando', 'crítica', 'critica')):
            recomendaciones.append("📖 Tu situación académica requiere atención. Considera buscar asesoría o grupos de estudio.")

        # ── Estrés específico por tipo de actividad ──────────
        if int(estres_exam) >= 4:
            recomendaciones.append("📝 Te estresan mucho los exámenes. Practica con exámenes anteriores y estudia en sesiones cortas regulares.")
        if int(estres_proy) >= 4:
            recomendaciones.append("🛠️ Los proyectos te generan estrés elevado. Divide cada proyecto en tareas pequeñas con fechas intermedias.")
        if int(estres_tareas) >= 4:
            recomendaciones.append("✏️ Las tareas te estresan. Intenta resolverlas el mismo día que se asignan para no acumularlas.")

        # ── Sin pendientes ────────────────────────────────────
        if not pendientes_total and valor_estres < 30:
            recomendaciones.append("🌟 Sin pendientes urgentes y estrés bajo. Aprovecha para adelantar material del siguiente tema.")

    except Exception as e:
        print(f"[estres] Error al generar recomendaciones para {boleta}: {e}")
        recomendaciones.append("No se pudieron generar recomendaciones en este momento.")

    return recomendaciones if recomendaciones else ["Sin recomendaciones disponibles por el momento."]
