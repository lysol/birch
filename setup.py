from setuptools import setup
from distutils.core import setup, Extension

open_simplex = Extension('birch.open_simplex',
                    sources = [
                        'birch/open_simplex.c',
                        'birch/_opensimplex.c'
                        ])

setup(name='birch',
      version='0.0.1',
      description='a game',
      url='http://github.com/lysol/birch',
      author='Derek Arnold',
      author_email='derek@derekarnold.net',
      license='ISC',
      packages=['birch'],
      install_requires=[
          'pyglet',
          'noise',
          'pillow'
          ],
      zip_safe=False,
      ext_modules=[open_simplex])
