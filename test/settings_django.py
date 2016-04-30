from os import path
test_dir = path.dirname(path.abspath(__file__))

from settings_resolver import resolver as s, deferred as d, resolve 

# Needed by Django
SECRET_KEY = 'abracadabra'
DEBUG = True
ALLOWED_HOSTS = []
ROOT_URLCONF = 'view'

# A practical example: a JS library URL that is computed from parts.
JSLIB_BASE = 'http://example.cdn/jslib/'
JSLIB_VER = '2.4.1'
JSLIB_URL = d(lambda: s.JSLIB_BASE + s.JSLIB_VER + '/jslib.js')

# Settings can be any type of value, and can depend on each other freely (as 
# long as there are no cycles). No need to think about the order of overrides.
# Here in settings.py, define all of the defaults:
COMIC = d(lambda: s.COMICS[s.COMIC_TITLE])
FIRST = False
CHARACTER = d(lambda: s.COMIC['characters'][0 if s.FIRST else -1] )
COMICS = {
  'Fantastic Four': {
    'characters': [
      'Mister Fantastic',
      'Invisible Woman',
      'Thing',
      'Human Torch',
    ],
  },
}
COMIC_TITLE = 'Fantastic Four'
HAPPY_KID = d(lambda: 'Zombo' if s.CHARACTER == 'Batman' else 'Wumbus')

# Override and resolve all the settings
resolve(globals(), yaml=path.join(test_dir, 'settings_local.yaml'))

