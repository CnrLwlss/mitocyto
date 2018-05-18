from PIL import Image
import numpy as np
import os
import scipy
from scipy import ndimage
import cv2
import colorsys
import time
import matplotlib.pyplot as plt
import skimage as ski
from skimage import restoration, filters, feature, segmentation, morphology, transform, draw
# Microsoft Visual C++ 14.0 is required. Get it with "Microsoft Visual C++ Build Tools": http://landinghub.visualstudio.com/visual-cpp-build-tools
import pandas as pd

def makeContours(arr,showedges = True, thickness = cv2.FILLED):
    arr[0,:-1] = arr[:-1,-1] = arr[-1,::-1] = arr[-2:0:-1,0] = arr.max()
    im2,contours,hierarchy = cv2.findContours(arr, 1, 2)
    contours = tidy(contours, alim=(500,9000), arlim=(0,10.0), clim=(0,100), cvxlim=(0.75,1.0))
    if showedges:
        todraw = arr
    else:
        todraw = np.zeros(arr.shape,dtype=np.uint8)
    rgb = Image.fromarray(drawcontours(todraw,contours,list(range(1,len(contours)+1)),thickness=thickness))
    return((rgb,contours))

def getthresh(arr, block_size=221):
    locthresh = filters.threshold_local(arr, block_size=block_size, offset=0)
    thresh = 255*(arr > (locthresh))
    return(thresh)

def edgesFromGrad(arr, block_size = 11, fname = "", delta = 6200):
    gy,gx= np.gradient(arr)
    grad = np.abs(np.hypot(gx,gy))
    if fname != "":
        Image.fromarray(np.array(np.round(65535.0*grad/np.max(grad)),dtype=np.uint16)).save(fname)
    #edges = np.zeros(grad.shape,dtype=np.uint8)
    #edges[grad>40000]=255
    locthresh = filters.threshold_local(np.abs(grad), block_size=block_size, offset=0)
    edgemask = np.abs(grad) > locthresh + delta
    edges = morphology.binary_dilation(morphology.skeletonize(morphology.remove_small_objects(edgemask,200)),selem=morphology.disk(1))
    #edges = edgemask
    return(np.array(edges,dtype=np.uint8))

#https://github.com/ShawnLYU/Quantile_Normalize
def quantileNormalize(df_input):
    df = df_input.copy()
    #compute rank
    dic = {}
    for col in df:
        dic.update({col : sorted(df[col])})
    sorted_df = pd.DataFrame(dic)
    rank = sorted_df.mean(axis = 1).tolist()
    #sort
    for col in df:
        t = np.searchsorted(np.sort(df[col]), df[col])
        df[col] = [rank[i] for i in t]
    return df

def findmembranes(arr_raw):
    '''Morphological operations to find cell membranes from dystrophin channel, or similar'''
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    kernelsm = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

    # Need to check here that the values in arr lie between 0 and 255!
    arr = np.array(arr_raw,dtype=np.uint8)

    recipe = [
        (cv2.dilate,kernelsm),
        (cv2.dilate,kernelsm),
        (cv2.dilate,kernelsm),
        #(cv2.dilate,kernel),
        #(cv2.dilate,kernel),
        #(cv2.erode,kernel),
        (cv2.erode,kernelsm),
        (cv2.erode,kernelsm),
        (cv2.erode,kernelsm)
        ]
    
    #arrf = ndimage.gaussian_filter(arr,0.3)
    #arrf = cv2.GaussianBlur(arr, ksize=(3,3),sigmaX=0,sigmaY=0)
    #arrf = cv2.medianBlur(arr,3)
    
    #arrf = cv2.bilateralFilter(arr,d=9,sigmaColor=1555,sigmaSpace=1555)
    #ret,thresh = cv2.threshold(arrf.astype(np.uint8),1,255,cv2.THRESH_BINARY)

    arrf = restoration.denoise_bilateral(arr,11,sigma_color=3,sigma_spatial=3,multichannel=False)
    Image.fromarray(makepseudo(arrf)).show()

    #glob_thresh = filters.threshold_otsu(arrf)
    #thresh = np.array(255*(arrf > glob_thresh/2.0),dtype=np.uint8)
    locthresh = filters.threshold_local(arrf, block_size=21, offset=0)
    thresh = arrf > (locthresh)
    Image.fromarray(makepseudo(255*thresh)).show()
    threshclean = morphology.remove_small_objects(thresh,600)      
    Image.fromarray(makepseudo(255*threshclean)).show()
    #thresh = morphology.skeletonize(thresh)
    #Image.fromarray(makepseudo(255*thresh)).show()
    #thresh = morphology.binary_dilation(thresh)
    #Image.fromarray(makepseudo(255*thresh)).show()

    thresh = np.array(255*thresh,dtype=np.uint8)
    comb0 = threshorig(arr,thresh)
    for func,kern in recipe:
      thresh = func(thresh,kern)
      Image.fromarray(makepseudo(thresh)).show()
    ithresh = cv2.bitwise_not(thresh)
    return((ithresh,comb0,threshorig(arr,thresh)))

