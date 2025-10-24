from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key_change_me')
# Conexión a MySQL (usa tus credenciales reales)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/sakila'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----- Models -----
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(80), nullable=True)  # ramo, individual, etc.
    precio = db.Column(db.Float, nullable=True)     # usar None o número real
    descripcion = db.Column(db.Text, nullable=True)
    imagen = db.Column(db.String(300), nullable=True)  # url o path
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    nombre_cliente = db.Column(db.String(200), nullable=True)
    telefono = db.Column(db.String(50), nullable=True)
    detalle = db.Column(db.Text, nullable=True)  # json string o texto
    total = db.Column(db.Float, default=0.0)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

# ----- Helpers -----
def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return User.query.get(uid)

def login_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*a, **kw):
        if not current_user():
            flash("Debes iniciar sesión para acceder a esa página.", "warning")
            return redirect(url_for('login'))
        return fn(*a, **kw)
    return wrapper

def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*a, **kw):
        u = current_user()
        if not u or not u.is_admin:
            flash("Acceso denegado. Sólo administradores.", "danger")
            return redirect(url_for('index'))
        return fn(*a, **kw)
    return wrapper

# ----- Routes -----
@app.route('/')
def index():
    return render_template('index.html', user=current_user())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('nombre', '').strip()
        email = request.form.get('correo', '').strip().lower()
        password = request.form.get('contrasena', '')
        confirm = request.form.get('confirma_contrasena', '')

        if not username or not email or not password:
            flash("Rellena todos los campos obligatorios.", "warning")
            return redirect(url_for('register'))

        if password != confirm:
            flash("Las contraseñas no coinciden.", "danger")
            return redirect(url_for('register'))

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Usuario o correo ya registrado.", "danger")
            return redirect(url_for('register'))

        u = User(username=username, email=email)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        flash("Registro exitoso. Por favor inicia sesión.", "success")
        return redirect(url_for('login'))

    return render_template('register.html', user=current_user())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('nombre', '').strip()
        password = request.form.get('contrasena', '')

        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash(f"Bienvenido, {user.username}!", "success")
            return redirect(url_for('menu'))
        else:
            flash("Nombre de usuario o contraseña incorrecta.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html', user=current_user())

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Has cerrado sesión.", "info")
    return redirect(url_for('index'))

@app.route('/menu')
def menu():
    productos = Product.query.order_by(Product.creado_en.desc()).all()
    return render_template('menu.html', catalogo=productos, user=current_user())

@app.route('/custom_order', methods=['GET', 'POST'])
@login_required
def custom_order():
    if request.method == 'POST':
        tipo_flor = request.form.get('tipo_flor')
        color = request.form.get('color')
        cantidad = request.form.get('cantidad')
        mensaje = request.form.get('mensaje')
        extra = request.form.get('extra')
        telefono = request.form.get('telefono')
        nombre_cliente = request.form.get('nombre_cliente') or current_user().username

        detalle = {
            "tipo_flor": tipo_flor,
            "color": color,
            "cantidad": cantidad,
            "mensaje": mensaje,
            "extra": extra
        }

        order = Order(
            usuario_id=current_user().id,
            nombre_cliente=nombre_cliente,
            telefono=telefono,
            detalle=str(detalle),
            total=0.0
        )
        db.session.add(order)
        db.session.commit()
        flash("Pedido personalizado creado con éxito.", "success")
        return redirect(url_for('menu'))

    return render_template('custom_order.html', user=current_user())

# ----- Admin routes -----
@app.route('/admin')
@admin_required
def admin_dashboard():
    usuarios = User.query.all()
    pedidos = Order.query.order_by(Order.creado_en.desc()).all()
    productos = Product.query.order_by(Product.creado_en.desc()).all()
    return render_template('admin/dashboard.html', usuarios=usuarios, pedidos=pedidos, productos=productos, user=current_user())

@app.route('/admin/product/new', methods=['GET', 'POST'])
@admin_required
def admin_new_product():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        tipo = request.form.get('tipo')
        precio = request.form.get('precio') or None
        descripcion = request.form.get('descripcion')
        imagen = request.form.get('imagen')
        precio_val = float(precio) if precio else None

        p = Product(nombre=nombre, tipo=tipo, precio=precio_val, descripcion=descripcion, imagen=imagen)
        db.session.add(p)
        db.session.commit()
        flash("Producto agregado al catálogo.", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/new_product.html', user=current_user())

@app.route('/admin/product/<int:pid>/delete', methods=['POST'])
@admin_required
def admin_delete_product(pid):
    p = Product.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    flash("Producto eliminado.", "info")
    return redirect(url_for('admin_dashboard'))

# ----- Debug / util route to init DB and seed -----
@app.cli.command('init-db')
def init_db():
    """Crear la base de datos y semillas iniciales (ejecutar: flask init-db)"""
    db.create_all()
    # Semilla: admin y algunos productos si no existen
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('adminpass')
        db.session.add(admin)
    if Product.query.count() == 0:
        p1 = Product(nombre='Rosas Eternas', tipo='ramo', precio=0.0, descripcion='Ramo elegante de rosas.')
        p2 = Product(nombre='Girasoles', tipo='ramo', precio=0.0, descripcion='Girasoles frescos.')
        p3 = Product(nombre='Tulipanes', tipo='ramo', precio=0.0, descripcion='Tulipanes coloridos.')
        db.session.add_all([p1, p2, p3])
    db.session.commit()
    print("Base de datos inicializada y semillas agregadas.")

if __name__ == '__main__':
    app.run(debug=True)
