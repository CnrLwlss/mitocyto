import numpy as np

from matplotlib.widgets import LassoSelector
from matplotlib.path import Path

class Found(Exception): pass

class SelectFromCollection:
    """
    Select indices from a matplotlib collection using `LassoSelector`.

    Selected indices are saved in the `ind` attribute. This tool fades out the
    points that are not part of the selection (i.e., reduces their alpha
    values). If your collection has alpha < 1, this tool will permanently
    alter the alpha values.

    Note that this tool selects collection objects based on their *origins*
    (i.e., `offsets`).

    Parameters
    ----------
    ax : `~matplotlib.axes.Axes`
        Axes to interact with.
    collection : `matplotlib.collections.Collection` subclass
        Collection you want to select from.
    alpha_other : 0 <= float <= 1
        To highlight a selection, this tool sets all selected points to an
        alpha value of 1 and non-selected points to *alpha_other*.
    """

    def __init__(self, ax, collection, alpha_other=0.3):
        self.canvas = ax.figure.canvas
        self.collection = collection
        self.alpha_other = alpha_other

        self.xys = collection.get_offsets()
        self.Npts = len(self.xys)

        # Ensure that we have separate colors for each object
        self.fc = collection.get_facecolors()
        if len(self.fc) == 0:
            raise ValueError('Collection must have a facecolor')
        elif len(self.fc) == 1:
            self.fc = np.tile(self.fc, (self.Npts, 1))

        self.lasso = LassoSelector(ax, onselect=self.onselect)
        self.ind = []

    def onselect(self, verts):
        path = Path(verts)
        self.ind = np.nonzero(path.contains_points(self.xys))[0]
        self.fc[:, -1] = self.alpha_other
        self.fc[self.ind, -1] = 1.0
        self.collection.set_facecolors(self.fc)
        self.canvas.draw_idle()

    def disconnect(self):
        self.lasso.disconnect_events()
        #self.fc[:, -1] = 1
        self.collection.set_facecolors(self.fc)
        self.canvas.draw_idle()


def main():
    import matplotlib.pyplot as plt
    import pandas as pd
    import os

    warrenurl = "https://raw.githubusercontent.com/CnrLwlss/Warren_2019/master/shiny/dat.txt"
    warrenfile = "dat.txt"
    if not os.path.isfile(warrenfile):
        print("No dat.txt file found, downloading data from Warren et al. (2020)...")
        warrendat = pd.read_csv(warrenurl,sep="\t")
        warrendat.to_csv(warrenfile,sep="\t")
    else:
        warrendat = pd.read_csv(warrenfile,sep="\t")
    mitochan = "VDAC1"
    oxchans = ["NDUFB8","UqCRC2","SDHA","COX4+4L2","GRIM19","MTCO1","OSCP"]
    pats = sorted(set(warrendat.patient_id))
    pats.sort()

    for pat in pats:
      for chan in oxchans:
        def selectFibres(ftype="deficient"):
            xpat = warrendat.value[(warrendat.channel==mitochan)&(warrendat.patient_id==pat)]
            ypat = warrendat.value[(warrendat.channel==chan)&(warrendat.patient_id==pat)]

            xctrl = warrendat.value[(warrendat.channel==mitochan)&(warrendat.patient_type=="control")]
            yctrl = warrendat.value[(warrendat.channel==chan)&(warrendat.patient_type=="control")]
            
            if ftype=="deficient":
              patcol = [1.0,0.0,0.0,0.3]
              pcstr = "red"
              xpat = np.log(xpat)
              ypat = np.log(ypat)
              xctrl = np.log(xctrl)
              yctrl = np.log(yctrl)
              xlab = "log("+mitochan+")"
              ylab = "log("+chan+")"
            if ftype=="overexp":
              patcol = [0.0,0.0,1.0,0.2]
              pcstr = "blue"
              xlab = mitochan
              ylab = chan
              
            maxx = np.max(np.concatenate((xpat.values,xctrl.values)))
            maxy = np.max(np.concatenate((ypat.values,yctrl.values)))

            subplot_kw = dict(xlim=(-0.1*maxx, 1.2*maxx), ylim=(-0.1*maxy, 1.2*maxy), autoscale_on=False)
            fig, ax = plt.subplots(subplot_kw=subplot_kw)

            ctrlpts = plt.scatter(xctrl, yctrl, s=30,color=[0.0,0.0,0.0,0.2],edgecolors=None,linewidths=0.0)
            patpts = plt.scatter(xpat,ypat,s=10,color=patcol,edgecolors=None,linewidths=0.0)

            ax.set_xlabel(xlab)
            ax.set_ylabel(ylab)
            
            selector = SelectFromCollection(ax, patpts,alpha_other=0.05)

            def accept(event):
              if event.key == "enter":
                selector.disconnect()
                plt.close()
              if event.key == "q":
                selector.disconnect()
                plt.close()
                selector.ind = "BREAK!"

            fig.canvas.mpl_connect("key_press_event", accept)
            ax.set_title(pat+": Select and press enter to define selected "+pcstr+" points as "+ftype)

            figManager = plt.get_current_fig_manager()
            figManager.window.showMaximized()

            plt.show()
            if selector.ind=="BREAK!":
                res = "BREAK!"
                return(res)
            res = np.full(len(xpat),False)
            res[selector.ind] = True
            return(res)
          
        mclass = dict()
        for ftype in ["deficient","overexp"]:
          mclass[ftype] = selectFibres(ftype)
          if mclass[ftype]=="BREAK!":
              print("Saving partial classification file...")
              warrendat.to_csv("dat_with_class_partial.txt",sep="\t")
              raise Found
          wd = warrendat[(warrendat.channel==chan)&(warrendat.patient_id==pat)].copy()
          wd.channel = chan+"_MCLASS_"+ftype.upper()
          wd.value = mclass[ftype]
          warrendat = pd.concat([warrendat,wd])

    warrendat.to_csv("dat_with_class.txt",sep="\t")

if __name__ == '__main__':
    try:
        main()
    except Found:
        print("Finished early and saved partial classification file")
