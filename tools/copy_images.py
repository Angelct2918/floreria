import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
src = root / 'images'
dst = root / 'static' / 'images'

tasks = [
    ('Girasol_Eterno.jpg', 'sunflower.jpg'),
    ('Tulipan_Eterno.jpg', 'tulip.jpg'),
    ('Rosas_Eternas.jpg', 'rose.jpg'),
    ('Flor_Unica.jpg', 'single1.jpg'),
    ('Flor_Unica_2jpg.jpg', 'single2.jpg'),
    ('Flor_Unica_3.jpg', 'single3.jpg'),
    ('Ramo-Clasico.jpg', 'Ramo-Clasico.jpg'),
    ('Ramo_Moderno.jpg', 'Ramo-Moderno.jpg'),
    ('Ramo_Deluxe.jpg', 'Ramo-Deluxe.jpg'),
]

copied = []
for s, d in tasks:
    s_path = src / s
    d_path = dst / d
    try:
        shutil.copy2(s_path, d_path)
        copied.append((s_path.name, d_path.name))
    except FileNotFoundError:
        print(f"NO ENCONTRADO: {s_path}")
    except Exception as e:
        print(f"ERROR copiando {s_path}: {e}")

if copied:
    print('Copiados:')
    for a, b in copied:
        print(f" - {a} -> {b}")
else:
    print('No se copiaron archivos (revisar mensajes).')
