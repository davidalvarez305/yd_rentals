import django_filters
from .models import Order

class OrderFilter(django_filters.FilterSet):
    external_id = django_filters.CharFilter(lookup_expr='iexact')
    user = django_filters.NumberFilter(field_name='user__user_id')
    date_created__gte = django_filters.DateFilter(field_name='date_created', lookup_expr='date__gte')
    date_created__lte = django_filters.DateFilter(field_name='date_created', lookup_expr='date__lte')

    class Meta:
        model = Order
        fields = ['external_id', 'user', 'date_created__gte', 'date_created__lte']