from .models import Order

def placed_orders_badge(request):
    count = Order.objects.filter(status='placed').count()
    print("Passou por /placed_orders_badge function")
    return str(count) if count > 0 else ""