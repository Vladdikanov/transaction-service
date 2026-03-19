from decimal import Decimal
import re
from django.core.exceptions import ValidationError

def format_currency(amount):

    return f"{amount:,.2f} ₽".replace(",", " ")

def parse_date(date_str):

    from datetime import datetime
    formats = ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValidationError(f"Неверный формат даты: {date_str}")

def validate_transaction_dependencies(transaction_data):

    from .models import Category, Subcategory
    
    category = Category.objects.get(id=transaction_data['category'])
    
    if category.type_id != int(transaction_data['type']):
        raise ValidationError('Категория не соответствует выбранному типу')
    
    if transaction_data.get('subcategory'):
        subcategory = Subcategory.objects.get(id=transaction_data['subcategory'])
        if subcategory.category_id != int(transaction_data['category']):
            raise ValidationError('Подкатегория не соответствует выбранной категории')
    
    return True

def get_filtered_queryset(queryset, filters):

    if filters.get('date_from'):
        queryset = queryset.filter(date__gte=filters['date_from'])
    if filters.get('date_to'):
        queryset = queryset.filter(date__lte=filters['date_to'])
    if filters.get('status'):
        queryset = queryset.filter(status_id=filters['status'])
    if filters.get('type'):
        queryset = queryset.filter(type_id=filters['type'])
    if filters.get('category'):
        queryset = queryset.filter(category_id=filters['category'])
    if filters.get('subcategory'):
        queryset = queryset.filter(subcategory_id=filters['subcategory'])
    
    return queryset