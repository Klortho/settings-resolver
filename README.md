# settings-resolver

[![Build Status](https://travis-ci.org/Klortho/settings-resolver.svg?branch=master)](https://travis-ci.org/Klortho/settings-resolver)

This package is intended as a replacement for, and is backward-compatible with,
the excellent 
[settings-overrider](https://github.com/kottenator/settings-overrider), which
allows you to override settings with environment variables or a YAML file, at 
runtime. It is ideal for use with Django settings, but could be used more
generally.

This package adds the ability to have settings whose values depend on other
settings, in such a way that those dependencies are not disrupted by the
overrides.

## Install

```
pip install settings-resolver
```

## Use

Using this package, 
settings that depend on other settings can be defined using lambdas, that are
resolved after all the overrides have been applied. For example, say you want
to define settings for some JavaScript library URLs, based on some constituent
parts, and that you'd like to be able to override any of those parts 
independently, and get a final URL value that matches what you expect.
The settings.py module would look like the following.

```python
from os import path
BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))

from settings_resolver import resolver as s, deferred as d, resolve 

CDN_BASE = 'https://cdnjs.cloudflare.com/ajax/libs/'

JQUERY_VER = '2.2.1'
JQUERY_URL = d(lambda: s.CDN_BASE + 'jquery/' + s.JQUERY_VER + '/jquery.js')

MATHJAX_VER = '2.6.1'
MATHJAX_URL = d(lambda: s.CDN_BASE + 'mathjax/' + s.MATHJAX_VER + '/MathJax.js')

resolve(globals(), 
        yaml=path.join(BASE_DIR, 'settings_local.yaml'), 
        env='DJANGO_')
```

In settings_local.yaml, you might have, for example:

```yaml
CDN_BASE: file:///var/cache/cdnjs/
MATHJAX_VER: 2.4.2
```

Because the values for JQUERY_URL and MATHJAX_URL are resolved late, after the
overrides have been applied, the computed URLs are correct:

```
JQUERY_URL == 'file:///var/cache/cdnjs/jquery/2.2.1/jquery.js'
MATHJAX_URL == 'file:///var/cache/cdnjs/mathjax/2.4.2/MathJax.js'
```

The `resolve()` function performs two tasks:

* If either `yaml` or `env` is given, it applies overrides from a YAML file, 
  environment variables, or both. For this, it delegates to 
  [settings-overrider](https://github.com/kottenator/settings-overrider) - see
  the README there for more details.
* It resolves all of the settings values, by recursively applying the deferred
  functions.

## Motivation

The normal style of defining and overriding settings is limited in how easily
various settings can dereference (use) each other. A naive attempt at defining
URLs as described above might look like this:

```python
JS_BASE = 'https://cdn.com/'
JS_VER = '2.4.1'
JS_URL = JS_BASE + JS_VER + '/jslib.js'

// Do overriding here:
JS_VER = '2.5.3'
...
print(JS_URL)    #=> 'https://cdn.com/2.4.1/jslib.js' -- override didn't work
```

Obviously, it doesn't work as we'd like, because the override happens too late, 
after the assignment statements, and they have no effect on the value of JS_URL.
Trying to fix this by putting the overrides first doesn't help, because that 
would be too *early*.

There are ways to make it work, of course. You could
do the overrides first, and then use the dictionary's `setdefault()` method, 
like this:

```python
// Do overriding here
JS_VER = '2.5.3'

_settings = globals()
_settings.setdefault('JS_BASE', 'https://cdn.com/')
_settings.setdefault('JS_VER', '2.4.1')
_settings.setdefault('JS_URL', JS_BASE + JS_VER + '/jslib.js')
```

This is less than ideal, however, for a number of reasons. It forces you to 
treat these settings specially, just because they dereference each other.
Also, you have to keep track of their mutated state at different points in the 
program. And, it's a very limited solution to the problem, because it only 
gives you one round of overriding. If you want to add more layers of defaults 
and overrides, things get very complicated very quickly.

This module, `settings-resolver`, uses a form of lazy initialization to 
provide the ability to define these kinds of interdependent settings in a more
robust and flexible way. It treats each of the settings variables as 
immutable, which not only means that they can dereference each other, but also 
that they can be moved around within the module freely -- the definition of
settings that deference others can come before or after those others, without
any effect on the final result.

The cost is a little bit of syntactic noise; but, compared to the `setdefault`
example above, it is much cleaner. Using this library, the example 
above would become:

```python
from settings_resolver import resolver as s, deferred as d, resolve

JS_BASE = 'https://cdn.com/'
JS_VER = '2.4.1'
JS_URL = d(lambda: s.JS_BASE + s.JS_VER + '/jslib.js')

// Do overriding here (as many layers as you want)
JS_VER = '2.5.3'

resolve(globals())

print(JS_URL)    #=>  'http://cdn/2.5.3/jslib.js'
```

The two main changes in syntax are:

1. Any assignment for a setting that depends on others must be wrapped in 
  `d(lambda: ... )`, which turns it into a "deferred" object. 
2. Inside the body of those deferreds, reference other settings as properties
  of `s`, which is an object that defines getter methods that implement the
  final resolution.

The lambda expressions that define these values are evaluated 
after all of the overrides have been done. When the `resolve()` function is 
called, everything is recursively evaluated, all of the `deferred`s are
unwrapped, and the `settings` module variables are updated.

This approach is very flexible. Settings dependencies are not limited to one
level -- they can recursively depend on others, with no problem (as long as there
are no cycles).

Also, they can be of any type -- they are not limited to strings.

The wrapped functions do not have to be lambdas, but it makes things
easier if they are. 

There are two caveats:

1. The *entire* right-hand side of the assignment must be wrapped. For example,
  this will not work:

    ```python
    JS_URL = d(lambda: s.JS_BASE + s.JS_VER) + '/jslib.js'
    ```

2. Do not mutate any of the settings from within the body of the deferred.
  Because of this requirement, I recommend always using lambda expressions 
  for the deferred, since mutating variables inside lambdas is very difficult
  to do (if not impossible).

# Developing

```
virtualenv -p python3 env
. env/bin/activate
pip install -e .[test]
py.test
```

