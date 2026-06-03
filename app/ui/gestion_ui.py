from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QPushButton, QMessageBox, QTreeWidget,
                             QTreeWidgetItem, QStackedWidget, QWidget, QFileDialog, QGroupBox)
from PyQt6.QtCore import Qt
from app.core import database
import json

class VentanaMapeo(QDialog):
    def __init__(self, parent=None, mapeo_actual=""):
        super().__init__(parent)
        self.setWindowTitle("Mapeo de Celdas Excel")
        self.resize(350, 450)
        self.mapeo = json.loads(mapeo_actual) if mapeo_actual else {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.fields = {
            "inquilino": QLineEdit(self.mapeo.get("inquilino", "")),
            "departamento": QLineEdit(self.mapeo.get("departamento", "")),
            "edificio": QLineEdit(self.mapeo.get("edificio", "")),
            "periodo": QLineEdit(self.mapeo.get("periodo", "")),
            "fecha": QLineEdit(self.mapeo.get("fecha", "")),
            "total": QLineEdit(self.mapeo.get("total", "")),
            "tabla_fila": QLineEdit(self.mapeo.get("tabla_fila", "")),
            "tabla_col_cant": QLineEdit(self.mapeo.get("tabla_col_cant", "")),
            "tabla_col_concepto": QLineEdit(self.mapeo.get("tabla_col_concepto", "")),
            "tabla_col_precio": QLineEdit(self.mapeo.get("tabla_col_precio", "")),
            "tabla_col_subtotal": QLineEdit(self.mapeo.get("tabla_col_subtotal", ""))
        }
        
        for k, v in self.fields.items():
            if k == "tabla_fila": v.setPlaceholderText("Ej: 15 (Número de fila)")
            elif k.startswith("tabla_col"): v.setPlaceholderText("Ej: A (Letra de columna)")
            else: v.setPlaceholderText("Ej: C5")
            form.addRow(f"{k.replace('tabla_col_', 'Columna ').capitalize()}:", v)
            
        btn_save = QPushButton("Guardar Mapeo")
        btn_save.clicked.connect(self.guardar)
        layout.addLayout(form)
        layout.addWidget(btn_save)

    def guardar(self):
        self.mapeo = {k: v.text().strip().upper() for k, v in self.fields.items()}
        self.accept()

class VentanaGestion(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestión de Edificios y Departamentos")
        self.resize(850, 500)
        
        self.init_ui()
        self.cargar_arbol()
        
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        
        # --- Panel Izquierdo: Árbol ---
        left_panel = QVBoxLayout()
        self.arbol = QTreeWidget()
        self.arbol.setHeaderLabel("Edificios y Departamentos")
        self.arbol.itemSelectionChanged.connect(self.mostrar_detalles)
        
        botones_layout = QHBoxLayout()
        btn_nuevo_edif = QPushButton("+ Nuevo Edificio")
        btn_nuevo_edif.clicked.connect(self.nuevo_edificio)
        btn_nuevo_dep = QPushButton("+ Depto al Edif.")
        btn_nuevo_dep.clicked.connect(self.nuevo_departamento)
        
        botones_layout.addWidget(btn_nuevo_edif)
        botones_layout.addWidget(btn_nuevo_dep)
        
        left_panel.addWidget(self.arbol)
        left_panel.addLayout(botones_layout)
        
        # --- Panel Derecho: Stacked Widget ---
        self.stacked = QStackedWidget()
        
        # Widget Vacio
        self.page_vacio = QWidget()
        
        # Widget Edificio
        self.page_edificio = QWidget()
        form_edif = QFormLayout(self.page_edificio)
        self.edif_nombre = QLineEdit()
        self.edif_dir = QLineEdit()
        self.edif_plantilla = QLineEdit()
        self.edif_guardado = QLineEdit()
        
        btn_plantilla = QPushButton("...")
        btn_plantilla.clicked.connect(self.buscar_plantilla)
        lay_plantilla = QHBoxLayout()
        lay_plantilla.addWidget(self.edif_plantilla)
        lay_plantilla.addWidget(btn_plantilla)
        
        btn_guardado = QPushButton("...")
        btn_guardado.clicked.connect(self.buscar_guardado)
        lay_guardado = QHBoxLayout()
        lay_guardado.addWidget(self.edif_guardado)
        lay_guardado.addWidget(btn_guardado)
        
        self.btn_mapeo = QPushButton("Configurar Mapeo de Celdas")
        self.btn_mapeo.clicked.connect(self.abrir_mapeo)
        
        form_edif.addRow("Nombre Edificio:", self.edif_nombre)
        form_edif.addRow("Dirección:", self.edif_dir)
        form_edif.addRow("Plantilla Excel:", lay_plantilla)
        form_edif.addRow("Mapeo de Datos:", self.btn_mapeo)
        form_edif.addRow("Carpeta de Guardado:", lay_guardado)
        
        btn_guardar_edif = QPushButton("Guardar Edificio")
        btn_guardar_edif.setStyleSheet("background-color: #27AE60; color: white; padding:8px; font-weight:bold;")
        btn_guardar_edif.clicked.connect(self.guardar_edificio)
        form_edif.addRow("", btn_guardar_edif)
        
        # Widget Departamento
        self.page_depto = QWidget()
        form_dep = QFormLayout(self.page_depto)
        self.dep_ident = QLineEdit()
        self.dep_ident.setPlaceholderText("Ej: 1A, PB C, Local 1")
        self.dep_inq = QLineEdit()
        self.dep_inicio = QLineEdit()
        self.dep_fin = QLineEdit()
        self.dep_dia = QLineEdit()
        self.dep_aumentos = QLineEdit()
        
        form_dep.addRow("Identificador:", self.dep_ident)
        form_dep.addRow("Inquilino:", self.dep_inq)
        form_dep.addRow("Inicio Contrato:", self.dep_inicio)
        form_dep.addRow("Fin Contrato:", self.dep_fin)
        form_dep.addRow("Día de Pago:", self.dep_dia)
        form_dep.addRow("Notas de Aumentos:", self.dep_aumentos)
        
        btn_guardar_dep = QPushButton("Guardar Departamento")
        btn_guardar_dep.setStyleSheet("background-color: #2980B9; color: white; padding:8px; font-weight:bold;")
        btn_guardar_dep.clicked.connect(self.guardar_departamento)
        form_dep.addRow("", btn_guardar_dep)
        
        self.stacked.addWidget(self.page_vacio)
        self.stacked.addWidget(self.page_edificio)
        self.stacked.addWidget(self.page_depto)
        
        main_layout.addLayout(left_panel, 1)
        main_layout.addWidget(self.stacked, 2)
        
        self.item_actual_id = None
        self.tipo_actual = None
        self.current_mapeo = ""

    def abrir_mapeo(self):
        diag = VentanaMapeo(self, self.current_mapeo)
        if diag.exec():
            self.current_mapeo = json.dumps(diag.mapeo)
            self.btn_mapeo.setText("Configurar Mapeo de Celdas (Configurado ✔️)")

    def buscar_plantilla(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar Plantilla Excel", "", "Excel (*.xlsx)")
        if archivo: self.edif_plantilla.setText(archivo)
        
    def buscar_guardado(self):
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta Específica")
        if carpeta: self.edif_guardado.setText(carpeta)

    def cargar_arbol(self):
        self.arbol.clear()
        edificios = database.obtener_edificios()
        departamentos = database.obtener_departamentos()
        
        for e in edificios:
            item_e = QTreeWidgetItem([e["nombre"]])
            item_e.setData(0, Qt.ItemDataRole.UserRole, e["id"])
            item_e.setData(0, Qt.ItemDataRole.UserRole+1, "edificio")
            self.arbol.addTopLevelItem(item_e)
            
            for d in departamentos:
                if d["edificio_id"] == e["id"]:
                    nombre_inq = d.get('inquilino', 'Sin Inquilino') or 'Sin Inquilino'
                    item_d = QTreeWidgetItem([f"Depto {d['identificador']} - {nombre_inq}"])
                    item_d.setData(0, Qt.ItemDataRole.UserRole, d["id"])
                    item_d.setData(0, Qt.ItemDataRole.UserRole+1, "departamento")
                    item_e.addChild(item_d)
            item_e.setExpanded(True)

    def mostrar_detalles(self):
        seleccion = self.arbol.selectedItems()
        if not seleccion:
            self.stacked.setCurrentWidget(self.page_vacio)
            return
            
        item = seleccion[0]
        self.item_actual_id = item.data(0, Qt.ItemDataRole.UserRole)
        self.tipo_actual = item.data(0, Qt.ItemDataRole.UserRole+1)
        
        if self.tipo_actual == "edificio":
            self.stacked.setCurrentWidget(self.page_edificio)
            edificios = database.obtener_edificios()
            edif = next((e for e in edificios if e["id"] == self.item_actual_id), None)
            if edif:
                self.edif_nombre.setText(edif["nombre"])
                self.edif_dir.setText(edif.get("direccion", "") or "")
                self.edif_plantilla.setText(edif.get("ruta_plantilla", "") or "")
                self.edif_guardado.setText(edif.get("ruta_guardado", "") or "")
                self.current_mapeo = edif.get("mapeo_celdas", "")
                if self.current_mapeo: self.btn_mapeo.setText("Configurar Mapeo de Celdas (Configurado ✔️)")
                else: self.btn_mapeo.setText("Configurar Mapeo de Celdas")
                
        elif self.tipo_actual == "departamento":
            self.stacked.setCurrentWidget(self.page_depto)
            deptos = database.obtener_departamentos()
            dep = next((d for d in deptos if d["id"] == self.item_actual_id), None)
            if dep:
                self.dep_ident.setText(dep["identificador"])
                self.dep_inq.setText(dep.get("inquilino", "") or "")
                self.dep_inicio.setText(dep.get("inicio_contrato", "") or "")
                self.dep_fin.setText(dep.get("fin_contrato", "") or "")
                self.dep_dia.setText(str(dep.get("dia_vencimiento_pago", "")))
                self.dep_aumentos.setText(dep.get("aumentos_notas", "") or "")

    def nuevo_edificio(self):
        self.arbol.clearSelection()
        self.item_actual_id = None
        self.tipo_actual = "edificio"
        self.edif_nombre.clear()
        self.edif_dir.clear()
        self.edif_plantilla.clear()
        self.edif_guardado.clear()
        self.current_mapeo = ""
        self.btn_mapeo.setText("Configurar Mapeo de Celdas")
        self.stacked.setCurrentWidget(self.page_edificio)
        self.edif_nombre.setFocus()
        
    def nuevo_departamento(self):
        seleccion = self.arbol.selectedItems()
        if not seleccion or seleccion[0].data(0, Qt.ItemDataRole.UserRole+1) != "edificio":
            QMessageBox.warning(self, "Aviso", "Primero selecciona un Edificio en la lista de la izquierda para agregarle un departamento.")
            return
            
        self.item_actual_id = None
        self.tipo_actual = "departamento"
        self.dep_ident.clear()
        self.dep_inq.clear()
        self.dep_inicio.clear()
        self.dep_fin.clear()
        self.dep_dia.clear()
        self.dep_aumentos.clear()
        self.stacked.setCurrentWidget(self.page_depto)
        self.dep_ident.setFocus()

    def guardar_edificio(self):
        nombre = self.edif_nombre.text().strip()
        if not nombre: return
        dir_val = self.edif_dir.text().strip()
        plantilla = self.edif_plantilla.text().strip()
        guardado = self.edif_guardado.text().strip()
        
        if self.item_actual_id and self.tipo_actual == "edificio":
            database.actualizar_edificio(self.item_actual_id, nombre, dir_val, plantilla, guardado, self.current_mapeo)
        else:
            database.agregar_edificio(nombre, dir_val, plantilla, guardado, self.current_mapeo)
            
        self.cargar_arbol()
        
    def guardar_departamento(self):
        identificador = self.dep_ident.text().strip()
        if not identificador: return
        
        inq = self.dep_inq.text().strip()
        ini = self.dep_inicio.text().strip()
        fin = self.dep_fin.text().strip()
        dia = self.dep_dia.text().strip()
        aum = self.dep_aumentos.text().strip()
        
        if self.item_actual_id and self.tipo_actual == "departamento":
            deptos = database.obtener_departamentos()
            dep = next((d for d in deptos if d["id"] == self.item_actual_id), None)
            edif_id = dep["edificio_id"] if dep else 0
            database.guardar_departamento(self.item_actual_id, edif_id, identificador, inq, ini, fin, dia, aum)
        else:
            seleccion = self.arbol.selectedItems()
            edif_id = seleccion[0].data(0, Qt.ItemDataRole.UserRole)
            database.guardar_departamento(None, edif_id, identificador, inq, ini, fin, dia, aum)
            
        self.cargar_arbol()
