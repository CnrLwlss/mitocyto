import tkinter as tk
from PIL import ImageTk, Image, ImageDraw
import os
import detectfibres as df
import cv2
import numpy as np

def makeContours(arr,showedges = True):
    arr[0,:-1] = arr[:-1,-1] = arr[-1,::-1] = arr[-2:0:-1,0] = arr.max()
    im2,contours,hierarchy = cv2.findContours(arr, 1, 2)
    contours = df.tidy(contours, alim=(200,9000), arlim=(0,10.0), clim=(0,100), cvxlim=(0.75,1.0))
    if showedges:
        todraw = arr
    else:
        todraw = np.zeros(arr.shape,dtype=np.uint8)
    rgb = Image.fromarray(df.drawcontours(todraw,contours,list(range(1,len(contours)+1))))
    return((rgb,contours))

def key(event):
    global img,current,ims, showedges, showcontours, draw, imtype
    curr0 = current
    k = event.keysym
    copying = False
    print("pressed", k)
    if k in keymap:
        i = keymap.find(k)
        if i < len(fnames):
            current = i
    if k =="x":
        print("Clearing edge image")
        clearEdges()
    if k == "c":
        copying = True
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
    if showcontours and current is not curr0:
        showcontours = False
    if showedges and current is not curr0:
        showedges = False
    if showedges and current is curr0:
        current = -1
    if showcontours:
        arr = np.array(ims[-1],dtype=np.uint8)
        imnew,contours = makeContours(arr,showedges)
        title = "Contours"
        C.delete("dot")
        root.title(title)
        img = ImageTk.PhotoImage(imnew.resize((wnew,hnew),Image.ANTIALIAS))
        C.itemconfig(C_image, image=img)
    else:
        imnew = ims[current]
        title = fnames[current]+" "+keymap[current]
        if current is not curr0:
            C.delete("dot")
            root.title(title)
            img = ImageTk.PhotoImage(imnew.resize((wnew,hnew),Image.ANTIALIAS))
            C.itemconfig(C_image, image=img)
    if copying:
        print("Copying current image to edge image")
        arr_orig = np.array(ims[-1])
        arr_new = np.array(ims[current])
        ims[-1] = Image.fromarray(np.maximum(arr_orig,arr_new))
        draw = ImageDraw.Draw(ims[-1])

def paint(event, colour = "white", rad = 2, sclx=1.0, scly=1.0):
    x1, y1 = ( event.x - rad ), ( event.y - rad )
    x2, y2 = ( event.x + rad ), ( event.y + rad )
    C.create_oval( x1, y1, x2, y2, fill = colour, outline=colour, tags="dot")
    if colour == "white": pcolour = 255
    if colour == "black": pcolour = 0
    draw.ellipse((int(round(float(x1)/sclx)), int(round(float(y1)/scly)), int(round(float(x2)/sclx)), int(round(float(y2)/scly))), fill = pcolour, outline=pcolour)

def clearEdges():
    global ims
    ims[-1] = Image.fromarray(np.zeros(ims[0].size[::-1],dtype=np.uint8))

keymap = "1234567890qwertyuiopasdfghjkl"
add_edit = "mitoim.png"
folder = "."
output = "."

showedges = False
showcontours = False
makeedges = False

files = os.listdir(folder)
files = [f for f in files if os.path.splitext(f)[1] in [".tiff",".TIFF",".jpg",".JPG",".jpeg",".JPEG",".png",".PNG"]]
files = [f for f in files if add_edit not in f]
files.sort()

edge = "Dystrophin"
isedge = [edge.lower() in f.lower() for f in files]
edgeind = [i for i, x in enumerate(isedge) if x]
current = edgeind[0]

ims = [Image.fromarray(df.makepseudo(np.array(Image.open(f)))) for f in files]
bigarr = np.zeros(ims[0].size[::-1]+(sum([not i for i in isedge]),),dtype=np.uint8)
ind = 0
for i,im in enumerate(ims):
    if not isedge[i]:
        bigarr[:,:,ind]=np.array(im)
        ind += 1
maxarr = np.max(bigarr,2)
meanarr = np.mean(bigarr,2)
medianarr = np.median(bigarr,2)
bigarr = None

ims = ims + [Image.fromarray(df.makepseudo(meanarr)),None]
clearEdges()
fnames = files + ["Mean","Edges"]

draw = ImageDraw.Draw(ims[-1])
w,h = ims[current].size

#Start the GUI
root = tk.Tk()
root.title(fnames[current]+" "+keymap[current])

# Prepare to resize images to fit in screen, if necessary
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

if w>screen_width:
    scl = float(screen_width)/float(w)
if scl*h>screen_height:
    scl = float(screen_height)/float(h)

wnew,hnew = int(round(scl*w)), int(round(scl*h))
sclx,scly = float(wnew)/float(w), float(wnew)/float(w)

img = ImageTk.PhotoImage(ims[current].resize((wnew,hnew),Image.ANTIALIAS))
C = tk.Canvas(root,width = wnew, height = hnew)
C_image = C.create_image(0,0,image=img,anchor='nw')

C.focus_set()
C.bind("<Key>", key)
C.bind("<B1-Motion>", lambda event: paint(event, colour = "white", rad = 2*scl, sclx = sclx, scly = scly))
C.bind("<B3-Motion>", lambda event: paint(event, colour = "black", rad = 5*scl, sclx = sclx, scly = scly))

C.pack()

root.mainloop()

timer = df.startTimer()
print("Saving edited cell membrane file... "+str(timer()))
ims[-1].save(os.path.join(output,"EDGE_"+add_edit))
print("Getting contours & saving preview... "+str(timer()))
arr = np.array(ims[-1],dtype=np.uint8)
ims = None

rgb,contours = makeContours(arr)
rgb.save(os.path.join(output,"CONTOURS_"+add_edit))
print("Building masks from contours... "+str(timer()))
masks = [df.makemask(arr.shape,cnt) for cnt in contours]
print("Building measures from contours... "+str(timer()))
centres = [df.getcentre(cnt) for cnt in contours]
areas = [cv2.contourArea(cnt) for cnt in contours]
aspects = [df.getaspect(cnt) for cnt in contours]
perims = [cv2.arcLength(cnt,True) for cnt in contours]
circs = [df.circularity(cnt) for cnt in contours]

print("Opening channel images... "+str(timer()))
fnames = fnames[0:-2]
froots = [fname.strip(".ome.tiff") for fname in fnames]
images = {froot:Image.open(os.path.join(folder,fnames[i])) for i,froot in enumerate(froots)}
arrays = {froot:np.array(images[froot],dtype=np.int) for froot in froots}
#psims = {froot:df.arrtorgb(arrays[froot]) for froot in froots}

print("Average values for each contour mask in each image... "+str(timer()))
avelogs = {froot:[np.mean(np.log(arrays[froot][msk[0],msk[1]]+1)) for msk in masks] for froot in froots}
fracpos = {froot:[np.sum(arrays[froot][msk[0],msk[1]]>0)/len(msk[0]) for msk in masks] for froot in froots}

print("Writing output to text file... "+str(timer()))
res = open(os.path.join(output,"results.csv"),"w")
res.write("Value,ID,Channel,Folder 1,Filename\n")

for j,froot in enumerate(froots):
    print("Writing "+froot+" results to file... "+str(timer()))
    res.writelines("\n".join([",".join([str(ml),str(i+1),froot,os.path.abspath(folder).split("\\")[-1],os.path.abspath(os.path.join(folder,fnames[j]))]) for i,ml in enumerate(avelogs[froot])]))
    res.write("\n")
res.close()
