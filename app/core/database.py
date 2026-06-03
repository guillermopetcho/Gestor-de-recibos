import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "mi_admin.db"

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
        FOREIGN KEY (edificio_id) REFERENCES edificios(id)
    )""")

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

# --- EDIFICIOS ---
def obtener_edificios():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM edificios WHERE activo=1 ORDER BY nombre").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def agregar_edificio(nombre, direccion, ruta_plantilla="", ruta_guardado="", mapeo_celdas=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO edificios (nombre, direccion, ruta_plantilla, ruta_guardado, mapeo_celdas) VALUES (?, ?, ?, ?, ?)",
              (nombre, direccion, ruta_plantilla, ruta_guardado, mapeo_celdas))
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id

def actualizar_edificio(edificio_id, nombre, direccion, ruta_plantilla, ruta_guardado, mapeo_celdas=""):
    conn = get_connection()
    conn.execute("UPDATE edificios SET nombre=?, direccion=?, ruta_plantilla=?, ruta_guardado=?, mapeo_celdas=? WHERE id=?",
                 (nombre, direccion, ruta_plantilla, ruta_guardado, mapeo_celdas, edificio_id))
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

def guardar_departamento(dep_id, edificio_id, identificador, inquilino, inicio, fin, dia, aumentos):
    conn = get_connection()
    c = conn.cursor()
    if dep_id:
        c.execute("""UPDATE departamentos SET identificador=?, inquilino=?, inicio_contrato=?, 
                     fin_contrato=?, dia_vencimiento_pago=?, aumentos_notas=? WHERE id=?""",
                  (identificador, inquilino, inicio, fin, dia, aumentos, dep_id))
    else:
        c.execute("""INSERT INTO departamentos (edificio_id, identificador, inquilino, inicio_contrato, 
                     fin_contrato, dia_vencimiento_pago, aumentos_notas) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                  (edificio_id, identificador, inquilino, inicio, fin, dia, aumentos))
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
        SELECT r.*, d.identificador, d.inquilino, e.nombre as edificio_nombre
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
        SELECT r.*, d.identificador, d.inquilino, e.nombre as edificio_nombre, e.ruta_plantilla, e.ruta_guardado, e.mapeo_celdas
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
    c.execute("INSERT INTO recibos (departamento_id, periodo) VALUES (?, ?)", (departamento_id, periodo))
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id

def actualizar_recibo(recibo_id, estado=None, archivo_excel=None, total=None, periodo=None, nota=None):
    conn = get_connection()
    campos = []
    valores = []
    if estado is not None: campos.append("estado=?"); valores.append(estado)
    if archivo_excel is not None: campos.append("archivo_excel=?"); valores.append(archivo_excel)
    if total is not None: campos.append("total=?"); valores.append(total)
    if periodo is not None: campos.append("periodo=?"); valores.append(periodo)
    if nota is not None: campos.append("nota=?"); valores.append(nota)
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
