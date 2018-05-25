from setuptools import setup, find_packages
import os

version='0.0.9'
f=open('mitocyto/version.py',"w")
f.write("__version__='{}'".format(version))
f.close()

setup(name='mitocyto',
      version=version,
      packages=['mitocyto','mitocyto_scripts'],
      install_requires=[
          'psutil','numpy','scipy','pandas','pillow','opencv-python','matplotlib','scikit-image'
      ],
      description='Image analysis of cells in serial sections',
      long_description=open('README.txt').read(),
      entry_points={"console_scripts":["mcgui = mitocyto_scripts.gui:main",
                                       "mcauto = mitocyto_scripts.auto:main",
                                       "mcmerge = mitocyto_scripts.getResults:main",
                                       "mcaddtags = mitocyto_scripts.tagFiles:addtags",
                                       "mcremovetags = mitocyto_scripts.tagFiles:removetags",
                                       "mcall = mitocyto_scripts.mitocytoAllTheThings:main"]},
      author='Conor Lawless',
      author_email='cnr.lwlss@gmail.com',
      url='http://cnr.lwlss.net',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Intended Audience :: Science/Research'
        ])
