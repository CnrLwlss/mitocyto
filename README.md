# mitocyto

Automatic and manual image analysis of cells in serial sections.  Software identifies areas corresponding to individual cells from a map of cell edges.  The edge map can be constructed automatically, either directly from an image representing cell membranes (for example a dystrophin channel), from a gradient map constructed from a channel (or from an average of all available channels).  The edge map can also be drawn by tracing over channel images (or over an average of all available channels).  Finally, automatic construction of the edge map can be improved by manual editing of areas where edge signal is weak.  We envisage that the latter scenario will be the most common manual workflow.

Once an edgemap is constructed it is used to identify cell areas, also known as regions of interest (ROIs) or contours.  For each cell area, for each available channel, average intensities are constructed and these are tabulated and written to an output file.  In order to preserve the laborious manual specification of the edge locations, and to allow a range of different analysis to be attempted in future, we preserve the edgemap by saving it as a binary image in lossless .png format.  We also save a coloured image representation of the identified cell areas (or contours).

## Installation

mitocyto is a Python program and the latest release of the software is packaged and distributed on PYPI.  If you have a working Python 3 installation, you can install mitocyto and all of its dependencies by executing the following on the command line:

pip install mitocyto
