from django.views.generic import ListView, DetailView
from django.db.models import Sum, Q

from admin_dashboard.mixins import StaffRequiredMixin
from payments.models.payment import Payment

class PaymentListView(StaffRequiredMixin, ListView):
    model = Payment
    template_name = 'admin_dashboard/payments/list.html'
    context_object_name = 'payments'
    paginate_by = 15

    def get_queryset(self):
        # pyrefly: ignore [missing-attribute]
        queryset = Payment.objects.all().select_related('booking', 'currency')
        
        # Transaction ID or booking uid search
        q = self.request.GET.get('search', '').strip()
        if q:
            queryset = queryset.filter(
                # pyrefly: ignore [unsupported-operation]
                Q(transaction_id__icontains=q) |
                Q(booking__booking_uid__icontains=q) |
                Q(booking__guest_name__icontains=q)
            )
            
        # Filter by gateway
        gateway = self.request.GET.get('gateway', '').strip()
        if gateway:
            queryset = queryset.filter(gateway=gateway)
            
        # Filter by status
        status = self.request.GET.get('status', '').strip()
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Gateway lists for filtering
        # pyrefly: ignore [missing-attribute]
        context['gateways'] = Payment.objects.values_list('gateway', flat=True).distinct()
        context['selected_gateway'] = self.request.GET.get('gateway', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('search', '')
        
        # Calculate revenue summaries for analytics cards
        # pyrefly: ignore [missing-attribute]
        total_payments = Payment.objects.filter(status='success')
        context['total_collected'] = total_payments.aggregate(total=Sum('amount'))['total'] or 0
        context['stripe_collected'] = total_payments.filter(gateway__iexact='stripe').aggregate(total=Sum('amount'))['total'] or 0
        context['esewa_collected'] = total_payments.filter(gateway__iexact='esewa').aggregate(total=Sum('amount'))['total'] or 0
        context['khalti_collected'] = total_payments.filter(gateway__iexact='khalti').aggregate(total=Sum('amount'))['total'] or 0
        # pyrefly: ignore [missing-attribute]
        context['refunded_collected'] = Payment.objects.filter(status='refunded').aggregate(total=Sum('amount'))['total'] or 0
        
        return context

class PaymentDetailView(StaffRequiredMixin, DetailView):
    model = Payment
    template_name = 'admin_dashboard/payments/detail.html'
    context_object_name = 'payment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Raw response formatting check (assuming stored in some payload/logs or check booking payload)
        # We can format raw payload details from the booking channel_raw_payload if present, or just display raw payment columns.
        booking = self.object.booking
        context['booking_raw_payload'] = booking.channel_raw_payload if booking else None
        return context
