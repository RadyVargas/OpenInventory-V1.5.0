from django import forms
from .models import Producto, Pedido, DetallePedido

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'stock', 'categoria']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control'}),
        }

DetallePedidoFormSet = forms.inlineformset_factory(
    Pedido, DetallePedido,
    fields=('producto', 'cantidad'), extra=1, can_delete=True,
    widgets={
        'producto': forms.Select(attrs={'class': 'form-select bg-dark text-white'}),
        'cantidad': forms.NumberInput(attrs={'class': 'form-control bg-dark text-white'}),
    }
)