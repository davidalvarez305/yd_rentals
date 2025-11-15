from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from core.models import Order
from core.serializers import OrderSerializer
from core.filters import OrderFilter

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-date_created')
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter