import mitocyto as mc
import argparse

def classCommands():
    parser = argparse.ArgumentParser(description="Manual classification of cells in 2Dmito plots.  Reads in single cell protein expression data from input file.  Identifies control subjects and patients.  Generates a series of 2D scatterplots showing relationship between an OXPHOS protein and a protein which is a surrogate for mitochondrial mass (e.g. VDAC1).  User compares increase in OXPHOS protein with mitochondrial mass in single cells from controls with the increase in a single patient and uses that comparison to inform a manual selection of patient cells where increase of OXPHOS protein with mitochondrial mass would be an outlier in control data.  Manual selection is by freehand drawing around the cells on scatterplot which are distinct from controls.")
    parser.add_argument("--mitochan", default="VDAC1", help="Mitochondrial mass surrogate protein name.  Must be present in Channel column of input file.")
    parser.add_argument("--oxphos", default=["MTCO1","NDUFB8"], help="List of OXPHOS proteins to classify, separated by space.  Names specified in Channel column of input file.",nargs="+")
    parser.add_argument("--warren", help="Classify data from Warren et al. (2020)?", action=argparse.BooleanOptionalAction)
    # Note that you now have --warren and --no-warren, which is canonical way to parse Booleans on commandline
    parser.add_argument("--input", default="dat.txt", help="Tab-delimited input text filename.  Input data should be in long form and contain data from controls and patient(s).  Each subject/section should have a unique identifier specified in the Filename column.  Data can have extra colums, but the following columns must be present: Value,ID,Channel,Filename  ID is cell ID.  Value is average pixel intensity for that protein & cell.  Note capitalisation in column names.")
    parser.add_argument("--output", default="class_dat.txt", help="Output filename.  File will be written to current directory in long format, input data repeated and classifications added.")
    parser.add_argument("--controls",default=["C01","C02","C03","C04","C05","C06","C07","C08","C09","C10","C11","C12"], help="List of section ids (contained in Filename column of input file) corresponding to control sections",nargs="+")
    return(parser.parse_args())

def main():
    try:
        c = classCommands()
        mc.classify(fname=c.input,outfname=c.output,getWarren=c.warren,mitochan=c.mitochan,oxchans=c.oxphos)
    except mc.Found:
        print("Finished early and saved partial classification file")
