from django import forms
from .models import Insumo, MovimientoStock

class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = ['nombre', 'categoria', 'unidad_medida', 'stock_actual', 'stock_minimo', 'precio_unitario', 'proveedor', 'activo']
        widgets = {
            'stock_actual': forms.NumberInput(attrs={'step': '0.01'}),
            'stock_minimo': forms.NumberInput(attrs={'step': '0.01'}),
            'precio_unitario': forms.NumberInput(attrs={'step': '1'}),
        }

class MovimientoStockForm(forms.ModelForm):
    class Meta:
        model = MovimientoStock
        fields = ['insumo', 'tipo_movimiento', 'cantidad', 'motivo']
        widgets = {
            'cantidad': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
        }
