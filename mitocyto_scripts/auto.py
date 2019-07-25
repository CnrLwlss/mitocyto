from PIL import Image, ImageDraw
import os
import mitocyto as mc
import cv2
import numpy as np
import webbrowser
import sys

def main():
    global arrs, edgeim, current, fnames, showedges, showcontours, modifier, imtype, C, root, draw, wnew, hnew, C_image, inp, froots
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
    imcfiles = [f for f in allfiles if os.path.splitext(f)[1] in [".imc",".IMC"]]
    if(len(imcfiles)>0):
        print("Analysing data from "+imcfiles[0]+" only...")
        fnames, froots, current, arrs = mc.makeArrsFromText(imcfiles[0],edge = "Dystrophin", add_edit = "mitocyto.png")
    else:
        fnames, froots, current, arrs = mc.makeArrs(folder,edge = "Dystrophin", add_edit = "mitocyto.png")

    edgemapfile = os.path.join(output,"EDGE_"+add_edit)
    averagefile = os.path.join(output,"AVE_"+add_edit)
    if os.path.isfile(edgemapfile):
        edgeim = Image.open(edgemapfile)
        arrs["Edges"] = np.array(edgeim,dtype=np.uint8)

    edgeim = Image.fromarray(mc.makepseudo(arrs["Edges"]))
    draw = ImageDraw.Draw(edgeim)
    h,w = arrs[froots[current]].shape

    timer = mc.startTimer()
    print("Saving edited cell membrane file... "+str(timer()))
    Image.fromarray(mc.makepseudo(arrs["Edges"])).save(edgemapfile)
    print("Saving average of all channels... "+str(timer()))
    Image.fromarray(mc.makepseudo(arrs["Mean"])).save(averagefile)

    #for i in range(0, len(arrs)-2):
    #    Image.fromarray(mc.makepseudo(arrs[i])).save(files[i]+".png")
    
    print("Getting contours & saving preview... "+str(timer()))

    arrs["Edges"] = np.array(edgeim, dtype=np.uint8)
    thresh = mc.makethresholded(arrs["Edges"],False,d=inp.smoothdiam,sigmaColor=inp.smoothsig,sigmaSpace=inp.smoothsig,blockSize=inp.threshblock)
    rgb,contours = mc.makeContours(thresh,showedges=True,alim=(inp.areamin,inp.areamax),arlim=(inp.ratiomin,inp.ratiomax),clim=(inp.circmin,inp.circmax),cvxlim=(inp.convexmin, inp.convexmax),numbercontours=True)

    arr = arrs["Edges"]
    #arrs = None

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

    print("Average values for each contour mask in each image... "+str(timer()))
    avelogs = {froot:[np.exp(np.mean(np.log(arrs[froot][msk[0],msk[1]]+1))) for msk in masks] for froot in froots}
    aves = {froot:[np.mean(arrs[froot][msk[0],msk[1]]+1) for msk in masks] for froot in froots}
    meds = {froot:[np.median(arrs[froot][msk[0],msk[1]]+1) for msk in masks] for froot in froots}
    fracpos = {froot:[np.sum(arrs[froot][msk[0],msk[1]]>0)/len(msk[0]) for msk in masks] for froot in froots}

    print("Writing output to text file... "+str(timer()))
    res = open(os.path.join(output,"results.csv"),"w")
    res.write("Value,ID,Channel,Folder 1,Filename\n")

    for j,froot in enumerate(froots):
        print("Writing "+froot+" results to file... "+str(timer()))
        #res.writelines("\n".join([",".join([str(ml),str(i+1),froot,os.path.abspath(folder).split("\\")[-1],os.path.abspath(os.path.join(folder,fnames[j]))]) for i,ml in enumerate(avelogs[froot])]))
        res.writelines("\n".join([",".join([str(ml),str(i+1),fnames[j],os.path.basename(os.path.dirname(os.path.abspath(folder))),os.path.basename(os.path.abspath(folder))]) for i,ml in enumerate(aves[froot])]))
        res.write("\n")
        res.writelines("\n".join([",".join([str(ml),str(i+1),"LOG_"+fnames[j],os.path.basename(os.path.dirname(os.path.abspath(folder))),os.path.basename(os.path.abspath(folder))]) for i,ml in enumerate(avelogs[froot])]))
        res.write("\n")
        res.writelines("\n".join([",".join([str(ml),str(i+1),"MED_"+fnames[j],os.path.basename(os.path.dirname(os.path.abspath(folder))),os.path.basename(os.path.abspath(folder))]) for i,ml in enumerate(meds[froot])]))
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
