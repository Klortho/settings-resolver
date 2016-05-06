from collections import abc

# This class builds upon the Chainmap class described here:
# http://code.activestate.com/recipes/305268/.
# It provides an elegant way to merge multiple hierarchical dictionaries or
# other mapping-type objects in Python.

class ChainMapTree(abc.Mapping):
    """Combine/overlay multiple hierarchical mappings. This efficiently merges
    multiple hierarchical (could be several layers deep) dictionaries, producing
    a new view into them that acts exactly like a merged dictionary, but without
    doing any copying.

    Because it doesn't actually copy the data, it is intended to be used only 
    with immutable mappings. It is safe to change *leaf* data values,
    and the results will be reflected here, but changing the structure of any
    of the trees will not work.
    """

    def __init__(self, *maps):
        _maps = list(maps)

        is_mapping = lambda x: isinstance(x, abc.Mapping)

        # Union of all keys of all of the maps whose values are mappings
        map_keys = set([key for m in maps 
            for key in m.keys() if is_mapping(m[key])
        ])

        # The child ChainMapTree for a given key
        def kid_chain(key):
            # The list of child mappings for this key
            kid_maps = [ m[key] for m in maps if key in m ]
            # Make sure they are all mappings
            not_mapping = lambda x: not(is_mapping(x))
            if any(map(not_mapping, kid_maps)): raise KeyError
            return ChainMapTree(*kid_maps)

        # A dictionary of ChainMapTrees for these keys
        kid_map_chains = dict((k, kid_chain(k)) for k in map_keys)

        # If non-empty, prepend it to the existing list
        if len(kid_map_chains.keys()) > 0:
            _maps.insert(0, kid_map_chains)
        self._maps = _maps

    def __getitem__(self, key):
        for mapping in self._maps:
            try:
                return mapping[key]
            except KeyError:
                pass
        raise KeyError(key)

    def __iter__(self):
        return self._maps.__iter__()

    def __len__(self):
        return self._maps.__len__()


if __name__ == "__main__":
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
    assert cmt.a == 1001
    assert cmt['b']['ba']['baa'] == 1211
    assert cmt['b']['ba']['bab'] == 3212
    assert cmt['b']['bb'] == 1022
    assert cmt['c'] == 1003
    assert cmt['d']['da'] == 3041
    assert cmt['e']['ea'] == 2051

    print('ok')
