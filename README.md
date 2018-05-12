# mitocyto

mitocyto is for automatic and manual image analysis of cells in sections.  Software identifies areas corresponding to individual cells from a map of cell edges.  The edge map can be constructed automatically, either directly from an image representing cell membranes (for example a dystrophin channel) or from a gradient map automatically constructed from a channel (or from an average of all available channels).  The edge map can also be drawn by tracing over individual channel images (or over an average of all available channels), using the mouse.  Automatic construction of the edge map can be improved by manual editing of areas where edge signal is weak.  We envisage that the scenario where a first draft of the edgemap is constructed automatically, followed by manual update, will be the most common workflow.

The edgemap is used to identify cell areas, also known as regions of interest (ROIs) or contours.  This works by identifying areas in the edgemap which are completely closed by edge, and filtering these by size, circularity, aspect ratio and convexity, in order to ensure that we are looking at cross-sections of cells.  For each cell area, for each available channel, average intensities are constructed and these are tabulated and written to an output file.  In order to preserve the laborious manual specification of the edge locations, and to allow a range of different analysis to be attempted in future, we preserve the edgemap by saving it as a binary image in lossless .png format.  We also save a coloured image representation of the identified cell areas (or contours).

## Installation

mitocyto is a Python program and the latest release of the software is packaged and distributed on PYPI.  If you have a working Python 3 installation, you can install mitocyto and all of its dependencies by executing the following on the command line:

```shell
pip install mitocyto
```

### Installation under Microsoft Windows

You will need a computer on which you have administrator rights, which has connection to the internet.  

#### Installing Python
First, you will need to download the latest version of Python for Windows:

[https://python.org/downloads](https://python.org/downloads)

When installing, *make sure to tick* "Add Python 3.x to PATH".  This will make your life much easier.

Select the default options (top button of two) to install Python, pip and to add Python to your PATH.  If offered the option of allowing longer path names, accept that.

#### Installing mitocyto and dependencies
To install mitocyto, together with all the other software libraries that it requires, you need to open a Command Prompt.  One way to do this is to use the Windows start button to search for "cmd", then click on the "Command Prompt" icon.

Type the following command into the Command Prompt window and press enter:

```shell
pip install mitocyto
```

The first time you do this, it could take several minutes to download and install various pieces of software, but after that first installation, any subsequent updates should be quite quick.

Once this stage has succesfully completed, mitocyto is installed on your machine.  To check the installation, first open Python.  For example, you can open it from the command line, by typing it's name (all lower case) followed by enter:

```shell
python
```

Then, once Python is open, type the following command, followed by enter:

```python
import mitocyto
```

It could take up to 30 seconds for this command to execute first time it is run, but if that command returns without error, then mitocyto has been installed successfully.  To exit Python, type `quit()`, followed by enter.

## Software Updates

If you need to update mitocyto to the latest version, simply type the following in terminal (or Command Prompt under Windows):

```shell
pip install --upgrade mitocyto
```

## Starting mcgui

Installing the software gives you a regular Python package named mitocyto, but it also installs some scripts onto your machine, which you can use without having to interact with Python at all.  One of these scripts is called `mcgui` (for mitocyto graphical user interface).  One way to start this script is to type the following command in a terminal or Command Prompt window, followed by enter:

```shell
mcgui
```

In order for `mcgui` to run correctly, it needs to be executed from a directory which contains a set of images, representing different channels from the same subject.  If you are comfortable changing directory on the command line, you can navigate to your directory of images from a single section and execute `mcgui` there.  

### Setting up a Windows shortcut
An alternative way to start the software is to set up a Windows shortcut, which can be copied into directories which need to be analysed.

Using Windows Explorer, navigate to a directory containing images for analysis.  Right-click on some white space in the directory (i.e. anywhere that is not a file or another directory).  Choose New -> Shortcut.  When prompted for location of the item, type `mcgui`, then hit the next button.  You can name the shortcut whatever you like.  This creates a shortcut in the directory with the images.  Before you can use it, you need to tell it that it should excute `mcgui` in the current directory.  To do that, right-click on the shortcut, choose Properties and edit the Start in box to read `%CD%`.  Then hit OK.  Your shortcut is now ready to use. 

## Using mcgui

`mcgui` loads all of the available image files in the current directory, ready to display.  mcgui creates pseudo-images from the original data, with maximal contrast for display purposes.  If any of the files include the text "Dystrophin" in their filename, that file will be displayed first.  You can navigate between files using the left and right arrow keys.  Alternatively, each image file is allocated a shortcut key, so that you can switch between those quickly.






