from setuptools import setup, find_packages
from distutils.core import setup, Extension

open_simplex = Extension('birch.open_simplex',
                    define_macros = [('_DEBUG', '1')],
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
      packages=find_packages(),
      package_dir={'birch': 'birch'},
      package_data={'birch': ['assets/*']},
      install_requires=[
          'pyglet',
          'noise',
          'pillow'
          ],
      zip_safe=False,
      ext_modules=[open_simplex])
