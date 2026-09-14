# 🦇 El Palacio del Cuervo - Sistema de Inventario

Este es un sistema de inventario web desarrollado en **Django** para la gestión de insumos de una cafetería temática. El sistema cuenta con una interfaz de usuario completamente personalizada bajo la estética **"Dark Gothic"** (Realeza Oscura), utilizando esquemas de color oscuros, efectos *glassmorphism* y detalles en color dorado.

## 🌟 Características Principales

*   **Identidad Visual Premium**: Interfaz oscura con paleta de colores personalizada (Negro Pluma, Espresso Ciruela, Rosa Antiguo, Dorado Palacio).
*   **Gestión de Inventario (CRUD Completo)**: Permite registrar, editar, listar y revisar insumos.
*   **Borrado Lógico (Soft Delete)**: Los insumos pueden ser deshabilitados sin ser borrados físicamente de la base de datos para no perder el historial de movimientos.
*   **Alertas Críticas y Sugerencias de Compra**: El sistema detecta automáticamente los productos que han bajado de su stock mínimo.
*   **Exportación a Excel**: Capacidad de generar y descargar sobre la marcha un archivo `.xlsx` (estilizado con los colores de la marca) con las sugerencias de compra.
*   **Sistema de Autenticación Integrado**: 
    *   **Usuarios Públicos/Invitados**: Solo pueden ver el Dashboard general y las sugerencias de compra.
    *   **Administradores**: Tienen acceso total a las vistas de modificación (CRUD) y ajustes manuales.
    *   Vistas fuertemente protegidas mediante `LoginRequiredMixin`.

## 🛠️ Tecnologías Utilizadas

*   **Backend**: Python, Django 6.1
*   **Frontend**: HTML5, Vanilla CSS, Bootstrap 5 (Base), Crispy Forms
*   **Base de Datos**: SQLite3
*   **Librerías Extra**: `openpyxl` (Para la exportación de archivos Excel)

## 🚀 Instrucciones de Instalación y Uso

1.  **Activar el entorno virtual**:
    ```bash
    .\venv\Scripts\activate
    ```

2.  **Instalar dependencias** (Si es necesario):
    ```bash
    pip install django django-crispy-forms crispy-bootstrap5 openpyxl
    ```

3.  **Aplicar migraciones** (La base de datos actual ya debería estar al día):
    ```bash
    python manage.py migrate
    ```

4.  **Levantar el servidor local**:
    ```bash
    python manage.py runserver
    ```

5.  **Abrir en el navegador**:
    Navega a [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## 🔐 Credenciales de Acceso (Profesor)

Para acceder a las opciones de administración, agregar productos o modificar stock, debes iniciar sesión haciendo clic en **"Iniciar Sesión Admin"** al final del menú lateral o acceder a `/admin/`.

*   **Usuario**: `admin`
*   **Contraseña**: `Admin123!`

---
*Desarrollado para Evaluación de Django Backend INACAP.*
