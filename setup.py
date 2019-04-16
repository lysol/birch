from setuptools import setup, find_packages
from distutils.core import setup, Extension

_perlin = Extension('birch._perlin',
                    sources = [
                        'birch/_perlin.c'
                        ])
_rect = Extension('birch._rect',
                    sources = [
                        'birch/_rect.c'
                        ])
_world = Extension('birch._world',
                    sources = [
                        'birch/_rect.c', 'birch/_world.c'
                        ])

setup(name='birch',
      version='0.0.1',
      description='a game',
      url='http://github.com/lysol/birch',
      author='Derek Arnold',
      author_email='derek@derekarnold.net',
      license='ISC',
      packages=find_packages(),
      package_dir={'birch': 'birch'},
      package_data={'birch': ['assets/*']},
      install_requires=[
          'pyglet',
          'noise',
          'pillow'
          ],
      zip_safe=False,
      ext_modules=[_perlin, _rect, _world])
