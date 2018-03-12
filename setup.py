from setuptools import setup

setup(name='Pigrow',
      version='0.25',
      description='Pigrow greenhouse automation software',
      url='http://github.com/pragmatismo/Pigrow',
      author='Pragmatismo',
      author_email='flyingcircus@example.com',
      license='GNU',
      packages=['pigrow'],
      install_requires=[
          'praw',
          'pexpect',
          'crontab',
          'matplotlib',
          'python-crontab',
      ],
      zip_safe=False)
