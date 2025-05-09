from bd_conexion import obtener_conexion
import hashlib
from psycopg2.extras import RealDictCursor

def obtener_ids_permisos_por_nombre(nombres_permisos):
    conexion = obtener_conexion()
    permisos_ids = []
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT id
            FROM public.permisos
            WHERE nombre = ANY(%s)
        """, (nombres_permisos,))
        resultados = cursor.fetchall()
        permisos_ids = [row[0] for row in resultados]
    conexion.close()
    return permisos_ids

def obtener_usuario_id(correo):
    conexion = obtener_conexion()
    usuario_id = None
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id FROM usuarios WHERE correo = %s", (correo,))
        usuario_id = cursor.fetchone()
    conexion.close()
    return usuario_id[0] if usuario_id else None

def eliminar_permisos(usuario_id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("DELETE FROM usuarios_permisos WHERE id_usuario = %s", (usuario_id,))
        conexion.commit()
    conexion.close()

def agregar_permiso(usuario_id, permiso_id):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("""
            INSERT INTO public.usuarios_permisos (id_usuario, id_permiso)
            VALUES (%s, %s)
        """, (usuario_id, permiso_id))
    conexion.commit()
    conexion.close()

def obtener_permisos_usuario(correo):
    conexion = obtener_conexion()
    permisos = []
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT p.nombre AS permiso_nombre
            FROM public.usuarios u
            JOIN public.personas ps ON u.id_persona = ps.id
            JOIN public.roles r ON ps.id_rol = r.id
            JOIN public.roles_permisos rp ON r.id = rp.rol_id
            JOIN public.permisos p ON rp.permiso_id = p.id
            WHERE u.correo = %s
            UNION
            SELECT DISTINCT p.nombre AS permiso_nombre
            FROM public.usuarios u
            JOIN public.usuarios_permisos up ON u.id = up.id_usuario
            JOIN public.permisos p ON up.id_permiso = p.id
            WHERE u.correo = %s;
        """, (correo, correo))
        permisos = cursor.fetchall()
    conexion.close()
    return [permiso[0] for permiso in permisos]

def obtener_permisos_por_rol(id_rol):
    conexion = obtener_conexion()
    permisos = []
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT p.nombre
            FROM public.permisos p
            INNER JOIN public.roles_permisos rp ON p.id = rp.permiso_id
            WHERE rp.rol_id = %s
        """, (id_rol,))
        permisos = cursor.fetchall()
    conexion.close()
    return [permiso[0] for permiso in permisos]

def obtener_roles():
    conexion = obtener_conexion()
    roles = []
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id, nombre, descripcion FROM roles WHERE estado = true")
        roles = cursor.fetchall()
    conexion.close()
    return roles

def obtener_usuario(correo):
    conexion = obtener_conexion()
    usuario = None
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT u.id AS usuario_id, u.correo, u.pass, u.token,
                   CONCAT(p.nombre, ' ', p.apellido) AS nombre_completo,
                   r.nombre AS rol_nombre, p.imagen, r.id
            FROM usuarios u
            JOIN personas p ON u.id_persona = p.id
            LEFT JOIN roles r ON p.id_rol = r.id
            WHERE u.correo = %s
        """, (correo,))
        usuario = cursor.fetchone()
    conexion.close()
    return usuario

def actualizartoken_usuario(correo, token):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE usuarios SET token = %s WHERE correo = %s", (token, correo))
    conexion.commit()
    conexion.close()

def eliminar_token_usuario(correo):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE usuarios SET token = '' WHERE correo = %s", (correo,))
    conexion.commit()
    conexion.close()

def agregar_usuario(correo, nombre, apellido, id_rol, password):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id FROM usuarios WHERE correo = %s", (correo,))
            if cursor.fetchone():
                print("El correo ya existe en la base de datos.")
                return False
            cursor.execute(
                "INSERT INTO personas (nombre, apellido, id_rol) VALUES (%s, %s, %s) RETURNING id",
                (nombre, apellido, id_rol)
            )
            id_persona = cursor.fetchone()[0]
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute(
                "INSERT INTO usuarios (correo, pass, token, id_persona) VALUES (%s, %s, '', %s)",
                (correo, hashed_password, id_persona)
            )
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al agregar usuario: {e}")
        conexion.rollback()
        return False
    finally:
        conexion.close()

def obtener_detalles_perfil(correo):
    conexion = obtener_conexion()
    perfil = None
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT p.nombre, p.apellido, r.nombre AS rol, p.imagen
            FROM personas p
            LEFT JOIN roles r ON p.id_rol = r.id
            JOIN usuarios u ON p.id = u.id_persona
            WHERE u.correo = %s
        """, (correo,))
        perfil = cursor.fetchone()
    conexion.close()
    return perfil

def obtener_todos_usuarios():
    conexion = obtener_conexion()
    usuarios = []
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT u.correo, p.nombre, p.apellido, r.nombre AS rol, r.id AS rol_id
            FROM usuarios u
            JOIN personas p ON u.id_persona = p.id
            LEFT JOIN roles r ON p.id_rol = r.id
        """)
        resultados = cursor.fetchall()
        for row in resultados:
            usuario = {
                'correo': row[0],
                'nombre': row[1],
                'apellido': row[2],
                'rol': row[3] if row[3] else 'Sin rol asignado',
                'rol_id': row[4] if row[4] else None
            }
            usuarios.append(usuario)
    conexion.close()
    return usuarios

def verificar_correo(correo):
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("SELECT 1 FROM usuarios WHERE correo = %s", (correo,))
        resultado = cursor.fetchone()
    conexion.close()
    return resultado is not None
