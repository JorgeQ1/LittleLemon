from rest_framework import generics
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from decimal import Decimal
from .models import MenuItem, Order, Cart, OrderItem
from .serializers import MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer



# Create your views here.
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    oredering_fields = ["price"]
    search_fields = ["title"]

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
