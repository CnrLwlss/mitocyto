from setuptools import setup, find_packages
import os

version='0.0.3'
f=open('mitocyto/version.py',"w")
f.write("__version__='{}'".format(version))
f.close()

setup(name='mitocyto',
      version=version,
      packages=['mitocyto','scripts'],
      install_requires=[
          'numpy','scipy','pandas','pillow','opencv-python','matplotlib','scikit-image'
      ],
      description='Image analysis of cells in serial sections',
      long_description=open('README.txt').read(),
      entry_points={"console_scripts":["mcgui = scripts.gui:wrapmain",
                                       "mcauto = scripts.other:main"]},
      author='Conor Lawless',
      author_email='cnr.lwlss@gmail.com',
      url='http://cnr.lwlss.net',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Intended Audience :: Science/Research'
        ])
