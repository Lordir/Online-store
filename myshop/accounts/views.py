from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.contrib.auth import authenticate, logout, login, get_user_model
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.core.mail import EmailMessage
from time import time

from cart.cart import Cart
from cart.forms import CartAddProductForm
from .forms import *
from .models import *
from .tokens import account_activation_token
from .utils import *


class Home(DataMixin, ListView):
    model = Product
    template_name = 'accounts/index.html'
    context_object_name = 'product'
    ordering = ['-views']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_mixin = self.get_user_context(title="Главная страница")
        context['position'] = 'home'
        return context | context_mixin

    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)


class HomeSortPriceDown(DataMixin, ListView):
    model = Product
    template_name = 'accounts/index.html'
    context_object_name = 'product'
    ordering = ['-price']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_mixin = self.get_user_context(title="Главная страница")
        context['position'] = 'home'
        return context | context_mixin

    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)


class HomeSortPriceUp(DataMixin, ListView):
    model = Product
    template_name = 'accounts/index.html'
    context_object_name = 'product'
    ordering = ['price']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_mixin = self.get_user_context(title="Главная страница")
        context['position'] = 'home'
        return context | context_mixin

    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)


class Info(DataMixin, TemplateView):
    template_name = 'accounts/info.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_mixin = self.get_user_context(title="Информация об магазине",
                                              selected_category=None)
        return context | context_mixin


class AddProduct(UserPassesTestMixin, LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddProductForm
    template_name = 'accounts/add_product.html'
    success_url = reverse_lazy('home')
    login_url = reverse_lazy('home')

    # raise_exception = True
    def test_func(self):
        if self.request.user.is_seller:
            return redirect('home')

    def form_valid(self, form):
        name = form.save()
        name.creator = self.request.user
        name.save()
        return super(AddProduct, self).form_valid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_mixin = self.get_user_context(title="Добавление товара",
                                              selected_category=None)
        return context | context_mixin


class Registry(DataMixin, CreateView):
    form_class = RegistryUserForm
    template_name = 'accounts/registry.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_mixin = self.get_user_context(title="Регистрация покупателя",
                                              selected_category=None)
        return context | context_mixin

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        user.save()
        print(user.password)
        current_site = get_current_site(self.request)
        mail_subject = 'Ссылка для подтверждения регистрации'
        message = render_to_string('accounts/activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        to_email = form.cleaned_data.get('email')
        email = EmailMessage(
            mail_subject, message, to=[to_email]
        )
        email.send()
        login(self.request, user)
        return redirect('registry_done')


class RegistrySeller(DataMixin, CreateView):
    form_class = RegistrySellerForm
    template_name = 'accounts/registry_seller.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_mixin = self.get_user_context(title="Регистрация продавца",
                                              selected_category=None)
        print(context | context_mixin)
        return context | context_mixin

    def form_valid(self, form):
        user = form.save()
        user.is_seller = True
        user.is_active = False
        user.save()
        current_site = get_current_site(self.request)
        mail_subject = 'Ссылка для подтверждения регистрации'
        message = render_to_string('accounts/activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        to_email = form.cleaned_data.get('email')
        email = EmailMessage(
            mail_subject, message, to=[to_email]
        )
        email.send()
        user = form.save()
        login(self.request, user)
        return redirect('registry_done')


def registry_done(request):
    return render(request, 'accounts/registry_done.html')


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'accounts/activate.html')
    else:
        return HttpResponse('Ссылка активации недействительна!')


class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'accounts/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_mixin = self.get_user_context(title="Авторизация",
                                              selected_category=None)
        return context | context_mixin

    def get_success_url(self):
        return reverse_lazy('home')


def logout_user(request):
    logout(request)
    return redirect('login')


class ShowProduct(DataMixin, DetailView):
    model = Product
    template_name = 'accounts/product.html'
    slug_url_kwarg = 'product_slug'
    context_object_name = 'product'

    # def get_object(self, *args, **kwargs):
    #     return Product.objects.filter(slug=Product.slug).update(views=F('views') + 1)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_mixin = self.get_user_context(title=context['product'],
                                              selected_category=None)
        context['other_profile'] = User.objects.filter(product__slug=self.kwargs['product_slug'])
        cart_product_form = CartAddProductForm()
        context['cart_product_form'] = cart_product_form
        Product.objects.filter(slug=self.kwargs['product_slug']).update(views=F('views') + 1)
        return context | context_mixin


