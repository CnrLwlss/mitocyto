try:
    # for Python2
    import Tkinter as tk
except ImportError:
    # for Python3
    import tkinter as tk
from PIL import ImageTk, Image, ImageDraw
import os
import mitocyto as mc
import cv2
import numpy as np
import webbrowser
import sys

def clearEdges():
    global arrs,edgeim
    arrs[-1] = np.zeros(arrs[0].shape,dtype=np.uint8)
    edgeim = Image.fromarray(arrs[-1])

def key(event,keymap):
    global img,current,ims, arrs, showedges, showcontours, draw, imtype, edgeim, contours, inp
    
    curr0 = current
    k = event.keysym
    if k not in ["Shift_L","Shift_R"]:
        showcontours = False
    copying = False
    #print("pressed", k)
    if k in keymap:
        i = keymap.find(k)
        if i < len(fnames):
            current = i
    if k =="x":
        print("Clearing edge image")
        clearEdges()
    if k == "c":
        copying = True
    if k =="h":
        webbrowser.open("https://github.com/CnrLwlss/mitocyto/blob/master/README.md")
    if k == "b":
        if imtype == "threshold":
            imtype = "raw"
        else:
            imtype = "threshold"
    if k == "n":
        if imtype == "edgemap":
            imtype = "raw"
        else:
            imtype = "edgemap"
    if k == "Left":
        current = (current - 1)%len(fnames)
    if k == "Right":
        current = (current + 1)%len(fnames)
    if k == "Escape":
        root.destroy()
        root.quit()
    if k == "space":
        showcontours = not showcontours
    if k == "z":
        showedges = not showedges
    #if showcontours and current is not curr0:
    #    showcontours = False
    if showedges and current is not curr0:
        showedges = False
    if showedges and current is curr0:
        current = -1
    if not modifier:
        if showcontours:
            arrs[-1] = np.array(edgeim, dtype=np.uint8)
            thresh = mc.makethresholded(arrs[-1],False, d=inp.smoothdiam,sigmaColor=inp.smoothsig,sigmaSpace=inp.smoothsig,blockSize=inp.threshblock)
            imnew,contours = mc.makeContours(thresh,showedges = True,alim=(inp.areamin,inp.areamax),arlim=(inp.ratiomin,inp.ratiomax),clim=(inp.circmin,inp.circmax),cvxlim=(inp.convexmin, inp.convexmax),numbercontours=False)
            #title = "mitocyto Contours"
            title = "mitocyto {} {} shortcut: {} press 'h' for help".format(fnames[current],imtype,keymap[current])
            C.delete("dot")
            root.title(title)
            blobs = imnew.resize((wnew,hnew),Image.ANTIALIAS).convert("RGBA")
            chann = Image.fromarray(mc.arrtorgb(arrs[current])).resize((wnew,hnew),Image.ANTIALIAS).convert("RGBA")
            merg = Image.blend(blobs,chann,alpha=0.6)
            img = ImageTk.PhotoImage(merg)
            C.itemconfig(C_image, image=img)
            #showcontours = False
        else:
            if imtype == "raw":
                arrnew = arrs[current]
                #title = "mitocyto Raw "+title
            if imtype == "threshold":
                arrnew = mc.getthresh(arrs[current])
                #title = "mitocyto Threshold "+title  
            if imtype == "edgemap":
                arrnew = mc.edgesFromGrad(arrs[current],block_size=51)
                #title = "mitocyto Edgemap "+title
            if current == -1 or current == len(arrs) - 1:
                imnew = edgeim
            else:
                imnew = Image.fromarray(mc.makepseudo(arrnew))
            #if current is not curr0:
            C.delete("dot")
            if current == len(fnames):
                fn = "AVERAGE"
                sc = ""
            elif current == len(fnames)+1:
                fn = "EDGE"
                sc = "z"
            elif 0 <= current < len(fnames):
                fn = fnames[current]
                if 0<= current < len(keymap):
                    sc = keymap[current]
                else:
                    sc = ""
            else:
                fn = ""
                sc = ""
            title = "mitocyto {} {} shortcut: {} press 'h' for help".format(imtype, fn ,sc)
            root.title(title)
            img = ImageTk.PhotoImage(imnew.resize((wnew,hnew),Image.ANTIALIAS))
            C.itemconfig(C_image, image=img)
    if copying:
        print("Copying current image to edge image")
        arrs[-1] = np.array(edgeim, dtype=np.uint8)
        arrs[-1] = np.maximum(arrs[-1],arrnew)
        edgeim = Image.fromarray(mc.makepseudo(arrs[-1]))
        draw = ImageDraw.Draw(edgeim)

