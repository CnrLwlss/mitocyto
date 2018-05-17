import multiprocessing as mp
import psutil
import mitocyto_scripts as mcs
import glob
import os

def runauto(d):
    '''Execute one of several mitocyto jobs in a multiprocessing pool'''
    current = os.path.abspath(os.curdir)
    os.chdir(d)
    mcs.auto.main()
    os.chdir(current)
    return d+" complete"

def main():
    with mp.Pool(processes=cpus) as pool:
        print(pool.map(runauto, tiffdirs))   

dirs = glob.glob('./**/', recursive=True)
tiffdirs = []
for d in dirs:
    adding = False
    flist = os.listdir(d)
    for f in flist:
        if f.endswith("tiff"):
            adding = True
    if adding:
        tiffdirs.append(d)

#checking = map(runauto,tiffdirs)
cpus = psutil.cpu_count(logical=False)
print("Running mitocyto.auto on {} CPUs...".format(cpus))

if __name__ == '__main__':
    main()
    
