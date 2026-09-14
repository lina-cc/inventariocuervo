from django.contrib import admin
from .models import Proveedor, Insumo, MovimientoStock

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre_empresa', 'contacto', 'telefono', 'email')
    search_fields = ('nombre_empresa', 'contacto')

@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'stock_actual', 'unidad_medida', 'stock_minimo', 'activo', 'esta_en_stock_critico')
    list_filter = ('categoria', 'activo')
    search_fields = ('nombre',)
    
    # Adding a display method for boolean property
    def esta_en_stock_critico(self, obj):
        return obj.esta_en_stock_critico
    esta_en_stock_critico.boolean = True
    esta_en_stock_critico.short_description = '¿Crítico?'

@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ('insumo', 'tipo_movimiento', 'cantidad', 'fecha_hora', 'motivo')
    list_filter = ('tipo_movimiento', 'fecha_hora')
    search_fields = ('insumo__nombre', 'motivo')
