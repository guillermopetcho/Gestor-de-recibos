from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QComboBox, QLineEdit, QPushButton, QMessageBox, QLabel)
from PyQt6.QtCore import Qt
from app.core import database

class VentanaEdicionMasiva(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edición Masiva de Recibos (Borradores)")
        self.resize(450, 300)
        
        self.recibos_borrador = []
        self.conceptos_disponibles = set()
        
        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        label_info = QLabel("Aplica ajustes de precio a todos los recibos que estén en estado 'Borrador'. Esto facilita las actualizaciones por inflación o suba de expensas para todos los departamentos en un solo clic.")
        label_info.setWordWrap(True)
        label_info.setStyleSheet("color: #3498DB; font-style: italic; margin-bottom: 15px; font-size: 13px;")
        layout.addWidget(label_info)
        
        form_layout = QFormLayout()
        
        self.cb_edificio = QComboBox()
        self.cb_edificio.currentIndexChanged.connect(self.filtrar_conceptos)
        
        self.cb_concepto = QComboBox()
        
        self.cb_tipo_ajuste = QComboBox()
        self.cb_tipo_ajuste.addItems([
            "Aumento Porcentual (+%)",
            "Descuento Porcentual (-%)",
            "Fijar Monto Exacto ($)",
            "Sumar Monto Fijo (+$)"
        ])
        
        self.le_valor = QLineEdit()
        self.le_valor.setPlaceholderText("Ej: 15 (para 15%) o 1500 (para $)")
        
        form_layout.addRow("Edificio Objetivo:", self.cb_edificio)
        form_layout.addRow("Concepto a Modificar:", self.cb_concepto)
        form_layout.addRow("Tipo de Ajuste:", self.cb_tipo_ajuste)
        form_layout.addRow("Valor del Ajuste:", self.le_valor)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        self.btn_aplicar = QPushButton("Aplicar Ajuste Masivo")
        self.btn_aplicar.setStyleSheet("background-color: #E67E22; color: white; font-weight: bold; padding: 10px; font-size: 14px; border-radius: 4px;")
        self.btn_aplicar.clicked.connect(self.aplicar_ajuste)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_aplicar)
        
        layout.addLayout(btn_layout)

    def cargar_datos(self):
        todos_recibos = database.obtener_recibos()
        # Filtrar los que tengan estado borrador
        self.recibos_borrador = [r for r in todos_recibos if str(r.get('estado', '')).lower() == 'borrador']
        
        self.cb_edificio.clear()
        self.cb_edificio.addItem("Todos los Edificios", -1)
        
        edificios_db = database.obtener_edificios()
        for e in edificios_db:
            self.cb_edificio.addItem(e['nombre'], e['id'])
            
        self.filtrar_conceptos()

    def filtrar_conceptos(self):
        self.cb_concepto.clear()
        self.conceptos_disponibles.clear()
        
        edif_id = self.cb_edificio.currentData()
        nombre_edif_sel = self.cb_edificio.currentText()
        
        for r in self.recibos_borrador:
            if edif_id != -1 and r['edificio_nombre'] != nombre_edif_sel:
                continue
                
            items = database.obtener_items_recibo(r['id'])
            for i in items:
                self.conceptos_disponibles.add(i['concepto'])
                
        for c in sorted(list(self.conceptos_disponibles)):
            self.cb_concepto.addItem(c)
            
        if not self.conceptos_disponibles:
            self.cb_concepto.addItem("-- No hay borradores/conceptos --")
            self.btn_aplicar.setEnabled(False)
            self.btn_aplicar.setStyleSheet("background-color: #7F8C8D; color: white; padding: 10px; border-radius: 4px;")
        else:
            self.btn_aplicar.setEnabled(True)
            self.btn_aplicar.setStyleSheet("background-color: #E67E22; color: white; font-weight: bold; padding: 10px; border-radius: 4px;")

    def aplicar_ajuste(self):
        if not self.conceptos_disponibles:
            return
            
        concepto_obj = self.cb_concepto.currentText()
        valor_str = self.le_valor.text().replace(',', '.')
        
        try:
            valor = float(valor_str)
        except ValueError:
            QMessageBox.warning(self, "Error", "Ingresa un valor numérico válido.\nNo incluyas signos de $ o %.")
            return
            
        if valor < 0:
            QMessageBox.warning(self, "Error", "El valor no puede ser negativo.")
            return
            
        tipo_ajuste = self.cb_tipo_ajuste.currentIndex()
        edif_id = self.cb_edificio.currentData()
        nombre_edif_sel = self.cb_edificio.currentText()
        
        # Confirmación de la operación para evitar errores críticos
        simbolo = "%" if tipo_ajuste in [0, 1] else "$"
        operacion_str = self.cb_tipo_ajuste.currentText()
        alcance = "TODOS los edificios" if edif_id == -1 else f"el edificio {nombre_edif_sel}"
        
        msg = f"¿Seguro que deseas aplicar un {operacion_str} de {valor}{simbolo} al concepto '{concepto_obj}' en {alcance}?\n\nEsta acción modificará todos los borradores que coincidan."
        resp = QMessageBox.question(self, "Confirmar Ajuste Masivo", msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if resp != QMessageBox.StandardButton.Yes:
            return
            
        items_modificados = 0
        recibos_afectados = set()
        
        for r in self.recibos_borrador:
            if edif_id != -1 and r['edificio_nombre'] != nombre_edif_sel:
                continue
                
            items = database.obtener_items_recibo(r['id'])
            for i in items:
                if i['concepto'] == concepto_obj:
                    precio_actual = float(i['precio_unitario'])
                    nuevo_precio = precio_actual
                    
                    if tipo_ajuste == 0:
                        nuevo_precio = precio_actual * (1 + valor / 100.0)
                    elif tipo_ajuste == 1:
                        nuevo_precio = precio_actual * (1 - valor / 100.0)
                    elif tipo_ajuste == 2:
                        nuevo_precio = valor
                    elif tipo_ajuste == 3:
                        nuevo_precio = precio_actual + valor
                        
                    if nuevo_precio < 0: nuevo_precio = 0
                    
                    database.actualizar_item(i['id'], i['categoria'], i['concepto'], i['cantidad'], nuevo_precio)
                    items_modificados += 1
                    recibos_afectados.add(r['id'])
                    
        if items_modificados > 0:
            QMessageBox.information(self, "Ajuste Exitoso", f"Se actualizaron {items_modificados} ítems en {len(recibos_afectados)} borradores.")
            self.accept()
        else:
            QMessageBox.information(self, "Sin Cambios", "No se encontró ningún ítem con ese concepto en los borradores disponibles.")
