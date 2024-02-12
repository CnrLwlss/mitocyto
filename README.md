# mitocyto

mitocyto is for automatic and manual image analysis of cells in images of tissue sections.  A map of cell edges (an edgemap) is constructed and used to identify areas corresponding to individual cells.  The edgemap can be constructed automatically, either directly from an image representing cell membranes (for example a dystrophin channel), from a thresholded version of an image or from a gradient map automatically constructed from a channel (or from an average of all available channels).  The edgemap can also be drawn by manual tracing over individual channel images (or over an average of all available channels), using the mouse.  Automatic construction of the edge map can be improved by manual editing of areas where edge signal is weak.  We envisage that the scenario where a first draft of the edgemap is constructed automatically, followed by manual update, will be the most common workflow.

The edgemap is used to identify distinct areas in the source images (also called contours) corresponding to individual cells.  This works by identifying areas in the edgemap which are completely enclosed by edge, and filtering these by size, circularity, aspect ratio and convexity to ensure that the areas represent plausible cells.  For each cell area and for each available channel, average intensities are constructed, tabulated and written to an output file.  In order to capture the laborious manual specification of the edge locations and to allow a range of different analyses to be carried out in future, we preserve the edgemap by saving it as a binary image in lossless .png format.  We also save a coloured, numbered image representation of the identified cell areas.

## Installation

