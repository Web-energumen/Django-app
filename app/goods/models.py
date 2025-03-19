from django.db import models
from django.urls import reverse_lazy


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name='Назва категорії')
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)

    class Meta:
        db_table = 'category'
        verbose_name = 'Категорію'
        verbose_name_plural = 'Категорії'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name='Назва товару')
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True, verbose_name='Опис товару')
    image = models.ImageField(upload_to='goods_images', blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, verbose_name='Ціна')
    discount = models.DecimalField(max_digits=4, decimal_places=2, default=0.00, verbose_name='Знижка в %')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Кількість')
    category = models.ForeignKey(to='Category', on_delete=models.CASCADE, verbose_name='Категорія')

    class Meta:
        db_table = 'product'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
        ordering = ['id']

    def __str__(self):
        return f'{self.name} Кількість - {self.quantity}'

    def get_absolute_url(self):
        return reverse_lazy('catalog:product', kwargs={'product_slug': self.slug})

    def display_id(self):
        return f'{self.id:05}'

    def sell_price(self):
        if self.discount:
            return round(self.price - self.price * self.discount/100, 2)

        return self.price
