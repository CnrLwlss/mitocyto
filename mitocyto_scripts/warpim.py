from PIL import Image, ImageTk, ImageDraw
Image.MAX_IMAGE_PIXELS = None
import numpy as np
import cv2

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
    global edges, edgescl, C
    def delta(event):
        if event.num == 5 or event.delta < 0:
            return -1 
        return 1
    
    if(delta(event))>0:
        edgerat = 1.005
        edgescl = edgescl * edgerat
    else:
        edgerat = 0.995
        edgescl = edgescl * edgerat
    print("New scaling factor: "+ str(scl / edgescl))
    print("Scaling, please wait...")
    #edges = edges0.resize([int(round(x*scl)) for x,scl in zip(edges0.size,[edgerat,edgerat])])
    edges = edge_orig.resize([int(round(x*s)) for x,s in zip(edge_orig.size,[edgescl,edgescl])],Image.ANTIALIAS)
    ew0,eh0 = edges0.size
    ew,eh = edges.size
    ex,ey = C.coords(C.C_edge)[:]
    C.edgeim = ImageTk.PhotoImage(edges)
    C.delete(C.C_edge)
    C.C_edge = C.create_image(int(ex), int(ey), image = C.edgeim)
    
    #C.scale(C.C_edge, lastx, lasty, edgescl, edgescl)
    C.pack(fill="both", expand=True)

def cropim(event, dcrop = 50):
    global edges, microscreen, micro, C, ws, hs, edgex, edgey, microimg, edgeimg, edgescl, scl, wi, hi, x0, y0
    print("Cropping, please wait...")
    we, he = edges.size
    unscale = float(micro.size[0])/float(microscreen.size[0])
    print("unscale: ",unscale)
    x0, y0 = (edgex - dcrop)*unscale, (edgey - dcrop)*unscale
    microscreen = micro.crop([x0, y0, (edgex+we+dcrop)*unscale,(edgey+he+dcrop)*unscale])
#    edgex, edgey = dcrop, dcrop

    wi, hi = microscreen.size

    if (float(wi)/float(hi)) > (float(ws)/float(hs)):
        scl = float(ws)/float(wi)
    else:
        scl = float(hs)/float(hi)
    print("scl: ",scl)
    wnew,hnew = int(round(scl*wi)), int(round(scl*hi))

    microscreen = microscreen.resize((wnew,hnew),Image.ANTIALIAS)
    dnew = float(dcrop)*hnew/(he + 2.0*dcrop)
    #edgescl = (scl*hi - 2.0*dnew)/he
    edgescl = (dnew/dcrop)*(he/edge_orig.size[1])
    print("edgescl: ",edgescl)
    #edges0 = edge_orig.resize([int(round(scl*wi - 2.0*dnew)), int(round(scl*hi- 2.0*dnew))], Image.ANTIALIAS)
    edges0 = edge_orig.resize([int(round(x*s)) for x, s in zip(edge_orig.size,[edgescl,edgescl])],Image.ANTIALIAS)
    edges = edges0.copy()

    microimg = ImageTk.PhotoImage(microscreen)
    edgeimg = ImageTk.PhotoImage(edges)

    C.delete(C.C_micro)
    C.delete(C.C_edge)

    C.C_micro = C.create_image(0, 0, image = microimg, anchor = 'nw')
    C.C_edge = C.create_image(int(round(dnew)), int(round(dnew)), image = edgeimg, anchor = 'nw')

    C.pack(fill="both", expand=True)

def finished(event):
    root.destroy()
    root.quit()

print("Opening images...")
edgepath = "H:\\charlotte W cytof\\patient\\m0164\\EDGE_mitocyto.png"
micropath = "E:\\IONRDW\\IF\\comb1\\M0164-12 OXPHOS-Image Export-02\\M0164-12 OXPHOS-Image Export-02_c1+2+3+4.tif"
edge_orig = Image.open(edgepath).convert("RGBA")
micro = Image.open(micropath)

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
scl0 = 3.1273
edgescl = scl0 * scl
count = 0
background = []
foreground = []
x0, y0 = 0, 0
print("Resizing images to fit screen...")
microscreen = micro.resize((wnew,hnew),Image.ANTIALIAS)
edges0 = edge_orig.resize([int(round(x*s)) for x,s in zip(edge_orig.size,[edgescl,edgescl])],Image.ANTIALIAS)
edges = edges0.copy()
#microscreen.paste(edges,(0,0),edges)

print("scl: ",scl)
print("edgescl: ",edgescl)

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
C.bind('<Escape>', finished)

C.focus_set() # Give canvas a keyboard focus!!

root.mainloop()

if len(background)>0:
    prad = 10
    microresult = micro.crop([x0, y0, x0 + wi, y0 + hi])
    edgeim = Image.open(edgepath).resize([int(round(m*edgescl/scl)) for m in edge_orig.size],Image.ANTIALIAS)
    edgeresult = Image.new(edgeim.mode,microresult.size)
    ox, oy = [int(round((m-e)/2.0)) for m,e in zip(microresult.size,edgeim.size)]
    bground = [[int(round(x/scl)),int(round(y/scl))] for x,y in background]
    fground = [[int(round(ox + x/scl)),int(round(oy + y/scl))] for x,y in foreground]
    edgeresult.paste(edgeim,[ox,oy])
    
    draw = ImageDraw.Draw(microresult)
    pts = [draw.ellipse([(x-prad,y-prad),(x+prad,y+prad)],fill="white") for x,y in bground]
    microresult.save("Micro.jpg")
    draw = ImageDraw.Draw(edgeresult)
    pts = [draw.ellipse([(x-prad,y-prad),(x+prad,y+prad)],fill="white") for x,y in fground]
    edgeresult.save("Edge.png")
    edgearr = np.array(edgeresult,dtype=np.uint8)
    bmap = np.array(bground,dtype=np.uint8)
    fmap = np.array(fground,dtype=np.uint8)
    #warpedge = cv2.remap(np.array(edgeresult,dtype=np.uint8),fmap,bmap,interpolation=cv2.INTER_LANCZOS4)
    

    
    
