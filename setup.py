from setuptools import setup, find_packages


setup(
    name='FragStatsPy',
    version='0.1',
    license='MIT',
    author="Scott Lawson",
    author_email='scott.lawson@uvm.edu',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/sclaw/FragStatsPy',
    keywords='landscape metrics',
    install_requires=[
          'pandas',
      ],

)