from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'clave_secreta_flask'  # Necesario si luego quieres usar mensajes flash o sesiones

# -----------------------------
# RUTA PRINCIPAL
# -----------------------------
@app.route('/')
def index():
    return render_template('index.html')

# -----------------------------
# RUTA DE INICIO DE SESIÓN
# -----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']

        # 🔐 Aquí podrías validar usuario y contraseña con una base de datos real.
        print(f"Iniciando sesión con: {correo}")

        # Ejemplo de mensaje opcional:
        flash('Inicio de sesión exitoso. ¡Bienvenido de nuevo!', 'success')
        return redirect(url_for('index'))
    
    return render_template('login.html')

# -----------------------------
# RUTA DE REGISTRO
# -----------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        contraseña = request.form['contraseña']

        # 🗂️ Aquí podrías guardar los datos en una base de datos
        print(f"Registrado: {nombre}, {correo}")

        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'info')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# -----------------------------
# EJECUCIÓN DE LA APP
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