def arrtorgb(arr):
    arrp = makepseudo(arr)
    rgb = np.zeros(arr.shape+(3,),'uint8')
    rgb[:,:,0] = arrp 
    rgb[:,:,1] = arrp 
    rgb[:,:,2] = arrp
    return(rgb)

def drawcontours(arr,contours,labels=[],thickness=cv2.FILLED):
    rgb = arrtorgb(arr)
    uselabs = len(labels)==len(contours)
    for i,cnt in enumerate(contours):
        h,s,l = np.random.random(), 1.0, 0.4 + np.random.random()/5.0
        r,g,b = [int(256*i) for i in colorsys.hls_to_rgb(h,l,s)]
        col = np.random.randint(50,200)
        cv2.drawContours(rgb,[cnt],-1,(r,g,b),thickness)
        if uselabs:
            cX,cY = getcentre(cnt)
            cv2.putText(rgb, str(labels[i]), (cX-5, cY+5),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    return(rgb)

def drawcentres(arr,contours,labels=[],ptrad=3):
    rgb = arrtorgb(arr)
    h,w = arr.shape
    uselabs = len(labels)==len(contours)
    for i,cnt in enumerate(contours):
        cX,cY = getcentre(cnt)
        cv2.circle(rgb, (cX,cY), ptrad, (255, 0, 0), -1)
        if uselabs:
            cv2.putText(rgb, str(i+1), (min(w-10,max(10,cX - 20)), min(h-10,max(10,cY - 10))),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            cv2.putText(rgb, str(labels[i]), (cX - 20, cY + 20),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
    return(rgb)
        
def getcentre(cnt):
    M = cv2.moments(cnt)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    return((cX,cY))

def makemask(shape,cnt):
    mask = np.zeros(shape)
    cv2.drawContours(mask,[cnt],-1,255,thickness=1)
    #return(mask>0)
    return(np.where(mask == 255))

def savearr(arr,fname):
    Image.fromarray(arr).save(fname, quality=80, optimize=True, progressive=True)

def makepseudo(arr,minpercent=5,maxpercent=95):
    minval,maxval = np.percentile(arr.flatten(),[minpercent,maxpercent])
    if(maxval>minval):
        arr = np.maximum(np.minimum(arr,maxval),minval)
        arr = arr-minval
        arrf = np.array(arr,dtype=np.float)
        arrf = np.array(np.round(255.0*np.minimum(1.0,arrf/(maxval-minval))),dtype=np.uint8)
    else:
        arrf = np.array(arr[:,:],dtype=np.uint8)
    return(arrf)

def threshorig(arr,thresh):
    parr = makepseudo(arr)
    rgbthresh = arrtorgb(thresh)
    rgbarr = arrtorgb(parr)
    rgbarr[:,:,1]=0
    rgbarr[:,:,2]=0
    rgbthresh[arr>np.min(parr)]=rgbarr[arr>np.min(parr)]
    return(rgbthresh)

def getaspect(cnt):
    x,y,w,h = cv2.boundingRect(cnt)
    aspect_ratio = float(w)/h
    return(aspect_ratio)

def circularity(cnt):
    return(4*np.pi*cv2.contourArea(cnt)/(cv2.arcLength(cnt,True)**2))

def tidy(contours, alim = (0,999999), arlim=(0,9999999), clim=(0,9999999), cvxlim=(0.0,1.0)):
    cnew = [cnt for cnt in contours if
            (alim[0] < cv2.contourArea(cnt) < alim[1]) and
            (arlim[0] < getaspect(cnt) < arlim[1]) and
            (clim[0] < circularity(cnt) < clim[1]) and
            (cvxlim[0] < cv2.contourArea(cnt)/cv2.contourArea(cv2.convexHull(cnt)) < cvxlim[1])
            ]
    return(cnew)

def startTimer():
    '''Returns time since last time function called'''
    t0 = [time.time()]
    def getTime():
        t1 = time.time()
        delta = t1-t0[0]
        t0[0] = time.time()
        return("%.2f" % delta)
    return(getTime)
