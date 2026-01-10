#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='floreria_josbet'
)

cursor = conn.cursor()

updates = [
    ('UPDATE productos SET imagen = %s WHERE nombre = %s', ('sunflower.jpg', 'Girasol eterno')),
    ('UPDATE productos SET imagen = %s WHERE nombre = %s', ('tulip.jpg', 'Tulipanes eternos')),
    ('UPDATE productos SET imagen = %s WHERE nombre = %s', ('rose.jpg', 'Rosas eternas')),
    ('UPDATE productos SET imagen = %s WHERE nombre = %s', ('single1.jpg', 'Flor única 1')),
    ('UPDATE productos SET imagen = %s WHERE nombre = %s', ('single2.jpg', 'Flor única 2')),
    ('UPDATE productos SET imagen = %s WHERE nombre = %s', ('single3.jpg', 'Flor única 3')),
    ('UPDATE productos SET imagen = %s WHERE nombre = %s', ('Ramo-Clasico.jpg', 'Ramo clásico')),
    ('UPDATE productos SET imagen = %s WHERE nombre = %s', ('Ramo-Moderno.jpg', 'Ramo moderno')),
    ('UPDATE productos SET imagen = %s WHERE nombre = %s', ('Ramo-Deluxe.jpg', 'Ramo deluxe')),
]

for sql, params in updates:
    cursor.execute(sql, params)

conn.commit()
print(f"✅ {cursor.rowcount} registros actualizados")
cursor.close()
conn.close()
