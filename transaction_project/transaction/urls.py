from django.urls import path
from . import views
app_name = 'transaction'
urlpatterns = [
    path('', views.transaction_list, name='transaction_list'),
    
    path('create/', views.transaction_create, name='transaction_create'),
    path('<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    path('<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    
    path('directories/', views.directory_list, name='directory_list'),
    path('directories/<str:model_type>/create/', views.directory_create, name='directory_create'),
    path('directories/<str:model_type>/<int:pk>/edit/', views.directory_edit, name='directory_edit'),
    path('directories/<str:model_type>/<int:pk>/delete/', views.directory_delete, name='directory_delete'),
    
    path('ajax/get-categories/', views.get_categories_by_type, name='get_categories'),
    path('ajax/get-subcategories/', views.get_subcategories_by_category, name='get_subcategories'),
]