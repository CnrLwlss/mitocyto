from PIL import Image
import numpy as np
import cv2
import mitocyto as mc

im = Image.open("pre_orig.png")
arr = np.array(im,dtype=np.uint8)

alim = (25,200)
d,sig,bs = 5,271,19
thresh = mc.makethresholded(arr,True,d=d,sigmaColor=sig,sigmaSpace=sig,blockSize=bs)
imnew,contours = mc.makeContours(thresh,showedges = True,alim=alim,numbercontours=False)
print(len(contours))
imnew.show()

# mcgui --areamin 25 --areamax 200 --smoothdiam 5 --smoothsig 271 --threshblock 19
