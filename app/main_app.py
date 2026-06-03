import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTreeWidget, QTreeWidgetItem,
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QMenu, QInputDialog, QSplitter)
from PyQt6.QtCore import Qt
from app.core import database
from app.core import excel_manager
from app.ui import gestion_ui
from app.ui import config_ui

class MiAdminApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mi-Admin - Panel Principal")
        self.resize(1000, 600)
        
        database.init_database()
        self.init_ui()
        self.cargar_datos_iniciales()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        left_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # --- PANEL IZQUIERDO ARRIBA (Lista Recibos) ---
        top_left_widget = QWidget()
        top_left_layout = QVBoxLayout(top_left_widget)
        top_left_layout.setContentsMargins(0, 0, 0, 0)
        
        label_recibos = QLabel("<b>Gestión de Selección</b>")
        self.lista_recibos = QTableWidget(0, 6)
        self.lista_recibos.setHorizontalHeaderLabels(["Edificio", "Identificador", "Nombre", "Período", "Total", "Nota"])
        self.lista_recibos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.lista_recibos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.lista_recibos.itemSelectionChanged.connect(self.on_recibo_seleccionado)
        self.lista_recibos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.lista_recibos.customContextMenuRequested.connect(self.mostrar_menu_recibos)
        
        top_left_layout.addWidget(label_recibos)
        top_left_layout.addWidget(self.lista_recibos)
        
        # --- PANEL IZQUIERDO ABAJO (Detalles) ---
        bottom_left_widget = QWidget()
        bottom_left_layout = QVBoxLayout(bottom_left_widget)
        bottom_left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.label_detalle = QLabel("<b>Detalle del Recibo: (Selecciona uno arriba)</b>")
        self.label_detalle.setStyleSheet("font-size: 14px; color: #3498DB; margin-top: 10px;")
        
        self.panel_cabecera = QWidget()
        self.panel_cabecera.setStyleSheet("background-color: #2D2D30; border: 1px solid #555; border-radius: 5px;")
        
        from PyQt6.QtWidgets import QGridLayout
        lay_cab = QGridLayout(self.panel_cabecera)
        
        self.lbl_cab_edif = QLabel("<b>Edificio:</b> -")
        self.lbl_cab_ident = QLabel("<b>Identificador:</b> -")
        self.lbl_cab_per = QLabel("<b>Período:</b> -")
        self.lbl_cab_fecha = QLabel("<b>Fecha:</b> -")
        self.lbl_cab_tot = QLabel("<b>Total a Cobrar:</b> $0.00")
        self.lbl_cab_tot.setStyleSheet("color: #2ECC71; font-weight: bold; font-size: 13px;")
        
        lay_cab.addWidget(self.lbl_cab_edif, 0, 0)
        lay_cab.addWidget(self.lbl_cab_ident, 0, 1)
        lay_cab.addWidget(self.lbl_cab_per, 1, 0)
        lay_cab.addWidget(self.lbl_cab_fecha, 1, 1)
        lay_cab.addWidget(self.lbl_cab_tot, 1, 2)
        
        self.tabla_items = QTableWidget(0, 5)
        self.tabla_items.setHorizontalHeaderLabels(["Cant.", "Categoría", "Concepto", "Precio Unit.", "Subtotal"])
        self.tabla_items.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        bottom_left_layout.addWidget(self.label_detalle)
        bottom_left_layout.addWidget(self.panel_cabecera)
        bottom_left_layout.addWidget(QLabel("<i>Doble clic en Precio, Concepto o Cantidad para editar los valores de la tabla:</i>"))
        bottom_left_layout.addWidget(self.tabla_items)
        
        left_splitter.addWidget(top_left_widget)
        left_splitter.addWidget(bottom_left_widget)
        left_splitter.setStretchFactor(0, 1)
        left_splitter.setStretchFactor(1, 2)
        
        # --- PANEL DERECHO ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        label_propiedades = QLabel("<b>Edificios y Departamentos</b>")
        self.arbol_propiedades = QTreeWidget()
        self.arbol_propiedades.setHeaderHidden(True)
        self.arbol_propiedades.itemChanged.connect(self.on_arbol_item_changed)
        
        botones_layout = QVBoxLayout()
        self.btn_configuracion = QPushButton("Configuración")
        self.btn_configuracion.setStyleSheet("color: #D35400; font-weight: bold; padding:10px;")
        self.btn_configuracion.clicked.connect(self.abrir_configuracion)
        
        self.btn_gestion = QPushButton("Gestión de Edificios")
        self.btn_gestion.setStyleSheet("color: #2980B9; font-weight: bold; padding:10px;")
        self.btn_gestion.clicked.connect(self.abrir_gestion_propiedades)
        
        self.btn_generar = QPushButton("Generar Recibos")
        self.btn_generar.setStyleSheet("background-color: #27AE60; color: white; font-weight: bold; font-size: 14px; padding:15px;")
        self.btn_generar.clicked.connect(self.generar_recibos_seleccionados)
        
        botones_layout.addWidget(self.btn_configuracion)
        botones_layout.addWidget(self.btn_gestion)
        botones_layout.addSpacing(10)
        botones_layout.addWidget(self.btn_generar)
        
        right_layout.addWidget(label_propiedades)
        right_layout.addWidget(self.arbol_propiedades)
        right_layout.addLayout(botones_layout)
        
        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(right_panel)
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 1)
        
        layout_central = QHBoxLayout(central_widget)
        layout_central.addWidget(main_splitter)
        
        self.tabla_items.cellChanged.connect(self.on_item_modificado)
        self._actualizando_tabla = False

    def on_arbol_item_changed(self, item, column):
        if item.data(0, Qt.ItemDataRole.UserRole+1) == "edificio":
            self.arbol_propiedades.blockSignals(True)
            estado = item.checkState(0)
            for i in range(item.childCount()):
                item.child(i).setCheckState(0, estado)
            self.arbol_propiedades.blockSignals(False)

    def mostrar_menu_recibos(self, pos):
        selected = self.lista_recibos.selectedItems()
        if not selected: return
        
        menu = QMenu(self)
        accion_editar = menu.addAction("Editar ")
        accion_copiar = menu.addAction("Duplicar ")
        menu.addSeparator()
        accion_borrar = menu.addAction("Eliminar")
        
        accion = menu.exec(self.lista_recibos.viewport().mapToGlobal(pos))
        if not accion: return
        
        r_id = self.lista_recibos.item(selected[0].row(), 0).data(Qt.ItemDataRole.UserRole)
        
        if accion == accion_borrar:
            resp = QMessageBox.question(self, "Eliminar", "¿Seguro que deseas eliminar permanentemente este recibo y sus ítems?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if resp == QMessageBox.StandardButton.Yes:
                database.eliminar_recibo(r_id)
                self.actualizar_lista_recibos()
                self.tabla_items.setRowCount(0)
                
        elif accion == accion_copiar:
            r = database.obtener_recibo(r_id)
            items = database.obtener_items_recibo(r_id)
            nuevo_id = database.crear_recibo(r["departamento_id"], r["periodo"] + " (Copia)")
            for item in items:
                database.agregar_item(nuevo_id, item["categoria"], item["concepto"], item["cantidad"], item["precio_unitario"])
            self.actualizar_lista_recibos()
            
        elif accion == accion_editar:
            r = database.obtener_recibo(r_id)
            nuevo_periodo, ok = QInputDialog.getText(self, "Editar Período", "Ingresa el nuevo período (Ej: 06/2026):", text=r["periodo"])
            if ok and nuevo_periodo.strip():
                database.actualizar_recibo(r_id, periodo=nuevo_periodo.strip())
                self.actualizar_lista_recibos()

    def abrir_nota(self, recibo_id):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit
        r = database.obtener_recibo(recibo_id)
        diag = QDialog(self)
        diag.setWindowTitle(f"Notas: Depto {r['identificador']}")
        diag.resize(400, 300)
        lay = QVBoxLayout(diag)
        text_edit = QTextEdit()
        text_edit.setPlainText(r.get("nota", "") or "")
        lay.addWidget(text_edit)
        btn_save = QPushButton("Guardar Nota")
        def save():
            database.actualizar_recibo(recibo_id, nota=text_edit.toPlainText().strip())
            diag.accept()
        btn_save.clicked.connect(save)
        lay.addWidget(btn_save)
        diag.exec()

    def cargar_datos_iniciales(self):
        self.actualizar_arbol_propiedades()
        self.actualizar_lista_recibos()

    def actualizar_arbol_propiedades(self):
        self.arbol_propiedades.clear()
        edificios = database.obtener_edificios()
        departamentos = database.obtener_departamentos()
        
        for e in edificios:
            item_e = QTreeWidgetItem([e["nombre"]])
            # Permitir tildar todo el edificio
            item_e.setFlags(item_e.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item_e.setCheckState(0, Qt.CheckState.Unchecked)
            item_e.setData(0, Qt.ItemDataRole.UserRole, e["id"])
            item_e.setData(0, Qt.ItemDataRole.UserRole+1, "edificio")
            
            for d in departamentos:
                if d["edificio_id"] == e["id"]:
                    item_d = QTreeWidgetItem([f"Depto {d['identificador']} - {d['inquilino']}"])
                    item_d.setFlags(item_d.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item_d.setCheckState(0, Qt.CheckState.Unchecked)
                    item_d.setData(0, Qt.ItemDataRole.UserRole, d["id"])
                    item_d.setData(0, Qt.ItemDataRole.UserRole+1, "departamento")
                    item_e.addChild(item_d)
                    
            self.arbol_propiedades.addTopLevelItem(item_e)
            item_e.setExpanded(True)

    def actualizar_lista_recibos(self):
        self.lista_recibos.setRowCount(0)
        recibos = database.obtener_recibos()

        for row, r in enumerate(recibos):
            self.lista_recibos.insertRow(row)
            
            item_edif = QTableWidgetItem(r['edificio_nombre'])
            item_edif.setData(Qt.ItemDataRole.UserRole, r["id"])
            
            self.lista_recibos.setItem(row, 0, item_edif)
            self.lista_recibos.setItem(row, 1, QTableWidgetItem(r["identificador"]))
            self.lista_recibos.setItem(row, 2, QTableWidgetItem(r["inquilino"] or ""))
            self.lista_recibos.setItem(row, 3, QTableWidgetItem(r["periodo"]))
            self.lista_recibos.setItem(row, 4, QTableWidgetItem(f"${r['total']:,.2f}"))
            
            btn_nota = QPushButton("📝")
            btn_nota.setStyleSheet("background-color: transparent; border: none; font-size: 16px;")
            btn_nota.clicked.connect(lambda checked, r_id=r["id"]: self.abrir_nota(r_id))
            
            widget_btn = QWidget()
            lay_btn = QHBoxLayout(widget_btn)
            lay_btn.setContentsMargins(0,0,0,0)
            lay_btn.addWidget(btn_nota)
            
            self.lista_recibos.setCellWidget(row, 5, widget_btn)

    def on_recibo_seleccionado(self):
        selected_rows = self.lista_recibos.selectionModel().selectedRows()
        if not selected_rows:
            self.tabla_items.setRowCount(0)
            self.label_detalle.setText("<b>Detalle del Recibo: (Selecciona uno arriba)</b>")
            self.lbl_cab_edif.setText("<b>Edificio:</b> -")
            self.lbl_cab_ident.setText("<b>Identificador:</b> -")
            self.lbl_cab_per.setText("<b>Período:</b> -")
            self.lbl_cab_fecha.setText("<b>Fecha:</b> -")
            self.lbl_cab_tot.setText("<b>Total a Cobrar:</b> $0.00")
            return
            
        r_ids = [self.lista_recibos.item(r.row(), 0).data(Qt.ItemDataRole.UserRole) for r in selected_rows]
        
        if len(r_ids) == 1:
            self.actualizar_tabla_items(r_ids[0])
        else:
            self._actualizando_tabla = True
            self.tabla_items.setRowCount(0)
            
            edificios, identificadores, periodos, fechas = [], [], [], []
            total_global = 0.0
            
            for rid in r_ids:
                r = database.obtener_recibo(rid)
                if r:
                    if r['edificio_nombre'] not in edificios: edificios.append(r['edificio_nombre'])
                    if r['identificador'] not in identificadores: identificadores.append(r['identificador'])
                    if r['periodo'] not in periodos: periodos.append(r['periodo'])
                    f_em = str(r['fecha_emision']).split(' ')[0]
                    if f_em not in fechas: fechas.append(f_em)
                    total_global += r['total']
                    
            self.label_detalle.setText(f"<b>📄 Resumen de Selección Múltiple ({len(r_ids)} recibos)</b>")
            self.lbl_cab_edif.setText(f"<b>Edificios:</b> {'; '.join(edificios)}")
            self.lbl_cab_ident.setText(f"<b>Identificadores:</b> {'; '.join(identificadores)}")
            self.lbl_cab_per.setText(f"<b>Períodos:</b> {'; '.join(periodos)}")
            self.lbl_cab_fecha.setText(f"<b>Fechas:</b> {'; '.join(fechas)}")
            self.lbl_cab_tot.setText(f"<b>Total Combinado:</b> ${total_global:,.2f}")
            self._actualizando_tabla = False

    def actualizar_tabla_items(self, recibo_id):
        self._actualizando_tabla = True
        self.tabla_items.setRowCount(0)
        
        # Cargar variables de cabecera que irán al Excel
        r = database.obtener_recibo(recibo_id)
        if r:
            self.label_detalle.setText(f"<b>📄 Resumen de Recibo</b>")
            self.lbl_cab_edif.setText(f"<b>Edificio:</b> {r['edificio_nombre']}")
            self.lbl_cab_ident.setText(f"<b>Identificador:</b> {r['identificador']}")
            self.lbl_cab_per.setText(f"<b>Período:</b> {r['periodo']}")
            self.lbl_cab_fecha.setText(f"<b>Fecha:</b> {str(r['fecha_emision']).split(' ')[0]}")
            self.lbl_cab_tot.setText(f"<b>Total a Cobrar:</b> ${r['total']:,.2f}")
            
        items = database.obtener_items_recibo(recibo_id)
        
        for row, item in enumerate(items):
            self.tabla_items.insertRow(row)
            item_cant = QTableWidgetItem(str(item["cantidad"]))
            item_cant.setData(Qt.ItemDataRole.UserRole, item["id"])
            
            self.tabla_items.setItem(row, 0, item_cant)
            self.tabla_items.setItem(row, 1, QTableWidgetItem(item["categoria"]))
            self.tabla_items.setItem(row, 2, QTableWidgetItem(item["concepto"]))
            self.tabla_items.setItem(row, 3, QTableWidgetItem(str(item['precio_unitario'])))
            
            item_sub = QTableWidgetItem(f"${item['subtotal']:,.2f}")
            item_sub.setFlags(item_sub.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tabla_items.setItem(row, 4, item_sub)
            
        self._actualizando_tabla = False

    def on_item_modificado(self, row, column):
        if self._actualizando_tabla: return
        
        item_id = self.tabla_items.item(row, 0).data(Qt.ItemDataRole.UserRole)
        try:
            cant = float(self.tabla_items.item(row, 0).text())
            cat = self.tabla_items.item(row, 1).text()
            conc = self.tabla_items.item(row, 2).text()
            precio = float(self.tabla_items.item(row, 3).text())
            
            database.actualizar_item(item_id, cat, conc, cant, precio)
            
            selected = self.lista_recibos.selectedItems()
            if selected:
                r_row = selected[0].row()
                self.actualizar_lista_recibos()
                self.lista_recibos.selectRow(r_row)
                self.actualizar_tabla_items(self.lista_recibos.item(r_row, 0).data(Qt.ItemDataRole.UserRole))
        except ValueError:
            pass

    def abrir_configuracion(self):
        dialogo = config_ui.VentanaConfig(self)
        dialogo.exec()
        aplicar_tema(QApplication.instance())

    def abrir_gestion_propiedades(self):
        dialogo = gestion_ui.VentanaGestion(self)
        dialogo.exec()
        self.actualizar_arbol_propiedades()

    def generar_recibos_seleccionados(self):
        deptos_tildados = []
        for i in range(self.arbol_propiedades.topLevelItemCount()):
            item_e = self.arbol_propiedades.topLevelItem(i)
            # Si el edificio está tildado, marcamos todos sus hijos
            if item_e.checkState(0) == Qt.CheckState.Checked:
                for j in range(item_e.childCount()):
                    deptos_tildados.append(item_e.child(j).data(0, Qt.ItemDataRole.UserRole))
            else:
                for j in range(item_e.childCount()):
                    if item_e.child(j).checkState(0) == Qt.CheckState.Checked:
                        deptos_tildados.append(item_e.child(j).data(0, Qt.ItemDataRole.UserRole))
                        
        deptos_tildados = list(set(deptos_tildados)) # Eliminar duplicados
        selected = self.lista_recibos.selectedItems()
        
        if deptos_tildados:
            import datetime
            mes_actual = datetime.datetime.now().strftime("%m/%Y")
            for d_id in deptos_tildados:
                r_id = database.crear_recibo(d_id, mes_actual)
                database.agregar_item(r_id, "Alquiler", "Alquiler", 1, 0)
                database.agregar_item(r_id, "Servicios", "Luz", 1, 0)
                database.agregar_item(r_id, "Servicios", "Agua", 1, 0)
            
            # Limpiar tildes
            for i in range(self.arbol_propiedades.topLevelItemCount()):
                self.arbol_propiedades.topLevelItem(i).setCheckState(0, Qt.CheckState.Unchecked)
                for j in range(self.arbol_propiedades.topLevelItem(i).childCount()):
                    self.arbol_propiedades.topLevelItem(i).child(j).setCheckState(0, Qt.CheckState.Unchecked)
                    
            self.actualizar_lista_recibos()
            QMessageBox.information(self, "Borradores Creados", f"Se crearon borradores para {len(deptos_tildados)} departamentos.\nEdita los precios abajo y luego presiona Generar de nuevo.")
            
        elif selected:
            selected_rows = self.lista_recibos.selectionModel().selectedRows()
            r_ids = [self.lista_recibos.item(r.row(), 0).data(Qt.ItemDataRole.UserRole) for r in selected_rows]
            exitos = 0
            ultima_ruta = ""
            for rid in r_ids:
                try:
                    ultima_ruta = excel_manager.generar_recibo_excel(rid)
                    database.actualizar_recibo(rid, estado="Generado")
                    exitos += 1
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error al generar recibo: {e}")
            
            if exitos > 0:
                self.actualizar_lista_recibos()
                mensaje = f"Se generaron {exitos} recibos exitosamente.\n\n¿Deseas abrir el último documento generado?"
                if len(r_ids) == 1:
                    mensaje = f"Recibo finalizado en:\n{ultima_ruta}\n\n¿Deseas abrirlo ahora?"
                res = QMessageBox.question(self, "Éxito", mensaje, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if res == QMessageBox.StandardButton.Yes and ultima_ruta: excel_manager.abrir_archivo(ultima_ruta)
        else:
            QMessageBox.warning(self, "Aviso", "Tilda departamentos a la derecha para crear borradores, o selecciona recibos a la izquierda para exportarlos.")


def aplicar_tema(app):
    tema = database.obtener_config("tema_visual")
    if tema == "Oscuro (Nocturno)":
        app.setStyleSheet("""
            QMainWindow, QDialog, QWidget { background-color: #2D2D30; color: #E0E0E0; }
            QLineEdit, QTextEdit, QComboBox { background-color: #3E3E42; color: #FFFFFF; border: 1px solid #555; padding: 4px; }
            QPushButton { background-color: #3E3E42; color: #FFFFFF; border: 1px solid #555; padding: 6px; border-radius: 4px; }
            QPushButton:hover { background-color: #4E4E52; }
            QTableWidget, QTreeWidget, QListWidget { background-color: #1E1E1E; color: #D4D4D4; alternate-background-color: #252526; }
            QHeaderView::section { background-color: #333333; color: white; padding: 4px; border: 1px solid #444; }
            QLabel { color: #E0E0E0; }
            QGroupBox { border: 1px solid #555; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }
            QTabWidget::pane { border: 1px solid #555; }
            QTabBar::tab { background: #2D2D30; color: #ccc; padding: 8px; border: 1px solid #555; }
            QTabBar::tab:selected { background: #3E3E42; color: white; }
        """)
    else:
        app.setStyleSheet("")

# Entry point moved to run.py
