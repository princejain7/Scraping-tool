import redis


class Cache:
    def __init__(self, host='localhost', port=6379):
        self.client = redis.Redis(host=host, port=port)

    def save(self, product):
        self.client.set(product['product_title'], product['product_price'])

    def load(self, product_title: str) -> float:
        return float(self.client.get(product_title) or 0)
