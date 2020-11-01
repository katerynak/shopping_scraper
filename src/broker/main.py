"""
A broker that receives messages with new objects from crawler, sorts them if
needed, and sends them to the django client.
"""
import ast
import os

import mongoengine as mongo
import redis

import data_sorting.product_sorter as product_sorter

# Environment variables that should be set.
ENVIRONMENT_VARS = [
    "CRAWLER_OUTPUT_QUEUE",
    "BROKER_PRODUCTS_OUTPUT_QUEUE",
    "MONGODB_NAME",
    "REDIS_HOST",
    "REDIS_PORT",
    "MONGODB_HOST",
    "MONGODB_PORT",
]

if __name__ == "__main__":
    # Check if the environment variables are defined.
    for env_var in ENVIRONMENT_VARS:
        assert env_var in os.environ, (
            "%s environment variable should be defined." % env_var
        )
    # Connect to the redis queue.
    print("connecting to redis...")
    redis_c = redis.Redis(
        host=os.environ["REDIS_HOST"], port=os.environ["REDIS_PORT"], charset="utf-8"
    )
    print("connected to redis")
    # Connect to the database.
    print("creating connection to mongodb")
    mongo.connect(
        os.environ["MONGODB_NAME"],
        host=os.environ["MONGODB_HOST"],
        port=int(os.environ["MONGODB_PORT"]),
    )
    print("connection to mongodb created")
    # Set up redis to wait for messages.
    redis_queues = []
    for queue in ["CRAWLER_OUTPUT_QUEUE"]:
        redis_queues.append(os.environ[queue])
    # TODO: remove this when no more recessary.
    # For debugging purpose only, clear the redis cache.
    redis_c.flushall()
    # Initialize product sorter.
    sorter = product_sorter.ProductSorter("memes")
    # Repeat this cycle.
    while True:
        # Check for a new message from the redis queue.
        task = redis_c.blpop(redis_queues, 0)
        received_queue = task[0].decode("utf-8")
        received_input = task[1].decode("utf-8")
        print("Received message from %s" % received_queue)
        # Parse the received input.
        try:
            received_input = ast.literal_eval(received_input)
            if received_queue == os.environ["CRAWLER_OUTPUT_QUEUE"]:
                print("Received {}".format(received_input))
            # Send the received input info to the client.
            # TODO: send to the client.
        except SyntaxError:
            print(
                f"Data from {received_queue} not a valid python dict, "
                f"discarding:\n {received_input}"
            )
