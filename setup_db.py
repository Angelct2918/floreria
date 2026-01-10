#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear la base de datos y tablas de la florería Josbet
Requiere: MySQL/XAMPP ejecutándose
Conexión: user=root, password="", host=localhost
"""

import mysql.connector
from mysql.connector import Error

def crear_bd():
    try:
        # Conectar a MySQL sin especificar BD (para crearla)
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            autocommit=True
        )
        cursor = conn.cursor()
        
        # Crear BD
        cursor.execute("DROP DATABASE IF EXISTS floreria_josbet")
        cursor.execute("CREATE DATABASE floreria_josbet CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✓ Base de datos 'floreria_josbet' creada")
        
        # Seleccionar BD
        cursor.execute("USE floreria_josbet")
        
        # Tabla de usuarios
        cursor.execute("""
            CREATE TABLE usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                correo VARCHAR(100) UNIQUE NOT NULL,
                contrasena VARCHAR(255) NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Tabla 'usuarios' creada")
        
        # Tabla de productos
        cursor.execute("""
            CREATE TABLE productos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT,
                precio DECIMAL(10, 2) NOT NULL,
                imagen VARCHAR(255),
                categoria VARCHAR(50)
            )
        """)
        print("✓ Tabla 'productos' creada")
        
        # Tabla de pedidos
        cursor.execute("""
            CREATE TABLE pedidos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                tipo_flor VARCHAR(100),
                color VARCHAR(50),
                cantidad INT DEFAULT 1,
                mensaje TEXT,
                extra_kit VARCHAR(50),
                extra TEXT,
                total DECIMAL(10, 2),
                estado VARCHAR(20) DEFAULT 'pendiente',
                fecha_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        print("✓ Tabla 'pedidos' creada")
        
        # Tabla de carrito
        cursor.execute("""
            CREATE TABLE carrito (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                producto_id INT NOT NULL,
                cantidad INT DEFAULT 1,
                fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        """)
        print("✓ Tabla 'carrito' creada")
        
        # Insertar productos de ejemplo
        productos = [
            ('Girasol eterno', 'Hermoso girasol de flores eternas', 25.99, 'sunflower.jpg', 'flores'),
            ('Tulipanes eternos', 'Ramo de tulipanes eternos variados', 35.99, 'tulip.jpg', 'flores'),
            ('Rosas eternas', 'Ramo de rosas rojas eternales', 45.99, 'rose.jpg', 'flores'),
            ('Flor única 1', 'Flor exótica única', 15.99, 'single1.jpg', 'individual'),
            ('Flor única 2', 'Flor decorativa especial', 18.99, 'single2.jpg', 'individual'),
            ('Flor única 3', 'Flor elegante y moderna', 20.99, 'single3.jpg', 'individual'),
            ('Ramo clásico', 'Ramo tradicional de flores mixtas', 39.99, None, 'ramos'),
            ('Ramo moderno', 'Ramo con diseño contemporáneo', 49.99, None, 'ramos'),
            ('Ramo deluxe', 'Ramo premium con flores premium', 69.99, None, 'ramos'),
        ]
        
        cursor.executemany(
            "INSERT INTO productos (nombre, descripcion, precio, imagen, categoria) VALUES (%s, %s, %s, %s, %s)",
            productos
        )
        print(f"✓ {cursor.rowcount} productos insertados")
        
        cursor.close()
        conn.close()
        print("\n✅ Base de datos configurada exitosamente")
        
    except Error as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    crear_bd()
