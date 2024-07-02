from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Order, Comment, Customer
from django.db.models import Count
from django.utils.html import format_html
from unfold.decorators import display
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe


@admin.action(description=('Mark selected orders as confirmed'))
def make_confirmed(modeladmin, request, queryset):
    queryset.update(status='confirmed')
    modeladmin.message_user(request, _("Selected orders have been marked as confirmed."))

@admin.action(description=('Mark selected orders as ready to pickup'))
def make_ready_to_pickup(modeladmin, request, queryset):
    queryset.update(status='ready_to_pickup')
    modeladmin.message_user(request, _("Selected orders have been marked as ready to pickup."))

@admin.action(description=('Mark selected orders as concluded'))
def make_concluded(modeladmin, request, queryset):
    queryset.update(status='concluded')
    modeladmin.message_user(request, _("Selected orders have been marked as concluded."))

@admin.action(description=('Mark selected orders as cancelled'))
def make_cancelled(modeladmin, request, queryset):
    queryset.update(status='cancelled')
    modeladmin.message_user(request, _("Selected orders have been marked as cancelled."))



class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1



@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ['order_id_with_link', 'customer', 'total_amount', 'styled_status', 'priority', 'formatted_created_at', 'cancel_button']
    list_filter = ('status', 'priority', 'payment_method', 'delivery_method')
    search_fields = ['customer', 'order_details']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CommentInline]
    actions = [make_confirmed, make_ready_to_pickup, make_concluded, make_cancelled]
    compressed_fields = True
    change_list_template = "orders/order_changelist.html"
    ordering = ('-created_at',)  # Ordena pelos mais recentes
    
    def order_id_with_link(self, obj):
        return format_html(
            '<a href="{}" id="order-row-{}">{}</a>', 
            obj.id, 
            obj.id,
            obj.id
        )

    order_id_with_link.short_description = 'Order ID'
    order_id_with_link.admin_order_field = 'id'

    # class Media:
    #     js = ('js/order_admin.js',)
    
    fieldsets = (
        (None, {
            'fields': ('customer', 'status', 'priority')
        }),
            (
            _("Pagamento"),
            {
                "classes": ["tab"],
                "fields": [
                    "total_amount",
                    "payment_method",
                ],
            },
        ),
        (
            _("Entrega"),
            {
                "classes": ["tab"],
                "fields": [
                    "delivery_method",
                ],
            },
        ),
                (
            _("Detalhes"),
            {
                "classes": ["tab"],
                "fields": [
                    "order_details",
                ],
            },
        ),
        ('Informações cronológicas', {
            "classes": ["tab"],
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('comments')

    @display(ordering='created_at', description=_('Criado em'))
    def formatted_created_at(self, obj):
        return obj.created_at.strftime('%d/%m/%y %H:%M:%S')

    @display(ordering='status', description=_('Status'))
    def styled_status(self, obj):
        status_classes = {
            'placed': 'bg-gray-100 text-gray-500',
            'confirmed': 'bg-blue-100 text-blue-500',
            'ready_to_pickup': 'bg-yellow-100 text-yellow-500',
            'concluded': 'bg-green-100 text-green-500',
            'cancelled': 'bg-red-100 text-red-500',
        }
        
        css_class = status_classes.get(obj.status, 'bg-gray-100 text-gray-500')
        
        next_status_url = reverse('orders:advance_status', args=[obj.id])
        return format_html(
            '<a href="{}" class="inline-block font-semibold leading-normal px-2 py-1 rounded text-xxs uppercase whitespace-nowrap {}">{}'
            '</a>',
            next_status_url,
            css_class,
            obj.get_status_display(),
        )

    @display(description=_('Cancelar'))
    def cancel_button(self, obj):
        svg_icon = mark_safe(
            '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="h-4 w-4">'
            '<path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />'
            '</svg>'
        )

        base_classes = "inline-block font-semibold rounded-full p-3 text-xxs uppercase whitespace-nowrap"
        
        if obj.status == 'cancelled':
            return format_html(
                '<div class="flex items-center gap-x-4 text-xs">'
                '<span class="{} bg-red-100 text-red-500 dark:bg-red-500/20" title="Pedido já cancelado">{}</span>'
                '</div>',
                base_classes, svg_icon
            )
        elif obj.status == 'concluded':
            return format_html(
                '<div class="flex items-center gap-x-4 text-xs">'
                '<span class="{} hover:bg-gray-100 text-gray-500 dark:bg-gray-500/20" title="Não é possível cancelar um pedido concluído">{}</span>'
                '</div>',
                base_classes, svg_icon
            )
        else:
            return format_html(
                '<div class="flex items-center gap-x-4 text-xs">'
                '<a href="{}" onclick="return confirmCancellation(event, {})" '
                'class="{} hover:bg-red-100 text-red-500 dark:bg-red-500/20" '
                'title="Cancelar este pedido">{}</a>'
                '</div>',
                reverse('orders:mark_cancelled', args=[obj.id]),
                obj.id,
                base_classes,
                svg_icon
            )


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ['order', 'content', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'order__customer']



@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    pass


def dashboard(request):
    context = {
        'total_orders': Order.objects.count(),
        'orders_by_status': Order.objects.values('status').annotate(count=Count('status')),
        'recent_orders': Order.objects.order_by('-created_at')[:5],
    }
    return context
