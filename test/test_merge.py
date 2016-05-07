import unittest
import os
import sys

import pprint
pp = pprint.PrettyPrinter(indent=4)

def settings_dict(module, keep=lambda k: k == k.upper()):
    """Returns a dictionary for a module namespace."""
    return {k: v for k, v in module.__dict__.items() if keep(k)}

def dump_settings(header, s):
    settings = s if isinstance(s, dict) else settings_dict(s)
    print('-----------------------------------------------------\n' + 
          header + ':')
    pp.pprint(settings)

def test_merge():
    from settings_resolver import ChainMapTree

    d1 = {'a':1, 'b':2, 'c': {'c1': 1, 'c2': 2}}
    d2 = {'a':3, 'd':4, 'c': {'c2': 4, 'c3': 3}}
    cm = ChainMapTree(d1, d2)
    assert cm['a'] == 1
    assert cm['b'] == 2
    assert cm['d'] == 4
    try:
        print(cm['f'])
    except KeyError:
        pass
    else:
        raise Exception('Did not raise KeyError for missing key')
    assert cm['c']['c1'] == 1
    assert cm['c']['c2'] == 2
    assert cm['c']['c3'] == 3

    assert 'a' in cm  and  'b' in cm  and  'd' in cm
    assert cm.get('a', 10) == 1
    assert cm.get('b', 20) == 2
    assert cm.get('d', 30) == 4
    assert cm.get('f', 40) == 40

    testDicts = [
        {
            'a': 1001,
            'b': {
                'ba': {
                    'baa': 1211
                },
                'bb': 1022,
            },
            'c': 1003,
        },
        {
            'a': 2001,
            'e': {
                'ea': 2051
            }
        },
        {
            'a': 3001,
            'b': {
                'ba': {
                    'baa': 3211,
                    'bab': 3212,
                },
                'bb': 3022
            },
            'd': {
                'da': 3041
            }
        },
    ]
    cmt = ChainMapTree(*testDicts)
    assert cmt['a'] == 1001
    assert cmt['b']['ba']['baa'] == 1211
    assert cmt['b']['ba']['bab'] == 3212
    assert cmt['b']['bb'] == 1022
    assert cmt['c'] == 1003
    assert cmt['d']['da'] == 3041
    assert cmt['e']['ea'] == 2051

