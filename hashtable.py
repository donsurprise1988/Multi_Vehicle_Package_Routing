# Hash Table Class

class HashTable:

    # HashTable Initialization:
    # The HashTable class is defined, and it takes a single argument size when instantiated.
    # The size specifies the number of slots or buckets in the hash table.
    # Using a load factor of 0.6 for resizing
    # Each slot in the table can store key-value pairs, but it starts empty.
    # Every time an element is inserted, the hash table checks to see if it needs to be resized
    def __init__(self, size):
        self.size = size
        self.hashmap = [[] for _ in range(0, self.size)]
        self.load_factor = 0.6
        self.count = 0

    # Method to resize hash table based that checks it's own size and rehashes everything if resized
    def _resize(self, new_size):
        old_hashmap = self.hashmap
        self.size = new_size
        self.hashmap = [[] for _ in range(0, self.size)]
        self.count = 0

        for bucket in old_hashmap:
            for key, value in bucket:
                self.set(key, value)  # Rehash all existing elements

    #
    def _check_load_factor(self):
        load_factor = self.count / self.size
        if load_factor > self.load_factor:
            new_size = self.size * 2  # You can adjust the resizing factor as needed
            self._resize(new_size)

    # The _hash method is used to compute the index where a key should be stored.
    # It uses the built-in hash function and takes the modulus of size to ensure the index falls within the valid
    # range of slots.
    def hashing_function(self, key):
        return hash(key) % self.size

    # The set method is used to add or update a key-value pair in the hash table.
    def set(self, key, value):
        hash_key = self.hashing_function(key)
        key_exists = False
        bucket = self.hashmap[hash_key]
        # chaining to handle item collision
        for i, key_value in enumerate(bucket):
            k, v = key_value
            if key == k:
                key_exists = True
                break
        if key_exists:
            # Update the existing key's value
            bucket[i] = ((key, value))
        else:
            # Add a new key-value pair to the bucket
            bucket.append((key, value))
            self.count += 1
            self._check_load_factor()

    # The get method is used to retrieve the value associated with a given key. Raises key error if it doesn't exist
    def get(self, key):
        hash_key = self.hashing_function(key)
        bucket = self.hashmap[hash_key]
        for key_value in bucket:
            k, v = key_value
            if key == k:
                return v

        raise KeyError(f'does not exist {key}')

    # The special __setitem__ method allows setting key-value pairs using square brackets.
    def __setitem__(self, key, value):
        return self.set(key, value)

    # The special __getitem__ method allows getting values using square brackets.
    def __getitem__(self, key):
        return self.get(key)

    # Define items so that it can be used on the __iter__ to iterate through the hashtable data structure
    def items(self):
        all_items = []
        for bucket in self.hashmap:
            for key, value in bucket:
                all_items.append((key, value))
        return all_items

    # Iterate through the key-value pairs using the items() method
    def __iter__(self):
        return iter(self.items())


