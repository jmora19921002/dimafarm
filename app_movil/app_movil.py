import flet as ft
import requests
import json
from datetime import datetime

# Configuración básica - deberías cambiar esto según tu API
API_BASE_URL = "http://tu-api-dimafarm.com/api"

def main(page: ft.Page):
    page.title = "Dimafarm"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # Variables de estado
    current_user = None
    current_pharmacy = None
    cart_items = []
    
    # Funciones de API (simuladas para el ejemplo)
    def login_user(email, password):
        # En una implementación real, harías una solicitud a tu API Flask
        if email == "cliente@ejemplo.com" and password == "password":
            return {"success": True, "user": {"id": 1, "name": "Juan Pérez", "email": email}}
        return {"success": False, "message": "Credenciales incorrectas"}
    
    def get_pharmacies():
        # Simulación de respuesta
        return [
            {"id": 1, "name": "Farmacia Central", "color": "#4CAF50", "logo": "🏥"},
            {"id": 2, "name": "Farmacia del Pueblo", "color": "#2196F3", "logo": "💊"},
        ]
    
    def get_products(pharmacy_id):
        # Simulación de respuesta
        return [
            {"id": 1, "name": "Paracetamol", "price": 5.99, "description": "Alivia el dolor y la fiebre", "image": "💊", "stock": 50},
            {"id": 2, "name": "Ibuprofeno", "price": 7.50, "description": "Antiinflamatorio y analgésico", "image": "💊", "stock": 30},
            {"id": 3, "name": "Vitamina C", "price": 12.99, "description": "Suplemento vitamínico", "image": "🍊", "stock": 20},
        ]
    
    # Funciones de navegación
    def go_login(e):
        page.clean()
        render_login()
    
    def go_pharmacy_selection(e):
        page.clean()
        render_pharmacy_selection()
    
    def go_product_list(e, pharmacy):
        nonlocal current_pharmacy
        current_pharmacy = pharmacy
        page.clean()
        render_product_list()
    
    def go_cart(e):
        page.clean()
        render_cart()
    
    def go_home(e):
        page.clean()
        if current_user:
            render_pharmacy_selection()
        else:
            render_login()
    
    # Vistas de la aplicación
    def render_login():
        email_field = ft.TextField(label="Email", width=300)
        password_field = ft.TextField(label="Contraseña", password=True, width=300)
        
        def do_login(e):
            result = login_user(email_field.value, password_field.value)
            if result["success"]:
                nonlocal current_user
                current_user = result["user"]
                go_pharmacy_selection(e)
            else:
                page.snack_bar = ft.SnackBar(ft.Text(result["message"]))
                page.snack_bar.open = True
                page.update()
        
        login_form = ft.Column([
            ft.Text("Bienvenido a Dimafarm", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
            email_field,
            password_field,
            ft.Container(height=20),
            ft.ElevatedButton("Iniciar Sesión", on_click=do_login, width=300),
            ft.TextButton("Continuar como invitado", on_click=go_pharmacy_selection)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        page.add(login_form)
    
    def render_pharmacy_selection():
        pharmacies = get_pharmacies()
        pharmacy_cards = []
        
        for pharmacy in pharmacies:
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            leading=ft.Text(pharmacy["logo"], size=24),
                            title=ft.Text(pharmacy["name"]),
                        ),
                        ft.Row([
                            ft.TextButton("Seleccionar", 
                                         on_click=lambda e, p=pharmacy: go_product_list(e, p))
                        ], alignment=ft.MainAxisAlignment.END),
                    ]),
                    width=400,
                    padding=10,
                )
            )
            pharmacy_cards.append(card)
        
        page.add(ft.Column([
            ft.Text("Selecciona una farmacia", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
        ] + pharmacy_cards))
    
    def render_product_list():
        products = get_products(current_pharmacy["id"])
        product_cards = []
        
        for product in products:
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            leading=ft.Text(product["image"], size=24),
                            title=ft.Text(product["name"]),
                            subtitle=ft.Text(f"${product['price']} - {product['description']}"),
                        ),
                        ft.Row([
                            ft.Text(f"Stock: {product['stock']}", size=12, color=ft.Colors.GREY),
                            ft.TextButton("Agregar al carrito", 
                                         on_click=lambda e, p=product: add_to_cart(e, p))
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ]),
                    width=400,
                    padding=10,
                )
            )
            product_cards.append(card)
        
        cart_badge = ft.Badge(
            content=ft.IconButton(icon=ft.Icons.SHOPPING_CART, on_click=go_cart),
            small_size=10,
        )
        
        if cart_items:
            cart_badge.value = len(cart_items)
        
        page.appbar = ft.AppBar(
            title=ft.Text(current_pharmacy["name"]),
            bgcolor=current_pharmacy["color"],
            actions=[cart_badge]
        )
        
        page.add(ft.Column([
            ft.Text("Productos disponibles", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(height=20),
        ] + product_cards))
    
    def add_to_cart(e, product):
        cart_items.append(product)
        page.snack_bar = ft.SnackBar(ft.Text(f"{product['name']} agregado al carrito!"))
        page.snack_bar.open = True
        page.update()
    
    def render_cart():
        if not cart_items:
            page.add(ft.Column([
                ft.Text("Tu carrito está vacío", size=20),
                ft.TextButton("Seguir comprando", on_click=lambda e: go_product_list(e, current_pharmacy))
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER))
            return
        
        cart_list = []
        total = 0
        
        for item in cart_items:
            total += item["price"]
            cart_list.append(
                ft.ListTile(
                    title=ft.Text(item["name"]),
                    subtitle=ft.Text(f"${item['price']}"),
                    trailing=ft.IconButton(icon=ft.Icons.DELETE, 
                                          on_click=lambda e, i=item: remove_from_cart(e, i))
                )
            )
        
        cart_list.extend([
            ft.Divider(),
            ft.ListTile(
                title=ft.Text("Total", weight=ft.FontWeight.BOLD),
                trailing=ft.Text(f"${total}", weight=ft.FontWeight.BOLD),
            ),
            ft.ElevatedButton("Proceder al pago", on_click=lambda e: checkout(e))
        ])
        
        page.appbar = ft.AppBar(
            title=ft.Text("Mi Carrito"),
            bgcolor=current_pharmacy["color"],
        )
        
        page.add(ft.Column(cart_list))
    
    def remove_from_cart(e, item):
        cart_items.remove(item)
        go_cart(e)
    
    def checkout(e):
        page.clean()
        page.add(ft.Column([
            ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=48),
            ft.Text("¡Compra realizada con éxito!", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("Tu pedido está siendo procesado."),
            ft.TextButton("Volver al inicio", on_click=go_home)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER))
    
    # Iniciar con la vista de login
    render_login()

# Ejecutar la aplicación
ft.app(target=main)