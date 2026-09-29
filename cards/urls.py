from django.urls import path

from .views import CardCreateView, CardListView, CardDeleteView


urlpatterns = [
    path("", CardCreateView.as_view(), name="card-create"),
    path("list/", CardListView.as_view(), name="card-list"),
    path("delete/<int:card_id>/", CardDeleteView.as_view(), name="card-delete"),
]