from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, TemplateView, View, DetailView, UpdateView
from .models import Insumo, MovimientoStock, InventarioDiario, DetalleInventarioDiario
from .forms import InsumoForm, MovimientoStockForm
from django.db.models import Count, Q, Sum, F
from django.utils import timezone
from django.http import HttpResponse
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from datetime import datetime

class DashboardView(TemplateView):
    template_name = 'inventario/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calcular alertas
        insumos = Insumo.objects.all()
        insumos_criticos = [i for i in insumos if i.esta_en_stock_critico]
        
        # Calcular valor total
        valor_total = sum([i.valor_total for i in insumos])
        
        context['total_insumos'] = insumos.count()
        context['valor_total'] = valor_total
        context['alertas_criticas'] = len(insumos_criticos)
        context['insumos_criticos'] = insumos_criticos[:5] # Últimos 5 críticos
        context['ultimos_movimientos'] = MovimientoStock.objects.all().order_by('-fecha_hora')[:10]
        
        return context

class InsumoListView(LoginRequiredMixin, ListView):
    model = Insumo
    template_name = 'inventario/insumo_list.html'
    context_object_name = 'insumos'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(nombre__icontains=query)
        # Ordenamos para que los inactivos queden al final
        return queryset.order_by('-activo', 'nombre')

class InsumoCreateView(LoginRequiredMixin, CreateView):
    model = Insumo
    form_class = InsumoForm
    template_name = 'inventario/insumo_form.html'
    success_url = reverse_lazy('inventario:insumo_list')

class InsumoUpdateView(LoginRequiredMixin, UpdateView):
    model = Insumo
    form_class = InsumoForm
    template_name = 'inventario/insumo_form.html'
    success_url = reverse_lazy('inventario:insumo_list')

class MovimientoCreateView(LoginRequiredMixin, CreateView):
    model = MovimientoStock
    form_class = MovimientoStockForm
    template_name = 'inventario/movimiento_form.html'
    success_url = reverse_lazy('inventario:insumo_list')

class TomaInventarioView(LoginRequiredMixin, View):
    template_name = 'inventario/toma_inventario.html'

    def get(self, request, *args, **kwargs):
        insumos = Insumo.objects.all().order_by('categoria', 'nombre')
        return render(request, self.template_name, {'insumos': insumos})

    def post(self, request, *args, **kwargs):
        # 1. Registrar salidas de stock si hubo cambios
        for key, value in request.POST.items():
            if key.startswith('salida_') and value.strip():
                try:
                    insumo_id = int(key.split('_')[1])
                    cantidad = float(value.replace(',', '.'))
                    if cantidad > 0:
                        insumo = Insumo.objects.get(id=insumo_id)
                        MovimientoStock.objects.create(
                            insumo=insumo,
                            tipo_movimiento='Salida',
                            cantidad=cantidad,
                            motivo='Toma de Inventario en Bodega'
                        )
                except (ValueError, Insumo.DoesNotExist):
                    continue
        
        # 2. Generar el Cierre Diario (Snapshot)
        todos_insumos = Insumo.objects.all()
        valor_total_bodega = sum([i.valor_total for i in todos_insumos])
        
        cierre = InventarioDiario.objects.create(
            valor_total_bodega=valor_total_bodega,
            operario=request.user.username if request.user.is_authenticated else 'Operario Anónimo'
        )
        
        # 3. Guardar el detalle de cada insumo en el Snapshot
        detalles = []
        for insumo in todos_insumos:
            detalles.append(DetalleInventarioDiario(
                inventario_diario=cierre,
                insumo=insumo,
                nombre_insumo_snapshot=insumo.nombre,
                stock_registrado=insumo.stock_actual,
                unidad_medida_snapshot=insumo.unidad_medida,
                precio_unitario_snapshot=insumo.precio_unitario,
                valor_total_snapshot=insumo.valor_total
            ))
        DetalleInventarioDiario.objects.bulk_create(detalles)
        
        return redirect('inventario:dashboard')

class HistorialInventarioListView(LoginRequiredMixin, ListView):
    model = InventarioDiario
    template_name = 'inventario/historial_list.html'
    context_object_name = 'cierres'
    paginate_by = 10

class InventarioDiarioDetailView(LoginRequiredMixin, DetailView):
    model = InventarioDiario
    template_name = 'inventario/historial_detail.html'
    context_object_name = 'cierre'

class ListaSugerenciaComprasView(ListView):
    model = Insumo
    template_name = 'inventario/sugerencias_compra.html'
    context_object_name = 'insumos_comprar'

    def get_queryset(self):
        # Insumos cuyo stock actual es menor o igual al mínimo
        return Insumo.objects.filter(stock_actual__lte=F('stock_minimo')).select_related('proveedor').order_by('proveedor__nombre_empresa', 'nombre')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use the objects that will be passed to the template
        insumos = context['insumos_comprar']
        
        # Calcular el costo estimado de reposición
        # (Para reponer al menos la diferencia para llegar al mínimo + un 20% extra de holgura, o un cálculo simple)
        # Aquí haremos un cálculo sencillo: comprar lo necesario para llevar el stock al doble del mínimo
        costo_total_estimado = 0
        for insumo in insumos:
            cantidad_a_comprar = (insumo.stock_minimo * 2) - insumo.stock_actual
            if cantidad_a_comprar > 0:
                costo_total_estimado += cantidad_a_comprar * insumo.precio_unitario
                insumo.cantidad_sugerida = cantidad_a_comprar
                insumo.costo_estimado = cantidad_a_comprar * insumo.precio_unitario
            else:
                insumo.cantidad_sugerida = 0
                insumo.costo_estimado = 0
        
        context['costo_total_estimado'] = costo_total_estimado
        return context

class ExportarComprasExcelView(View):
    def get(self, request, *args, **kwargs):
        insumos = Insumo.objects.filter(stock_actual__lte=F('stock_minimo')).select_related('proveedor').order_by('proveedor__nombre_empresa', 'nombre')

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Sugerencias de Compra"

        # Estilos
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill("solid", fgColor="231A24") # Color Espresso Ciruela
        
        headers = ['Proveedor', 'Insumo', 'Categoría', 'Stock Actual', 'Stock Mínimo', 'Unidad', 'Cantidad Sugerida a Comprar', 'Costo Estimado']
        ws.append(headers)

        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")

        for insumo in insumos:
            proveedor_nombre = insumo.proveedor.nombre_empresa if insumo.proveedor else "Sin Proveedor"
            cantidad_sugerida = (insumo.stock_minimo * 2) - insumo.stock_actual
            cantidad_sugerida = cantidad_sugerida if cantidad_sugerida > 0 else 0
            costo_estimado = cantidad_sugerida * insumo.precio_unitario

            ws.append([
                proveedor_nombre,
                insumo.nombre,
                insumo.categoria,
                float(insumo.stock_actual),
                float(insumo.stock_minimo),
                insumo.unidad_medida,
                float(cantidad_sugerida),
                float(costo_estimado)
            ])

        # Autoajustar columnas
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column].width = adjusted_width

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=Sugerencias_Compras_{datetime.now().strftime("%Y%m%d")}.xlsx'
        
        wb.save(response)
        return response
