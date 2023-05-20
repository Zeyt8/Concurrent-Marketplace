# Marketplace

## Organisation

I used a different approach to the producer consumer problem.

I only used locks, not semaphores. I used a lock for acquiring producer ids, cart ids and for reserving a product. Because carts are separate entities, placing orders or removing items from the carts do not need a lock.

Also, I am tracking products made by each producer in a separate list, so that also doesn't need a lock.

I found this assignment a bit useful in thinking about the producer consumer problem in a different way and to find my own syncronizing solution.

The implementation is only a bit more complicated than the naive approach.

There is 1 problem that might occur if following the given instructions about the producers. If the product lists are all full with product id1 and some consumer is waiting for product id2 to be available, the consumer will wait forever. This happens even if the producers do produce id2, because they won't be able to add to the list, due to it being full.

This could be fixed by the producers not producing products in the order specified in the json, but by prioritizing products missing from the already published products.

## Implementation

All the requirements are implemented. I didn't add any extra features.

I had some difficulties about understanding what the parameters *producer* and *carts* in the constructors were and how to use them. The comments are very vague and aren't describing everything that is needed. I had to look at the tests to understand what they were.

That wasn't hard, but I found using fixed content format lists and dictionaries to be a bit annoying. Instead of having producer orders be represented as ["productId", quantity, wait_time] and consumer orders as {"type": "operation", "prod": "productId", "quantity": quantity}, I would have preferred to have them as classes with corresponding attributes. This would have made the code more readable and easier to understand.

## Used Resources

I used the documentation links given in the assignment. I also looked at the producer consumer problem on ocw on APD class.

## Git

https://github.com/Zeyt8/CSA-Projects/tree/master/assignments/1-marketplace