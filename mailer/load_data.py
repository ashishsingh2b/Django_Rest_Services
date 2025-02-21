import json
from django.core.management.base import BaseCommand
from models import AmazonProduct  # Import your model

class Command(BaseCommand):
    help = "Load Amazon products from amazon.json into the database"

    def handle(self, *args, **kwargs):
        json_file_path = "/home/ts/Desktop/Ashish SIngh (ASS)/email_services/amazon.json"

        # Read JSON file
        with open(json_file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Insert data into the database
        for item in data:
            AmazonProduct.objects.create(
                product_name=item.get("product_name", [""])[0],
                product_price=item.get("product_price", [""])[0],
                product_MRP=item.get("product_MRP", [""])[0],
                product_img=item.get("product_img", [""])[0],
                product_rating=item.get("product_rating", [""])[0],
                total_customer_rating=int(item.get("total_customer_rating", [0])[0]),
                product_page_url=item.get("product_page_url", [""])[0]
            )

        self.stdout.write(self.style.SUCCESS("Successfully loaded Amazon products into the database."))
