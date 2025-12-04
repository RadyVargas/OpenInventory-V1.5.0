"""
este archivo arregla errores del codigo,NO TOCAR!.

"""


#!/usr/bin/env python
# -*- coding: utf-8 -*-

content = r'''{% extends 'base.html' %}
{% block content %}
<h2>Pedidos pendientes</h2>

{% if pedidos %}
<ul>
    {% for pedido in pedidos %}
    <li>
        Pedido #{{ pedido.id }} - {{ pedido.nombre_cliente|default:pedido.usuario.get_full_name }} - {{ pedido.fecha_creacion|date:"d/m/Y H:i" }}
        <a href="{% url 'tomar_pedido' pedido.id %}">Tomar pedido</a>
    </li>
    {% endfor %}
</ul>
{% else %}
<p>No hay pedidos pendientes.</p>
{% endif %}
{% endblock %}'''

with open(r'productos\templates\productos\lista_pedidos.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("lista_pedidos.html written successfully!")
