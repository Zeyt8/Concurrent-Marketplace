"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
from typing import List
from time import sleep, time

from tema.marketplace import Marketplace


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    name: str
    carts: List[List]
    marketplace: Marketplace
    retry_wait_time: time

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        super().__init__(**kwargs)
        self.name = kwargs["name"]
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time

    def run(self):
        """
        Thread run method.

        Execute the orders in the given list.
        """
        for cart in self.carts:
            # for each cart, acquire a new cart id
            cart_id = self.marketplace.new_cart()
            for operation in cart:
                # extract the operation type, product and quantity
                op_type = operation["type"]
                product = operation["product"]
                quantity = operation["quantity"]
                # if it's an add operation, repeat the operation by the quantity specified
                # if we couldn't add the product to the cart, wait for the retry time
                if op_type == "add":
                    for _ in range(quantity):
                        while not self.marketplace.add_to_cart(cart_id, product):
                            sleep(self.retry_wait_time)
                # if it's a remove operation, just repeat the operation by the quantity specified
                elif op_type == "remove":
                    for _ in range(quantity):
                        self.marketplace.remove_from_cart(cart_id, product)
            # place the order and print the bought products for this cart
            bought = self.marketplace.place_order(cart_id)
            for product in bought:
                print(f"{self.name} bought {product}")
