A directory containing definitions of database tables schemas.

Module organization:
  - `Product.py`: definition of `Product` table schema. Here the time invariant
    information of the products will be stored.
  - `ProductPrice.py`: ddefinition of `ProductPrice` table schema. Here the most
    probable to change in time information is stored. Each time it changes, a new
    row in the database is created along with the change date. So in this way
    all the changes in time can be tracked.