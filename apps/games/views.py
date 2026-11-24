from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q

from apps.consoles.models import ConsoleCapacity
from apps.consoles.views import SESSION_CAPACITY, _require_customer
from .models import Game, GameCategory, Genre, GamePlatformVersion, Platform


PLATFORM_MAP = {
    "PlayStation 4": [Platform.PS4],
    "PlayStation 4 Slim": [Platform.PS4_SLIM, Platform.PS4],
    "PlayStation 4 Pro": [Platform.PS4_PRO, Platform.PS4],
    "PlayStation 5": [Platform.PS5],
    "PlayStation 5 Slim": [Platform.PS5_SLIM, Platform.PS5],
    "PlayStation 5 Pro": [Platform.PS5_PRO, Platform.PS5],
    "Xbox One": [Platform.XBOX_ONE],
    "Xbox One S": [Platform.XBOX_ONE_S, Platform.XBOX_ONE],
    "Xbox One X": [Platform.XBOX_ONE_X, Platform.XBOX_ONE],
    "Xbox Series S": [Platform.XBOX_SERIES_S],
    "Xbox Series X": [Platform.XBOX_SERIES_X],
}


def _get_capacity(request):
    capacity_id = request.session.get(SESSION_CAPACITY)
    if not capacity_id:
        return None
    try:
        return ConsoleCapacity.objects.select_related(
            "console_model", "console_type"
        ).get(pk=capacity_id, is_active=True)
    except ConsoleCapacity.DoesNotExist:
        return None


def _cart_summary(request, capacity):
    """خلاصه سبد + محاسبه ظرفیت"""
    cart = request.session.get("cart", {})
    items = []
    total = 0.0
    for vid, data in cart.items():
        items.append({"version_id": int(vid), **data})
        total += float(data["size_gb"])

    usable = float(capacity.usable_capacity) if capacity else 0.0
    remaining = usable - total
    overflow = max(0.0, total - usable)
    percent = min(100.0, (total / usable * 100.0)) if usable > 0 else 0.0

    return {
        "items": items,
        "count": len(items),
        "total": round(total, 2),
        "usable": round(usable, 2),
        "remaining": round(remaining, 2),
        "overflow": round(overflow, 2),
        "percent": round(percent, 1),
    }


@require_http_methods(["GET"])
def game_list(request):
    customer = _require_customer(request)
    if not customer:
        return redirect("accounts:landing")

    capacity = _get_capacity(request)
    if not capacity:
        messages.warning(request, "لطفاً ابتدا کنسول خود را انتخاب کنید.")
        return redirect("consoles:select")

    compatible_platforms = PLATFORM_MAP.get(capacity.console_model.name, [])

    versions_qs = GamePlatformVersion.objects.filter(
        is_active=True,
        platform__in=compatible_platforms,
        console_type=capacity.console_type,
        game__is_active=True,
    ).select_related("game", "console_type")

    q = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    genre_slug = request.GET.get("genre", "").strip()
    kid_friendly = request.GET.get("kid", "") == "1"
    family_friendly = request.GET.get("family", "") == "1"
    age_group = request.GET.get("age", "").strip()
    sort = request.GET.get("sort", "name")

    if q:
        versions_qs = versions_qs.filter(
            Q(game__title_fa__icontains=q) | Q(game__title_en__icontains=q)
        )
    if category_slug:
        versions_qs = versions_qs.filter(game__categories__slug=category_slug)
    if genre_slug:
        versions_qs = versions_qs.filter(game__genres__slug=genre_slug)
    if kid_friendly:
        versions_qs = versions_qs.filter(game__is_kid_friendly=True)
    if family_friendly:
        versions_qs = versions_qs.filter(game__is_family_friendly=True)
    if age_group:
        versions_qs = versions_qs.filter(game__age_group=age_group)

    if sort == "size_asc":
        versions_qs = versions_qs.order_by("size_gb")
    elif sort == "size_desc":
        versions_qs = versions_qs.order_by("-size_gb")
    else:
        versions_qs = versions_qs.order_by("game__title_fa")

    seen_games = set()
    unique_versions = []
    for v in versions_qs:
        if v.game_id not in seen_games:
            seen_games.add(v.game_id)
            unique_versions.append(v)

    categories = GameCategory.objects.filter(is_active=True)
    genres = Genre.objects.filter(is_active=True)
    from .models import AgeGroup
    age_groups = AgeGroup.choices

    summary = _cart_summary(request, capacity)
    cart_id_ints = set(x["version_id"] for x in summary["items"])

    context = {
        "customer": customer,
        "capacity": capacity,
        "versions": unique_versions,
        "categories": categories,
        "genres": genres,
        "age_groups": age_groups,
        "summary": summary,
        "cart_id_ints": cart_id_ints,
        "current_filters": {
            "q": q, "category": category_slug, "genre": genre_slug,
            "kid": kid_friendly, "family": family_friendly,
            "age": age_group, "sort": sort,
        },
    }
    return render(request, "customer/game_list.html", context)


@require_http_methods(["POST"])
def add_game(request):
    customer = _require_customer(request)
    if not customer:
        return redirect("accounts:landing")

    version_id = request.POST.get("version_id")
    if not version_id:
        messages.error(request, "بازی انتخاب‌شده معتبر نیست.")
        return redirect("games:list")

    cart = request.session.get("cart", {})
    if version_id in cart:
        messages.info(request, "این بازی قبلاً به سبد اضافه شده است.")
    else:
        try:
            version = GamePlatformVersion.objects.select_related(
                "game", "console_type"
            ).get(pk=version_id, is_active=True)
            cart[version_id] = {
                "game_title": version.game.title_fa,
                "game_title_en": version.game.title_en,
                "size_gb": float(version.size_gb),
                "platform": version.get_platform_display(),
                "console_type": version.console_type.name,
            }
            request.session["cart"] = cart
            messages.success(request, f"«{version.game.title_fa}» به سبد اضافه شد.")
        except GamePlatformVersion.DoesNotExist:
            messages.error(request, "بازی موردنظر یافت نشد.")

    return redirect("games:list")


@require_http_methods(["POST"])
def remove_game(request):
    customer = _require_customer(request)
    if not customer:
        return redirect("accounts:landing")

    version_id = request.POST.get("version_id")
    cart = request.session.get("cart", {})
    if version_id in cart:
        del cart[version_id]
        request.session["cart"] = cart
        messages.success(request, "بازی از سبد حذف شد.")
    return redirect(request.POST.get("next", "games:list"))


@require_http_methods(["POST"])
def clear_cart(request):
    request.session["cart"] = {}
    messages.info(request, "سبد خرید پاک شد.")
    return redirect("games:list")