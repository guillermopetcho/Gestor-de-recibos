# Mi-Admin: Gestor de Recibos Inmobiliarios 🏢📄

**Mi-Admin** es una aplicación de escritorio profesional desarrollada en Python y PyQt6 diseñada para administrar la cobranza, facturación y control de recibos de edificios y departamentos.

## 🌟 Características Principales
- **Cobranza Jerárquica:** Combinación automática de gastos fijos del edificio con gastos particulares del departamento.
- **Plantillas Dinámicas:** Inyección directa de datos sobre cualquier archivo de Excel (.xlsx) usando mapeos de celdas o etiquetas dinámicas.
- **Automatización:** Autoincremento inteligente del número de recibos, cálculo de subtotales y generación de documentos.
- **Portabilidad:** Base de datos embebida (SQLite3) con despliegue a través de un único archivo ejecutable (`.exe`) para Windows.

## 🔄 Flujo de Trabajo del Sistema

A continuación se detalla el ciclo de vida de la información y la interacción del usuario con el sistema:

```mermaid
graph TD
    A([Inicio: Ejecución de GestorRecibos.exe]) --> B[(Base de Datos SQLite)]
    B -->|Carga de Entidades| C[Dashboard Principal]
    
    subgraph Módulo de Administración (Setup)
        C --> D[Gestión de Propiedades]
        D --> E[Definir Edificios y Conceptos Globales]
        D --> F[Definir Departamentos e Inquilinos]
        D --> G[Crear/Cargar Mapeos de Excel]
        E -.-> B
        F -.-> B
        G -.-> B
    end
    
    subgraph Módulo de Operación (Mensual)
        C --> H[Crear Nuevos Recibos]
        H --> I[Fusión de Gastos: Edificios + Deptos]
        I --> J[Cálculo de Totales y Nro. Recibo Auto-incremental]
        J --> K[Gestión: Edición Masiva / Edición Individual]
        K -.-> B
    end
    
    subgraph Módulo de Exportación (Cierre)
        K --> L{Emitir Recibos}
        L --> M[Lectura de Plantilla Excel Origen]
        M --> N[Inyección de Datos según Mapeo / Etiquetas]
        N --> O[Guardar archivo .XLSX]
        N --> P[Conversión a .PDF]
    end
```

## 📂 Estructura del Código Fuente

```text
Mi-Admin/
├── run.py                 <-- Lanzador del entorno de producción.
├── app/                   <-- Código fuente principal de la aplicación.
│   ├── __init__.py
│   ├── main_app.py        <-- Dashboard y ventanas principales.
│   ├── core/              <-- Motor de procesamiento de datos.
│   │   ├── __init__.py
│   │   ├── database.py    <-- Interfaz SQLite (CRUD y esquemas).
│   │   └── excel_manager.py <-- Lógica de inyección en plantillas.
│   └── ui/                <-- Formularios de la interfaz de usuario.
│       ├── __init__.py
│       ├── gestion_ui.py  <-- Ventanas de gestión (Árbol, Mapeo, Conceptos, etc).
│       └── config_ui.py   <-- Ventanas secundarias.
├── data/                  <-- Carpeta autogenerada: Almacena mi_admin.db.
└── recibos/               <-- Directorio de salida predeterminado para XLSX y PDF.
```

## 🛠️ Tecnologías
- **Core:** Python 3.10+
- **GUI:** PyQt6
- **Base de Datos:** SQLite3
- **Exportación:** openpyxl (Excel), LibreOffice (PDF)
- **Empaquetado:** PyInstaller
