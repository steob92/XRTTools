# XRTTools
Analysis Tools for XRT Data

Includes bash scripts for automated XRT analysis

## Pre-requisites

Download and install the [HEASoft](https://heasarc.gsfc.nasa.gov/docs/software/heasoft/) package and the HEASARC Calibration Database ([CALDB](https://heasarc.gsfc.nasa.gov/docs/heasarc/caldb/caldb_intro.html))

After downloading and installing HEASoft and CALDB, make sure to initialize them every time you start a new session.
For that, set the environmental variables:
```
export HEADAS=<path to HEASoft build dir>/heasoft-6.xx/x86_64-pc-linux-gnu-libc2.17/
export CALDB=<path to CALDB build dir>/caldb/
```
### Initialization

One can initialize HEASoft and CALDB by setting:
```
alias heainit=". $HEADAS/headas-init.sh"
alias caldbinit=". $CALDB/software/tools/caldbinit.sh"
```

and

```
heainit
caldbinit
```

---

## Downloading data from HEASARC

Download data from HEASARC:

1. Go to https://heasarc.gsfc.nasa.gov/cgi-bin/W3Browse/w3browse.pl
2. Type in the object name
3. Check the **Swift** box
4. Click on **Start Search**
5. Select the observations you would like to download by clicking on the white boxes on the left side of screen
6. Unmark **Swift UVOT Data** in case you don't want them
7. Click on the **Retrieve Data Products for selected rows** link
8. Click on **Retrieve** button and wait until TAR file is created.  This may take up to 5 minutes depending on how many files you are retrieving

Now you can retrieve the data using the link to the tar file using, e.g., `wget full_path_link_from_webpage` and untar the data `tar -xvf w3browse-num.tar`

---

# Using XRTTools

XRTTools contains:

* scripts to manage the processing of *Level 1* data files into *Level 2* (cleaned event-lists), the data reduction into *Level 3* files, and basic testing
* a python module that serves as wrapper of [PyXspec](https://heasarc.gsfc.nasa.gov/xanadu/xspec/python/html/index.html) basic functionalities

A more detailed view into the data structure and analysis is provided [here](https://www.swift.ac.uk/analysis/xrt/files.php).

## Running the Analysis

### XRTPipeline

First, one needs to run `bin/XRTPipeline.sh`. This script runs the HEASoft [xrtpipeline](https://www.swift.ac.uk/analysis/xrt/xrtpipeline.php)(please refer to the link for more detailed instructions) for a given data set of a particular source, stored in `Data/`.

Usage:
```
./bin/XRTPipeline.sh -r SourceRA -d SourceDec -f /Path/To/Data/Files"
```
Example:
```
./bin/XRTPipeline.sh -r 356.77015 -d 51.70497 -f /1ES2344/Swift-XRT/
```
where `/1ES2344/Swift-XRT/` is expected to have a `Data/` directory that contains `OBS_ID/xrt/` and `OBS_ID/auxil/`.
Outputs are written to `/1ES2344/Swift-XRT/Reprocessed/`.

### ReduceXRT

After running `XRTPipeline.sh`, one needs now to run `bin/ReduceXRT.sh`.
This script will:
1. Create symbolic links to the required [RMF files](https://www.swift.ac.uk/analysis/xrt/rmfs.php) provided with CALDB, that were used during the *xrtpipeline* routine
2. Using [xselect](https://www.swift.ac.uk/analysis/xrt/xselect.php), extract images using the cleaned event-list file generated with *xrtpipeline*
3. Correct [pile-up](https://www.swift.ac.uk/analysis/xrt/pileup.php) effects for observations taken in *Photon Counting* mode
4. Using *xselect*, extract the observed count spectrum from previously defined on and off source regions
5. Using [xrtmkarf](https://heasarc.gsfc.nasa.gov/ftools/caldb/help/xrtmkarf.html), generate Ancillary Response Files ([ARF](https://www.swift.ac.uk/analysis/xrt/arfs.php))
6. And group all required files, using [grppha](https://heasarc.gsfc.nasa.gov/lheasoft/ftools/fhelp/grppha.txt)

Usage:
```
./bin/ReduceXRT.sh -r SourceRA -d SourceDec -f /Path/To/Reduced/Files -p /path/to/pileup.csv
```

Example:
```
./bin/ReduceXRT.sh -r 356.77015 -d 51.70497 -f ./1ES2344/Swift-XRT/Reduced/ -p ./pileup.csv
```
where RA and Dec are in degrees.
`./1ES2344/Swift-XRT/Reduced/` contains `OBS_ID/sw<OBS_ID>*cl.evt`
`pileup.csv` is in the format `OBS_ID,NPIXELS`

### TestReduction

**Optionally**, one can use `TestReduction.sh` to:
* Check which mode has a higher exposure time (WT modes are favoured) and generate a run selection file
* Test if all required files were generated (or properly linked) during the XRTPipeline and ReduceXRT routines

Usage:
```
./bin/TestReduction.sh -f /Path/To/Reduced/Files
```

Example:
```
./bin/TestReduction.sh -f ./1ES2344/Swift-XRT/Reduced/
```

---

## XRTAnalysis

The [XRTAnalysis](https://github.com/steob92/XRTTools/blob/master/XRTAnalysis/XRTAnalysis.py) module contains a class and methods that facilitate the use of the *PyXspec* package, and a module to calculate the deabsorbed spectrum.

To start an usual *XRTAnalysis* session, do:

```python
In [1]: from XRTAnalysis import XRT_Analysis as xrt
In [2]: analysis = xrt() # initialize the class
```

To load a grouped pha file from inside it's origin directory (`<SOURCE>/Reprocessed/OBS_ID`):
```python
In [3]: analysis.addSpectrum("wt_grp.pha") # loading the grouped windowed  timing mode grouped file
```

Now to set energy range, the model and the hydrogen column density to be used in the fitting:
```python
In [4]: analysis.setcfluxMinMax(0.3,10.) # that is the energy range of the deabsorbed spectrum (cflux) in keV
In [5]: analysis.setModel() # the default model is a power law
In [6]: analysis.setNH(0.0206) # in  units of 10.e22 atoms cm-2
```
You can use this [nH online calculator](https://www.swift.ac.uk/analysis/nhtot/) to get the values for a particular source.

After that, we are set to perform the fit. Do that by running:

```python
In [7]: analysis.doFit()
```

Now one can use many functionalities to retrieve results from the analysis. Some are listed below:
```python
analysis.getFitResults() # returns a dict with SED, integral flux, best fit model parameters, etc.
analysis.getFlux() # returns a tuple with integral flux, upper and lower errors

import matplotlib.pyplot as plt
analysis.plotEnergySpectrum() # returns a matplotlib.pyplot.figure with the absorbed and deabsorbed SEDs in the given range
plt.show() # to show the plot

from astropy.table import Table
SED_table = analysis.writeSpecTable() # returns a table with SED points, and energies
```

The user is invited to create their own scripts.

# Acknowledgements


Most of the code in this repository was created by, or adapted from, the combined efforts of Amy Furniss (amy.furniss@gmail.com) and Ste O'Brien(stephan.obrien@mcgill.ca).

For further questions and comments, please contact Ste O'Brien(stephan.obrien@mcgill.ca) and/or Pedro Batista(pedro.batista@desy.de)
