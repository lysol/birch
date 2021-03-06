import os
from setuptools import setup, find_packages
import distutils
import distutils.command.build
from distutils.core import setup, Extension


_birch = Extension('birch._birch',
                    sources = [
                        'birch/_perlin.c',
                        'birch/_rect.c',
                        'birch/_world.c',
                        'birch/_birch.c'
                        ])

# Override build command
class BuildCommand(distutils.command.build.build):

    def run(self):
        print('>>>>>> Running asset build')
        examples_path = 'birch/examples'
        listing = os.listdir(examples_path)
        from build_assets import build_assets
        for fn in filter(lambda fn: os.path.isdir(fn) and not fn.endswith('__pycache__'),
            map(lambda fn: '%s/%s' % (examples_path, fn), listing)):
            print('Processing assets for example %s' % fn)
            build_assets('%s/assets_src' % fn, '%s/assets' % fn)
        super().run()

setup(name='birch',
      version='0.0.1',
      description='a game',
      url='http://github.com/lysol/birch',
      author='Derek Arnold',
      author_email='derek@derekarnold.net',
      license='ISC',
      packages=find_packages(),
      package_dir={'birch': 'birch'},
      package_data={'birch': [
          'examples/**/assets/*',
          'examples/**/maps/*'
          ]},
      install_requires=[
          'pyglet==1.5.17',
          'noise',
          'pillow',
          'cairosvg',
          'numpy'
          ],
      zip_safe=False,
      cmdclass={"build": BuildCommand},
      ext_modules=[_birch])
