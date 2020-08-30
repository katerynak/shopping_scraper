from PIL import Image


class SendToOut(object):
	"""
	Pushes the scraped data to redis queue
	"""

	def process_item(self, item, spider):

		spider.redis_connection.lpush(spider.output_queue, str(dict(item)))
		return item


class LoadImages(object):
	"""
	Loads images in memory to store them in redis
	"""

	def process_item(self, item, spider):
		images_dir = spider.settings.get("IMAGES_STORE")
		if images_dir[-1] != "/":
			images_dir = images_dir + "/"
		im = Image.open(images_dir + item["images"][0]["path"])
		item["image"] = im

		return item


class ValidateItem(object):
	"""
	Checks if an item is a valid item
	"""

	def process_item(self, item, spider):

		# to be implemented
		return item