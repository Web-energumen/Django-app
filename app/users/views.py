from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Prefetch
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView

from carts.models import Cart
from common.mixins import CacheMixin
from orders.models import Order, OrderItem
from users.forms import ProfileForm, UserLoginForm, UserRegistrationForm


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = UserLoginForm

    # success_url = reverse_lazy('main:index')

    def get_success_url(self):
        redirect_page = self.request.POST.get('next', None)
        if redirect_page and redirect_page != reverse('user:logout'):
            return redirect_page
        return reverse_lazy('main:index')

    def form_valid(self, form):
        session_key = self.request.session.session_key
        user = form.get_user()
        if user:
            auth.login(self.request, user)
            if session_key:
                forgot_carts = Cart.objects.filter(user=user)
                if forgot_carts.exists():
                    forgot_carts.delete()
                Cart.objects.filter(session_key=session_key).update(user=user)

                messages.success(self.request, f'{user.username}, Ви успішно увійшли в аккаунт!')
                return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(UserLoginView, self).get_context_data(**kwargs)
        context['title'] = 'Home - Авторизація'
        return context


class UserRegistrationView(CreateView):
    template_name = 'users/registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('user:profile')

    def form_valid(self, form):
        session_key = self.request.session.session_key
        self.object = form.save(commit=True)

        auth.login(self.request, self.object)

        if session_key:
            Cart.objects.filter(session_key=session_key).update(user=self.object)

        messages.success(self.request, f'{self.object.username}, Ваш обліковий запис успішно створено!')
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(UserRegistrationView, self).get_context_data(**kwargs)
        context['title'] = 'Home - Реєстрація'
        return context


class UserProfileView(LoginRequiredMixin, CacheMixin, UpdateView):
    template_name = 'users/profile.html'
    form_class = ProfileForm
    success_url = reverse_lazy('user:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Ваш профіль успішно оновлено!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Профіль користувача'

        orders = (
            Order.objects.filter(user=self.request.user).prefetch_related(
                Prefetch(
                    'orderitem_set',
                    queryset=OrderItem.objects.select_related('product')
                )
            )
            .order_by('-id')
        )

        context['orders'] = CacheMixin.set_get_cache(orders, f'user_{self.request.user.id}_orders', 60 * 2)
        return context


class UserCartView(TemplateView):
    template_name = 'users/users_cart.html'

    def get_context_data(self, **kwargs):
        context = super(UserCartView, self).get_context_data(**kwargs)
        context['title'] = 'Home - Кошик',
        return context


@login_required
def logout(request):
    messages.success(request, f'{request.user.username} Ви вийшли з аккаунта!')
    auth.logout(request)
    return redirect(reverse_lazy('user:login'))

# def login(request):
#     if request.method == 'POST':
#         form = UserLoginForm(data=request.POST)
#         if form.is_valid():
#             username = request.POST['username']
#             password = request.POST['password']
#             user = auth.authenticate(username=username, password=password)
#
#             session_key = request.session.session_key
#
#             if user and user.is_active:
#                 auth.login(request, user)
#                 messages.success(request, 'Ви успішно увійшли в аккаунт!')
#
#                 if session_key:
#                     Cart.objects.filter(session_key=session_key).update(user=user)
#
#                 redirect_page = request.POST.get('next', None)
#                 if redirect_page and redirect_page != reverse_lazy('user:logout'):
#                     return redirect(request.POST.get('next'))
#
#                 return redirect(reverse_lazy('main:index'))
#     else:
#         form = UserLoginForm()
#
#     context = {
#         'title': 'Login',
#         'form': form,
#     }
#     return render(request, 'users/login.html', context=context)


# def registration(request):
#     if request.method == 'POST':
#         form = UserRegistrationForm(data=request.POST)
#         if form.is_valid():
#             form.save()
#
#             session_key = request.session.session_key
#
#             user = form.instance
#             auth.login(request, user)
#
#             if session_key:
#                 Cart.objects.filter(session_key=session_key).update(user=user)
#
#             messages.success(request, 'Обліковий запис успішно створено!')
#             return redirect(reverse_lazy('main:index'))
#     else:
#         form = UserRegistrationForm()
#
#     context = {
#         'title': 'Registration',
#         'form': form,
#     }
#     return render(request, 'users/registration.html', context=context)


# @login_required
# def profile(request):
#     if request.method == 'POST':
#         form = ProfileForm(data=request.POST, instance=request.user, files=request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Ваш профіль успішно оновлено!')
#             return redirect(reverse_lazy('user:profile'))
#     else:
#         form = ProfileForm(instance=request.user)
#
#     orders = (
#         Order.objects.filter(user=request.user).prefetch_related(
#             Prefetch(
#                 'orderitem_set',
#                 queryset=OrderItem.objects.select_related('product')
#             )
#         )
#         .order_by('-id')
#     )
#
#     context = {
#         'title': 'Profile',
#         'form': form,
#         'orders': orders,
#     }
#     return render(request, 'users/profile.html', context=context)
