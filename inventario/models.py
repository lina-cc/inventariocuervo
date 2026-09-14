from django.db import models
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

class Proveedor(models.Model):
    nombre_empresa = models.CharField(max_length=150, verbose_name="Nombre de la Empresa")
    contacto = models.CharField(max_length=150, verbose_name="Nombre del Contacto")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(verbose_name="Correo Electrónico")
    direccion = models.TextField(verbose_name="Dirección Física")

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre_empresa']

    def __str__(self):
        return f"{self.nombre_empresa} ({self.contacto})"

class Insumo(models.Model):
    CATEGORIAS = [
        ('Materia Prima', 'Materia Prima'),
        ('Desechables', 'Desechables'),
        ('Envasados', 'Envasados'),
        ('Limpieza', 'Limpieza'),
    ]
    
    UNIDADES = [
        ('kg', 'Kilogramos'),
        ('litros', 'Litros'),
        ('unidades', 'Unidades'),
        ('gr', 'Gramos'),
    ]

    nombre = models.CharField(max_length=200, verbose_name="Nombre del Insumo")
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, verbose_name="Categoría")
    unidad_medida = models.CharField(max_length=20, choices=UNIDADES, verbose_name="Unidad de Medida")
    stock_actual = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        validators=[MinValueValidator(0)],
        verbose_name="Stock Actual"
    )
    stock_minimo = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        validators=[MinValueValidator(0)],
        verbose_name="Stock Mínimo (Alerta)"
    )
    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=1000,
        validators=[MinValueValidator(0)],
        verbose_name="Precio Unitario ($)",
        help_text="Costo por unidad de medida"
    )
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='insumos')
    activo = models.BooleanField(default=True, verbose_name="Habilitado", help_text="Desmarcar para deshabilitar el insumo en lugar de borrarlo.")

    class Meta:
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - {self.stock_actual} {self.unidad_medida}"

    @property
    def esta_en_stock_critico(self):
        """Devuelve True si el stock actual es menor o igual al mínimo."""
        return self.stock_actual <= self.stock_minimo
    
    @property
    def get_stock_status_color(self):
        """Helper para la UI (Bootstrap color class)"""
        if self.stock_actual <= 0:
            return "danger" # Agotado
        if self.esta_en_stock_critico:
            return "warning" # Crítico
        return "success" # OK


    @property
    def valor_total(self):
        """Calcula el dinero inmovilizado de este insumo."""
        return self.stock_actual * self.precio_unitario


class MovimientoStock(models.Model):
    TIPOS = [
        ('Entrada', 'Entrada / Compra'),
        ('Salida', 'Salida / Uso / Merma'),
    ]

    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name='movimientos')
    tipo_movimiento = models.CharField(max_length=20, choices=TIPOS, verbose_name="Tipo de Movimiento")
    cantidad = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Cantidad"
    )
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")
    motivo = models.CharField(max_length=255, verbose_name="Motivo / Descripción", help_text="Ej: Compra semanal, Uso diario, Merma por caducidad")

    class Meta:
        verbose_name = "Movimiento de Stock"
        verbose_name_plural = "Movimientos de Stock"
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"{self.tipo_movimiento} de {self.cantidad} - {self.insumo.nombre} ({self.fecha_hora.strftime('%d/%m/%Y %H:%M')})"

# Uso de signals para mantener la separación de responsabilidades 
# (separando la lógica del guardado del modelo principal)
@receiver(post_save, sender=MovimientoStock)
def actualizar_stock_insumo(sender, instance, created, **kwargs):
    if created: # Solo actualizar el stock al crear el movimiento, no al editar (para simplificar la lógica en este alcance)
        insumo = instance.insumo
        if instance.tipo_movimiento == 'Entrada':
            insumo.stock_actual += instance.cantidad
        elif instance.tipo_movimiento == 'Salida':
            # Nota: a nivel de validación de formulario se debería evitar que salga más de lo que hay,
            # pero aquí garantizamos que reste.
            insumo.stock_actual -= instance.cantidad
        insumo.save()

class InventarioDiario(models.Model):
    fecha = models.DateField(auto_now_add=True, verbose_name="Fecha del Cierre")
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora Exacta")
    valor_total_bodega = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Valor Total ($)")
    operario = models.CharField(max_length=100, blank=True, null=True, verbose_name="Operario Responsable")

    class Meta:
        verbose_name = "Cierre de Inventario"
        verbose_name_plural = "Cierres de Inventarios"
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"Inventario del {self.fecha.strftime('%d/%m/%Y')} - ${self.valor_total_bodega:,.0f}"

class DetalleInventarioDiario(models.Model):
    inventario_diario = models.ForeignKey(InventarioDiario, on_delete=models.CASCADE, related_name='detalles')
    insumo = models.ForeignKey(Insumo, on_delete=models.SET_NULL, null=True, related_name='cierres_historicos')
    nombre_insumo_snapshot = models.CharField(max_length=200, verbose_name="Nombre al momento del cierre")
    stock_registrado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Stock Registrado")
    unidad_medida_snapshot = models.CharField(max_length=20, verbose_name="Unidad de Medida")
    precio_unitario_snapshot = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio Unitario ($)")
    valor_total_snapshot = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor Total ($)")

    class Meta:
        verbose_name = "Detalle de Cierre"
        verbose_name_plural = "Detalles de Cierres"

    def __str__(self):
        return f"{self.nombre_insumo_snapshot}: {self.stock_registrado} @ ${self.precio_unitario_snapshot}"
