Shopping web scraper: scrapes products from different Dutch supermarkets, processes
and organizes the results.

A personal project to practise with `scrapy`, `MongoDB`, `Redis`, `Docker` and
`flask`.

## Usage

Shop scraper is delivered with `docker` and good to go with `docker-compose`:
```bash
> docker-compose up
```

If you need to rebuild old images, start the app by running the script:
```bash
> ./run.sh
```

## Interface

When the app is up and running, you can open the webapp from browser, 
from `0.0.0.0:5000`.

There you will find the search page:

![img.png](figures/search_page.png)

Digit the search term and press `Search` to see the results page:

![img_1.png](figures/results_page.png)

Note: digit the search term in Dutch since the supermarkets of interest are from
the Netherlands.
Here you can see the results from different supermarkets in a single table,
with product name, shop price, unit price and unit measure, image and
a link to the shop.

All the columns are sortable (except the 'image' column), and there is a search
bar where you can search for a particular product.

## Architecture

The project is composed of different units, each of them is a docker container
(except for the client, which is served by the flask backend).
The communication is done by using message-passing through `redis` over docker
networks.

![](figures/architecture_diagram.svg)

## Repo organization

  - `client`: `flask` client and backend
  - `broker`: a broker which directs requests traffic from the client back-end
    to crawlers
  - `crawling`: crawling of products from web shops, their processing and
    insertion into the db
  - `data_collections`: database schema definition
  - `data_processing`: tools to make products comparisons, e.g., to check
    if two products are the same, or to normalize product measure units and
    quantities
