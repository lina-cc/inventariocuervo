import random
from django.core.management.base import BaseCommand
from inventario.models import Proveedor, Insumo, MovimientoStock

class Command(BaseCommand):
    help = 'Carga datos de prueba realistas para la cafetería (Proveedores e Insumos)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Limpiando base de datos...")
        MovimientoStock.objects.all().delete()
        Insumo.objects.all().delete()
        Proveedor.objects.all().delete()

        self.stdout.write("Creando Proveedores...")
        proveedores_data = [
            {"nombre": "Cafetaleros de Altura S.A.", "contacto": "Juan Pérez", "tel": "+56912345678"},
            {"nombre": "Distribuidora Lácteos del Sur", "contacto": "Ana Gómez", "tel": "+56987654321"},
            {"nombre": "EcoEnvases SpA", "contacto": "Carlos Ruiz", "tel": "+56911223344"},
            {"nombre": "Dulces y Siropes Ltda", "contacto": "María López", "tel": "+56999887766"},
        ]
        proveedores = []
        for p in proveedores_data:
            proveedor = Proveedor.objects.create(
                nombre_empresa=p["nombre"],
                contacto=p["contacto"],
                telefono=p["tel"],
                email=f"{p['contacto'].split()[0].lower()}@{p['nombre'].replace(' ', '').lower()}.cl",
                direccion="Calle Ficticia 123, Santiago"
            )
            proveedores.append(proveedor)

        self.stdout.write("Creando Insumos...")
        insumos_data = [
            # Materia Prima
            {"nombre": "Café Grano Arábica", "cat": "Materia Prima", "um": "kg", "stock": 15, "min": 5, "prov": proveedores[0]},
            {"nombre": "Café Grano Robusta", "cat": "Materia Prima", "um": "kg", "stock": 8, "min": 10, "prov": proveedores[0]}, # Stock Crítico
            {"nombre": "Leche Entera", "cat": "Materia Prima", "um": "litros", "stock": 50, "min": 20, "prov": proveedores[1]},
            {"nombre": "Leche Descremada", "cat": "Materia Prima", "um": "litros", "stock": 10, "min": 15, "prov": proveedores[1]}, # Stock Crítico
            {"nombre": "Leche de Almendras", "cat": "Materia Prima", "um": "litros", "stock": 5, "min": 5, "prov": proveedores[1]}, # Stock Crítico
            {"nombre": "Sirope de Vainilla", "cat": "Envasados", "um": "litros", "stock": 2, "min": 3, "prov": proveedores[3]}, # Stock Crítico
            {"nombre": "Sirope de Caramelo", "cat": "Envasados", "um": "litros", "stock": 6, "min": 3, "prov": proveedores[3]},
            {"nombre": "Azúcar Blanca", "cat": "Materia Prima", "um": "kg", "stock": 20, "min": 10, "prov": proveedores[3]},
            {"nombre": "Azúcar Rubia", "cat": "Materia Prima", "um": "kg", "stock": 8, "min": 10, "prov": proveedores[3]}, # Stock Crítico
            
            # Desechables
            {"nombre": "Vasos Polipapel 8oz", "cat": "Desechables", "um": "unidades", "stock": 500, "min": 200, "prov": proveedores[2]},
            {"nombre": "Vasos Polipapel 12oz", "cat": "Desechables", "um": "unidades", "stock": 150, "min": 300, "prov": proveedores[2]}, # Stock Crítico
            {"nombre": "Tapas para Vasos 8oz/12oz", "cat": "Desechables", "um": "unidades", "stock": 600, "min": 500, "prov": proveedores[2]},
            {"nombre": "Revolvedores de Madera", "cat": "Desechables", "um": "unidades", "stock": 1000, "min": 500, "prov": proveedores[2]},
            {"nombre": "Servilletas", "cat": "Desechables", "um": "unidades", "stock": 200, "min": 1000, "prov": proveedores[2]}, # Stock Crítico
            
            # Limpieza
            {"nombre": "Detergente Multiuso", "cat": "Limpieza", "um": "litros", "stock": 10, "min": 5, "prov": None},
            {"nombre": "Cloro Gel", "cat": "Limpieza", "um": "litros", "stock": 2, "min": 3, "prov": None}, # Stock Crítico
        ]

        for i_data in insumos_data:
            insumo = Insumo.objects.create(
                nombre=i_data["nombre"],
                categoria=i_data["cat"],
                unidad_medida=i_data["um"],
                stock_actual=i_data["stock"],
                stock_minimo=i_data["min"],
                proveedor=i_data["prov"]
            )
            # Registrar un movimiento de entrada inicial para que quede registro
            MovimientoStock.objects.create(
                insumo=insumo,
                tipo_movimiento='Entrada',
                cantidad=i_data["stock"],
                motivo='Inventario inicial / Apertura'
            )
            # Como la señal de guardado suma al stock, el stock_actual se duplicaría,
            # pero en nuestro seed lo vamos a corregir para que quede el correcto:
            insumo.stock_actual = i_data["stock"]
            insumo.save()

        self.stdout.write(self.style.SUCCESS("¡Base de datos poblada exitosamente con datos realistas para la cafetería!"))
