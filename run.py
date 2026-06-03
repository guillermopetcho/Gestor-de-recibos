import sys
from PyQt6.QtWidgets import QApplication

from app.core import database
from app.main_app import MiAdminApp, aplicar_tema

def main():
    # Inicializar la base de datos local
    database.init_database()
    
    # Iniciar aplicación de Qt
    app = QApplication(sys.argv)
    
    # Aplicar el tema configurado (Oscuro o Claro)
    aplicar_tema(app)
    
    # Instanciar y mostrar la ventana principal
    window = MiAdminApp()
    window.show()
    
    # Ejecutar el bucle principal de la aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
