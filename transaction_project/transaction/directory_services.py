from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from .models import Status, Type, Category, Subcategory

class DirectoryService:

    
    MODELS_MAP = {
        'status': Status,
        'type': Type,
        'category': Category,
        'subcategory': Subcategory,
    }
    
    @classmethod
    def get_model(cls, model_type):

        return cls.MODELS_MAP.get(model_type)
    
    @classmethod
    def get_verbose_name(cls, model_type):

        model = cls.get_model(model_type)
        return model._meta.verbose_name if model else None
    
    @classmethod
    def create(cls, model_type, data):

        model = cls.get_model(model_type)
        if not model:
            raise ValueError(f'Неизвестный тип: {model_type}')
        
        name = data.get('name', '').strip()
        if not name:
            raise ValueError('Название не может быть пустым')
        
        # Проверка уникальности
        if model_type in ['status', 'type']:
            if model.objects.filter(name=name).exists():
                raise ValueError(f'"{name}" уже существует')
            return model.objects.create(name=name)
        
        elif model_type == 'category':
            type_id = data.get('type')
            if not type_id:
                raise ValueError('Необходимо выбрать тип')
            
            type_obj = get_object_or_404(Type, pk=type_id)
            
            if Category.objects.filter(name=name, type=type_obj).exists():
                raise ValueError(f'Категория "{name}" с типом "{type_obj.name}" уже существует')
            
            return Category.objects.create(name=name, type=type_obj)
        
        elif model_type == 'subcategory':
            category_id = data.get('category')
            if not category_id:
                raise ValueError('Необходимо выбрать категорию')
            
            category_obj = get_object_or_404(Category, pk=category_id)
            
            if Subcategory.objects.filter(name=name, category=category_obj).exists():
                raise ValueError(f'Подкатегория "{name}" в категории "{category_obj.name}" уже существует')
            
            return Subcategory.objects.create(name=name, category=category_obj)
    
    @classmethod
    def update(cls, model_type, pk, data):

        model = cls.get_model(model_type)
        obj = get_object_or_404(model, pk=pk)
        
        obj.name = data.get('name', obj.name)
        
        if model_type == 'category' and 'type' in data:
            obj.type = get_object_or_404(Type, pk=data['type'])
        elif model_type == 'subcategory' and 'category' in data:
            obj.category = get_object_or_404(Category, pk=data['category'])
        
        obj.save()
        return obj
    
    @classmethod
    def delete(cls, model_type, pk):

        model = cls.get_model(model_type)
        obj = get_object_or_404(model, pk=pk)
        obj.delete()
        return True
    
    @classmethod
    def get_context_data(cls, model_type, obj=None):

        context = {
            'model_type': model_type,
            'verbose_name': cls.get_verbose_name(model_type),
        }
        
        if model_type == 'category':
            context['types'] = Type.objects.all()
        elif model_type == 'subcategory':
            context['categories'] = Category.objects.select_related('type').all()
        
        if obj:
            context['obj'] = obj
        
        return context