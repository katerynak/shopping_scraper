from django.shortcuts import render
import os
import redis
import re
import string

from .forms import ShoppingListForm

# checking for the environment vars
for var_name in ["CRAWLER_PRODUCTS_INPUT_QUEUE", "BROKER_PRODUCTS_OUTPUT_QUEUE", "REDIS_HOST", "REDIS_PORT"]:
    assert var_name in os.environ, "%s environment variable is missing." % var_name

print("connecting to redis")
redis_connection = redis.Redis(host=os.environ["REDIS_HOST"], port=os.environ["REDIS_PORT"])
print("connected to redis")


def index(request):
    """
    the home page, containing the products input form
    """
    form = ShoppingListForm()
    return render(request, 'shopping/home.html', {'form': form})


def results(request):
    """
    displaying the crawler best results
    """
    form = ShoppingListForm()
    if request.method == "POST":
        form = ShoppingListForm(request.POST)
        if form.is_valid():
            # parse products
            products = re.sub('[' + string.punctuation + ']', '', form.data["shopping_list"]).split()
            if len(products) > 0:
                # send the received input to redis
                for product in products:
                    redis_connection.lpush(os.environ["CRAWLER_PRODUCTS_INPUT_QUEUE"], product)
    context = {'form': form}
    return render(request, 'shopping/search_results.html', context)