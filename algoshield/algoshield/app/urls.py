from django.urls import path
from .views import (create_standalone, 
    index, 
    initial_funds, 
    assign_room, 
    deploy_contract,
    send_funds,
    AppartmentCreateView,
    Appartments,
    create_customer,
    sign_in, sign_out)


urlpatterns = [
    path("", index, name="index"),
    path("create-standalone/", create_standalone, name="create-standalone"),
    path('create-customer/', create_customer, name='create_customer'),

    path('sign-in/', sign_in, name='sign_in'),
    path('sign-out/', sign_out, name='sign_out'),

    path("initial-funds/<str:receiver>/", initial_funds, name="initial-funds"),
    path('send-funds/', send_funds, name='send-funds'),

    path('deploy-contract/', deploy_contract, name='deploy-contract'),
    path("appartments/create/", AppartmentCreateView.as_view(), name="create_appartment"),
    path('appartments/', Appartments.as_view(), name='appartments'),
    path('assign-room/', assign_room, name='assign-room'),
]