from rest_framework import generics
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from decimal import Decimal
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .models import MenuItem, Order, Cart, OrderItem
from .serializers import MenuItemSerializer, UserOrderSerializer, UserSerializer, UserCartSerializer



# Create your views here.
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    oredering_fields = ["price"]
    search_fields = ["title"]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [AllowAny()]

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    def get_permissions(self):
        if self.request.method == 'POST' or self.request.method == 'PUT' \
                or self.request.method == 'DELETE' or self.request.method == 'PATCH':
            return [IsAdminUser()]
        return [AllowAny()]
    
class ManagerUsersView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        manager_group = Group.objects.get(name='Manager') # get managers group
        queryset = User.objects.filter(groups=manager_group) #users in managers group
        return queryset
    
    def perform_create(self, serializer):
        manager_group = Group.objects.get(name='Manager')
        user = serializer.save()
        user.groups.add(manager_group)
        return Response("user added to the manager group", status=201)
        

class SingleManagerUserView(generics.RetrieveDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        manager_group = Group.objects.get(name='Manager')
        queryset = User.objects.filter(groups=manager_group)
        return queryset
    
    
class DeliveryCrewsView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        delivery_group = Group.objects.get(name='delivery crew') # get managers group
        queryset = User.objects.filter(groups=delivery_group) #users in managers group
        return queryset
    
    def perform_create(self, serializer):
        delivery_group = Group.objects.get(name='delivery crew')
        user = serializer.save()
        user.groups.add(delivery_group)
        

class SingleDeliveryCrewView(generics.RetrieveDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        delivery_group = Group.objects.get(name='delivery crew')
        queryset = User.objects.filter(groups=delivery_group)
        return queryset
    
    
class CustomerCart(generics.ListCreateAPIView):
    serializer_class = UserCartSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)
    
    def perform_create(self, serializer):
        menuitem = self.request.data.get('menuitem')
        quantity = self.request.data.get('quantity')
        unit_price = MenuItem.objects.get(pk=menuitem).price
        quantity = int(quantity)
        price = quantity * unit_price
        serializer.save(user=self.request.user, price=price)
        
    def delete_cart(self, request):
        user = self.request.user
        Cart.objects.filter(user=user).delete()
        return Response(status=204)
    

class OrdersView(generics.ListCreateAPIView):
    serializer_class = UserOrderSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    def perform_create(self, serializer):
        cart_items = Cart.objects.filter(user=self.request.user)
        total = self.calculate_total(cart_items)
        order = serializer.save(user=self.request.user, total=total)
        
        for cart_item in cart_items:
            OrderItem.objects.create(menuitem=cart_item.menuitem, quantity=cart_item.quantity,
                                     unit_price=cart_item.unit_price, price=cart_item.price, order=order)
            cart_item.delete()
            
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='manager').exists():
            return Order.objects.all()
        return Order.objects.filter(user=user)
    
    def calculate_total(self, cart_items):
        total = Decimal(0)
        for cart_item in cart_items:
            total += cart_item.price
        return total
    
    
class SingleOrderView(generics.RetrieveDestroyAPIView):
    serializer_class = UserOrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='manager').exists():
            return Order.objects.all()
        return Order.objects.filter(user=user)