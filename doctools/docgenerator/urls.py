from django.urls import path, re_path
from spectools import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('<slug:schema_slug>-reference/', views.reference_homepage, name='reference_homepage'),
    path('<slug:schema_slug>-reference/examples/', views.example_list, name='example_list'),
    path('<slug:schema_slug>-reference/examples/<slug:slug>/', views.example_detail, name='example_detail'),
    path('<slug:schema_slug>-reference/objects/', views.json_object_list, name='json_object_list'),
    path('<slug:schema_slug>-reference/objects/<slug:slug>/', views.json_object_detail, name='json_object_detail'),
    path('<slug:schema_slug>-schema.json', views.json_schema, name='json_schema'),
    path('comparisons/<slug:slug>/', views.format_comparison_detail, name='format_comparison_detail'),
    re_path(r'^.*$', views.static_page_or_collection_detail),
]
