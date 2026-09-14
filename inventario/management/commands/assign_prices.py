import random
from django.core.management.base import BaseCommand
from inventario.models import Insumo

class Command(BaseCommand):
    help = 'Asigna precios realistas a los insumos existentes'

    def handle(self, *args, **kwargs):
        self.stdout.write("Asignando precios...")
        precios = {
            "Café Grano Arábica": 15000,
            "Café Grano Robusta": 12000,
            "Leche Entera": 1200,
            "Leche Descremada": 1300,
            "Leche de Almendras": 2500,
            "Sirope de Vainilla": 8500,
            "Sirope de Caramelo": 8500,
            "Azúcar Blanca": 1500,
            "Azúcar Rubia": 2000,
            "Vasos Polipapel 8oz": 50,
            "Vasos Polipapel 12oz": 70,
            "Tapas para Vasos 8oz/12oz": 20,
            "Revolvedores de Madera": 10,
            "Servilletas": 5,
            "Detergente Multiuso": 3500,
            "Cloro Gel": 2000,
        }
        
        for nombre, precio in precios.items():
            try:
                insumo = Insumo.objects.get(nombre=nombre)
                insumo.precio_unitario = precio
                insumo.save()
            except Insumo.DoesNotExist:
                pass
        
        # Para cualquier otro que no esté en la lista
        for insumo in Insumo.objects.filter(precio_unitario=1000):
            insumo.precio_unitario = random.randint(1000, 10000)
            insumo.save()
            
        self.stdout.write(self.style.SUCCESS("¡Precios asignados correctamente!"))
