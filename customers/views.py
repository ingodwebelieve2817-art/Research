from rest_framework import viewsets, permissions, filters
from .models import Customer
from .serializers import CustomerSerializer
from activities.models import ActivityLog


class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on Customer records.
    Every database alteration triggers an audit trail log in ActivityLog.
    """

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Add search filtering by name, city, or phone
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "city", "phone"]

    def perform_create(self, serializer):
        customer = serializer.save()
        ActivityLog.objects.create(
            user=self.request.user,
            action="Customer Created",
            details=f"Created customer '{customer.name}' in city '{customer.city}' (Phone: {customer.phone}).",
        )

    def perform_update(self, serializer):
        customer = serializer.save()
        ActivityLog.objects.create(
            user=self.request.user,
            action="Customer Updated",
            details=f"Updated customer details for '{customer.name}' (ID: {customer.id}).",
        )

    def perform_destroy(self, instance):
        customer_name = instance.name
        customer_id = instance.id
        instance.delete()
        ActivityLog.objects.create(
            user=self.request.user,
            action="Customer Deleted",
            details=f"Deleted customer '{customer_name}' (ID: {customer_id}).",
        )
