"""
This module represents the Producer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
from time import sleep, time
from typing import List

from tema.marketplace import Marketplace


class Producer(Thread):
    """
    Class that represents a producer.
    """

    products: List[List]
    marketplace: Marketplace
    republish_wait_time: time

    def __init__(self, products, marketplace, republish_wait_time, **kwargs):
        """
        Constructor.

        @type products: List()
        @param products: a list of products that the producer will produce

        @type marketplace: Marketplace
        @param marketplace: a reference to the marketplace

        @type republish_wait_time: Time
        @param republish_wait_time: the number of seconds that a producer must
        wait until the marketplace becomes available

        @type kwargs:
        @param kwargs: other arguments that are passed to the Thread's __init__()
        """
        super().__init__(**kwargs)
        self.products = products
        self.marketplace = marketplace
        self.republish_wait_time = republish_wait_time

    def run(self):
        """
        Thread run method.

        Publish the products from the given list.
        """
        producer_id = self.marketplace.register_producer()
        # infinitely produce products by iterating through the list of products
        while True:
            for product_info in self.products:
                product = product_info[0]
                product_quantity = product_info[1]
                product_wait = product_info[2]
                # repeat the publishing of the product for the given quantity
                # if the marketplace is full, wait for the given time
                for _ in range(product_quantity):
                    while not self.marketplace.publish(producer_id, product):
                        sleep(self.republish_wait_time)
                    sleep(product_wait)
