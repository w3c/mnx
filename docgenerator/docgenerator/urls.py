from django.contrib import admin
from django.urls import path
from spec import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('elements/', views.element_list, name='element_list'),
    path('elements/<slug:slug>/', views.element_detail, name='element_detail'),
    path('element-tree/', views.element_tree, name='element_tree'),
    path('data-types/', views.data_type_list, name='data_type_list'),
    path('data-types/<slug:slug>/', views.data_type_detail, name='data_type_detail'),
    path('examples/', views.example_list, name='example_list'),
    path('examples/<slug:slug>/', views.example_detail, name='example_detail'),
    path('concepts/', views.concept_list, name='concept_list'),
    path('concepts/<slug:slug>/', views.concept_detail, name='concept_detail'),
    path('comparisons/<slug:slug>/', views.format_comparison_detail, name='format_comparison_detail'),
    path('admin/', admin.site.urls),
]
