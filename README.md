# mitocyto

Automatic and manual image analysis of cells in serial sections.  Software identifies areas corresponding to individual cells from a map of cell edges.  The edge map can be constructed automatically, either directly from an image representing cell membranes (for example a dystrophin channel), from a gradient map constructed from a channel (or from an average of all available channels).  The edge map can also be drawn by tracing over channel images (or over an average of all available channels).  Finally, automatic construction of the edge map can be improved by manual editing of areas where edge signal is weak.  We envisage that the latter scenario will be the most common manual workflow.

Once an edgemap is constructed it is used to identify cell areas, also known as regions of interest (ROIs) or contours.  For each cell area, for each available channel, average intensities are constructed and these are tabulated and written to an output file.  In order to preserve the laborious manual specification of the edge locations, and to allow a range of different analysis to be attempted in future, we preserve the edgemap by saving it as a binary image in lossless .png format.  We also save a coloured image representation of the identified cell areas (or contours).

## Installation

mitocyto is a Python program and the latest release of the software is packaged and distributed on PYPI.  If you have a working Python 3 installation, you can install mitocyto and all of its dependencies by executing the following on the command line:

```shell
pip install mitocyto
```

### Installation under Microsoft Windows

First, you will need to download the latest version of Python for Windows:

[https://python.org/downloads](https://python.org/downloads)

When installing, *make sure to tick* "Add Python 3.x to PATH".  This will make your life much easier.

Select the default options (top button) to install Python, pip and to add Python to your PATH.  If offered the option of allowing longer path names, accept that.

To install mitocyto, together with all the other software that it requires, you need to open a Command Prompt.  One way to do this is to use the start button to search for "cmd", then click on the "Command Prompt" icon.

Type the following command into the Command Prompt window and press enter:

```shell
pip install mitocyto
```

The first time you do this, it could take several minutes to download and install various pieces of software, but after that first installation, any subsequent updates should be quite quick.

## Software Updates

To update mitocyto to the latest version, type the following in terminal (or Command Prompt under Windows):

```shell
pip install --upgrade mitocyto
```

### Using the software










