from rest_framework import serializers
from core.models import Order, OrderItem, Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['item', 'name', 'description', 'subcategory', 'external_id']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['order', 'item', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    external_id = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = ['order_id', 'external_id', 'user', 'date_created', 'items']
