import glob
import os
import shutil

def main(addtag):

    probs = ["Pt.ome.tiff","89Y.ome.tiff","Xe.ome.tiff","Ar.ome.tiff","Cs.ome.tiff","Ba.ome.tiff","Gd.ome.tiff","Eu.ome.tiff","Sm.ome.tiff","Nd.ome.tiff","Rh.ome.tiff","DNA2.ome.tiff","DNA1.ome.tiff","Os.ome.tiff","Er.ome.tiff","Ho.ome.tiff"]

    dirs = glob.glob('./**/', recursive=True)

    addtag = False
    tag = ".ARCHIVE"

    for d in dirs:
        files = os.listdir(d)
        for f in files:
            if addtag:
                for prob in probs:
                    if prob in f and tag not in f:
                        src = os.path.join(d,f)
                        dst = os.path.join(d,f+".ARCHIVE")
                        print("Renaming "+src+" to "+dst+"...")
                        try:
                            shutil.move(src,dst)
                        except:
                            print("Problem tagging "+src+"...")
            else:
                if tag in f:
                    fnew = f.replace(tag,"")
                    src = os.path.join(d,f)
                    dst = os.path.join(d,fnew)
                    print("Renaming "+src+" to "+dst+"...")
                    try:
                        shutil.move(src,dst)
                    except:
                        print("Problem untagging "+src+"...")
                
if __name__=="__main__":
    main(True)


