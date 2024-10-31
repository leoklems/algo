from django.urls import path
from .views import create_standalone, index, initial_funds, assign_room, deploy_contract


urlpatterns = [
    path("", index, name="index"),
    path("create-standalone/", create_standalone, name="create-standalone"),
    path("initial-funds/<str:receiver>/", initial_funds, name="initial-funds"),

    path('deploy-contract/', deploy_contract, name='deploy-contract'),
    path('assign-room/', assign_room, name='assign-room'),
]