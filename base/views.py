from django.shortcuts import render
from .models import product_collection

def home(request):
    # MongoDB aggregation pipeline to calculate sentiment counts and product info
    pipeline = [
        {
            "$group": {
                "_id": "$product_id",  # Group by product_id (unique product identifier)
                "product_title": {"$first": "$product_title"},  # Get the product title
                "product_image": {"$first": "$product_images.large"},  # Get the large product images
                "category": {"$first": "$category"},  # Get the category
                "average_rating": {"$first": "$product_average_rating"},  # Get the average rating
                "store": {"$first": "$store"},  # Get the store
                "positive_reviews": {
                    "$sum": {"$cond": [{"$eq": ["$Sentiment", "positive"]}, 1, 0]}
                },
                "neutral_reviews": {
                    "$sum": {"$cond": [{"$eq": ["$Sentiment", "neutral"]}, 1, 0]}
                },
                "negative_reviews": {
                    "$sum": {"$cond": [{"$eq": ["$Sentiment", "negative"]}, 1, 0]}
                },
            }
        },
        {
            "$project": {
                "_id": 0,  # Exclude the MongoDB `_id` field
                "product_id": "$_id",  # Rename `_id` to `product_id`
                "product_title": 1,
                "product_image": 1,
                "category": 1,
                "average_rating": 1,
                "store": 1,
                "positive_reviews": 1,
                "neutral_reviews": 1,
                "negative_reviews": 1,
            }
        }
    ]

    aggregated_products = list(product_collection.aggregate(pipeline))
    return render(request, 'base/home.html', {"products": aggregated_products})


def product_detail(request, product_id):
    # Retrieve product details and reviews from MongoDB
    product = product_collection.find_one({"product_id": product_id}, {"_id": 0})
    if not product:
        return render(request, 'base/404.html', status=404)  # Optional: handle not found

    # Retrieve the reviews for the product
    reviews = list(product_collection.find(
        {"product_id": product_id},
        {"_id": 0, "review_title": 1, "review_text": 1, "Sentiment": 1}
    ))

    return render(request, 'base/product_detail.html', {"product": product, "reviews": reviews})



def getAllProducts(request):
    products=product_collection.find()
    return(products)