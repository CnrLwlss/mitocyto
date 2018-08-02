from PIL import Image, ImageTk
Image.MAX_IMAGE_PIXELS = None
import numpy as np

import tkinter as tk

global count, C_edge, edges, C, C_newedge

def RBGAImage(path):
    return Image.open(path).convert("RGBA")

def next_image(event):
    global edgex, edgey, lastx, lasty
    dx, dy = event.x - lastx, event.y - lasty
    edgex, edgey = edgex + dx, edgey + dy
    lastx, lasty = lastx + dx, lasty + dy
    C.move(C.C_edge, dx, dy)
    draw(background,foreground)

def set_root(event):
    global lastx, lasty
    lastx, lasty = event.x, event.y

def annotate(event,r = 2):
    ex,ey = C.coords(C.C_edge)[:]
    background.append([event.x,event.y])
    foreground.append([event.x - ex, event.y - ey])
    C.create_oval(event.x - r, event.y - r, event.x + r, event.y + r, fill="blue", tags="maplines")

def draw(back,fore,r = 2):
    ex,ey = C.coords(C.C_edge)[:]
    C.delete("maplines")
    for b,f in zip(background,foreground):
        C.create_oval(b[0] - r, b[1] - r, b[0] + r, b[1] + r, fill="blue", tags="maplines")
        C.create_line(b[0],b[1],f[0]+ex,f[1]+ey,fill="red",width=2,tags="maplines")
        C.create_oval(f[0]+ex - r, f[1]+ey - r, f[0]+ex + r, f[1]+ey + r, fill="blue", tags="maplines")
        
# Mouse wheel handler for Mac, Windows and Linux
# Windows, Mac: Binding to <MouseWheel> is being used
# Linux: Binding to <Button-4> and <Button-5> is being used

def MouseWheelHandler(event):
    global count, edges, edgescl

    def delta(event):
        if event.num == 5 or event.delta < 0:
            return -1 
        return 1
    
    if(delta(event))>0:
        edgescl = edgescl * 1.005
        count+=1
    else:
        edgescl = edgescl * 0.995
        count-=1
    print("New scaling factor: "+ str(scl0 * edgescl))
    print("Scaling, please wait...")
    edges = edges0.resize([int(round(x*scl)) for x,scl in zip(edges0.size,[edgescl,edgescl])])
    ew0,eh0 = edges0.size
    ew,eh = edges.size
    ex,ey = C.coords(C.C_edge)[:]
    C.edgeim = ImageTk.PhotoImage(edges)
    C.delete(C.C_edge)
    C.C_edge = C.create_image(int(ex), int(ey), image = C.edgeim)
    
    C.scale(C.C_edge, lastx, lasty, edgescl, edgescl)
    C.pack(fill="both", expand=True)

def cropim(event, dcrop = 50):
    global edges, microscreen, micro, C, ws, hs, edgex, edgey, microimg, edgeimg, newscl
    print("Cropping, please wait...")
    we, he = edges.size
    unscale = float(micro.size[0])/float(microscreen.size[0])
    microscreen = micro.crop([(edgex - dcrop)*unscale, (edgey - dcrop)*unscale,(edgex+we+dcrop)*unscale,(edgey+he+dcrop)*unscale])
#    edgex, edgey = dcrop, dcrop

    wi, hi = microscreen.size

    if (float(wi)/float(hi)) > (float(ws)/float(hs)):
        newscl = float(ws)/float(wi)
    else:
        newscl = float(hs)/float(hi)

    #newscl = newscl * scl2
    wnew,hnew = int(round(newscl*wi)), int(round(newscl*hi))

    microscreen = microscreen.resize((wnew,hnew),Image.ANTIALIAS)
    #edges0 = edge_orig.resize([int(round(newscl*wi - 2.0*newscl*dcrop/unscale)), int(round(newscl*hi- 2.0*newscl*dcrop/unscale))],Image.ANTIALIAS)
    dnew = float(dcrop)*hnew/(he + 2*dcrop)
    edges0 = edge_orig.resize([int(round(newscl*wi - 2.0*dnew)), int(round(newscl*hi- 2.0*dnew))], Image.ANTIALIAS)
    edges = edges0.copy()

    microimg = ImageTk.PhotoImage(microscreen)
    edgeimg = ImageTk.PhotoImage(edges)

    C.delete(C.C_micro)
    C.delete(C.C_edge)

    C.C_micro = C.create_image(0, 0, image = microimg, anchor = 'nw')
    C.C_edge = C.create_image(int(round(dnew)), int(round(dnew)), image = edgeimg, anchor = 'nw')

    C.pack(fill="both", expand=True)

print("Opening images...")
edge_orig = RBGAImage("H:\\charlotte W cytof\\patient\\m0164\\EDGE_mitocyto.png")
micro = RBGAImage("E:\\IONRDW\\IF\\comb1\\M0164-12 OXPHOS-Image Export-02\\M0164-12 OXPHOS-Image Export-02_c1+2+3+4.tif")

print("Converting black in edge image to transparent...")
whitealpha = 0.5
edgearr = np.array(edge_orig)
edgearr[...,3] = np.array(np.round(edgearr[...,2] * whitealpha),dtype=np.uint8)
edge_orig  = Image.fromarray(edgearr)

print("Starting the GUI...")
root = tk.Tk()
title = "warping images"
root.title(title)

# Prepare to resize images to fit in screen, if necessary
ws = root.winfo_screenwidth()
hs= root.winfo_screenheight()
root.geometry('%dx%d+%d+%d' % (ws, hs, 0, 0))

wi,hi = micro.size

if (float(wi)/float(hi)) > (float(ws)/float(hs)):
    scl = float(ws)/float(wi)
else:
    scl = float(hs)/float(hi)
    
wnew,hnew = int(round(scl*wi)), int(round(scl*hi))
sclx,scly = float(wnew)/float(wi), float(hnew)/float(hi)

edgex, edgey = 0, 0
lastx, lasty = 0, 0
scl0 = 3.13
edgescl = 1.0
newscl = scl0 * scl * edgescl
count = 0
background = []
foreground = []

print("Resizing images to fit screen...")
microscreen = micro.resize((wnew,hnew),Image.ANTIALIAS)
edges0 = edge_orig.resize([int(round(x*scl)) for x,scl in zip(edge_orig.size,[newscl,newscl])],Image.ANTIALIAS)
edges = edges0.copy()
#microscreen.paste(edges,(0,0),edges)

microimg = ImageTk.PhotoImage(microscreen)
edgeimg = ImageTk.PhotoImage(edges)

C = tk.Canvas(root, width = wnew, height = hnew)

C.C_micro = C.create_image(0, 0, image = microimg, anchor = 'nw')
C.C_edge = C.create_image(edgex, edgey, image = edgeimg, anchor = 'nw')

C.pack(fill="both", expand=True)

C.bind("<MouseWheel>",MouseWheelHandler)
C.bind("<Button-4>",MouseWheelHandler)
C.bind("<Button-5>",MouseWheelHandler) 

C.bind('<Button-1>', set_root)
C.bind('<Button-3>', annotate)
C.bind('<B1-Motion>', next_image)
C.bind('c', cropim)
C.focus_set() # Give canvas a keyboard focus!!

root.mainloop()
