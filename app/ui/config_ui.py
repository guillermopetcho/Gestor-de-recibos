from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QPushButton, QMessageBox, QTabWidget,
                             QWidget, QComboBox, QFileDialog, QLabel)
from app.core import database

class VentanaConfig(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración del Sistema")
        self.resize(500, 400)
        
        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        
        # --- Pestaña 1: Empresa ---
        tab_empresa = QWidget()
        form_empresa = QFormLayout(tab_empresa)
        self.edit_nombre = QLineEdit()
        self.edit_dir = QLineEdit()
        self.edit_tel = QLineEdit()
        self.edit_email = QLineEdit()
        form_empresa.addRow("Nombre / Razón Social:", self.edit_nombre)
        form_empresa.addRow("Dirección Comercial:", self.edit_dir)
        form_empresa.addRow("Teléfono:", self.edit_tel)
        form_empresa.addRow("Email de Contacto:", self.edit_email)
        
        # --- Pestaña 2: Apariencia e Interfaz ---
        tab_sistema = QWidget()
        form_sistema = QFormLayout(tab_sistema)
        self.combo_tema = QComboBox()
        self.combo_tema.addItems(["Claro (Por defecto)", "Oscuro (Nocturno)"])
        self.combo_moneda = QComboBox()
        self.combo_moneda.addItems(["$ (Pesos)", "U$D (Dólares)", "€ (Euros)"])
        form_sistema.addRow("Tema Visual:", self.combo_tema)
        form_sistema.addRow("Símbolo de Moneda:", self.combo_moneda)
        
        # --- Pestaña 3: Rutas y Almacenamiento ---
        tab_rutas = QWidget()
        form_rutas = QFormLayout(tab_rutas)
        
        # Ruta de guardado
        self.edit_ruta_guardado = QLineEdit()
        btn_buscar_guardado = QPushButton("Examinar...")
        btn_buscar_guardado.clicked.connect(self.seleccionar_ruta_guardado)
        layout_ruta_g = QHBoxLayout()
        layout_ruta_g.addWidget(self.edit_ruta_guardado)
        layout_ruta_g.addWidget(btn_buscar_guardado)
        
        # Opciones de salida
        self.combo_formato = QComboBox()
        self.combo_formato.addItems(["Solo Excel (.xlsx)", "Excel y PDF"])
        
        form_rutas.addRow("Carpeta de Recibos:", layout_ruta_g)
        form_rutas.addRow("Formato de Salida Principal:", self.combo_formato)
        
        # --- Pestaña 4: Envío y Comunicaciones ---
        tab_envio = QWidget()
        form_envio = QFormLayout(tab_envio)
        self.edit_msg_whatsapp = QLineEdit()
        self.edit_msg_whatsapp.setPlaceholderText("Ej: Hola, adjunto el recibo de tu alquiler correspondiente al mes...")
        
        nota_envio = QLabel("<i>Próximamente: Integración automática con correo electrónico y WhatsApp Web.</i>")
        nota_envio.setWordWrap(True)
        
        form_envio.addRow("Mensaje Base WhatsApp:", self.edit_msg_whatsapp)
        form_envio.addRow("", nota_envio)
        
        # Añadir todas las pestañas al TabWidget
        self.tabs.addTab(tab_empresa, " Empresa")
        self.tabs.addTab(tab_sistema, "Apariencia")
        self.tabs.addTab(tab_rutas, "Rutas - Archivos")
        self.tabs.addTab(tab_envio, "Comunicaciones")
        
        # Botón guardar general
        btn_guardar = QPushButton("Guardar Toda la Configuración")
        btn_guardar.setStyleSheet("background-color: #2C3E50; color: white; font-weight: bold; padding: 10px; font-size: 13px;")
        btn_guardar.clicked.connect(self.guardar_datos)
        
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(btn_guardar)

    def seleccionar_ruta_guardado(self):
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta para Guardar Recibos")
        if carpeta:
            self.edit_ruta_guardado.setText(carpeta)

    def cargar_datos(self):
        config = database.obtener_config()
        self.edit_nombre.setText(config.get("administrador_nombre", ""))
        self.edit_dir.setText(config.get("administrador_direccion", ""))
        self.edit_tel.setText(config.get("administrador_telefono", ""))
        self.edit_email.setText(config.get("administrador_email", ""))
        
        tema = config.get("tema_visual", "Claro (Por defecto)")
        if tema in [self.combo_tema.itemText(i) for i in range(self.combo_tema.count())]:
            self.combo_tema.setCurrentText(tema)
            
        self.edit_ruta_guardado.setText(config.get("ruta_guardado", "recibos"))
        self.edit_msg_whatsapp.setText(config.get("msg_whatsapp", ""))
        
        formato = config.get("formato_salida", "Solo Excel (.xlsx)")
        if formato in [self.combo_formato.itemText(i) for i in range(self.combo_formato.count())]:
            self.combo_formato.setCurrentText(formato)

    def guardar_datos(self):
        database.guardar_config("administrador_nombre", self.edit_nombre.text().strip())
        database.guardar_config("administrador_direccion", self.edit_dir.text().strip())
        database.guardar_config("administrador_telefono", self.edit_tel.text().strip())
        database.guardar_config("administrador_email", self.edit_email.text().strip())
        
        database.guardar_config("tema_visual", self.combo_tema.currentText())
        database.guardar_config("ruta_guardado", self.edit_ruta_guardado.text().strip())
        database.guardar_config("msg_whatsapp", self.edit_msg_whatsapp.text().strip())
        database.guardar_config("formato_salida", self.combo_formato.currentText())
        
        QMessageBox.information(self, "Configuración Guardada", 
                                "La configuración del sistema ha sido actualizada correctamente.\n\n"
                                "Los cambios visuales se aplicarán de inmediato.")
        self.accept()
