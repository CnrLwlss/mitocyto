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
import pandas as pd
import webbrowser
import sys
import re

def clearEdges():
    global arrs,edgeim, froots
    arrs["Edges"] = np.zeros(arrs[froots[0]].shape,dtype=np.uint8)
    edgeim = Image.fromarray(arrs["Edges"])

def key(event,keymap):
    global img,current,ims, arrs, showedges, showcontours, draw, imtype, edgeim, contours, inp, froots
    
    curr0 = current
    k = event.keysym
    if k not in ["Shift_L","Shift_R"]:
        showcontours = False
    copying = False
    #print("pressed", k)
    if k in keymap:
        i = keymap.find(k)
        if i < len(froots):
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
        current = (current - 1)%len(froots)
    if k == "Right":
        current = (current + 1)%len(froots)
    if k == "Escape":
        root.destroy()
        root.quit()
        return()
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
            arrs["Edges"] = np.array(edgeim, dtype=np.uint8)
            thresh = mc.makethresholded(arrs["Edges"],False, d=inp.smoothdiam,sigmaColor=inp.smoothsig,sigmaSpace=inp.smoothsig,blockSize=inp.threshblock)
            imnew,contours = mc.makeContours(thresh,showedges = True,alim=(inp.areamin,inp.areamax),arlim=(inp.ratiomin,inp.ratiomax),clim=(inp.circmin,inp.circmax),cvxlim=(inp.convexmin, inp.convexmax),numbercontours=False)
            #title = "mitocyto Contours"
            if current<len(keymap):
                kk = keymap[current]
            else:
                kk = ""
            title = "mitocyto {} {} shortcut: {} press 'h' for help".format(imtype,froots[current],kk)
            C.delete("dot")
            root.title(title)
            blobs = imnew.resize((wnew,hnew),Image.ANTIALIAS).convert("RGBA")
            chann = Image.fromarray(mc.arrtorgb(arrs[froots[current]])).resize((wnew,hnew),Image.ANTIALIAS).convert("RGBA")
            merg = Image.blend(blobs,chann,alpha=0.6)
            img = ImageTk.PhotoImage(merg)
            C.itemconfig(C_image, image=img)
            #showcontours = False
        else:
            if imtype == "raw":
                arrnew = arrs[froots[current]]
                #title = "mitocyto Raw "+title
            if imtype == "threshold":
                arrnew = mc.getthresh(arrs[froots[current]])
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
            if current == len(froots):
                fn = "AVERAGE"
                sc = ""
            elif current == len(froots)+1:
                fn = "EDGE"
                sc = "z"
            elif 0 <= current < len(froots):
                fn = froots[current]
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
        arrs["Edges"] = np.array(edgeim, dtype=np.uint8)
        arrs["Edges"] = np.maximum(arrs["Edges"],arrnew)
        edgeim = Image.fromarray(mc.makepseudo(arrs["Edges"]))
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
        cv2.drawContours(arrs["Edges"],[cnt],-1,(255),cv2.FILLED)
    edgeim = Image.fromarray(mc.makepseudo(arrs["Edges"]))
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
    global arrs, edgeim, current, froots, showedges, showcontours, modifier, imtype, C, root, draw, wnew, hnew, C_image,sclx,scly, inp
    print("mitocyto "+mc.__version__)
    print("opencv "+cv2.__version__)
    inp = mc.getCommands()
    print("command executed:")
    print(" ".join(sys.argv))

    fext = [".imc",".IMC"]
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

    clearEdges()

    edgemapfile = os.path.join(output,"EDGE_"+add_edit)
    averagefile = os.path.join(output,"AVE_"+add_edit)
    if os.path.isfile(edgemapfile):
        edgeim = Image.open(edgemapfile)
        arrs["Edges"] = np.array(edgeim,dtype=np.uint8)

    edgeim = Image.fromarray(mc.makepseudo(arrs["Edges"]))
    draw = ImageDraw.Draw(edgeim)
    h,w = arrs[froots[current]].shape

    #Start the GUI
    root = tk.Tk()
    imtype = "raw"
    if current<len(keymap):
        kk = keymap[current]
    else:
        kk = ""
    title = "mitocyto {} {} shortcut: {} press 'h' for help".format(imtype,froots[current],kk)
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

    img = ImageTk.PhotoImage(Image.fromarray(mc.makepseudo(arrs[froots[current]])).resize((wnew,hnew),Image.ANTIALIAS))
    C = tk.Canvas(root,width = wnew, height = hnew)
    C_image = C.create_image(0,0,image=img,anchor='nw')

    C.focus_set()
    C.bind("<B1-Motion>", lambda event: paint(event, colour = "white", rad = 1, sclx = sclx, scly = scly))
    C.bind("<B3-Motion>", lambda event: paint(event, colour = "black", rad = 5, sclx = sclx, scly = scly))
    C.bind("<Shift-Button-1>", lambda event: fillcontour(event))
    C.bind("<KeyPress>", lambda event: checkmod(event, keymap = keymap, press = True))
    C.bind("<KeyRelease>", lambda event: checkmod(event, keymap = keymap, press = False))
            
    C.pack()

    root.mainloop()
    arrs["Edges"] = np.array(edgeim,dtype=np.uint8)

    timer = mc.startTimer()
    print("Saving edited cell membrane file... "+str(timer()))
    Image.fromarray(mc.makepseudo(arrs["Edges"])).save(edgemapfile)
    print("Saving average of all channels... "+str(timer()))
    Image.fromarray(mc.makepseudo(arrs["Mean"])).save(averagefile)

    #for i in range(0, len(arrs)-2):
    #    Image.fromarray(mc.makepseudo(arrs[i])).save(files[i]+".png")
    
    print("Getting contours & saving preview... "+str(timer()))
    arr = arrs["Edges"]
    #arrs = None
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
    #images = {froot:Image.open(os.path.join(folder,fnames[i])) for i,froot in enumerate(froots)}
    #arrays = {froot:np.array(Image.open(os.path.join(folder,fnames[i])),dtype=np.uint16) for i,froot in enumerate(froots)}
    #arrays = {froot:np.array(images[froot],dtype=np.uint16) for froot in froots}
    #psims = {froot:mc.arrtorgb(arrays[froot]) for froot in froots}

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
