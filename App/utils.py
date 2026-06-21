import pymysql as sql
import json


def conectar_db():
    """Conexión global a la base de datos. Lee settings.json desde el directorio raíz."""
    cfg = json.loads(open('settings.json', 'r', encoding='utf-8').read())
    return sql.connect(
        host=cfg['host'],
        user=cfg['user'],
        password=cfg['password'],
        database=cfg['database']
    )


def get_semestre(boleta):
    """
    Devuelve el semestre actual del usuario según quiz_base.
    Retorna el entero del semestre, o None si no existe registro.
    """
    try:
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("SELECT semestre FROM quiz_base WHERE usuario_boleta = %s", (str(boleta),))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"[utils] Error al obtener semestre para boleta {boleta}: {e}")
        return None


def get_rol(boleta):
    """
    Devuelve el nombre del rol del usuario ('Alumno' o 'Administrador').
    Retorna None si no se puede determinar.
    """
    try:
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT r.nombre FROM usuario u JOIN roles r ON u.roles_idroles = r.idroles WHERE u.boleta = %s",
            (str(boleta),)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"[utils] Error al obtener rol para boleta {boleta}: {e}")
        return None
