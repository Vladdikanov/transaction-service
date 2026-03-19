from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class Type(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Тип'
        verbose_name_plural = 'Типы операций'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Status(models.Model):

    name = models.CharField('Название', max_length=100, unique=True)
    
    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы операций'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField('Название', max_length=100)
    type = models.ForeignKey(
        Type, 
        on_delete=models.CASCADE, 
        related_name='categories',
        verbose_name='Тип операции'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['type__name', 'name']
        unique_together = ['name', 'type']
    
    def __str__(self):
        return f"{self.name} ({self.type.name})"

class Subcategory(models.Model):
    name = models.CharField('Название', max_length=100)
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='subcategories',
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'
        ordering = ['category__name', 'name']
        unique_together = ['name', 'category']
    def __str__(self):
        return f"{self.name} ({self.category.name})"


class Transaction(models.Model):
    date = models.DateTimeField('Дата создания записи', default=timezone.now)
    status = models.ForeignKey(
        Status, 
        on_delete=models.PROTECT,
        verbose_name='Статус'
    )
    type = models.ForeignKey(
        Type, 
        on_delete=models.PROTECT,
        verbose_name='Тип'
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT,
        verbose_name='Категория'
    )
    subcategory = models.ForeignKey(
        Subcategory, 
        on_delete=models.PROTECT,
        verbose_name='Подкатегория',
        null=True,
        blank=True
    )
    amount = models.DecimalField(
        'Сумма', 
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    comment = models.TextField('Комментарий', blank=True)
    
    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'
        ordering = ['-date', '-date']
    
    def __str__(self):
        return f"{self.date} - {self.status} - {self.amount}₽"
    
    def clean(self):
        if self.category and self.type and self.category.type != self.type:
            raise ValidationError('Категория не соответствует выбранному типу')
        
        if self.subcategory and self.category and self.subcategory.category != self.category:
            raise ValidationError('Подкатегория не соответствует выбранной категории')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)