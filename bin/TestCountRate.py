''' scripts to test if we are below the pileup count rate threshold'''
from astropy.io import fits
from astropy.table import Table
import sys



if __name__ == "__main__":

    file = sys.argv[1]
    ffits = fits.open(file)

    cutoff = 0.5

    # convert spectra to Table
    tabl_spec = Table.read(ffits[1])
    rate = sum(tabl_spec["COUNTS"]) / tabl_spec.meta["EXPOSURE"]

    print ("\n\n########################\n\n")
    print ("\t\tCount Rate: %0.2f cts/s" %(rate))
    print ("\n\n########################\n\n")
    if ( rate <= cutoff ):
        sys.exit(0)
    else:
        sys.exit(1)
