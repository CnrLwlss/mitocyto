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
    
if __name__ == "__main__":
    fmembrane = "176Yb_Dystrophin.ome.tiff"
    folders = ["control 1 mo355\control 1 m0355-16 analysis\control 1","Control 2 m1212\control 2 m1212 analysis\ROI003_ROI 03","Patient 2 m1105\patient M1105 analysis\ROI001_ROI 01"]
    folders = folders[2:3]
    for folder in folders:

        timer = startTimer()

        foldroot = folder.split("\\")[0]
        output = foldroot + "_results"

        if not os.path.exists(output):
            os.makedirs(output)


        # Drop loading controls and failed channels
        drop = ["133Cs","134Xe","138Ba","158Gd","89Y","80ArAr","208Pb","195Pt","TOMM20","DNA1","DNA2"]
        fnames = [fname for fname in os.listdir(folder) if fname.endswith(".tiff") and (sum([d in fname for d in drop])==0)]
        froots = [fname.strip(".ome.tiff") for fname in fnames]

        print("Opening channel images... "+str(timer()))
        images = {froot:Image.open(os.path.join(folder,fnames[i])) for i,froot in enumerate(froots)}
        arrays = {froot:np.array(images[froot],dtype=np.int) for froot in froots}
        psims = {froot:arrtorgb(arrays[froot]) for froot in froots}

        notmembrane = [f for f in froots if "Dystrophin" not in f]
        scaled = np.zeros(list(arrays[froots[0]].shape)+[len(notmembrane)])
        for i,froot in enumerate(notmembrane):
            scaled[:,:,i] = (arrays[froot]-arrays[froot].mean())/arrays[froot].std()
        combn = np.max(scaled,axis=2)
        if combn.min()<0: combn += -1*combn.min()
        savearr(makepseudo(combn),"B_combn.png")
        combns = restoration.denoise_bilateral(combn,31,sigma_color=300,sigma_spatial=4,multichannel=False)
        combnsm = filters.median(combn/255.0)*255.0
        savearr(makepseudo(combns),"B_combns.png")
        #Image.fromarray(makepseudo(combns)).show()

        gy,gx= np.gradient(combns)
        grad = np.hypot(gx,gy)

        #Image.fromarray(makepseudo(np.maximum(0,combn-arrays['168Er_Cox4']))).show()
        
        savearr(makepseudo(grad),"combnsgrad2.png")
        #edges = np.zeros(grad.shape,dtype=np.uint8)
        #edges[grad>0.05]=255
        locthresh = filters.threshold_local(np.abs(grad), block_size=11, offset=0)
        edgemask = np.abs(grad) > (locthresh+0.01)
        #Image.fromarray(255*edgemask).show()
        edges = morphology.binary_dilation(morphology.skeletonize(morphology.remove_small_objects(edgemask,200)),selem=morphology.disk(1))
        Image.fromarray(255*edges).save("combnsgrad2_edges.png")

##        fig,ax1 = plt.subplots()
##        ax1.plot(combns[500,:])
##        ax2 = ax1.twinx()
##        ax2.plot([0 for x in grad[500,:]],color="grey")
##        ax2.plot(gx[500,:],color="red")
##        plt.show()
        
        arr = arrays['168Er_Cox4']
        savearr(makepseudo(arr),"A_original.png")
        savearr(makepseudo(arrays['176Yb_Dystrophin']),"C_membranes.png")
    
        arrarr = np.array([arrays[f] for f in froots])
        for f in froots:
            print(f,arrays[f].min(),arrays[f].max())
            arr = np.array(arrays[f],dtype=np.uint8)
            arr = cv2.GaussianBlur(arr, ksize=(7,7),sigmaX=0,sigmaY=0)
            arr = makepseudo(arr)
    
        im = Image.open(os.path.join(folder,fmembrane))
        arr = np.array(im,dtype=np.int)
        arr[edges] = np.percentile(arr,95)
        Image.fromarray(makepseudo(arr)).save("Test.png")
        ithresh,comb0,combN = findmembranes(arr)
    
        im2,contours,hierarchy = cv2.findContours(ithresh, 1, 2)
        print(str(len(contours))+" contours found")
    
        print("Filtering contours... "+str(timer()))
        #contours = tidy(contours, alim=(250,5800), arlim=(0.5,2.0), clim=(0.35,1.4))
        #contours = tidy(contours, alim=(450,580000), arlim=(0,3.0), clim=(0.35,1.4))
        contours = tidy(contours, alim=(200,5000), arlim=(0,10.0), clim=(0,100), cvxlim=(0.75,1.0))
        print("Building masks from contours... "+str(timer()))
        masks = [makemask(arr.shape,cnt) for cnt in contours]
        print("Building measures from contours")
        centres = [getcentre(cnt) for cnt in contours]
        areas = [cv2.contourArea(cnt) for cnt in contours]
        aspects = [getaspect(cnt) for cnt in contours]
        perims = [cv2.arcLength(cnt,True) for cnt in contours]
        circs = [circularity(cnt) for cnt in contours]
    
        rgb = drawcontours(arr,contours,list(range(1,len(contours)+1)),thickness=1)
        savearr(rgb,os.path.join(output,"Contours.png"))
        #Image.fromarray(rgb).show()

        rgb = drawcontours(ithresh,contours,list(range(1,len(contours)+1)),thickness=1)
        savearr(rgb,os.path.join(output,"Contours_Thresh.png"))
        #Image.fromarray(rgb).show()
    
        print("Building 4 panel preview... "+str(timer()))
        h,w=arr.shape
        panels = np.zeros([x*2 for x in rgb.shape[0:2]]+[rgb.shape[2]],dtype=np.uint8)
        panels[0:h,0:w] = arrtorgb(makepseudo(arr))
        panels[0:h,w:2*w] = comb0
        panels[h:2*h,0:w] = combN
        panels[h:2*h,w:2*w] = rgb
        #Image.fromarray(panels).show()
        savearr(panels,os.path.join(output,"Panels.png"))
    
        fnames = [fname for fname in os.listdir(folder) if fname is not fmembrane and fname.endswith(".tiff")]
        froots = [fname.strip(".ome.tiff") for fname in fnames]
    
        print("Opening channel images... "+str(timer()))
        images = {froot:Image.open(os.path.join(folder,fnames[i])) for i,froot in enumerate(froots)}
        arrays = {froot:np.array(images[froot],dtype=np.int) for froot in froots}
        psims = {froot:arrtorgb(arrays[froot]) for froot in froots}
    
        print("Average values for each contour mask in each image... "+str(timer()))
        avelogs = {froot:[np.mean(np.log(arrays[froot][msk[0],msk[1]]+1)) for msk in masks] for froot in froots}
        fracpos = {froot:[np.sum(arrays[froot][msk[0],msk[1]]>0)/np.sum(msk[0],msk[1]) for msk in masks] for froot in froots}
    
        print("Writing output to text file... "+str(timer()))
        res = open(os.path.join(output,foldroot+"_results.csv"),"w")
        res.write("Value,ID,Channel,Folder 1,Filename\n")
    
        print(folder)
        for froot in froots:
            print("Writing "+froot+" results to file... "+str(timer()))
            res.writelines("\n".join([",".join([str(ml),str(i+1),froot,folder,froot]) for i,ml in enumerate(avelogs[froot])]))
            res.write("\n")
            print("Drawing "+froot+" centres on image... "+str(timer()))
            labs = ["{0:.3}".format(num) for num in avelogs[froot]]
            rgb = drawcentres(arrays[froot],contours,labs)
            savearr(rgb,os.path.join(output,froot+"_centres.jpg"))
        res.close()
