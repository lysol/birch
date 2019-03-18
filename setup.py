from setuptools import setup

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
          'pygame'
          ],
      zip_safe=False)
