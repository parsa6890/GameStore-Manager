from django.core.management.base import BaseCommand
from apps.consoles.models import ConsoleBrand, ConsoleType, ConsoleModel, ConsoleCapacity


TYPES = [
    {"name": "کپی‌خور", "slug": "copy"},
    {"name": "اکانتی", "slug": "account"},
    {"name": "معمولی", "slug": "normal"},
]


# (nominal, usable) بر اساس نوع کنسول
CONSOLES_DATA = {
    "Sony": {
        "models": [
            {
                "name": "PlayStation 4",
                "capacities": {
                    "copy": [(500, 400), (1000, 850)],
                    "account": [(500, 350), (1000, 700)],
                    "normal": [(500, 400), (1000, 850)],
                },
            },
            {
                "name": "PlayStation 4 Slim",
                "capacities": {
                    "copy": [(500, 400), (1000, 900)],
                    "account": [(500, 350), (1000, 400)],
                    "normal": [(500, 400), (1000, 850)],
                },
            },
            {
                "name": "PlayStation 4 Pro",
                "capacities": {
                    "copy": [(1000, 900), (2000, 1800)],
                    "account": [(1000, 700), (2000, 1400)],
                    "normal": [(1000, 850), (2000, 1700)],
                },
            },
            {
                "name": "PlayStation 5",
                "capacities": {
                    "copy": [(825, 667)],
                    "account": [(825, 500)],
                    "normal": [(825, 667)],
                },
            },
            {
                "name": "PlayStation 5 Slim",
                "capacities": {
                    "copy": [(1000, 842)],
                    "account": [(1000, 600)],
                    "normal": [(1000, 842)],
                },
            },
            {
                "name": "PlayStation 5 Pro",
                "capacities": {
                    "copy": [(2000, 1700)],
                    "account": [(2000, 1200)],
                    "normal": [(2000, 1700)],
                },
            },
        ],
    },
    "Microsoft": {
        "models": [
            {
                "name": "Xbox One",
                "capacities": {
                    "copy": [(500, 362), (1000, 780)],
                    "account": [(500, 300), (1000, 650)],
                    "normal": [(500, 362), (1000, 780)],
                },
            },
            {
                "name": "Xbox One S",
                "capacities": {
                    "copy": [(500, 362), (1000, 780)],
                    "account": [(500, 300), (1000, 650)],
                    "normal": [(500, 362), (1000, 780)],
                },
            },
            {
                "name": "Xbox One X",
                "capacities": {
                    "copy": [(1000, 780)],
                    "account": [(1000, 650)],
                    "normal": [(1000, 780)],
                },
            },
            {
                "name": "Xbox Series S",
                "capacities": {
                    "copy": [(512, 364)],
                    "account": [(512, 300)],
                    "normal": [(512, 364)],
                },
            },
            {
                "name": "Xbox Series X",
                "capacities": {
                    "copy": [(1000, 802)],
                    "account": [(1000, 700)],
                    "normal": [(1000, 802)],
                },
            },
        ],
    },
}


class Command(BaseCommand):
    help = "Seed console brands, types, models and capacities"

    def handle(self, *args, **options):
        # 1. Console Types
        type_map = {}
        for t in TYPES:
            obj, created = ConsoleType.objects.get_or_create(
                slug=t["slug"],
                defaults={"name": t["name"], "is_active": True},
            )
            type_map[t["slug"]] = obj
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ Type: {t['name']}"))

        created_brands = 0
        created_models = 0
        created_caps = 0

        for brand_name, brand_data in CONSOLES_DATA.items():
            brand, brand_created = ConsoleBrand.objects.get_or_create(
                name=brand_name, defaults={"is_active": True}
            )
            if brand_created:
                created_brands += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Brand: {brand_name}"))

            for model_data in brand_data["models"]:
                model, model_created = ConsoleModel.objects.get_or_create(
                    brand=brand,
                    name=model_data["name"],
                    defaults={"is_active": True},
                )
                if model_created:
                    created_models += 1
                    self.stdout.write(f"  ✓ Model: {model_data['name']}")

                for type_slug, caps in model_data["capacities"].items():
                    console_type = type_map[type_slug]
                    for nominal, usable in caps:
                        _, cap_created = ConsoleCapacity.objects.get_or_create(
                            console_model=model,
                            console_type=console_type,
                            nominal_capacity=nominal,
                            defaults={"usable_capacity": usable, "is_active": True},
                        )
                        if cap_created:
                            created_caps += 1
                            self.stdout.write(
                                f"    ✓ {console_type.name}: {nominal}GB (usable: {usable}GB)"
                            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Done! Brands: {created_brands}, Models: {created_models}, Capacities: {created_caps}"
            )
        )