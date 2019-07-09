from PIL import Image, ImageDraw
import os
import mitocyto as mc
import cv2
import numpy as np
import webbrowser
import sys

def main():
    global arrs, edgeim, current, fnames, showedges, showcontours, modifier, imtype, C, root, draw, wnew, hnew, C_image, inp
    print("mitocyto "+mc.__version__)
    print("opencv "+cv2.__version__)
    inp = mc.getCommands()
    print("command executed:")
    print(" ".join(sys.argv))
    
    keymap = "1234567890qwertyuiopasdfg"
    add_edit = "mitocyto.png"
    folder = "."
    output = "."

    showedges = False
    showcontours = False
    modifier = False
    imtype = "raw"

    allfiles = os.listdir(folder)
    allfiles = [f for f in allfiles if os.path.splitext(f)[1] in [".tiff",".TIFF",".jpg",".JPG",".jpeg",".JPEG",".png",".PNG"]]
    files = [f for f in allfiles if add_edit not in f]
    files.sort()

    edge = "Dystrophin"
    isedge = [edge.lower() in f.lower() for f in files]
    edgeind = [i for i, x in enumerate(isedge) if x]
    if len(edgeind)>0:
        current = edgeind[0]
    else:
        current = 0

    arrs = [np.array(Image.open(f)) for f in files]
    #ims = [Image.fromarray(mc.makepseudo(arr)) for arr in arrs]
    #ims = [Image.fromarray(mc.makepseudo(np.array(Image.open(f)))) for f in files]
    bigarr = np.zeros(arrs[0].shape+(sum([not i for i in isedge]),),dtype=np.uint8)
    ind = 0
    for i,arr in enumerate(arrs):
        if not isedge[i]:
            bigarr[:,:,ind]=arr
            ind += 1
    #maxarr = np.max(bigarr,2)
    meanarr = np.mean(bigarr,2)
    #medianarr = np.median(bigarr,2)
    bigarr = None

    arrs = arrs + [meanarr,arrs[edgeind[0]]]
    
    fnames = files + ["Mean","Edges"]

    edgemapfile = os.path.join(output,"EDGE_"+add_edit)
    averagefile = os.path.join(output,"AVE_"+add_edit)
    if os.path.isfile(edgemapfile):
        edgeim = Image.open(edgemapfile)
        arrs[-1] = np.array(edgeim,dtype=np.uint8)

    edgeim = Image.fromarray(mc.makepseudo(arrs[-1]))
    draw = ImageDraw.Draw(edgeim)
    h,w = arrs[current].shape

    timer = mc.startTimer()
    print("Saving edited cell membrane file... "+str(timer()))
    Image.fromarray(mc.makepseudo(arrs[-1])).save(edgemapfile)
    print("Saving average of all channels... "+str(timer()))
    Image.fromarray(mc.makepseudo(arrs[-2])).save(averagefile)

    #for i in range(0, len(arrs)-2):
    #    Image.fromarray(mc.makepseudo(arrs[i])).save(files[i]+".png")
    
    print("Getting contours & saving preview... "+str(timer()))
    arr = arrs[-1]
    arrs = None


    thresh = mc.makethresholded(arr,False,d=inp.smoothdiam,sigmaColor=inp.smoothsig,sigmaSpace=inp.smoothsig,blockSize=inp.threshblock)
    rgb,contours = mc.makeContours(thresh,showedges=True,alim=(inp.areamin,inp.areamax),arlim=(inp.ratiomin,inp.ratiomax),clim=(inp.circmin,inp.circmax),cvxlim=(inp.convexmin, inp.convexmax),numbercontours=True)
    
    #rgb,contours = mc.makeContours(mc.makepseudo(arr))
    rgb.save(os.path.join(output,"CONTOURS_"+add_edit))
    print("Building masks from contours... "+str(timer()))
    masks = [mc.makemask(arr.shape,cnt) for cnt in contours]
    print("Building measures from contours... "+str(timer()))
    centres = [mc.getcentre(cnt) for cnt in contours]
    areas = [cv2.contourArea(cnt) for cnt in contours]
    aspects = [mc.getaspect(cnt) for cnt in contours]
    perims = [cv2.arcLength(cnt,True) for cnt in contours]
    circs = [mc.circularity(cnt) for cnt in contours]
    xvals = [c[0] for c in centres]
    yvals = [c[1] for c in centres]

    print("Opening channel images... "+str(timer()))
    fnames = fnames[0:-2]
    froots = [fname.strip(".ome.tiff") for fname in fnames]
    #images = {froot:Image.open(os.path.join(folder,fnames[i])) for i,froot in enumerate(froots)}
    arrays = {froot:np.array(Image.open(os.path.join(folder,fnames[i])),dtype=np.uint16) for i,froot in enumerate(froots)}
    #psims = {froot:mc.arrtorgb(arrays[froot]) for froot in froots}

    print("Average values for each contour mask in each image... "+str(timer()))
    avelogs = {froot:[np.exp(np.mean(np.log(arrays[froot][msk[0],msk[1]]+1))) for msk in masks] for froot in froots}
    aves = {froot:[np.mean(arrays[froot][msk[0],msk[1]]+1) for msk in masks] for froot in froots}
    meds = {froot:[np.median(arrays[froot][msk[0],msk[1]]+1) for msk in masks] for froot in froots}
    fracpos = {froot:[np.sum(arrays[froot][msk[0],msk[1]]>0)/len(msk[0]) for msk in masks] for froot in froots}

    print("Writing output to text file... "+str(timer()))
    res = open(os.path.join(output,"results.csv"),"w")
    res.write("Value,ID,Channel,Folder 1,Filename\n")

    for j,froot in enumerate(froots):
        print("Writing "+froot+" results to file... "+str(timer()))
        #res.writelines("\n".join([",".join([str(ml),str(i+1),froot,os.path.abspath(folder).split("\\")[-1],os.path.abspath(os.path.join(folder,fnames[j]))]) for i,ml in enumerate(avelogs[froot])]))
        res.writelines("\n".join([",".join([str(ml),str(i+1),froot,os.path.basename(os.path.dirname(os.path.abspath(folder))),os.path.basename(os.path.abspath(folder))]) for i,ml in enumerate(aves[froot])]))
        res.write("\n")
        res.writelines("\n".join([",".join([str(ml),str(i+1),"LOG_"+froot,os.path.basename(os.path.dirname(os.path.abspath(folder))),os.path.basename(os.path.abspath(folder))]) for i,ml in enumerate(avelogs[froot])]))
        res.write("\n")
        res.writelines("\n".join([",".join([str(ml),str(i+1),"MED_"+froot,os.path.basename(os.path.dirname(os.path.abspath(folder))),os.path.basename(os.path.abspath(folder))]) for i,ml in enumerate(meds[froot])]))
        res.write("\n")
    for channel,vals in zip(["Area","AspectRatio","Perimeter","Circularity","xCoord","yCoord"],[areas,aspects,perims,circs,xvals,yvals]):
        print("Writing "+channel+" results to file... "+str(timer()))
        res.writelines("\n".join([",".join([str(ml),str(i+1),channel,os.path.basename(os.path.dirname(os.path.abspath(folder))),os.path.basename(os.path.abspath(folder))]) for i,ml in enumerate(vals)]))
        res.write("\n")
    res.close()

if __name__ == '__main__':
    try:
        main()
    except:
        mc.time.sleep(5)