class ShowCategory(DataMixin, ListView):
    model = Product
    template_name = 'accounts/index.html'
    context_object_name = 'product'
    allow_empty = False
    ordering = ['-views']

    def get_queryset(self):
        return super().get_queryset().filter(category__slug=self.kwargs['category_slug'], is_published=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        category1 = Category.objects.get(slug=self.kwargs['category_slug'])
        context_mixin = self.get_user_context(title='Категория - ' + str(category1.name),
                                              selected_category=category1.pk)
        context['position'] = 'category'
        return context | context_mixin


class ShowCategorySortPriceDown(DataMixin, ListView):
    model = Product
    template_name = 'accounts/index.html'
    context_object_name = 'product'
    allow_empty = False
    ordering = ['-price']

    def get_queryset(self):
        return super().get_queryset().filter(category__slug=self.kwargs['category_slug'], is_published=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_mixin = self.get_user_context(title='Категория - ' + str(context['product'][0].category),
                                              selected_category=context['product'][0].category_id)
        context['position'] = 'category'
        return context | context_mixin


class ShowCategorySortPriceUp(DataMixin, ListView):
    model = Product
    template_name = 'accounts/index.html'
    context_object_name = 'product'
    allow_empty = False
    ordering = ['price']

    def get_queryset(self):
        return super().get_queryset().filter(category__slug=self.kwargs['category_slug'], is_published=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_mixin = self.get_user_context(title='Категория - ' + str(context['product'][0].category),
                                              selected_category=context['product'][0].category_id)
        context['position'] = 'category'
        return context | context_mixin


class UserProfile(LoginRequiredMixin, DataMixin, ListView):
    # form_class = UserEditForm
    model = Product
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('home')
    login_url = reverse_lazy('login')
    context_object_name = 'product'
    paginate_by = 10

    def get_queryset(self):
        return Product.objects.filter(creator__id=self.kwargs['profile_id'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_mixin = self.get_user_context(title='Личный кабинет',
                                              selected_category=None)
        context['other_profile'] = User.objects.filter(id=self.kwargs['profile_id'])
        return context | context_mixin


class EditUser(LoginRequiredMixin, DataMixin, UpdateView):
    form_class = EditUserForm
    template_name = 'accounts/edit_user.html'
    success_url = reverse_lazy('home')

    # login_url = reverse_lazy('login')

    def get_object(self):
        return get_object_or_404(User, username=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_mixin = self.get_user_context(title="Редактировать данные",
                                              selected_category=None)
        return context | context_mixin


class EditProduct(DataMixin, UpdateView):
    model = Product
    template_name = 'accounts/edit_product.html'
    form_class = AddProductForm

    def get_object(self):
        return get_object_or_404(Product, slug=self.kwargs['product_slug'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_mixin = self.get_user_context(title="Редактировать данные о товаре",
                                              selected_category=None)
        return context | context_mixin


class DeleteProduct(DataMixin, DeleteView):
    model = Product
    template_name = 'accounts/delete_product.html'
    success_url = reverse_lazy('home')

    def get_object(self):
        return get_object_or_404(Product, slug=self.kwargs['product_slug'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_mixin = self.get_user_context(title="Удалить товар",
                                              selected_category=None)
        return context | context_mixin


class ChangePassword(DataMixin, PasswordChangeView):
    form_class = ChangePasswordForm
    success_url = reverse_lazy('home')
    template_name = 'accounts/change_password.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_mixin = self.get_user_context(title="Смена пароля",
                                              selected_category=None)
        return context | context_mixin


class CreateOrder(LoginRequiredMixin, DataMixin, TemplateView):
    template_name = 'accounts/create_order.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_mixin = self.get_user_context(title="Оформление заказа",
                                              selected_category=None)
        cart = Cart(self.request)
        order_number = int(time())
        total_price = 0
        for item in cart:
            name_seller = User.objects.filter(product__title=item['product'])
            total_price += item['price']
            Order.objects.create(name_seller=name_seller[0], product=item['product'], price=item['price'],
                                 number=item['quantity'], order_number=order_number)
            print(name_seller[0])
            print(item)
        cart.clear()
        context['price'] = total_price
        context['order_number'] = order_number
        return context | context_mixin


def CheckOrder(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        label = request.POST.get('label')
        order = Order.objects.filter(order_number=label)
        product = Product.objects.filter(order__order_number=label)
        tmp = -1
        for item in order:
            tmp += 1
            item.paid = True
            item.save()
            user = User.objects.get(username=item.name_seller)
            if amount >= 0:
                user.balance += product[tmp].price
                amount -= product[tmp].price
                product[tmp].number -= 1
                user.save()
    return redirect('home')


def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")
