from django.http import JsonResponse
from django.views import View

from carts.mixins import CartMixin
from carts.models import Cart
from goods.models import Product


class CartAddView(CartMixin, View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id=product_id)

        cart = self.get_cart(request, product=product)

        if cart:
            cart.quantity += 1
            cart.save()
        else:
            Cart.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key if not request.user.is_authenticated else None,
                product=product,
                quantity=1
            )

        response_data = {
            'message': 'Товар додано до кошика',
            'cart_items_html': self.render_cart(request)
        }

        return JsonResponse(response_data)


class CartChangeView(CartMixin, View):
    def post(self, request):
        cart_id = request.POST.get("cart_id")

        cart = self.get_cart(request, cart_id=cart_id)

        cart.quantity = request.POST.get("quantity")
        cart.save()

        quantity = cart.quantity

        response_data = {
            "message": "Змінено кількість",
            "quantity": quantity,
            'cart_items_html': self.render_cart(request)
        }

        return JsonResponse(response_data)


class CartRemoveView(CartMixin, View):
    def post(self, request):
        cart_id = request.POST.get("cart_id")

        cart = self.get_cart(request, cart_id=cart_id)
        quantity = cart.quantity
        cart.delete()

        response_data = {
            "message": "Товар видалено",
            "quantity_deleted": quantity,
            'cart_items_html': self.render_cart(request)
        }

        return JsonResponse(response_data)
