# views.py
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import Transaction, Status, Type, Category, Subcategory
from .forms import TransactionForm
from .services import TransactionService
from .directory_services import DirectoryService
from .utils import get_filtered_queryset

# ---------- Транзакции ----------
def transaction_list(request):

    transactions = Transaction.objects.select_related(
        'status', 'type', 'category', 'subcategory'
    ).all()
    
    # Применяем фильтры через сервис
    transactions = TransactionService.filter_transactions(
        transactions, request.GET
    )
    
    context = {
        'transactions': transactions,
        'statuses': Status.objects.all(),
        'types': Type.objects.all(),
        'categories': Category.objects.all(),
        'subcategories': Subcategory.objects.all(),
        'filters': request.GET,
    }
    return render(request, 'transaction/transaction_list.html', context)

def transaction_create(request):

    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            try:
                
                transaction = TransactionService.create_transaction(form.cleaned_data)
                messages.success(request, 'Транзакция успешно создана!')
                return redirect('transaction:transaction_list')
            except (ValueError, KeyError) as e:
                messages.error(request, str(e))
    else:
        form = TransactionForm()
    
    return render(request, 'transaction/transaction_form.html', {
        'form': form,
        'title': 'Создание транзакции'
    })

def transaction_edit(request, pk):

    transaction = get_object_or_404(Transaction, pk=pk)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            try:
                TransactionService.update_transaction(
                    transaction, form.cleaned_data
                )
                messages.success(request, 'Транзакция успешно обновлена!')
                return redirect('transaction:transaction_list')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = TransactionForm(instance=transaction)
    
    return render(request, 'transaction/transaction_form.html', {
        'form': form,
        'title': 'Редактирование транзакции'
    })

def transaction_delete(request, pk):

    transaction = get_object_or_404(Transaction, pk=pk)
    
    if request.method == 'POST':
        TransactionService.delete_transaction(transaction)
        messages.success(request, 'Транзакция удалена!')
        return redirect('transaction:transaction_list')
    
    return render(request, 'transaction/transaction_confirm_delete.html', {
        'transaction': transaction
    })


def directory_list(request):

    context = {
        'statuses': Status.objects.all(),
        'types': Type.objects.all(),
        'categories': Category.objects.select_related('type').all(),
        'subcategories': Subcategory.objects.select_related('category__type').all(),
    }
    return render(request, 'transaction/directory_list.html', context)

def directory_create(request, model_type):

    if request.method == 'POST':
        try:
            DirectoryService.create(model_type, request.POST.dict())
            messages.success(
                request, 
                f'{DirectoryService.get_verbose_name(model_type)} успешно создан!'
            )
            return redirect('transaction:directory_list')
        except ValueError as e:
            messages.error(request, str(e))
    

    context = DirectoryService.get_context_data(model_type)
    return render(request, 'transaction/directory_form.html', context)

def directory_edit(request, model_type, pk):

    if request.method == 'POST':
        try:
            DirectoryService.update(model_type, pk, request.POST.dict())
            messages.success(
                request,
                f'{DirectoryService.get_verbose_name(model_type)} успешно обновлен!'
            )
            return redirect('transaction:directory_list')
        except ValueError as e:
            messages.error(request, str(e))
    

    model = DirectoryService.get_model(model_type)
    obj = get_object_or_404(model, pk=pk)
    context = DirectoryService.get_context_data(model_type, obj)
    return render(request, 'transaction/directory_form.html', context)

def directory_delete(request, model_type, pk):
    if request.method == 'POST':
        DirectoryService.delete(model_type, pk)
        messages.success(
            request,
            f'{DirectoryService.get_verbose_name(model_type)} успешно удален!'
        )
        return redirect('transaction:directory_list')
    

    model = DirectoryService.get_model(model_type)
    obj = get_object_or_404(model, pk=pk)
    context = {
        'obj': obj,
        'model_type': model_type,
        'verbose_name': model._meta.verbose_name,
    }
    return render(request, 'transaction/directory_confirm_delete.html', context)

def get_categories_by_type(request):

    type_id = request.GET.get('type_id')
    if type_id:
        categories = Category.objects.filter(type_id=type_id).values('id', 'name')
        return JsonResponse(list(categories), safe=False)
    return JsonResponse([], safe=False)

def get_subcategories_by_category(request):

    category_id = request.GET.get('category_id')
    if category_id:
        subcategories = Subcategory.objects.filter(category_id=category_id).values('id', 'name')
        return JsonResponse(list(subcategories), safe=False)
    return JsonResponse([], safe=False)