def paint(event, colour = "white", rad = 2, sclx=1.0, scly=1.0):
    global arrs, draw, edgeim
    if not modifier:
        x1, y1 = ( event.x - rad ), ( event.y - rad )
        x2, y2 = ( event.x + rad ), ( event.y + rad )
        C.create_oval( x1, y1, x2, y2, fill = colour, outline=colour, tags="dot")
        if colour == "white": pcolour = 255
        if colour == "black": pcolour = 0
        draw.ellipse((int(round(float(x1)/sclx)), int(round(float(y1)/scly)), int(round(float(x2)/sclx)), int(round(float(y2)/scly))), fill = pcolour, outline=pcolour)

def fillcontour(event):
    global arrs, contours, edgeim, draw, sclx, scly
    point = (int(round(float(event.x)/sclx)), int(round(float(event.y)/scly)))
    clicked = [(i,cnt) for i,cnt in enumerate(contours) if cv2.pointPolygonTest(cnt, point, measureDist = False) >= 0]
    for i,cnt in clicked:
        print("Deleting contour number "+str(i+1))
        cv2.drawContours(arrs[-1],[cnt],-1,(255),cv2.FILLED)
    edgeim = Image.fromarray(mc.makepseudo(arrs[-1]))
    draw = ImageDraw.Draw(edgeim)

def checkmod(event, keymap, modkeys = ["Shift_L","Shift_R"], press = True):
    global modifier
    if event.keysym in modkeys:
        if modifier is not press:
            modifier = press
            #print("Modifier: "+str(modifier))
    elif press:
        key(event, keymap)

def main():       
    global arrs, edgeim, current, fnames, showedges, showcontours, modifier, imtype, C, root, draw, wnew, hnew, C_image,sclx,scly, inp
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

    arrs = arrs + [meanarr,None]
    clearEdges()
    fnames = files + ["Mean","Edges"]

    edgemapfile = os.path.join(output,"EDGE_"+add_edit)
    averagefile = os.path.join(output,"AVE_"+add_edit)
    if os.path.isfile(edgemapfile):
        edgeim = Image.open(edgemapfile)
        arrs[-1] = np.array(edgeim,dtype=np.uint8)

    edgeim = Image.fromarray(mc.makepseudo(arrs[-1]))
    draw = ImageDraw.Draw(edgeim)
    h,w = arrs[current].shape

    #Start the GUI
    root = tk.Tk()
    imtype = "raw"
    title = "mitocyto {} {} shortcut: {} press 'h' for help".format(imtype,fnames[current],keymap[current])
    root.title(title)

    # Prepare to resize images to fit in screen, if necessary
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    if w>screen_width:
        scl = float(screen_width)/float(w)
    else:
        scl = 1.0
    if scl*h>screen_height:
        scl = float(screen_height)/float(h)

    wnew,hnew = int(round(scl*w)), int(round(scl*h))
    sclx,scly = float(wnew)/float(w), float(hnew)/float(h)

    img = ImageTk.PhotoImage(Image.fromarray(mc.makepseudo(arrs[current])).resize((wnew,hnew),Image.ANTIALIAS))
    C = tk.Canvas(root,width = wnew, height = hnew)
    C_image = C.create_image(0,0,image=img,anchor='nw')

    C.focus_set()
    C.bind("<B1-Motion>", lambda event: paint(event, colour = "white", rad = 1, sclx = sclx, scly = scly))
    C.bind("<B3-Motion>", lambda event: paint(event, colour = "black", rad = 5, sclx = sclx, scly = scly))
    C.bind("<Shift-Button-1>", lambda event: fillcontour(event))
    C.bind("<KeyPress>", lambda event:  checkmod(event, keymap = keymap, press = True))
    C.bind("<KeyRelease>", lambda event: checkmod(event, keymap = keymap, press = False))
            
    C.pack()

    root.mainloop()
    arrs[-1] = np.array(edgeim,dtype=np.uint8)

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
    #arrays = {froot:np.array(images[froot],dtype=np.uint16) for froot in froots}
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
