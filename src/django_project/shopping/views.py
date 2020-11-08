from django.shortcuts import render
import os
import redis
import re
import string

from .forms import ShoppingListForm

# Checking for the environment vars.
for var_name in [
    "CRAWLER_PRODUCTS_INPUT_QUEUE",
    "BROKER_PRODUCTS_OUTPUT_QUEUE",
    "REDIS_HOST",
    "REDIS_PORT",
]:
    assert var_name in os.environ, "%s environment variable is missing." % var_name

print("connecting to redis")
redis_connection = redis.Redis(
    host=os.environ["REDIS_HOST"], port=os.environ["REDIS_PORT"]
)
print("connected to redis")


def index(request):
    """
    The home page, containing the products input form.
    """
    form = ShoppingListForm()
    return render(request, "shopping/home.html", {"form": form})


def results(request):
    """
    Display the crawler best results.
    """
    form = ShoppingListForm()
    if request.method == "POST":
        form = ShoppingListForm(request.POST)
        if form.is_valid():
            # Parse products.
            products = re.sub(
                "[" + string.punctuation + "]", "", form.data["shopping_list"]
            ).split()
            if len(products) > 0:
                # Send the received input to redis.
                for product in products:
                    redis_connection.lpush(
                        os.environ["CRAWLER_PRODUCTS_INPUT_QUEUE"], product
                    )
    context = {"form": form}
    # TODO: add a waitinig loop to update results once they arrive.
    return render(request, "shopping/search_results.html", context)
