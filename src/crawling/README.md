Products crawling from the supermarket websites. 

For each search term and supermarket a spider instance is created, 
it makes the requests and parses the information received.

Module organization:
  - `main.py`: the main loop receiving and sending messages to/from `redis`
  - `items.py`: definition of items to crawle
  - `pipelines.py`: contains classes of all the item processing pipelines
  - `spiders/`: contains spider classes for each supermarket

TODO:
  - [X] AH spider
  - [X] Coop spider
  - [ ] Jumbo spider
  - [X] Insert the results into db
  - [X] Send new items to broker
  - [ ] Make a 
  [pool of user agents](https://developers.whatismybrowser.com/useragents/explore/operating_system_name/linux/) 
  to be rotated. Additional best practices: [font1](https://www.scrapehero.com/how-to-fake-and-rotate-user-agents-using-python-3/),
  [font2](https://docs.scrapy.org/en/latest/topics/practices.html).
