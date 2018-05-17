import glob
import os
import shutil

def main():
    resultsdir = "mitocyto_merged_output"
    files = glob.glob('./**/results.csv', recursive=True)
    files = [f for f in files if resultsdir not in f]

    dirs = [os.path.dirname(f) for f in files]
    bases = [os.path.basename(d) for d in dirs]

    print("Building "+resultsdir+" directory...")
    if not os.path.exists(resultsdir):
        os.makedirs(resultsdir)

    outf = "mitocyto_merged_results.csv"
    print("Merging results.csv files to "+outf+"...")
    fout=open(os.path.join(resultsdir,outf),"w")
    for line in open(files[0]):
        fout.write(line)    
    for fname in files[1:]:
        f = open(fname)
        f.readline() 
        for line in f:
             fout.write(line)
        f.close() 
    fout.close()

    print("Copying image files...")
    for d in dirs:
        string = d.replace(".","").replace("\\","_")+"_"
        for x in ["CONTOURS_mitocyto.png","AVE_mitocyto.png","EDGE_mitocyto.png"]:
            src = os.path.join(d,x)
            dst = os.path.join(resultsdir,string+x)
            try:
                shutil.copyfile(src,dst)
            except:
                print(src+" missing?")


if __name__ == "__main__":
    main()
