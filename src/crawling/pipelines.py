class SendToOut(object):
	"""
	A pipeline that pushes the scraped data to redis queue
	"""

	def process_item(self, item, spider):

		spider.redis_connection.lpush(spider.output_queue, str(item))
		return item


