from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from apps.accounts.views import _get_customer
from apps.consoles.views import SESSION_CAPACITY
from apps.consoles.models import ConsoleCapacity
from apps.games.views import _cart_summary, _get_capacity

from .models import Order, OrderStatus
from .services import create_order, OrderError, hash_token


SESSION_ORDER_TOKEN = "last_order_token"


@require_http_methods(["GET", "POST"])
def checkout(request):
    """صفحه بررسی نهایی و ثبت سفارش"""
    customer = _get_customer(request)
    if not customer:
        return redirect("accounts:landing")

    capacity = _get_capacity(request)
    if not capacity:
        messages.warning(request, "لطفاً ابتدا کنسول خود را انتخاب کنید.")
        return redirect("consoles:select")

    cart = request.session.get("cart", {})
    if not cart:
        messages.warning(request, "سبد خرید شما خالی است.")
        return redirect("games:list")

    summary = _cart_summary(request, capacity)

    if request.method == "POST":
        try:
            order, raw_token = create_order(customer, capacity.id, cart)
        except OrderError as e:
            messages.error(request, str(e))
            return redirect("games:list")

        # ذخیره توکن خام در Session برای دسترسی به سفارش
        tokens = request.session.get(SESSION_ORDER_TOKEN, {})
        tokens[order.order_number] = raw_token
        request.session[SESSION_ORDER_TOKEN] = tokens

        # پاک کردن سبد
        request.session["cart"] = {}
        request.session.pop(SESSION_CAPACITY, None)

        messages.success(request, f"سفارش شما با شماره {order.order_number} ثبت شد.")
        return redirect("orders:success", order_number=order.order_number)

    return render(request, "customer/checkout.html", {
        "customer": customer,
        "capacity": capacity,
        "summary": summary,
    })


@require_http_methods(["GET"])
def order_success(request, order_number):
    """صفحه موفقیت پس از ثبت سفارش"""
    customer = _get_customer(request)
    if not customer:
        return redirect("accounts:landing")

    order = get_object_or_404(Order, order_number=order_number, customer=customer)
    return render(request, "customer/order_success.html", {
        "order": order,
        "customer": customer,
    })


@require_http_methods(["GET"])
def order_detail(request, order_number, token):
    """مشاهده سفارش با توکن دسترسی (برای پیگیری)"""
    try:
        token_hash = hash_token(token)
        order = Order.objects.select_related(
            "customer", "console_model", "console_capacity"
        ).prefetch_related("items").get(
            order_number=order_number,
            access_token_hash=token_hash,
        )
    except Order.DoesNotExist:
        messages.error(request, "سفارش موردنظر یافت نشد یا دسترسی معتبر نیست.")
        return redirect("accounts:landing")

    return render(request, "customer/order_detail.html", {
        "order": order,
        "items": order.items.all(),
        "history": order.status_history.all(),
    })


@require_http_methods(["GET"])
def my_orders(request):
    """سفارش‌های مشتری در نشست فعلی"""
    customer = _get_customer(request)
    if not customer:
        return redirect("accounts:landing")

    tokens = request.session.get(SESSION_ORDER_TOKEN, {})

    orders = []
    for order_number, raw_token in tokens.items():
        try:
            token_hash = hash_token(raw_token)
            order = Order.objects.get(
                order_number=order_number,
                access_token_hash=token_hash,
                customer=customer,
            )
            orders.append(order)
        except Order.DoesNotExist:
            continue

    orders.sort(key=lambda o: o.created_at, reverse=True)

    return render(request, "customer/my_orders.html", {
        "customer": customer,
        "orders": orders,
    })