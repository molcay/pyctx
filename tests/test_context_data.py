import json
from unittest import TestCase

from pyctx.context_data import ContextData


class TestContextData(TestCase):
    def setUp(self):
        self.wanted_dict = {
            'a': 3,
            'e/b.c/d': True,
            'e/b.c/e': 1,
            'b/a': {'c': 6, 'pi': 3.14},
            'b/a/c': 'value for c of a of b'
        }
        self.wanted_dict_flat = {
            'a': 3,
            'e': {
                'b.c': {
                    'd': True,
                    'e': 1
                }
            },
            'b': {
                'a': {
                    'c': 'value for c of a of b',
                    'pi': 3.14
                }
            }
        }
        self.cd = ContextData()
        self.cd.update({'a': 3})
        self.cd.update({'e/b.c/d': True})
        self.cd.update({'e/b.c/e': 1})
        self.cd.update({'b/a': {'c': 6, 'pi': 3.14}})
        self.cd.update({'b/a/c': 'value for c of a of b'})

    def test_has_correct_types(self):
        self.assertTrue(isinstance(self.cd, dict))
        self.assertTrue(isinstance(self.cd, ContextData))

    def test_update_is_working(self):
        self.assertDictEqual(self.cd, self.wanted_dict)
        self.assertNotEqual(self.cd, {})

    def test_flat_method(self):
        self.assertDictEqual(self.cd.flat(), self.wanted_dict_flat)
        self.assertEqual(json.dumps(self.cd.flat()), json.dumps(self.wanted_dict_flat))

    def test_flat_method_with_raw_data(self):
        cd = ContextData()
        cd.update({
            "x": {
                "w": 5,
            },
            "x/y": {
                "a": 3,
            },
            "x/y/z": 5,
            "x/t/w/b": 6,
            "x/t/w": {
                "a": 7,
            },
        })
        print(json.dumps(cd.flat()))
