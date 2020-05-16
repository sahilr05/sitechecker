from django.conf import settings
import redis

class RedisManager:
    """Simple Manager for Redis Backend"""

    def __init__(self, name):
        """The default connection parameters are: host='localhost', port=6379, connection=0"""
        # host = settings.REDIS_HOST_NAME
        # port = settings.REDIS_PORT
        self.connection = redis.StrictRedis(host="localhost", port = 6379, db=0)
        # host = "localhost"
        # port = 6379

        # self.connection = redis.StrictRedis(host, port, decode_responses=True)
        self.key = '%s' % (name)

    def qsize(self):
        """Return the approximate size of the queue."""
        return self.connection.llen(self.key)

    def empty(self):
        """Return True if the queue is empty, False otherwise."""
        return self.qsize() == 0

    def push_back(self, item):
        """Put item into the queue."""
        self.connection.rpush(self.key, item)

    def push_front(self, item):
        """Put item into the queue."""
        self.connection.lpush(self.key, item)

    def pop_left(self):
        popped = self.connection.lpop(self.key)
        return popped

    def pop_right(self):
        popped = self.connection.rpop(self.key)
        return popped

    def get(self, block=True, timeout=None):
        """Remove and return an item from the queue.
        If optional args block is true and timeout is None (the default), block
        if necessary until an item is available."""
        # if block:
        #     item = self.connection.blpop(self.key, timeout=timeout)
        # else:
        #     item = self.connection.lpop(self.key)
        # if item:
        #     item = item[1]
        # return item
        # self.val =
        return  self.connection.get(self.key)

    def get_nowait(self):
        """Equivalent to get(False)."""
        return self.get(False)

    def set_value(self, item, *ttl):
        self.connection.set(self.key, item)

    def delete_key(self):
        self.connection.delete(self.key)

    def get_list(self):
        return self.connection.lrange(self.key, 0, (self.qsize() + 1))

    def get_value(self):
        return self.connection.get(self.key)