The latest version is v0.0.19: source code is [here](https://github.com/CnrLwlss/mitocyto/releases/tag/v0.0.19).

mitocyto is a Python program and the latest release of the software is packaged and distributed on PYPI.  If you have a working Python 3 installation, you can install mitocyto and all of its dependencies simply by executing the following at the command line:

```shell
pip install mitocyto
```

### Installation under Microsoft Windows

You will need to have administrator rights on your computer for installing software and a connection to the internet.  

#### Installing Python
First, you will need to download the latest version of Python for Windows.  Python is a general computing language that is very useful for automating all kinds of tasks, not just for image analysis.  You can download the latest installation file for Python here:

[https://python.org/downloads](https://python.org/downloads)

When installing, **make sure to tick** "Add Python 3.x to PATH".  This will make your life much easier.

Select the default options (the top button out of the two) to install Python, pip and to add Python to your PATH.  If offered the option of allowing longer path names, accept that.

#### Installing mitocyto and dependencies
In order to install mitocyto you need to open a Command Prompt.  One way to do this is to use the Windows start button to search for "cmd", then click on the "Command Prompt" icon.

To download and install the mitocyto software, along with other Python software that it requires to run, simply type the following command into the Command Prompt window and press enter:

```shell
pip install mitocyto
```

The first time you do this, it could take several minutes to download and install various pieces of software, but after that first installation, any subsequent updates should be quite quick.

Once this stage has successfully completed, mitocyto is installed on your machine.  To check the installation, first open Python.  For example, you can open it from the command line, by typing it's name (all lower case) followed by enter:

```shell
python
```

Then, once Python is open, type the following command, followed by enter:

```python
import mitocyto
```

It could take up to 30 seconds for this command to execute the first time you run it, but if that command returns without error, then mitocyto has been installed successfully.  To exit Python and return to a regular Command Prompt, type `quit()` followed by enter.

## Software Updates

If you need to update mitocyto to the latest version, simply type the following in terminal (or Command Prompt under Windows):

```shell
pip install --upgrade mitocyto
```

## Starting mcgui

Installing the software gives you a regular Python package named mitocyto, but it also installs some programs onto your machine, which you can use without having to interact with Python at all.  One of these programs is called `mcgui` (for mitocyto graphical user interface).  One way to start this script is to type the following command in a terminal or Command Prompt window, followed by enter:

```shell
mcgui
```

In order for `mcgui` to run correctly, it needs to be executed from a directory which contains a set of images, representing different channels from the same subject.  If you are comfortable changing directory on the command line, you can navigate to your directory of images from a single section and execute `mcgui` there.  

### Setting up a Windows shortcut
An alternative way to start the software on Windows is to create a shortcut which can be copied into any directories which need to be analysed.

Using Windows Explorer, navigate to a directory containing images for analysis.  Right-click on some white space in the directory (i.e. anywhere that is not a file or another directory).  Choose New -> Shortcut.  When prompted for location of the item, type `mcgui`, then hit the next button.  You can name the shortcut "mcgui", for example.  This creates a shortcut in the current directory.  Before you can use it, you need to tell it that it should execute the program `mcgui` in the current directory.  To do that, right-click on the shortcut, choose Properties and edit the contents of the Start in box to read `%CD%`.  Then hit OK.  Your Windows shortcut is now ready to use and to copy around your computer.

## Using mcgui

<p>
<figure>
  <img src="/images/channel.png" alt="One channel from cross-section of muscle tissue"/>
  <figcaption>An example channel (COX4) from a series loaded into mitocyto</figcaption>
</figure>
</p>


`mcgui` loads all of the available image files in the current directory, ready to display.  `mcgui` creates pseudo-images from the original data, with maximal contrast for display purposes.  If any of the files include the text "Dystrophin" in their filename, that file will be displayed first.  You can navigate between pseudo-images using the left and right arrow keys.  Alternatively, each image file is allocated a shortcut key (see window title bar), so that you can switch between those quickly.

<p>
<figure>
  <img src="/images/EDGE_mitocyto.png" alt="mitocyto edgemap"/>
  <figcaption>Edge map estimated directly from a dystrophin channel (dystrophin stains cell membranes)</figcaption>
</figure>
</p>

`mcgui` also constructs two new images: the edgemap and an average image generated by combining all of the original images in the directory.  You can access these images by continually pressing the right arrow until you have come to the end of the list.  The average image is the second last in the list, and the edgemap is the last.  The edgemap image is the most useful, at any time, you can jump to this image by pressing its shortcut key: "z".

<p>
<figure>
  <img src="/images/AVE_mitocyto.png" alt="mitocyto average of all available images"/>
  <figcaption>The average of several images which have been loaded into mitocyto</figcaption>
</figure>
</p>

The first time you run `mcgui`, the edgemap is empty.  If one of your channels (e.g. the dystrophin channel) corresponds to a direct observation of cell membranes, you can copy this image to the edgemap by navigating to it and pressing "c" to copy the signal across.  If you want to exaggerate the cell membrane signal before copying it across, you can first threshold the image by pressing "b".  If you have copied the wrong data across, you can clear the edgemap at any time by pressing "x".  If you have no reliable map of cell membranes, you can estimate it by calculating the thresholded gradient in a regular channel (or from the average of all channels) by navigating to that channel and pressing "n".  Finally, to calculate and display the set of contours calculated for the current edgemap press the space bar.

<p>
<figure>
  <img src="/images/EDGE_threshave.png" alt="mitocyto thresholded average image"/>
  <figcaption>Thresholded version of the average of several images which have been loaded into mitocyto</figcaption>
</figure>
</p>

It is also possible to manually edit the edgemap, using the mouse.  To add a new edge, or strengthen an existing edge, simply trace or paint over any of the displayed images using the left mouse button.  To delete edges, or to blacken signal in the centre of cells, paint with the right mouse button.  If you want to eradicate an existing contour from the contour map, hold down the shift button and then left click on the offending contour.  This will fill that area with edge: i.e. paint it white on the edge map.

<p>
<figure>
  <img src="/images/CONTOURS_mitocyto.png" alt="mitocyto cell areas"/>
  <figcaption>Labelled mitocyto cell areas, estimated from the edgemap followed by filtering</figcaption>
</figure>
</p>

Once you are happy with the edgemap and the calculated contours, press the escape button to write results to file and to close `mcgui`.  Before it closes, the program will write a new .png file representing the edgemap used, another .png file representing the estimated locations of the cell areas and tabulated estimates of channel intensities in each cell area as a .csv file.

If an edgemap file saved by `mcgui` is already present in the directory (named EDGE_mitocyto.png) then that data will be automatically loaded into the edgemap.  This useful feature allows us a way to save manual work on constructing edgemaps and resume editing at a later date.  We can also copy edgemap image files from one directory to another if we need to examine the same contours on adjacent sections, for example.  The image can be resized and rotated in a photo editing program to suit another section, if necessary.

### Keyboard shortcuts
* 1-0: Select specific image from directory & display filename
* q-p: Select specific image from directory & display filename
* a-g: Select specific image from directory & display filename
* x: Clear edgemap
* c: Copy image currently displayed to edgemap
* b: Toggle threshold mode for current image
* h: Open this help page to read documentation
* n: Toggle gradient mode for current image
* z: Display edgemap
* Left arrow: Display previous image from list of images in directory
* Right arrow: Display next image from list of images in directory
* Space bar: Display cell areas estimated from edgemap

### Mouse
* Left-click paint on any image: draw edge on edgemap
* Right-click paint on any image: delete edge on edgemap
* Shift-left-click on a cell area: fill area with "edge" (i.e. paint white on whitemap)
 
## Using mcclass
mcclass is a commandline tool to manually classify the OXPHOS status of individual cells based on analysing average single cell protein intensities displayed as a 2D scatterplot.  Classification is by visual inspection of 2Dmito plots: scatterplots showing single cell protein level profiles, comparing levels of mitochondrial mass (mito membrane protein, x-axis) with levels of oxphos protein (y-axis) in control subjects and in an individual patient section.  Deficent cells are usually identified as those occupying the bottom fork of a v-shape in the 2Dmito plot, where the healthy cells from the patient section are similar to cells from control subjects and exclusively occupy the upper fork. 

mcclass has been upgraded recently to make it a formal part of the mitocyto workflow, so please upgrade your mitocyto installation before trying it out:

```shell
pip install --upgrade mitocyto
```

To manually classify cells with mcclass first look at the documentation:

```shell
mcclass --help
```

Which will display:

```
mcclass --help
usage: mcclass [-h] [--mitochan MITOCHAN] [--oxphos OXPHOS [OXPHOS ...]] [--warren | --no-warren] [--input INPUT] [--output OUTPUT] [--controls CONTROLS [CONTROLS ...]]

Manual classification of cells in 2Dmito plots. Reads in single cell protein expression data from input file. Identifies control subjects and patients. Generates a series of 2D scatterplots showing relationship between an OXPHOS protein and a protein
which is a surrogate for mitochondrial mass (e.g. VDAC1). User compares increase in OXPHOS protein with mitochondrial mass in single cells from controls with the increase in a single patient and uses that comparison to inform a manual selection of
patient cells where increase of OXPHOS protein with mitochondrial mass would be an outlier in control data. Manual selection is by freehand drawing around the cells on scatterplot which are distinct from controls.

options:
  -h, --help            show this help message and exit
  --mitochan MITOCHAN   Mitochondrial mass surrogate protein name. Must be present in Channel column of input file.
  --oxphos OXPHOS [OXPHOS ...]
                        List of OXPHOS proteins to classify, separated by space. Names specified in Channel column of input file.
  --warren, --no-warren
                        Classify data from Warren et al. (2020)?
  --input INPUT         Tab-delimited input text filename. Input data should be in long form and contain data from controls and patient(s). Each subject/section should have a unique identifier specified in the Filename column. Data can have extra
                        colums, but the following columns must be present: Value,ID,Channel,Filename ID is cell ID. Value is average pixel intensity for that protein & cell. Note capitalisation in column names.
  --output OUTPUT       Output filename. File will be written to current directory in long format, input data repeated and classifications added.
  --controls CONTROLS [CONTROLS ...]
                        List of section ids (contained in Filename column of input file) corresponding to control sections
```

Once you have successfully launched mcclass on some appropriately formatted input data, follow the on-screen instructions.  Click on the image below to see a live demo of the re-analysis of some data from [Warren et al. (2020).](https://www.nature.com/articles/s41598-020-70885-3 ):

[![mcclass video](images/mcclass_vidframe.png)](https://vimeo.com/conor/mcclass)
