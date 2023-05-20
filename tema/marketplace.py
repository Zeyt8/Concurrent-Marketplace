"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Lock
import time
from typing import Dict, List, Tuple
import logging
import logging.handlers
import unittest

from tema.product import Product

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """

    queue_size_per_producer: int
    cart_id: int = 0
    producer_id: int = 0

    cart_id_lock: Lock = Lock()
    producer_id_lock: Lock = Lock()

    # the products that are available in the marketplace
    # the key is the producer id and the value is a list of products
    products: Dict[int, List[Product]] = {}
    # the limits for each producer
    # the key is the producer id and the value is the current number of products
    product_limits: Dict[int, int] = {}
    # carts and their contents
    # the key is the cart id and the value is a list of tuples (product, producer id)
    carts: Dict[int, List[Tuple[Product, int]]] = {}

    reserve_lock: Lock = Lock()

    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.queue_size_per_producer = queue_size_per_producer

        # setup logging
        log_file = 'marketplace.log'
        max_size = 100000
        backup_count = 5
        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_size, backupCount=backup_count
            )

        formatter = logging.Formatter(
            '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
            datefmt='%H:%M:%S'
            )
        formatter.converter = time.gmtime
        handler.setFormatter(formatter)

        handler.setLevel(logging.DEBUG)

        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.DEBUG)

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        logging.info("Entered register_producer")
        # lock so that only one producer can register at a time
        # producer id is incremental
        with self.producer_id_lock:
            self.producer_id += 1
            self.products[self.producer_id] = []
            self.product_limits[self.producer_id] = 0
            logging.info("Exited register_producer with producer_id %d", self.producer_id)
            return self.producer_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        logging.info("Entered publish with producer_id %d and product %s", producer_id, product)
        # if the list is full, return False
        if self.product_limits[producer_id] >= self.queue_size_per_producer:
            logging.info("Exited publish because queue is full")
            return False
        # add the product to the list and increment the current number of products for the producer
        self.products[producer_id].append(product)
        self.product_limits[producer_id] += 1
        logging.info("Exited publish and added product to queue")
        return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        logging.info("Entered new_cart")
        # lock so that only one cart can be created at a time
        # cart id is incremental
        with self.cart_id_lock:
            self.cart_id += 1
            self.carts[self.cart_id] = []
            logging.info("Exited new_cart with cart_id %d", self.cart_id)
            return self.cart_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        logging.info("Entered add_to_cart with cart_id %d and product %s", cart_id, product)
        # lock so that one product can be added to a single cart at a time
        with self.reserve_lock:
            for prod_id, prod in self.products.items():
                if product in prod:
                    self.carts[cart_id].append((product, prod_id))
                    prod.remove(product)
                    logging.info("Exited add_to_cart and added product to cart")
                    return True
            logging.info("Exited add_to_cart because product is not available")
            return False


    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        logging.info("Entered remove_from_cart with cart_id %d and product %s", cart_id, product)
        (prod, prod_id) = next(
            ((prod, prod_id) for (prod, prod_id) in self.carts[cart_id] if prod == product),
            (None, None)
            )
        if prod is None:
            logging.info("Exited remove_from_cart because product is not in cart")
            return
        self.products[prod_id].append(prod)
        self.carts[cart_id].remove((prod, prod_id))
        logging.info("Exited remove_from_cart and removed product from cart")

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        logging.info("Entered place_order with cart_id %d", cart_id)
        for _, prod_id in self.carts[cart_id]:
            self.product_limits[prod_id] -= 1
        logging.info("Exited place_order and returned products from cart")
        return [prod for prod, _ in self.carts[cart_id]]


class TestMarketplace(unittest.TestCase):
    """
    Class that tests the Marketplace class
    """

    def setUp(self):
        self.marketplace = Marketplace(10)

    def test_register_producer(self):
        """
        Tests the register_producer method
        """
        self.assertEqual(self.marketplace.register_producer(), 1)
        self.assertEqual(self.marketplace.register_producer(), 2)

    def test_publish(self):
        """
        Tests the publish method
        """
        producer_id = self.marketplace.register_producer()
        product = Product("product1", 1)
        for _ in range(0, 10):
            self.assertTrue(self.marketplace.publish(producer_id, product))
        self.assertFalse(self.marketplace.publish(producer_id, product))

    def test_new_cart(self):
        """
        Tests the new_cart method
        """
        self.assertEqual(self.marketplace.new_cart(), 1)
        self.assertEqual(self.marketplace.new_cart(), 2)

    def test_add_to_cart(self):
        """
        Tests the add_to_cart method
        """
        producer_id = self.marketplace.register_producer()
        cart_id = self.marketplace.new_cart()
        product = Product("product1", 1)
        self.assertFalse(self.marketplace.add_to_cart(cart_id, product))
        self.marketplace.publish(producer_id, product)
        self.assertTrue(self.marketplace.add_to_cart(cart_id, product))
        self.assertFalse(self.marketplace.add_to_cart(cart_id, product))

    def test_remove_from_cart(self):
        """
        Tests the remove_from_cart method
        """
        cart_id = self.marketplace.new_cart()
        product = Product("product1", 1)
        self.marketplace.publish(1, product)
        self.marketplace.add_to_cart(cart_id, product)
        self.marketplace.remove_from_cart(cart_id, product)
        self.assertTrue(self.marketplace.add_to_cart(cart_id, product))

    def test_place_order(self):
        """
        Tests the place_order method
        """
        cart_id = self.marketplace.new_cart()
        product = Product("product1", 1)
        self.marketplace.publish(1, product)
        product2 = Product("product2", 2)
        self.marketplace.publish(1, product2)
        self.marketplace.add_to_cart(cart_id, product)
        self.marketplace.add_to_cart(cart_id, product2)
        self.assertEqual(self.marketplace.place_order(cart_id), [product, product2])
