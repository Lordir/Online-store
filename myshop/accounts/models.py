from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from transliterate import slugify, translit
from time import time


def get_slug(s):
    new_slug = translit(s, 'ru')
    new_slug = slugify(new_slug)
    return new_slug + '-' + str(int(time()))


class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    slug = models.SlugField(max_length=255, blank=True, unique=True, db_index=True, verbose_name="URL")
    content = models.TextField(max_length=1000, verbose_name="Описание")
    price = models.FloatField(max_length=10, verbose_name="Цена", validators=[MinValueValidator(1)])
    number = models.FloatField(max_length=10, verbose_name="Количество", validators=[MinValueValidator(0)])
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", verbose_name="Фотограция")
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")
    views = models.PositiveIntegerField(default=0, verbose_name="Просмотров")
    category = models.ForeignKey('Category', on_delete=models.PROTECT, verbose_name="Категория")
    creator = models.ForeignKey('User', on_delete=models.PROTECT, default=1, verbose_name="Создатель")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product', kwargs={'product_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = get_slug(self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Товары'
        verbose_name_plural = 'Товары'
        # ordering = ['-views']


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name="Категория")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'category_slug': self.slug})

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['id']


class User(AbstractUser):
    username = models.CharField(error_messages={'unique': 'A user with that username already exists.'},
                                help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                                max_length=150, unique=True, verbose_name='username')
    password = models.CharField(max_length=128, verbose_name='password')
    email = models.EmailField(max_length=254, verbose_name='email address')
    last_login = models.DateTimeField(blank=True, null=True, verbose_name='last login')
    first_name = models.CharField(blank=True, max_length=150, verbose_name='first name')
    last_name = models.CharField(blank=True, max_length=150, verbose_name='last name')
    is_superuser = models.BooleanField(default=False, verbose_name='superuser status')
    is_active = models.BooleanField(default=True, verbose_name='active')
    updated_on = models.DateTimeField(auto_now=True)
    is_seller = models.BooleanField(default=False)
    balance = models.FloatField(max_length=10, default=0, verbose_name="Баланс")

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('profile', kwargs={'profile_id': self.pk})


class Order(models.Model):
    name_seller = models.ForeignKey('User', on_delete=models.PROTECT, verbose_name="Продавец", default="0")
    product = models.ForeignKey('Product', on_delete=models.PROTECT, verbose_name="Товар")
    price = models.FloatField(max_length=10, verbose_name="Цена", validators=[MinValueValidator(1)])
    number = models.FloatField(max_length=10, verbose_name="Количество", validators=[MinValueValidator(0)])
    paid = models.BooleanField(default=False, verbose_name="Оплата")
    order_number = models.FloatField(verbose_name="Номер заказа")

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

