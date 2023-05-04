from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User
from datetime import datetime


# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ["id", "title"]


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "featured", "category"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']


class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    unit_price = serializers.DecimalField(
        max_digits=6, decimal_places=2, source="menuitem.price", read_only=True
    )

    class Meta:
        model = Cart
        fields = ["user_id", "user", "menuitem", "quantity", "unit_price", "price"]
        extra_kwargs = {"price": {"read_only": True}}


class OrderSerializer(serializers.ModelSerializer):
    # user = serializers.PrimaryKeyRelatedField(
    #     queryset=User.objects.all(), default=serializers.CurrentUserDefault()
    # )
    user = UserSerializer(read_only=True)
    delivery_crew = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "delivery_crew", "status", "total", "date"]


class OrderItemSerializer(serializers.ModelSerializer):
    unit_price = serializers.DecimalField(
        max_digits=6, decimal_places=2, source="menuitem.price", read_only=True
    )
    name = serializers.CharField(source="menuitem.title", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["name", "quantity", "unit_price", "price"]
        extra_kwargs = {"menutiem": {"read_only": True}}
