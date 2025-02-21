import json

# Path to the JSON file
JSON_FILE_PATH = "/home/ts/Desktop/Ashish SIngh (ASS)/email_services/mailer/amazon.json"

def search_products(query=None, min_price=None, max_price=None, min_rating=None):
    """
    Search for products inside the JSON file based on the given criteria.
    """
    try:
        # Load JSON data from file
        with open(JSON_FILE_PATH, "r", encoding="utf-8") as file:
            products = json.load(file)

        # Convert single product entries into a list
        if isinstance(products, dict):
            products = [products]

        filtered_products = []

        for product in products:
            # Ensure product_name is extracted properly
            name_data = product.get("product_name", [""])
            name = name_data[0].lower() if isinstance(name_data, list) else name_data.lower()

            # Handle missing price values safely
            price_text = product.get("product_price", ["₹0"])
            price_text = price_text[0] if isinstance(price_text, list) and price_text else "₹0"

            try:
                price = float(price_text.replace("₹", "").replace(",", ""))
            except ValueError:
                price = 0.0

            # Handle missing rating values safely
            rating_text = product.get("product_rating", ["0 out of 5 stars"])
            rating_text = rating_text[0] if isinstance(rating_text, list) and rating_text else "0 out of 5 stars"

            try:
                rating = float(rating_text.split()[0]) if isinstance(rating_text, str) else 0.0
            except ValueError:
                rating = 0.0

            # Apply filters
            if query and query.lower() not in name:
                continue
            
            if min_price and price < float(min_price):
                continue
            
            if max_price and price > float(max_price):
                continue
            
            if min_rating and rating < float(min_rating):
                continue

            filtered_products.append(product)

        print(f"Filtered Products Count: {len(filtered_products)}")

        return filtered_products

    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}
