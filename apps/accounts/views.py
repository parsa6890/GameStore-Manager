from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from .models import Customer
from .forms import CustomerForm


SESSION_KEY = "customer_id"


def _get_customer(request):
    cid = request.session.get(SESSION_KEY)
    if not cid:
        return None
    try:
        return Customer.objects.get(pk=cid, is_active=True)
    except Customer.DoesNotExist:
        request.session.pop(SESSION_KEY, None)
        return None


@require_http_methods(["GET", "POST"])
def start(request):
    """صفحه شروع / ثبت اطلاعات مشتری"""
    customer = _get_customer(request)

    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            mobile = form.cleaned_data["mobile"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]

            existing = Customer.objects.filter(mobile=mobile).first()
            if existing:
                existing.first_name = first_name
                existing.last_name = last_name
                existing.save(update_fields=["first_name", "last_name", "updated_at"])
                obj = existing
                messages.info(request, f"خوش برگشتی {obj.full_name}!")
            else:
                obj = Customer.objects.create(
                    mobile=mobile,
                    first_name=first_name,
                    last_name=last_name,
                )
                messages.success(request, f"خوش آمدید {obj.full_name}!")

            request.session[SESSION_KEY] = obj.pk
            return redirect("consoles:select")
        else:
            # 🔍 چاپ خطاهای فرم برای دیباگ
            print("FORM ERRORS:", form.errors)
            print("FORM DATA:", request.POST)
    else:
        if customer:
            form = CustomerForm(initial={
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "mobile": customer.mobile,
            })
        else:
            form = CustomerForm()

    return render(request, "customer/start.html", {"form": form, "customer": customer})


def logout_view(request):
    request.session.flush()
    messages.info(request, "از حساب خود خارج شدید.")
    return redirect("accounts:start")