from django.urls import path
from .views import (
    DashboardView, InsumoListView, InsumoCreateView, 
    MovimientoCreateView, TomaInventarioView, 
    HistorialInventarioListView, InventarioDiarioDetailView,
    ListaSugerenciaComprasView, ExportarComprasExcelView,
    InsumoUpdateView
)

app_name = 'inventario'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('insumos/', InsumoListView.as_view(), name='insumo_list'),
    path('insumos/nuevo/', InsumoCreateView.as_view(), name='insumo_create'),
    path('insumos/editar/<int:pk>/', InsumoUpdateView.as_view(), name='insumo_update'),
    path('movimientos/nuevo/', MovimientoCreateView.as_view(), name='movimiento_create'),
    path('toma-fisica/', TomaInventarioView.as_view(), name='toma_inventario'),
    path('historial/', HistorialInventarioListView.as_view(), name='historial_list'),
    path('historial/<int:pk>/', InventarioDiarioDetailView.as_view(), name='historial_detail'),
    path('sugerencias-compra/', ListaSugerenciaComprasView.as_view(), name='sugerencia_compras'),
    path('sugerencias-compra/exportar-excel/', ExportarComprasExcelView.as_view(), name='exportar_compras_excel'),
]
