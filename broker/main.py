"""
A broker that receives messages with new objects from crawler, sorts them if
needed, and sends them to the django client.
"""
import ast
import os
import datetime

import mongoengine as mongo
import mongoengine.queryset.visitor as mongo_visitor
import redis

import data_collections.Product as Product
import data_collections.ProductPrice as ProductPrice


# Environment variables that should be set.
ENVIRONMENT_VARS = [
    "CRAWLER_PRODUCTS_INPUT_QUEUE",
    "BROKER_PRODUCTS_OUTPUT_QUEUE",
    "BROKER_PRODUCTS_INPUT_QUEUE",
    "MONGODB_NAME",
    "REDIS_HOST",
    "REDIS_PORT",
    "MONGODB_HOST",
    "MONGODB_PORT",
]


def wait_for_input():
    """
    Loop waiting for the user input.

    Loop waiting for a message with the user input from the `redis` queue.
    When an input is received, exits the loop and returns the received message.

    :return: the received message from the `redis` queue
    """
    # Flag showing whether the input was found.
    found_input = False
    # Loop until receive a message.
    while not found_input:
        print("Waiting for an input.")
        # Check for a new message from the redis queue.
        task = redis_connection.blpop(redis_queues, 0)
        received_queue = task[0].decode("utf-8")
        received_input = task[1].decode("utf-8")
        print(f"Received message from {received_queue}")
        found_input = True
    return received_input


def present_in_db(search_term, time_delta):
    """
    Checks if a product is present in the database.

    :param search_term: user search term
    :param time_delta: used to decide whether an entry is "old" or not
    :return: True if there are recent entries in the db related to the search
        term, False otherwise
    """
    # Look for product into the db.
    product_prices = ProductPrice.ProductPrice.objects(
        (mongo_visitor.Q(search_term=search_term))
    ).order_by("date")
    if len(product_prices) == 0:
        return False
    last_insertion_datetime = product_prices[0].date
    current_datetime = datetime.datetime.now()
    if current_datetime - last_insertion_datetime > time_delta:
        return False
    return True


if __name__ == "__main__":
    # Check if the environment variables are defined.
    for env_var in ENVIRONMENT_VARS:
        assert env_var in os.environ, (
            "%s environment variable should be defined." % env_var
        )
    # Connect to the redis instance.
    print("Connecting to redis...")
    redis_connection = redis.Redis(
        host=os.environ["REDIS_HOST"], port=os.environ["REDIS_PORT"], charset="utf-8"
    )
    print("Connected to redis.")
    # Connect to the database.
    print("Creating connection to mongodb.")
    mongo.connect(
        os.environ["MONGODB_NAME"],
        host=os.environ["MONGODB_HOST"],
        port=int(os.environ["MONGODB_PORT"]),
    )
    print("Connection to mongodb created.")
    # Set up redis to wait for messages.
    redis_queues = []
    # Listen to the input queue
    for queue in ["BROKER_PRODUCTS_INPUT_QUEUE"]:
        redis_queues.append(os.environ[queue])
    # For debugging purpose only, clear the redis cache.
    redis_connection.flushall()
    # Repeat this cycle.
    while True:
        # Wait for the user input.
        new_search_term = wait_for_input()
        # Check if there are recent entries for the search term.
        crawl = not present_in_db(new_search_term, datetime.timedelta(minutes=15))
        if crawl:
            redis_connection.lpush(
                os.environ["CRAWLER_PRODUCTS_INPUT_QUEUE"], new_search_term
            )
