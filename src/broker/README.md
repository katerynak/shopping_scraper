Collects the information from the `redis` queue, sorts the results if needed,
and sends them to the `django` client.

Module organization:
  - `main.py`: the main loop receiving and sending messages to/from `redis`
  - `data_processing/`: scripts for sorting of the results

TODO: 
- [X] Receive the results
- [ ] Send the results to client
- [ ] Results ranking