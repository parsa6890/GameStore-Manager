from django.core.management.base import BaseCommand
from apps.consoles.models import ConsoleBrand, ConsoleModel, ConsoleCapacity


CONSOLES_DATA = {
    "Sony": {
        "models": [
            {
                "name": "PlayStation 4",
                "capacities": [(500, 400), (1000, 850)],
            },
            {
                "name": "PlayStation 4 Slim",
                "capacities": [(500, 400), (1000, 850)],
            },
            {
                "name": "PlayStation 4 Pro",
                "capacities": [(1000, 850), (2000, 1700)],
            },
            {
                "name": "PlayStation 5",
                "capacities": [(825, 667)],
            },
            {
                "name": "PlayStation 5 Slim",
                "capacities": [(1000, 842)],
            },
            {
                "name": "PlayStation 5 Pro",
                "capacities": [(2000, 1700)],
            },
        ],
    },
    "Microsoft": {
        "models": [
            {
                "name": "Xbox One",
                "capacities": [(500, 362), (1000, 780)],
            },
            {
                "name": "Xbox One S",
                "capacities": [(500, 362), (1000, 780)],
            },
            {
                "name": "Xbox One X",
                "capacities": [(1000, 780)],
            },
            {
                "name": "Xbox Series S",
                "capacities": [(512, 364)],
            },
            {
                "name": "Xbox Series X",
                "capacities": [(1000, 802)],
            },
        ],
    },
}


class Command(BaseCommand):
    help = "Seed console brands, models and capacities"

    def handle(self, *args, **options):
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

                for nominal, usable in model_data["capacities"]:
                    _, cap_created = ConsoleCapacity.objects.get_or_create(
                        console_model=model,
                        nominal_capacity=nominal,
                        defaults={"usable_capacity": usable, "is_active": True},
                    )
                    if cap_created:
                        created_caps += 1
                        self.stdout.write(
                            f"    ✓ Capacity: {nominal}GB (usable: {usable}GB)"
                        )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Done! Brands: {created_brands}, Models: {created_models}, Capacities: {created_caps}"
            )
        )