import random
import string
import unittest
from unittest.mock import patch

from hashmap import HashMap


def random_string():
    return ''.join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(5)
    )


class BaseHashMapSetup(object):
    def setUp(self):
        self.hash_map = HashMap()
        self.key_1, self.value_1 = 'key_1', 'value_1'
        self.key_2, self.value_2 = 'key_2', 'value_2'
        self.key_3, self.value_3 = 'key_3', 'value_3'


class HashMapGetItemTests(BaseHashMapSetup, unittest.TestCase):

    def setUp(self):
        super().setUp()

    def test_first_key_error(self):
        # test first key error
        self.assertRaises(KeyError, self.hash_map.__getitem__, 'bad key')

    @patch('hashmap.HashMap._hash_function')
    def test_get_item_from_collision_list(self, _hash_function):
        _hash_function.return_value = 0
        self.hash_map['key'] = 'value'
        self.hash_map['key_2'] = 'value_2'
        self.assertEqual(self.hash_map['key_2'], 'value_2')

    @patch('hashmap.HashMap._hash_function')
    def test_second_key_error_from_collision_list(self, _hash_function):
        _hash_function.return_value = 0
        self.hash_map[self.key_1] = self.value_1
        self.hash_map[self.key_2] = self.value_2
        self.assertRaises(KeyError, self.hash_map.__getitem__, self.key_3)

    def test_item_return_from_container(self):
        self.hash_map[self.key_1] = self.value_1
        self.assertEqual(self.hash_map[self.key_1], self.value_1)

    @patch('hashmap.HashMap._hash_function')
    def test_third_key_error(self, _hash_function):
        # Test third KeyError. Two keys have the same hash. Test getitem with
        # key that is not present.
        _hash_function.return_value = 0
        self.hash_map[self.key_1] = self.value_1
        self.assertRaises(KeyError, self.hash_map.__getitem__, self.key_2)


class InsertIntoBucketArrayTests(BaseHashMapSetup, unittest.TestCase):

    def test_basic_insert(self):
        self.hash_map[self.key_1] = self.value_1
        self.assertEqual(self.hash_map[self.key_1], self.value_1)

    @patch('hashmap.HashMap._hash_function')
    def test_collision_inserting(self, _hash_function):
        _hash_function.return_value = 0
        self.hash_map[self.key_1] = self.value_1
        self.hash_map[self.key_2] = self.value_2
        self.hash_map[self.key_3] = self.value_3
        self.assertEqual(self.hash_map[self.key_1], self.value_1)
        self.assertEqual(self.hash_map[self.key_2], self.value_2)
        self.assertEqual(self.hash_map[self.key_3], self.value_3)
        self.assertEqual(len(self.hash_map._bucket_array[0]), 3)

    @patch('hashmap.HashMap._hash_function')
    def test_collision_list_resassigning(self, _hash_function):
        _hash_function.return_value = 0
        self.hash_map[self.key_1] = self.value_1
        self.hash_map[self.key_2] = self.value_2
        self.hash_map[self.key_2] = self.value_3
        self.assertEqual(len(self.hash_map._bucket_array[0]), 2)
        self.assertEqual(self.hash_map[self.key_2], self.value_3)

    @patch('hashmap.HashMap._hash_function')
    def test_basic_bucket_tuple_reassignment(self, _hash_function):
        _hash_function.return_value = 0
        self.hash_map[self.key_1] = self.value_1
        self.hash_map[self.key_1] = self.value_2
        self.assertEqual(self.hash_map[self.key_1], self.value_2)


class HashMapDeleteTests(BaseHashMapSetup, unittest.TestCase):
    def test_first_key_error(self):
        self.assertRaises(
            KeyError, self.hash_map.__delitem__, self.key_1
        )

    @patch('hashmap.HashMap._hash_function')
    def test_delete_item_in_collision_list(self, _hash_function):
        _hash_function.return_value = 0
        self.hash_map[self.key_1] = self.value_1
        self.hash_map[self.key_2] = self.value_2
        del self.hash_map[self.key_2]
        self.assertRaises(KeyError, self.hash_map.__getitem__, self.key_2)

    @patch('hashmap.HashMap._hash_function')
    def test_second_key_error_raise_through_collision_list(self,
                                                           _hash_function):
        _hash_function.return_value = 0
        self.hash_map[self.key_1] = self.value_1
        self.hash_map[self.key_2] = self.value_2
        self.assertRaises(KeyError, self.hash_map.__delitem__, self.key_3)

    def test_deletion_of_item_from_bucket(self):
        self.hash_map[self.key_1] = self.key_2
        del self.hash_map[self.key_1]
        self.assertRaises(KeyError, self.hash_map.__delitem__, self.key_1)
        self.assertEqual(self.hash_map._item_count, 0)

    @patch('hashmap.HashMap._hash_function')
    def test_last_key_error_raise(self, _hash_function):
        _hash_function.return_value = 0
        self.hash_map[self.key_1] = self.key_2
        self.assertRaises(KeyError, self.hash_map.__delitem__, self.key_2)


class HashMapTests(BaseHashMapSetup, unittest.TestCase):

    def test_init(self):
        hash_map = HashMap()
        self.assertEqual(len(hash_map._bucket_array), 10)

        hash_map = HashMap(('key', 'value'))
        self.assertEqual(len(hash_map._bucket_array), 10)

        hash_map = HashMap([
            (self.key_1, self.value_1),
            (self.key_2, self.value_2)
        ])
        self.assertEqual(len(hash_map._bucket_array), 10)
        self.assertRaises(TypeError, HashMap, 'string')

    def test_len(self):
        self.assertEqual(len(self.hash_map), 0)

        self.hash_map[self.key_1] = self.key_2
        self.assertEqual(len(self.hash_map), 1)

        del self.hash_map[self.key_1]
        self.assertEqual(len(self.hash_map), 0)

    def test_doubling(self):
        # Add 7 items
        for i in range(7):
            self.hash_map[i] = random_string()

        # Doubling occurs on 8th item (> 7/10)
        self.assertEqual(len(self.hash_map._bucket_array), 10)

        self.hash_map[8] = random_string()
        self.assertEqual(len(self.hash_map._bucket_array), 20)

        # Next doubling on 15th item
        for i in range(9, 16):
            self.hash_map[i] = random_string()
        self.assertEqual(len(self.hash_map._bucket_array), 40)

    def test_halving(self):
        # add 8 items
        for i in range(8):
            self.hash_map[i] = random_string()
        self.assertEqual(len(self.hash_map._bucket_array), 20)

        # Minimum density is 2/10. We have 8 items / in a 20 len array.
        # Remove 5 items to reach 3 items.
        for i in range(5):
            del self.hash_map[i]
        self.assertEqual(len(self.hash_map._bucket_array), 10)

    @patch('hashmap.HashMap._hash_function')
    def test_switch_bucket_array(self, _hash_function):
        # Test that includes doubling scenario where the array to double
        # has a collision list
        _hash_function.return_value = 0

        for i in range(8):
            self.hash_map[i] = random_string()

        # Make sure all the items are in the new array
        for i in range(8):
            self.assertTrue(i in self.hash_map)

    def test_contains(self):
        self.assertFalse(self.key_1 in self.hash_map)

    def test_pop(self):
        self.hash_map[self.key_1] = self.value_1
        self.assertEqual(self.hash_map.pop(self.key_1), self.value_1)
        self.assertEqual(len(self.hash_map), 0)

    def test_string(self):
        self.hash_map[self.key_1] = self.value_1
        self.assertIn("('key_1', 'value_1')", str(self.hash_map))


if __name__ == '__main__':
    unittest.main()
