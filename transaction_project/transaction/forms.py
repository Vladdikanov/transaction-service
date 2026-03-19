from django import forms
from django.core.exceptions import ValidationError
from .models import Transaction, Status, Type, Category, Subcategory

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['date', 'status', 'type', 'category', 'subcategory', 'amount', 'comment']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Добавляем классы Bootstrap
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Если есть выбранная категория, фильтруем подкатегории
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = Subcategory.objects.filter(category_id=category_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.category:
            self.fields['subcategory'].queryset = Subcategory.objects.filter(category=self.instance.category)
        
        # Подкатегория не обязательна
        self.fields['subcategory'].required = False

class DirectoryForm(forms.Form):
    """Универсальная форма для справочников"""
    name = forms.CharField(
        max_length=100, 
        label='Название',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, model_type=None, parent_field=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_type = model_type
        self.parent_field = parent_field
        
        if parent_field:
            self.fields['parent'] = forms.ModelChoiceField(
                queryset=parent_field,
                label='Родитель',
                widget=forms.Select(attrs={'class': 'form-control'})
            )