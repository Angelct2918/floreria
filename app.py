#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación Flask para Florería Josbet - Versión con PyMySQL
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import pymysql
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_josbet_2024'

# Configuración de MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'floreria_josbet',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db():
    """Crear conexión a la BD"""
    return pymysql.connect(**DB_CONFIG)

def login_required(f):
    """Decorador para proteger rutas"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesión primero', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Rutas para servir imágenes sueltas (carpeta `images/`) y helper para plantillas
@app.route('/images/<path:filename>')
def serve_image(filename):
    images_dir = os.path.join(app.root_path, 'images')
    return send_from_directory(images_dir, filename)


@app.context_processor
def inject_helpers():
    STATIC_IMG_DIR = os.path.join(app.root_path, 'static', 'images')
    IMAGES_DIR = os.path.join(app.root_path, 'images')

    def image_url(filename):
        # Devuelve la URL correcta comprobando primero `static/images`, luego `images/`,
        # y por último intentando mapeos conocidos; si todo falla, usa un placeholder.
        if not filename:
            return url_for('static', filename='images/sunflower.svg')

        static_path = os.path.join(STATIC_IMG_DIR, filename)
        if os.path.exists(static_path):
            return url_for('static', filename='images/' + filename)

        images_path = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(images_path):
            return url_for('serve_image', filename=filename)

        # Mapeos conocidos entre nombres en BD y archivos reales en `images/`
        mapping = {
            'sunflower.jpg': 'Girasol_Eterno.jpg',
            'tulip.jpg': 'Tulipan_Eterno.jpg',
            'rose.jpg': 'Rosas_Eternas.jpg',
            'single1.jpg': 'Flor_Unica.jpg',
            'single2.jpg': 'Flor_Unica_2jpg.jpg',
            'single3.jpg': 'Flor_Unica_3.jpg',
            'Ramo-Clasico.jpg': 'Ramo-Clasico.jpg',
            'Ramo-Moderno.jpg': 'Ramo_Moderno.jpg',
            'Ramo-Deluxe.jpg': 'Ramo_Deluxe.jpg',
        }

        alt = mapping.get(filename)
        if alt and os.path.exists(os.path.join(IMAGES_DIR, alt)):
            return url_for('serve_image', filename=alt)

        return url_for('static', filename='images/sunflower.svg')

    return dict(image_url=image_url)

# ========== RUTAS PÚBLICAS ==========

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth')
def auth():
    return render_template('auth.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo', '')
        contrasena = request.form.get('contrasena', '')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE correo = %s', (correo,))
            usuario = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if usuario and usuario['contrasena'] == contrasena:
                session['usuario_id'] = usuario['id']
                session['nombre'] = usuario['nombre']
                flash(f'¡Bienvenido {usuario["nombre"]}!', 'success')
                return redirect(url_for('menu'))
            else:
                flash('Correo o contraseña incorrectos', 'danger')
        except Exception as e:
            flash(f'Error de conexión: {str(e)}', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '')
        correo = request.form.get('correo', '')
        contrasena = request.form.get('contrasena', '')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM usuarios WHERE correo = %s', (correo,))
            
            if cursor.fetchone():
                flash('El correo ya está registrado', 'danger')
            else:
                cursor.execute(
                    'INSERT INTO usuarios (nombre, correo, contrasena) VALUES (%s, %s, %s)',
                    (nombre, correo, contrasena)
                )
                conn.commit()
                flash('¡Registro exitoso! Ahora inicia sesión', 'success')
                cursor.close()
                conn.close()
                return redirect(url_for('login'))
            
            cursor.close()
            conn.close()
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('register.html')

# ========== RUTAS PROTEGIDAS ==========

@app.route('/menu')
@login_required
def menu():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM productos')
        productos = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('menu.html', productos=productos)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return render_template('menu.html', productos=[])

@app.route('/carrito')
@login_required
def carrito():
    usuario_id = session['usuario_id']
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, p.id as producto_id, p.nombre, p.precio, c.cantidad
            FROM carrito c
            JOIN productos p ON c.producto_id = p.id
            WHERE c.usuario_id = %s
        """, (usuario_id,))
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        
        total = sum(item['precio'] * item['cantidad'] for item in items) if items else 0
        return render_template('carrito.html', items=items, total=total)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return render_template('carrito.html', items=[], total=0)

