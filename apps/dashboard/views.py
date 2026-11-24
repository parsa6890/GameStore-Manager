from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta

from apps.orders.models import Order, OrderStatus, OrderItem
from apps.orders.services import update_order_status, OrderError
from apps.accounts.models import Customer
from apps.games.models import Game


@staff_member_required
def dashboard(request):
    """داشبورد اصلی مدیریت"""
    today = timezone.now().date()
    week_ago = timezone.now() - timedelta(days=7)
    month_ago = timezone.now() - timedelta(days=30)

    total_customers = Customer.objects.filter(is_active=True).count()
    total_orders = Order.objects.count()
    orders_today = Order.objects.filter(created_at__date=today).count()
    orders_week = Order.objects.filter(created_at__gte=week_ago).count()
    orders_month = Order.objects.filter(created_at__gte=month_ago).count()

    status_counts = Order.objects.values("status").annotate(count=Count("id"))
    status_map = {s["status"]: s["count"] for s in status_counts}

    # ساختار لیست برای تمپلیت
    status_breakdown = [
        {"label": label, "count": status_map.get(value, 0)}
        for value, label in OrderStatus.choices
    ]

    recent_orders = Order.objects.select_related("customer", "console_model").order_by("-created_at")[:10]

    # محبوب‌ترین بازی‌ها
    top_games = (
        OrderItem.objects.values("game_title_snapshot")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    context = {
        "total_customers": total_customers,
        "total_orders": total_orders,
        "orders_today": orders_today,
        "orders_week": orders_week,
        "orders_month": orders_month,
        "status_map": status_map,
        "status_breakdown": status_breakdown,
        "recent_orders": recent_orders,
        "top_games": top_games,
        "order_status_choices": OrderStatus.choices,
    }
    return render(request, "dashboard/dashboard.html", context)


@staff_member_required
def order_list(request):
    """لیست سفارش‌ها با جستجو و فیلتر"""
    q = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()
    date_filter = request.GET.get("date", "").strip()

    orders = Order.objects.select_related(
        "customer", "console_model"
    ).order_by("-created_at")

    if q:
        orders = orders.filter(
            Q(order_number__icontains=q) |
            Q(customer__first_name__icontains=q) |
            Q(customer__last_name__icontains=q) |
            Q(customer__mobile__icontains=q)
        )
    if status_filter:
        orders = orders.filter(status=status_filter)
    if date_filter == "today":
        orders = orders.filter(created_at__date=timezone.now().date())
    elif date_filter == "week":
        orders = orders.filter(created_at__gte=timezone.now() - timedelta(days=7))
    elif date_filter == "month":
        orders = orders.filter(created_at__gte=timezone.now() - timedelta(days=30))

    # صفحه‌بندی
    from django.core.paginator import Paginator
    paginator = Paginator(orders, 20)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "orders": page_obj,
        "q": q,
        "status_filter": status_filter,
        "date_filter": date_filter,
        "order_status_choices": OrderStatus.choices,
    }
    return render(request, "dashboard/order_list.html", context)


@staff_member_required
def order_detail(request, order_number):
    """جزئیات سفارش + تغییر وضعیت"""
    order = get_object_or_404(
        Order.objects.select_related(
            "customer", "console_model", "console_capacity"
        ).prefetch_related("items", "status_history"),
        order_number=order_number,
    )

    if request.method == "POST":
        new_status = request.POST.get("status")
        note = request.POST.get("note", "").strip()
        if new_status:
            try:
                update_order_status(order, new_status, user=request.user, note=note)
                messages.success(request, "وضعیت سفارش به‌روزرسانی شد.")
                return redirect("dashboard:order_detail", order_number=order.order_number)
            except OrderError as e:
                messages.error(request, str(e))

    context = {
        "order": order,
        "items": order.items.all(),
        "history": order.status_history.all(),
        "order_status_choices": OrderStatus.choices,
    }
    return render(request, "dashboard/order_detail.html", context)


@staff_member_required
def customer_list(request):
    """لیست مشتریان"""
    q = request.GET.get("q", "").strip()
    customers = Customer.objects.filter(is_active=True).annotate(
        orders_count=Count("orders"),
        last_order_date=__import__("django.db.models", fromlist=["Max"]).Max("orders__created_at"),
    ).order_by("-created_at")

    if q:
        customers = customers.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(mobile__icontains=q)
        )

    from django.core.paginator import Paginator
    paginator = Paginator(customers, 20)
    page_obj = paginator.get_page(request.GET.get("page", 1))

    context = {
        "page_obj": page_obj,
        "customers": page_obj,
        "q": q,
    }
    return render(request, "dashboard/customer_list.html", context)


@staff_member_required
def customer_detail(request, customer_id):
    """جزئیات مشتری + سفارش‌هایش"""
    customer = get_object_or_404(Customer, pk=customer_id)
    orders = customer.orders.select_related("console_model").order_by("-created_at")

    context = {
        "customer": customer,
        "orders": orders,
    }
    return render(request, "dashboard/customer_detail.html", context)

@staff_member_required
def order_print(request, order_number):
    """نسخه چاپی سفارش"""
    order = get_object_or_404(
        Order.objects.select_related("customer", "console_model").prefetch_related("items"),
        order_number=order_number,
    )
    return render(request, "dashboard/order_print.html", {
        "order": order,
        "items": order.items.all(),
    })