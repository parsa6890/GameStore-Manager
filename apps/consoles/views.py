from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from .models import ConsoleBrand, ConsoleType, ConsoleModel, ConsoleCapacity


SESSION_CAPACITY = "console_capacity_id"


def _require_customer(request):
    from apps.accounts.views import _get_customer
    customer = _get_customer(request)
    if not customer:
        messages.warning(request, "لطفاً ابتدا اطلاعات خود را وارد کنید.")
        return None
    return customer


@require_http_methods(["GET"])
def select(request):
    """صفحه انتخاب برند → مدل → نوع → ظرفیت"""
    customer = _require_customer(request)
    if not customer:
        return redirect("accounts:start")

    brands = ConsoleBrand.objects.filter(is_active=True).prefetch_related(
        "models", "models__capacities", "models__capacities__console_type"
    )
    types = ConsoleType.objects.filter(is_active=True)

    # ساختار داده برای جاوااسکریپت
    import json
    brands_data = []
    for brand in brands:
        models_data = []
        for model in brand.models.filter(is_active=True):
            caps_data = []
            for cap in model.capacities.filter(is_active=True):
                caps_data.append({
                    "id": cap.id,
                    "type_id": cap.console_type_id,
                    "type_name": cap.console_type.name,
                    "nominal": float(cap.nominal_capacity),
                    "usable": float(cap.usable_capacity),
                })
            models_data.append({
                "id": model.id,
                "name": model.name,
                "capacities": caps_data,
            })
        brands_data.append({
            "id": brand.id,
            "name": brand.name,
            "models": models_data,
        })

    selected_capacity_id = request.session.get(SESSION_CAPACITY)

    return render(request, "customer/select_console.html", {
        "customer": customer,
        "brands": brands,
        "types": types,
        "brands_json": json.dumps(brands_data, ensure_ascii=False),
        "selected_capacity_id": selected_capacity_id,
    })


@require_http_methods(["POST"])
def save_capacity(request):
    """ذخیره ظرفیت انتخاب‌شده در Session"""
    customer = _require_customer(request)
    if not customer:
        return redirect("accounts:start")

    capacity_id = request.POST.get("capacity_id")
    if not capacity_id:
        messages.error(request, "لطفاً ظرفیت کنسول خود را انتخاب کنید.")
        return redirect("consoles:select")

    try:
        capacity = ConsoleCapacity.objects.select_related(
            "console_model", "console_type"
        ).get(pk=capacity_id, is_active=True)
    except ConsoleCapacity.DoesNotExist:
        messages.error(request, "ظرفیت انتخاب‌شده معتبر نیست.")
        return redirect("consoles:select")

    request.session[SESSION_CAPACITY] = capacity.id
    messages.success(
        request,
        f"کنسول شما: {capacity.console_model.name} - {capacity.console_type.name} - {capacity.nominal_capacity}GB"
    )
    return redirect("games:list")