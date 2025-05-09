from flask import Flask, render_template, request, redirect, make_response, flash, url_for
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity, set_access_cookies, unset_jwt_cookies
)
import hashlib
import controladores.controlador_usuarios as controlador_usuarios
from bd_conexion import obtener_conexion
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False 
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_SESSION_COOKIE'] = True
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=30)

jwt = JWTManager(app)

# Vista para el login
@app.route("/")
@app.route("/login_user")
def login():
    resp = make_response(render_template("login_user.html"))
    unset_jwt_cookies(resp)
    return resp

# Vista del formulario de registro
@app.route("/registrar")
def form_registro():
    return render_template("registro.html")

# Registro de usuario con rol por defecto "usuario"
@app.route('/registrar', methods=['POST'])
def registrar_usuario():
    correo = request.form['correo']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    password = request.form['password']

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    conexion = obtener_conexion()
    with conexion:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id FROM roles WHERE LOWER(nombre) = 'usuario'")
            resultado = cursor.fetchone()
            if not resultado:
                flash("No se encontró el rol 'usuario'.")
                return redirect(url_for('form_registro'))
            id_rol_usuario = resultado[0]

            cursor.execute("""
                INSERT INTO personas (nombre, apellido, id_rol)
                VALUES (%s, %s, %s) RETURNING id
            """, (nombre, apellido, id_rol_usuario))
            id_persona = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO usuarios (correo, pass, token, id_persona)
                VALUES (%s, %s, '', %s)
            """, (correo, hashed_password, id_persona))

    return redirect(url_for('login'))

# Procesamiento del login
@app.route("/procesar_login", methods=["POST"])
def procesar_login():
    try:
        correo = request.form["correo"]
        password = request.form["password"].strip()
        usuario = controlador_usuarios.obtener_usuario(correo)
        if not usuario:
            flash("Usuario no encontrado.")
            return redirect("/login_user")

        h = hashlib.new("sha256")
        h.update(password.encode('utf-8'))
        encpass = h.hexdigest().lower()

        if encpass == usuario[2].lower():
            access_token = create_access_token(identity=correo)
            controlador_usuarios.actualizartoken_usuario(correo, access_token)
            resp = make_response(redirect("/index"))
            set_access_cookies(resp, access_token)
            return resp
        else:
            flash("Contraseña incorrecta.")
            return redirect("/login_user")
    except Exception as e:
        flash("Ocurrió un error. Por favor, inténtelo de nuevo.")
        return redirect("/login_user")

# Cierre de sesión
@app.route("/procesar_logout")
@jwt_required()
def procesar_logout():
    correo = get_jwt_identity()
    controlador_usuarios.eliminar_token_usuario(correo)
    resp = make_response(redirect("/login_user"))
    unset_jwt_cookies(resp)
    flash("Sesión cerrada correctamente.")
    return resp

# Página protegida
@app.route("/index")
@jwt_required()
def index():
    correo = get_jwt_identity()
    usuario = controlador_usuarios.obtener_usuario(correo)
    return render_template("index.html", usuario=usuario)

# Evitar caché para prevenir acceso con "flecha atrás"
@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, public, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Manejo de errores JWT
@jwt.unauthorized_loader
def custom_unauthorized_response(err_str):
    return redirect(url_for('login'))

@jwt.invalid_token_loader
def custom_invalid_token_response(err_str):
    return redirect(url_for('login'))

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    flash("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.")
    resp = make_response(redirect(url_for('login')))
    unset_jwt_cookies(resp)
    return resp

@app.errorhandler(401)
def unauthorized_error_handler(e):
    flash("No autorizado. Por favor, inicia sesión.")
    resp = make_response(redirect(url_for('login')))
    unset_jwt_cookies(resp)
    return resp

# Iniciar servidor
if __name__ == "__main__":
    app.run(debug=True)
