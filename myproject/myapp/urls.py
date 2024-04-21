# myapp/urls.py
from django.urls import path
from .views import autocomplete_search, search_form, search_location, show_subplots, generate_folium_map

urlpatterns = [
    path('autocomplete_search/', autocomplete_search, name='autocomplete_search'),
    path('search/form/', search_form , name='search_places_html'),
    path('search_location/', search_location , name='search_location'),
    path('show_subplots/', show_subplots , name='show_subplots'),
    path('generate_folium_map/', generate_folium_map , name='generate_folium_map'),
]
