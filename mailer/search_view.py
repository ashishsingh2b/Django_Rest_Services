from rest_framework.response import Response
from rest_framework.decorators import api_view
from .search_service import search_products

@api_view(['GET'])
def search_product_view(request):
    """
    API endpoint to search products inside the JSON file.
    """
    query = None
    min_price, max_price = None, None

    # Handling price filters from the 'query' parameter
    query_params = request.GET.getlist("query")  # Get multiple values for 'query'
    
    for param in query_params:
        if "price<" in param:
            max_price = param.split("price<")[1]
        elif "price>" in param:
            min_price = param.split("price>")[1]
        else:
            query = param  # If it's not a price filter, assume it's a search term

    min_rating = request.GET.get("min_rating", None)

    print(f"Query: {query}, Min Price: {min_price}, Max Price: {max_price}, Min Rating: {min_rating}")

    products = search_products(query=query, min_price=min_price, max_price=max_price, min_rating=min_rating)

    return Response({"results": products})
