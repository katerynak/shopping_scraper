Collects the information from the `redis` queue, receives search requests for a given search term
    and, if there are no recent products in the db for the given term, forwards
    the search term to one of the crawlers.

Module organization:
  - `main.py`: the main loop receiving and sending messages to/from `redis`
  - `data_processing/`: scripts for sorting of the results
