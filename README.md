```text
Mi-Admin/
├── run.py                 <-- Nuevo lanzador limpio y directo.
├── app/                   <-- Todo el código del programa.
│   ├── __init__.py
│   ├── main_app.py        <-- La interfaz principal.
│   ├── core/              <-- El "cerebro" del software.
│   │   ├── __init__.py
│   │   ├── database.py    <-- Conexiones y consultas SQL.
│   │   └── excel_manager.py <-- Lógica de plantillas e inyección.
│   └── ui/                <-- Las ventanas secundarias.
│       ├── __init__.py
│       ├── gestion_ui.py  <-- Ventanas de edificios y mapeo.
│       └── config_ui.py   <-- Ventanas de configuraciones.
├── data/                  <-- Aquí vive tu mi_admin.db (Protegido).
├── config/                <-- Espacio para futuros archivos .ini o temas.
└── recibos/               <-- Carpeta de salida por defecto.
```
