import os
import redis
import ast
from mongoengine import *

from data_processing.product_sorter import ProductSorter

if __name__ == "__main__":
	for env_var in ["CRAWLER_OUTPUT_QUEUE", "BROKER_PRODUCTS_OUTPUT_QUEUE"
					"MONGODB_NAME",
					"REDIS_HOST", "REDIS_PORT", "MONGODB_HOST", "MONGODB_PORT"]:
		assert env_var in os.environ, "%s environment variable should be defined." % env_var

	print("connecting to redis...")
	redis_c = redis.Redis(host=os.environ["REDIS_HOST"], port=os.environ["REDIS_PORT"], charset="utf-8")
	print("connected to redis")

	print("creating connection to mongodb")
	connect(os.environ["MONGODB_NAME"], host=os.environ["MONGODB_HOST"], port=int(os.environ["MONGODB_PORT"]))
	print("connection to mongodb created")

	# setting up redis to wait for messages
	redis_queues = []
	for queue in ["CRAWLER_OUTPUT_QUEUE"]:
		redis_queues.append(os.environ[queue])

	# for debugging purpose only
	redis_c.flushall()

	sorter = ProductSorter("memes")

	while True:
		task = redis_c.blpop(redis_queues, 0)
		received_queue = task[0].decode("utf-8")
		received_input = task[1].decode("utf-8")
		print("received message from %s" % received_queue)

		try:
			received_input = ast.literal_eval(received_input)
			if received_queue == os.environ["CRAWLER_OUTPUT_QUEUE"]:
				print("received {}".format(received_input))
				better = sorter.compare(received_input["product_id"], received_input["shop"])
				# if better:
				# 	send the result to the client

				# process_product(received_input)
		except SyntaxError:
			print("Data from %s not a valid python dict, discarding:\n %s" % (received_queue, received_input))
