from setuptools import setup

setup(
    name='settings-resolver',
    version='1.0.4',
    description='Allows interdependent Django settings overrides, through late binding',
    long_description=(
        'Use lambda functions to specify your Django settings. '
        'Because they are resolved late, after all overrides, they can reference '
        'each other seamlessly.'
    ),
    url='https://github.com/klortho/settings-resolver',
    author='Chris Maloney',
    author_email='voldrani@gmail.com',
    license='WTFPL',
    packages=['settings_resolver'],
    install_requires=[
        'PyYAML', 
        'settings-overrider'
    ],
    extras_require={
        'test': [
            'django',
            'pytest',
            'pytest-cov',
        ],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'
    ],
)
