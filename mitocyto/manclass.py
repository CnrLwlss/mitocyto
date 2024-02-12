import numpy as np
import platform

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


def classify(fname="dat.txt",outfname="class_dat.txt",getWarren=True,mitochan="VDAC1",oxchans=["NDUFB8","MTCO1"],controls=["C01","C02","C03","C04","C05","C06","C07","C08","C09","C10","C11","C12"]):
    import matplotlib.pyplot as plt
    import pandas as pd
    import os

    if getWarren:
        warrenurl = "https://raw.githubusercontent.com/CnrLwlss/Warren_2019/master/shiny/Warren_2020_chans.csv"
        warrenfile = "Warren_2020_data.txt"
        if not os.path.isfile(warrenfile):
            print("No "+warrenfile+" file found, downloading data from Warren et al. (2020)...")
            dat = pd.read_csv(warrenurl,sep=",",header=0)
            dat.to_csv(warrenfile,sep=",",index=False)
        else:
            dat = pd.read_csv(warrenfile,sep=",",header=0)
    else:
        dat = pd.read_csv(fname,sep=",",header=0)
    dat.drop('Unnamed: 0', axis=1, inplace=True, errors="ignore")  
    pats = sorted(set(dat.Filename))
    pats.sort()
    
    allchans = sorted(set(dat.Channel))
    print("All available channels:")
    print(allchans)

    for pat in pats:
      for chan in oxchans:
        def selectFibres(ftype="deficient"):
            xpat = dat.Value[(dat.Channel==mitochan)&(dat.Filename==pat)]
            ypat = dat.Value[(dat.Channel==chan)&(dat.Filename==pat)]

            xctrl = dat.Value[(dat.Channel==mitochan)&(dat.Filename.isin(controls))]
            yctrl = dat.Value[(dat.Channel==chan)&(dat.Filename.isin(controls))]
            
            xpat = np.log(xpat)
            ypat = np.log(ypat)
            xctrl = np.log(xctrl)
            yctrl = np.log(yctrl)
            xlab = "log("+mitochan+")"
            ylab = "log("+chan+")"
            
            if ftype=="deficient":
              patcol = [1.0,0.0,0.0,0.3]
              pcstr = "red"
            if ftype=="overexp":
              patcol = [0.0,0.0,1.0,0.2]
              pcstr = "blue"
              
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

            if platform.system()=="Windows":
                figManager = plt.get_current_fig_manager()
                figManager.window.showMaximized()

            plt.show()
            if type(selector.ind) is str and selector.ind=="BREAK!":
                res = "BREAK!"
                return(res)
            res = np.full(len(xpat),False)
            res[selector.ind] = True
            return(res)
          
        mclass = dict()
        for ftype in ["deficient","overexp"]:
          mclass[ftype] = selectFibres(ftype)
          if np.isin("BREAK!",mclass[ftype]):
              print("Saving partial classification file...")
              dat.to_csv("dat_with_class_partial.txt",sep=",",index=False)
              raise Found
          d = dat[(dat.Channel==chan)&(dat.Filename==pat)].copy()
          d.Channel = chan+"_MCLASS_"+ftype.upper()
          d.Value = mclass[ftype]
          dat = pd.concat([dat,d])

    dat.to_csv(outfname,sep=",",index=False)

if __name__ == '__main__':
    try:
        classify(fname="dat.txt",outfname="class_dat.txt",getWarren=True,mitochan="VDAC1",oxchans=["NDUFB8","MTCO1"])
    except Found:
        print("Finished early and saved partial classification file")
