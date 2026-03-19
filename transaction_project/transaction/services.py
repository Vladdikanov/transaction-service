from django.db import transaction as db_transaction
from django.utils import timezone
from django.contrib import messages
from .models import Transaction, Category, Subcategory
from .utils import validate_transaction_dependencies
from decimal import Decimal

class TransactionService:
    
    @staticmethod
    @staticmethod
    def create_transaction(data):

        category_id = data['category'].id if hasattr(data['category'], 'id') else int(data['category'])
        type_id = data['type'].id if hasattr(data['type'], 'id') else int(data['type'])
        

        category = Category.objects.get(id=category_id)
        if category.type_id != type_id:
            raise ValueError('Категория не соответствует выбранному типу')
        
        if data.get('subcategory'):
            subcategory_id = data['subcategory'].id if hasattr(data['subcategory'], 'id') else int(data['subcategory'])
            subcategory = Subcategory.objects.get(id=subcategory_id)
            if subcategory.category_id != category_id:
                raise ValueError('Подкатегория не соответствует выбранной категории')
        

        transaction = Transaction.objects.create(
            date=data.get('date', timezone.now()),
            status_id=data['status'].id if hasattr(data['status'], 'id') else int(data['status']),
            type_id=type_id,
            category_id=category_id,
            subcategory_id=subcategory_id if data.get('subcategory') else None,
            amount=Decimal(str(data['amount'])),
            comment=data.get('comment', '')
        )
        
        return transaction
    
    @staticmethod
    def update_transaction(transaction, data):

        if 'category' in data and int(data['category']) != transaction.category_id:
            category = Category.objects.get(id=data['category'])
            if category.type_id != int(data.get('type', transaction.type_id)):
                raise ValueError('Категория не соответствует типу')
        

        for field, value in data.items():
            if hasattr(transaction, field) and value is not None:
                setattr(transaction, field, value)
        
        transaction.save()
        return transaction
    
    @staticmethod
    def delete_transaction(transaction):

        transaction.delete()
    
    @staticmethod
    def filter_transactions(queryset, filters):
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