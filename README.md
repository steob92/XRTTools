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

Initialize HEASoft and CALDB using:
```
alias heainit=". $HEADAS/headas-init.sh"
alias caldbinit=". $CALDB/software/tools/caldbinit.sh"
```
## Downloading data from HEASARC

Download data from HEASARC:

1. Go to https://heasarc.gsfc.nasa.gov/cgi-bin/W3Browse/w3browse.pl
2. Type in the object name
3. Check the **Swift** box
4. Click on **Start Search**
5. Select the observations you would like to download by clicking on the white boxes on the left side of screen
6. Unmark **Swift UVOT Data** in case you don't want them
7. Click on Retrieve button and wait until TAR file is created.  This may take up to 5 minutes depending on how many files you are retrieving

Now you can retrieve the data using the link to the tar file using, e.g., `wget full_path_link_from_webpage` and untar the data `tar -xvf w3browse-num.tar`
