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

def test_defaults():
    import test.settings_defaults as s
    dump_settings('test_defaults', s)
    assert s.JSLIB_BASE == 'http://example.cdn/jslib/'
    assert s.JSLIB_VER == '2.4.1'
    assert s.JSLIB_URL == 'http://example.cdn/jslib/2.4.1/jslib.js'
    assert s.COMIC['characters'][0] == 'Mister Fantastic'
    assert s.FIRST == False
    assert s.CHARACTER == 'Human Torch'
    assert s.HAPPY_KID == 'Wumbus'

def test_robin():
    import test.settings_robin as s
    dump_settings('test_robin', s)
    assert s.JSLIB_URL == 'http://example.cdn/jslib/2.5.3/jslib.js'
    assert s.CHARACTER == 'Robin'
    assert s.HAPPY_KID == 'Wumbus'

def test_batman():
    import test.settings_batman as s
    dump_settings('test_batman', s)
    assert s.JSLIB_URL == 'http://example.cdn/jslib/2.5.3/jslib.js'
    assert s.CHARACTER == 'Batman'
    assert s.HAPPY_KID == 'Zombo'

def test_django():
    """Test in a real django environment"""

    # Use django to read and process the settings file
    from django.conf import settings, global_settings
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'test.settings_django')
    settings._setup()

    # Get the ones we're interested in
    all_settings = settings_dict(settings._wrapped)
    default_settings = settings_dict(global_settings)
    user_settings = {k: v for k, v in all_settings.items() 
      if not(k in default_settings)}

    dump_settings('test_django', user_settings)
    assert user_settings['JSLIB_URL'] == 'http://example.cdn/jslib/2.5.3/jslib.js'
    assert user_settings['CHARACTER'] == 'Batman'
    assert user_settings['HAPPY_KID'] == 'Zombo'
