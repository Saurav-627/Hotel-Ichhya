from django.views.generic import ListView, DetailView
from django.db.models import Sum, Q, CharField
from django.db.models.functions import Coalesce

from admin_dashboard.mixins import StaffRequiredMixin
from payments.models.payment import Payment
from payments.models.payment_processor import PaymentProcessor

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
            queryset = queryset.filter(gateway__iexact=gateway)
            
        # Filter by status
        status = self.request.GET.get('status', '').strip()
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Only show is_published payment processors for the gateway filter
        published_processors = PaymentProcessor.objects.filter(is_published=True).order_by('name')
        selected_gateway = self.request.GET.get('gateway', '').strip()
        selected_status = self.request.GET.get('status', '').strip()
        search_query = self.request.GET.get('search', '').strip()

        context['published_processors'] = published_processors
        context['status_choices'] = Payment.STATUS_CHOICES
        context['selected_gateway'] = selected_gateway
        context['selected_status'] = selected_status
        context['search_query'] = search_query
        context['has_active_filters'] = bool(search_query or selected_gateway or selected_status)
        
        # Calculate revenue summaries for analytics cards grouped by currency
        def get_currency_breakdown(queryset):
            annotated = queryset.annotate(
                cur_code=Coalesce('currency__iso_code', 'booking__currency_code', output_field=CharField())
            )
            breakdown = annotated.values('cur_code').annotate(total=Sum('amount'))
            return {item['cur_code']: item['total'] for item in breakdown}

        total_payments = Payment.objects.filter(status='success')
        refunded_payments = Payment.objects.filter(status='refunded')

        # Dynamically build stats for published processors
        processor_stats = []
        for proc in published_processors:
            processor_stats.append({
                'processor': proc,
                'breakdown': get_currency_breakdown(total_payments.filter(gateway__iexact=proc.code))
            })

        context['total_collected'] = get_currency_breakdown(total_payments)
        context['processor_stats'] = processor_stats
        context['refunded_collected'] = get_currency_breakdown(refunded_payments)
        
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
