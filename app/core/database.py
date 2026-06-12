import sqlite3
import os
from pathlib import Path

import sys

# Determinar la ruta base dependiendo de si es un ejecutable o script
if getattr(sys, 'frozen', False):
    # Si es un ejecutable (PyInstaller), la base es la carpeta donde está el .exe
    BASE_DIR = Path(sys.executable).parent
else:
    # Si es el script original, la base es la raíz del proyecto (3 niveles arriba de database.py)
    BASE_DIR = Path(__file__).parent.parent.parent

DB_PATH = BASE_DIR / "data" / "mi_admin.db"
def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS configuracion (clave TEXT PRIMARY KEY, valor TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS papelera (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT,
        nombre TEXT,
        datos_json TEXT,
        fecha TEXT DEFAULT (datetime('now','localtime'))
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS mapeos_guardados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        contenido TEXT NOT NULL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS edificios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        direccion TEXT,
        ruta_plantilla TEXT,
        ruta_guardado TEXT,
        activo INTEGER DEFAULT 1
    )""")

    try:
        c.execute("ALTER TABLE edificios ADD COLUMN mapeo_celdas TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        c.execute("ALTER TABLE edificios ADD COLUMN conceptos_default TEXT")
    except sqlite3.OperationalError:
        pass

    c.execute("""CREATE TABLE IF NOT EXISTS departamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        edificio_id INTEGER NOT NULL,
        identificador TEXT NOT NULL,
        inquilino TEXT,
        inicio_contrato TEXT,
        fin_contrato TEXT,
        dia_vencimiento_pago INTEGER DEFAULT 10,
        aumentos_notas TEXT,
        activo INTEGER DEFAULT 1,
        conceptos_default TEXT,
        FOREIGN KEY (edificio_id) REFERENCES edificios(id)
    )""")
    
    try:
        c.execute("ALTER TABLE departamentos ADD COLUMN conceptos_default TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        c.execute("ALTER TABLE departamentos ADD COLUMN numero_recibo INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass

    c.execute("""CREATE TABLE IF NOT EXISTS conceptos_edificio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        edificio_id INTEGER NOT NULL,
        categoria TEXT,
        concepto TEXT NOT NULL,
        precio_default REAL DEFAULT 0.0,
        FOREIGN KEY (edificio_id) REFERENCES edificios(id)
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS recibos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        departamento_id INTEGER NOT NULL,
        periodo TEXT NOT NULL,
        fecha_emision TEXT DEFAULT (datetime('now','localtime')),
        total REAL DEFAULT 0.0,
        estado TEXT DEFAULT 'borrador',
        archivo_excel TEXT,
        nota TEXT DEFAULT '',
        FOREIGN KEY (departamento_id) REFERENCES departamentos(id)
    )""")

    try:
        c.execute("ALTER TABLE recibos ADD COLUMN nota TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
        
    try:
        c.execute("ALTER TABLE recibos ADD COLUMN numero_recibo INTEGER")
    except sqlite3.OperationalError:
        pass

    c.execute("""CREATE TABLE IF NOT EXISTS recibo_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recibo_id INTEGER NOT NULL,
        categoria TEXT,
        concepto TEXT NOT NULL,
        cantidad REAL DEFAULT 1.0,
        precio_unitario REAL DEFAULT 0.0,
        subtotal REAL DEFAULT 0.0,
        FOREIGN KEY (recibo_id) REFERENCES recibos(id) ON DELETE CASCADE
    )""")

    conn.commit()
    conn.close()

# Configuración General
def obtener_config(clave=None):
    conn = get_connection()
    if clave:
        row = conn.execute("SELECT valor FROM configuracion WHERE clave=?", (clave,)).fetchone()
        conn.close()
        return row["valor"] if row else None
    else:
        rows = conn.execute("SELECT * FROM configuracion").fetchall()
        conn.close()
        return {r["clave"]: r["valor"] for r in rows}

def guardar_config(clave, valor):
    conn = get_connection()
    conn.execute("INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)", (clave, valor))
    conn.commit()
    conn.close()

# --- MAPEOS GUARDADOS ---
def obtener_mapeos_guardados():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM mapeos_guardados ORDER BY nombre").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def guardar_mapeo_guardado(nombre, contenido):
    conn = get_connection()
    conn.execute("INSERT OR REPLACE INTO mapeos_guardados (nombre, contenido) VALUES (?, ?)", (nombre, contenido))
    conn.commit()
    conn.close()

def eliminar_mapeo_guardado(id):
    conn = get_connection()
    conn.execute("DELETE FROM mapeos_guardados WHERE id=?", (id,))
    conn.commit()
    conn.close()

# --- PAPELERA ---
def guardar_en_papelera(tipo, nombre, datos_json):
    conn = get_connection()
    conn.execute("INSERT INTO papelera (tipo, nombre, datos_json) VALUES (?, ?, ?)", (tipo, nombre, datos_json))
    conn.commit()
    conn.close()

def obtener_papelera():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM papelera ORDER BY fecha DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def vaciar_papelera():
    conn = get_connection()
    conn.execute("DELETE FROM papelera")
    conn.commit()
    conn.close()

# --- EDIFICIOS ---
def obtener_edificios():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM edificios WHERE activo=1 ORDER BY nombre").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def agregar_edificio(nombre, direccion, ruta_plantilla="", ruta_guardado="", mapeo_celdas="", conceptos_default=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO edificios (nombre, direccion, ruta_plantilla, ruta_guardado, mapeo_celdas, conceptos_default) VALUES (?, ?, ?, ?, ?, ?)",
              (nombre, direccion, ruta_plantilla, ruta_guardado, mapeo_celdas, conceptos_default))
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id

def actualizar_edificio(edificio_id, nombre, direccion, ruta_plantilla, ruta_guardado, mapeo_celdas="", conceptos_default=""):
    conn = get_connection()
    conn.execute("UPDATE edificios SET nombre=?, direccion=?, ruta_plantilla=?, ruta_guardado=?, mapeo_celdas=?, conceptos_default=? WHERE id=?",
                 (nombre, direccion, ruta_plantilla, ruta_guardado, mapeo_celdas, conceptos_default, edificio_id))
    conn.commit()
    conn.close()

def actualizar_conceptos_edificio(edificio_id, conceptos_default):
    conn = get_connection()
    conn.execute("UPDATE edificios SET conceptos_default=? WHERE id=?", (conceptos_default, edificio_id))
    conn.commit()
    conn.close()

def eliminar_edificio(edificio_id):
    import json
    conn = get_connection()
    edif = conn.execute("SELECT * FROM edificios WHERE id=?", (edificio_id,)).fetchone()
    if edif:
        guardar_en_papelera("Edificio", edif["nombre"], json.dumps(dict(edif)))
        
    deps = conn.execute("SELECT id FROM departamentos WHERE edificio_id=?", (edificio_id,)).fetchall()
    for d in deps:
        eliminar_departamento(d["id"])
        
    conn.execute("DELETE FROM conceptos_edificio WHERE edificio_id=?", (edificio_id,))
    conn.execute("DELETE FROM edificios WHERE id=?", (edificio_id,))
    conn.commit()
    conn.close()

# --- DEPARTAMENTOS ---
def obtener_departamentos(edificio_id=None):
    conn = get_connection()
    if edificio_id:
        rows = conn.execute("SELECT * FROM departamentos WHERE edificio_id=? AND activo=1 ORDER BY identificador", (edificio_id,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT d.*, e.nombre as edificio_nombre 
            FROM departamentos d JOIN edificios e ON d.edificio_id = e.id 
            WHERE d.activo=1 AND e.activo=1 ORDER BY e.nombre, d.identificador
        """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def guardar_departamento(dep_id, edificio_id, identificador, inquilino, inicio, fin, dia, aumentos, conceptos_default="", numero_recibo=1):
    conn = get_connection()
    c = conn.cursor()
    if dep_id:
        c.execute("""UPDATE departamentos SET identificador=?, inquilino=?, inicio_contrato=?, 
                     fin_contrato=?, dia_vencimiento_pago=?, aumentos_notas=?, conceptos_default=?, numero_recibo=? WHERE id=?""",
                  (identificador, inquilino, inicio, fin, dia, aumentos, conceptos_default, numero_recibo, dep_id))
    else:
        c.execute("""INSERT INTO departamentos (edificio_id, identificador, inquilino, inicio_contrato, 
                     fin_contrato, dia_vencimiento_pago, aumentos_notas, conceptos_default, numero_recibo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (edificio_id, identificador, inquilino, inicio, fin, dia, aumentos, conceptos_default, numero_recibo))
    conn.commit()
    conn.close()

def actualizar_conceptos_departamento(dep_id, conceptos_default):
    conn = get_connection()
    conn.execute("UPDATE departamentos SET conceptos_default=? WHERE id=?", (conceptos_default, dep_id))
    conn.commit()
    conn.close()

def eliminar_departamento(dep_id):
    import json
    conn = get_connection()
    dep = conn.execute("SELECT * FROM departamentos WHERE id=?", (dep_id,)).fetchone()
    if dep:
        guardar_en_papelera("Departamento", dep["identificador"], json.dumps(dict(dep)))
    # Eliminar items de recibos asociados
    conn.execute("DELETE FROM recibo_items WHERE recibo_id IN (SELECT id FROM recibos WHERE departamento_id=?)", (dep_id,))
    # Eliminar recibos asociados
    conn.execute("DELETE FROM recibos WHERE departamento_id=?", (dep_id,))
    # Eliminar el departamento
    conn.execute("DELETE FROM departamentos WHERE id=?", (dep_id,))
    conn.commit()
    conn.close()

# --- CONCEPTOS POR EDIFICIO ---
def obtener_conceptos_edificio(edificio_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM conceptos_edificio WHERE edificio_id=?", (edificio_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def guardar_concepto_edificio(edificio_id, categoria, concepto, precio):
    conn = get_connection()
    conn.execute("INSERT INTO conceptos_edificio (edificio_id, categoria, concepto, precio_default) VALUES (?, ?, ?, ?)",
                 (edificio_id, categoria, concepto, precio))
    conn.commit()
    conn.close()

def limpiar_conceptos_edificio(edificio_id):
    conn = get_connection()
    conn.execute("DELETE FROM conceptos_edificio WHERE edificio_id=?", (edificio_id,))
    conn.commit()
    conn.close()

# --- RECIBOS ---
def obtener_recibos():
    conn = get_connection()
    rows = conn.execute("""
        SELECT r.*, d.identificador, d.inquilino, d.inicio_contrato, d.fin_contrato, e.nombre as edificio_nombre
        FROM recibos r 
        JOIN departamentos d ON r.departamento_id = d.id
        JOIN edificios e ON d.edificio_id = e.id
        ORDER BY r.fecha_emision DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def obtener_recibo(recibo_id):
    conn = get_connection()
    row = conn.execute("""
        SELECT r.*, d.identificador, d.inquilino, d.inicio_contrato, d.fin_contrato, e.nombre as edificio_nombre, e.ruta_plantilla, e.ruta_guardado, e.mapeo_celdas
        FROM recibos r 
        JOIN departamentos d ON r.departamento_id = d.id
        JOIN edificios e ON d.edificio_id = e.id
        WHERE r.id=?
    """, (recibo_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def crear_recibo(departamento_id, periodo):
    conn = get_connection()
    c = conn.cursor()
    row = c.execute("SELECT numero_recibo FROM departamentos WHERE id=?", (departamento_id,)).fetchone()
    nro_recibo = row["numero_recibo"] if row and row["numero_recibo"] is not None else 1
    
    c.execute("INSERT INTO recibos (departamento_id, periodo, numero_recibo) VALUES (?, ?, ?)", (departamento_id, periodo, nro_recibo))
    new_id = c.lastrowid
    
    c.execute("UPDATE departamentos SET numero_recibo = numero_recibo + 1 WHERE id=?", (departamento_id,))
    
    conn.commit()
    conn.close()
    return new_id

def actualizar_recibo(recibo_id, estado=None, archivo_excel=None, total=None, periodo=None, nota=None, fecha_emision=None):
    conn = get_connection()
    campos = []
    valores = []
    if estado is not None: campos.append("estado=?"); valores.append(estado)
    if archivo_excel is not None: campos.append("archivo_excel=?"); valores.append(archivo_excel)
    if total is not None: campos.append("total=?"); valores.append(total)
    if periodo is not None: campos.append("periodo=?"); valores.append(periodo)
    if nota is not None: campos.append("nota=?"); valores.append(nota)
    if fecha_emision is not None: campos.append("fecha_emision=?"); valores.append(fecha_emision)
    if campos:
        valores.append(recibo_id)
        conn.execute(f"UPDATE recibos SET {', '.join(campos)} WHERE id=?", valores)
        conn.commit()
    conn.close()

def eliminar_recibo(recibo_id):
    conn = get_connection()
    conn.execute("DELETE FROM recibos WHERE id=?", (recibo_id,))
    conn.commit()
    conn.close()

# --- ITEMS RECIBO ---
def obtener_items_recibo(recibo_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM recibo_items WHERE recibo_id=? ORDER BY id", (recibo_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def agregar_item(recibo_id, categoria, concepto, cantidad, precio_unitario):
    subtotal = cantidad * precio_unitario
    conn = get_connection()
    conn.execute("""INSERT INTO recibo_items (recibo_id, categoria, concepto, cantidad, precio_unitario, subtotal)
                 VALUES (?, ?, ?, ?, ?, ?)""", (recibo_id, categoria, concepto, cantidad, precio_unitario, subtotal))
    conn.commit()
    conn.close()
    _recalcular_total(recibo_id)

def actualizar_item(item_id, categoria, concepto, cantidad, precio_unitario):
    subtotal = cantidad * precio_unitario
    conn = get_connection()
    conn.execute("""UPDATE recibo_items SET categoria=?, concepto=?, cantidad=?, precio_unitario=?, subtotal=? 
                    WHERE id=?""", (categoria, concepto, cantidad, precio_unitario, subtotal, item_id))
    row = conn.execute("SELECT recibo_id FROM recibo_items WHERE id=?", (item_id,)).fetchone()
    conn.commit()
    conn.close()
    if row: _recalcular_total(row["recibo_id"])

def _recalcular_total(recibo_id):
    conn = get_connection()
    row = conn.execute("SELECT COALESCE(SUM(subtotal), 0) as total FROM recibo_items WHERE recibo_id=?", (recibo_id,)).fetchone()
    conn.execute("UPDATE recibos SET total=? WHERE id=?", (row["total"], recibo_id))
    conn.commit()
    conn.close()
