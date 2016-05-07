#!/usr/bin/env python

from collections import abc

# This is similar to Python's collections.ChainMap class, but works with
# hierarchical (nested) dicts, not just flat ones.
# It was inspired by the Chainmap class described here:
# http://code.activestate.com/recipes/305268/.
# This provides an elegant way to merge multiple hierarchical dictionaries or
# other mapping-type objects in Python.

is_mapping = lambda x: isinstance(x, abc.Mapping)
not_mapping = lambda x: not(is_mapping(x))

class MergedTree(abc.Mapping):
    """Combine/overlay multiple hierarchical mappings. This efficiently merges
    multiple hierarchical (could be several layers deep) dictionaries, producing
    a new view into them that acts exactly like a merged dictionary, but without
    doing any copying.

    Because it doesn't actually copy the data, it is intended to be used only 
    with immutable mappings. It is safe to change *leaf* data values,
    and the results will be reflected here, but changing the structure of any
    of the trees will not work.

    Or, you can convert it to a normal dict tree immediately after you create
    it, with the .dict() method.
    """
    def __init__(self, *maps):
        _maps = list(maps)

        # All keys of kids that are mappings
        kid_keys = set([key for m in maps 
            for key in m.keys() if is_mapping(m[key])])

        # This will be a dictionary of lists of mappings
        kid_maps = {};
        for key in kid_keys:
            # The list of child mappings for this key
            kmaps = [ m[key] for m in maps if key in m ]
            # Make sure they are *all* mappings
            if any(map(not_mapping, kmaps)): raise KeyError(key)
            # Recurse
            kid_maps[key] = MergedTree(*kmaps)

        # If non-empty, prepend it to the existing list
        if len(kid_maps.keys()) > 0: _maps.insert(0, kid_maps)

        self._maps = _maps

    def __getitem__(self, key):
        for mapping in self._maps:
            try:
                return mapping[key]
            except KeyError:
                pass
        raise KeyError(key)

    def __iter__(self):
        return set([key for m in self._maps for key in m.keys()]).__iter__()

    def __len__(self):
        return len(self)

    def dict(self):
        """
        Use this explict conversion method to do a deep conversion to a 
        run-of-the-mill, mutable dictionary tree
        """
        # This "regularizes" a child value, meaning that if it's a MergedTree, 
        # it's converted to a dict.
        regv = lambda v: v.dict() if isinstance(v, MergedTree) else v
        # Create dict with an iterator that returns "regularized" tuples 
        return dict(map(lambda k: (k, regv(self[k])), self))


if __name__ == "__main__":
    d1 = {'a':1, 'b':2, 'c': {'c1': 1, 'c2': 2}}
    d2 = {'a':3, 'd':4, 'c': {'c2': 4, 'c3': 3}}
    cm = MergedTree(d1, d2)
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
    cmt = MergedTree(*testDicts)
    assert cmt['a'] == 1001
    assert cmt['b']['ba']['baa'] == 1211
    assert cmt['b']['ba']['bab'] == 3212
    assert cmt['b']['bb'] == 1022
    assert cmt['c'] == 1003
    assert cmt['d']['da'] == 3041
    assert cmt['e']['ea'] == 2051

    print('ok')
