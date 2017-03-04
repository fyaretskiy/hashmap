class HashMap(object):
    """
    Instantiation:
    Instantiate without args, with tuple or list of tuples:
    hash_map = HashMap()
    hash_map = HashMap(('key', 'value'))
    hash_map = HashMap(
        [('key', 'value'), ('key_2', 'value_2')]
    )

    Operations:
    hash_map[key] = value
    del hash_map[key]
    len(hash_map)
    hash_map.pop(key)
    key in hash_map

    _bucket_array variable representation, sequence of NoneType, lists,
    and tuples:
    [None, None, (k1, v1), (k2, v2), [(k3, v3), (k4, v4)]]
    """
    _MAX_DENSITY = 7 / 10
    _MIN_DENSITY = 2 / 10

    def __init__(self, arg=None):
        """
        :param args: (X,Y) or [(X,Y), (A,b)] tuple, or list of tuples where
        (key, value)
        """
        if arg:
            if isinstance(arg, tuple):
                key_value_pairs = [arg]
            elif isinstance(arg, list):
                key_value_pairs = arg
            else:
                raise TypeError('HashMap accepts only tuples or lists')
        else:
            key_value_pairs = []

        self._item_count = len(key_value_pairs)

        initial_size = max(self._item_count * 2, 10)
        self._bucket_array = [None] * initial_size

        for key, value in key_value_pairs:
            self[key] = value

    def __getitem__(self, key_requested):
        """
        :param key_requested:
        :return: value
        """
        bucket_item = self._get_bucket(key_requested)

        if not bucket_item:
            raise KeyError('{}'.format(key_requested))

        elif isinstance(bucket_item, list):
            for key_value in bucket_item:
                if key_value[0] == key_requested:
                    return key_value[1]

            # if key != key_request and hash(key) == hash(key_requested)
            raise KeyError('{}'.format(key_requested))

        else:
            if bucket_item[0] == key_requested:
                return bucket_item[1]
            else:
                raise KeyError('{}'.format(key_requested))

    def _insert_in_bucket_array(self, key, value, bucket_array,
                                increment_count=True):
        """
        :param bucket_array: The list object the key value pair is being
         inserted into.
        :param increment_count: Boolean, False when func called for doubling or
         halving the bucket array.
        """
        index = self._hash_function(key, bucket_length=len(bucket_array))
        bucket_item = self._get_bucket(key, bucket_array=bucket_array)
        new_entry = False

        # Bucket is empty
        if not bucket_item:
            bucket_array[index] = (key, value)
            new_entry = True

        # Existing Collision list
        elif isinstance(bucket_item, list):

            # check if key exists in collision list
            reassignment = False
            existing_value = None
            for key_value in bucket_item:
                if key_value[0] == key:
                    reassignment = True
                    existing_value = key_value[1]

            if reassignment:
                bucket_item.remove((key, existing_value))
                bucket_item.append((key, value))

            if not reassignment:
                bucket_item.append((key, value))
                new_entry = True

        # Reassignment on tuple
        elif isinstance(bucket_item, tuple) and bucket_item[0] == key:
            bucket_array[index] = (key, value)

        # First collision
        else:
            new_collision_list = [
                bucket_item,
                (key, value)]

            bucket_array[index] = new_collision_list
            new_entry = True

        if new_entry and increment_count:
            self._increment_count()

    def __setitem__(self, key, value):
        self._insert_in_bucket_array(key, value, self._bucket_array)

    def __delitem__(self, key):
        bucket_item = self._get_bucket(key)

        if not bucket_item:
            raise KeyError('{}'.format(key))

        # Iterate over items and remove tuple from the list. If the length of
        # the list is 1, convert collision list back to a tuple.
        elif isinstance(bucket_item, list):
            found = False
            value = None
            for key_value in bucket_item:
                if key == key_value[0]:
                    found = True
                    value = key_value[1]

            if found:
                bucket_item.remove((key, value))
                self._decrement_count()
            else:
                raise KeyError('{}'.format(key))

            if len(bucket_item) == 1:
                index = self._hash_function(key, len(self._bucket_array))
                self._bucket_array[index] = (bucket_item[0][0],
                                             bucket_item[0][1])

        # Bucket is tuple
        else:

            # Found the correct key, remove reference to tuple.
            if key == bucket_item[0]:
                index = self._hash_function(key, len(self._bucket_array))
                self._bucket_array[index] = None
                self._decrement_count()

            # Tuple key stored doesn't match the key arg
            else:
                raise KeyError('{}'.format(key))

    def __len__(self):
        return self._item_count

    def _get_bucket(self, key, bucket_array=None):

        if not bucket_array:
            bucket_array = self._bucket_array

        index = self._hash_function(key, len(bucket_array))
        return bucket_array[index]

    @property
    def population_density(self):
        return self._item_count / len(self._bucket_array)

    def _increment_count(self):
        self._item_count += 1
        if self.population_density > self._MAX_DENSITY:
            self._double()

    def _decrement_count(self):
        self._item_count -= 1

        if self.population_density < self._MIN_DENSITY \
                and len(self._bucket_array) > 10:
            self._halve()

    def _double(self):
        new_bucket_array = [None] * len(self._bucket_array) * 2
        self._switch_bucket_array(new_bucket_array)

    def _halve(self):
        new_bucket_array = [None] * (len(self._bucket_array) // 2)
        self._switch_bucket_array(new_bucket_array)

    def _switch_bucket_array(self, new_bucket_array):
        """
        Used in doubling and halving the bucket array.
        """

        # Iterate over self.buckets and place them in new array
        for bucket in self._bucket_array:

            if isinstance(bucket, tuple):
                self._insert_in_bucket_array(bucket[0], bucket[1],
                                             new_bucket_array,
                                             increment_count=False)

            elif isinstance(bucket, list):
                for key_value in bucket:
                    self._insert_in_bucket_array(key_value[0], key_value[1],
                                                 new_bucket_array,
                                                 increment_count=False)

        self._bucket_array = new_bucket_array

    def _hash_function(self, key, bucket_length):
        return hash(key) % bucket_length

    def __contains__(self, item):
        try:
            self.__getitem__(item)
            return True
        except KeyError:
            return False

    def pop(self, key):
        item = self[key]
        del self[key]
        return item

    def __str__(self):
        return str(self._bucket_array)
