from django.test import TestCase

from .models import *


class LoginViewTest(TestCase):

    def setUp(self):
        user = User.objects.create_user(username='test', password='123testpass', email='09mn@mail.ru')
        user.save()

    def test_login_with_correct_data(self):
        login = self.client.login(username='test', password='123testpass')
        self.assertTrue(login)

    def test_login_with_wrong_username(self):
        login = self.client.login(username='wrong', password='123testpass')
        self.assertFalse(login)

    def test_login_with_wrong_password(self):
        login = self.client.login(username='test', password='wrong')
        self.assertFalse(login)


class AddProductViewTest(TestCase):

    def setUp(self):
        user = User.objects.create_user(username='test', password='123testpass', email='09mn@mail.ru')
        user.save()
        category = Category.objects.create(name='category1')
        category.save()

    def test_access_add_product(self):
        user = User.objects.get(id=1)
        user.is_seller = True
        user.save()
        self.client.login(username='test', password='123testpass')
        resp = self.client.get(reverse('add_product'))
        self.assertEqual(resp.status_code, 200)

    def test_without_access_add_product(self):
        self.client.login(username='test', password='123testpass')
        resp = self.client.get(reverse('add_product'))
        self.assertEqual(resp.status_code, 403)


class ProductModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='test', password='123testpass', email='09mn@mail.ru')
        category = Category.objects.create(name='category1')
        Product.objects.create(title='rtx', content='test', price='123', number='1', is_published=True,
                               category=category,
                               creator=user)

    def test_category_label(self):
        product = Product.objects.get(id=1)
        category = product.category
        self.assertEquals(str(category), 'category1')

    def test_creator_label(self):
        product = Product.objects.get(id=1)
        creator = product.creator
        self.assertEquals(str(creator), 'test')

    def test_views_label(self):
        product = Product.objects.get(id=1)
        views = product.views
        self.assertEquals(str(views), '0')

    def test_slug_label(self):
        product = Product.objects.get(id=1)
        slug = product.slug
        self.assertFalse(slug == 'Null')

    def test_title_max_length_label(self):
        product = Product.objects.get(id=1)
        max_length = product._meta.get_field('title').max_length
        self.assertEquals(max_length, 255)

    def test_get_absolute_url(self):
        product = Product.objects.get(id=1)
        slug = product.slug
        url = '/product/' + str(slug) + '/'
        self.assertEquals(product.get_absolute_url(), url)


class CategoryModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='test1', password='123testpass1', email='09mn@mail1.ru')
        category = Category.objects.create(name='category2', slug='category123')
        Product.objects.create(title='rtx1', content='test1', price='1231', number='11', is_published=True,
                               category=category,
                               creator=user)

    def test_name_label(self):
        category = Category.objects.get(id=1)
        category = category._meta.get_field('name').verbose_name
        self.assertEquals(str(category), 'Категория')

    def test_slug_label(self):
        category = Category.objects.get(id=1)
        slug = category.slug
        self.assertFalse(slug == 'Null')

    def test_get_absolute_url(self):
        category = Category.objects.get(id=1)
        self.assertEquals(category.get_absolute_url(), '/category/category123/')


class UserModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='test1', password='123testpass1', email='09mn@mail1.ru')

    def test_is_seller_label(self):
        user = User.objects.get(id=1)
        is_seller = user.is_seller
        self.assertEquals(str(is_seller), 'False')

    def test_balance_label(self):
        user = User.objects.get(id=1)
        balance = int(user.balance)
        self.assertEquals(str(balance), '0')

    def test_is_superuser_label(self):
        user = User.objects.get(id=1)
        is_superuser = user.is_superuser
        self.assertEquals(str(is_superuser), 'False')

    def test_get_absolute_url(self):
        user = User.objects.get(id=1)
        self.assertEquals(user.get_absolute_url(), '/profile/1/')


class CheckOrderViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='test1', password='123testpass1', email='09mn@mail1.ru')
        user2 = User.objects.create_user(username='test2', password='123testpass1', email='09mmn@mail1.ru')
        category = Category.objects.create(name='category2', slug='category123')
        product = Product.objects.create(title='rtx1', content='test1', price='1231', number='11', is_published=True,
                                         category=category,
                                         creator=user)
        Order.objects.create(name_seller=user, product=product, price='1231', number='1', order_number='44444')
        Order.objects.create(name_seller=user, product=product, price='55', number='1', order_number='322')
        Order.objects.create(name_seller=user2, product=product, price='66', number='1', order_number='322')
        Order.objects.create(name_seller=user2, product=product, price='33', number='3', order_number='123')

    def test_balance(self):
        amount = 1231
        label = 44444
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
                user.save()
        int_balance = int(user.balance)
        self.assertEquals(str(int_balance), '1231')

    def test_balance_when_2_product(self):
        amount = 1231
        label = 121
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
                user.save()
                int_balance = int(user.balance)
                self.assertEquals(str(int_balance), '55')
                self.assertEquals(str(int_balance), '66')