@app.route('/agregar-carrito/<int:producto_id>', methods=['POST'])
@login_required
def agregar_carrito(producto_id):
    usuario_id = session['usuario_id']
    cantidad = request.form.get('cantidad', 1, type=int)
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM carrito WHERE usuario_id = %s AND producto_id = %s',
            (usuario_id, producto_id)
        )
        item = cursor.fetchone()
        
        if item:
            cursor.execute(
                'UPDATE carrito SET cantidad = cantidad + %s WHERE usuario_id = %s AND producto_id = %s',
                (cantidad, usuario_id, producto_id)
            )
        else:
            cursor.execute(
                'INSERT INTO carrito (usuario_id, producto_id, cantidad) VALUES (%s, %s, %s)',
                (usuario_id, producto_id, cantidad)
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Producto agregado al carrito', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('menu'))

@app.route('/eliminar-carrito/<int:item_id>', methods=['POST'])
@login_required
def eliminar_carrito(item_id):
    usuario_id = session['usuario_id']
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM carrito WHERE id = %s AND usuario_id = %s', (item_id, usuario_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Producto eliminado del carrito', 'info')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('carrito'))

@app.route('/pedido-personalizado', methods=['GET', 'POST'])
@login_required
def pedido_personalizado():
    if request.method == 'POST':
        usuario_id = session['usuario_id']
        tipo_flor = request.form.get('tipo', '')
        color = request.form.get('color', '')
        cantidad = request.form.get('cantidad', 1)
        mensaje = request.form.get('mensaje', '')
        extra_kit = request.form.get('extraKit', 'ninguno')
        extra = request.form.get('extra', '')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pedidos (usuario_id, tipo_flor, color, cantidad, mensaje, extra_kit, extra, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'pendiente')
            """, (usuario_id, tipo_flor, color, cantidad, mensaje, extra_kit, extra))
            
            conn.commit()
            pedido_id = cursor.lastrowid
            cursor.close()
            conn.close()
            
            flash(f'¡Pedido #{pedido_id} creado exitosamente!', 'success')
            return redirect(url_for('mis_pedidos'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('pedido-personalizado.html')

@app.route('/mis-pedidos')
@login_required
def mis_pedidos():
    usuario_id = session['usuario_id']
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pedidos WHERE usuario_id = %s ORDER BY fecha_pedido DESC', (usuario_id,))
        pedidos = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('mis-pedidos.html', pedidos=pedidos)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return render_template('mis-pedidos.html', pedidos=[])

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    usuario_id = session['usuario_id']
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.id, p.id as producto_id, p.nombre, p.precio, c.cantidad
            FROM carrito c
            JOIN productos p ON c.producto_id = p.id
            WHERE c.usuario_id = %s
        """, (usuario_id,))
        items = cursor.fetchall()
        
        if request.method == 'POST':
            if not items:
                flash('El carrito está vacío', 'warning')
                cursor.close()
                conn.close()
                return redirect(url_for('carrito'))
            
            total = sum(item['precio'] * item['cantidad'] for item in items)
            
            # Crear pedidos
            for item in items:
                cursor.execute("""
                    INSERT INTO pedidos (usuario_id, tipo_flor, cantidad, total, estado)
                    VALUES (%s, %s, %s, %s, 'confirmado')
                """, (usuario_id, item['nombre'], item['cantidad'], item['precio'] * item['cantidad']))
            
            # Limpiar carrito
            cursor.execute('DELETE FROM carrito WHERE usuario_id = %s', (usuario_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('¡Compra realizada exitosamente!', 'success')
            return redirect(url_for('mis_pedidos'))
        
        # GET
        total = sum(item['precio'] * item['cantidad'] for item in items) if items else 0
        cursor.close()
        conn.close()
        return render_template('checkout.html', items=items, total=total)
    
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return render_template('checkout.html', items=[], total=0)

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('index'))

# ========== MANEJO DE ERRORES ==========

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    print("✅ Iniciando Florería Josbet en http://127.0.0.1:5000")
    print("📌 Presiona Ctrl+C para detener")
    app.run(debug=True, host='127.0.0.1', port=5000)
