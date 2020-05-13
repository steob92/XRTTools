#!/bin/bash
'''
    Script to reduce and group XRT data
    Both PC and WT modes
'''


function usage()
{
  echo "Usage: ReduceXRT.sh -r SourceRA -d SourceDec -f /Path/To/Reduced/Files"
  echo "Example: ReduceXRT.sh -r 356.77015 -d 51.70497 -f ./Reduced"
  echo -e "\t where RA and Dec are in degrees"
  echo -e "\t ./Reduced contains OBS_ID/swOBD_ID*cl.evt"

}
SUBDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
RA=-1
DEC=-1


while getopts ":hr:d:f:e:" opt; do
  case ${opt} in
    r )
      RA=${OPTARG}
      ;;
    d )
      DEC=${OPTARG}
      ;;
    e )
      RA=356.77015
      DEC=51.70497
      ;;
    h )
      usage
      ;;
    \? ) usage
      ;;
  esac
done
echo "RA: $RA"
echo "DEC: $DEC"



# Run xselect to extract image data
function extract_image()
{

    xselect <<EOF
xrt

read event $1


extract image
save image $2.img

exit

EOF
}

# Run xselect to extract filtered spectra
function extract_spectrum()
{

  FILE=$1
  FILT=$2
  SPEC=$3
  xselect <<EOF
xrt

read event $FILE


filter region $FILT

extract spectrum

save spectrum $SPEC

exit

EOF
}

# Run grppha to change the backscale for WT mode
function change_backscale()
{

  SCALE=$1
  FILEIN=$2
  FILEOUT=$3
  grppha<<EOF
$FILEIN
!$FILEOUT
chkey BACKSCAL $SCALE
exit

EOF
}

# Grouping various files together for xspec
# Assuming a minimum of 20 counts per bin
function group_pha()
{

  SRCPHA=$1
  GRPPHA=$2
  BACKPHA=$3
  RMF=$4
  ARF=$5
  grppha<<EOF
$SRCPHA
!$GRPPHA
group min 20
chkey BACKFILE ./$BACKPHA
chkey RESPFILE ./$RMF
chkey ANCRFILE ./$ARF
exit

EOF
}

# Run extract_image for either pc or wt cleaned events in that directory
function extract_image_all()
{
  # Looking for PC files
  PCFILE=$(ls *pc*_cl.evt)
  PCRMFFILE=$(ls *pc*.rmf)
  PCEXPFILE=$(ls *pc*_ex.img)
  NFILE_PC=$(ls *pc*_cl.evt | wc -l)

  # Looking for WT files
  WTFILE=$(ls *wt*_cl.evt)
  WTRMFFILE=$(ls *wt*.rmf)
  WTEXPFILE=$(ls *wt*_ex.img)
  NFILE_WT=$(ls *wt*_cl.evt | wc -l)

  # Extract PC image
  if [ "$NFILE_PC" -eq "1" ]; then
    echo "##########################"
    echo "Extracting PC"
    echo "##########################"

    rm pc.img pc_cl.evt
    extract_image "$PCFILE" "pc"
    ln -s $PCFILE pc_cl.evt
    ln -s $PCRMFFILE pc.rmf
    ln -s $PCEXPFILE pc_ex.img
  fi

  # Extract WT file
  if [ "$NFILE_WT" -eq "1" ]; then
    echo "##########################"
    echo "Extracting WT"
    echo "##########################"

    rm wt.img wt_cl.evt
    extract_image "$WTFILE" "wt"
    ln -s $WTFILE wt_cl.evt
    ln -s $WTRMFFILE wt.rmf
    ln -s $WTEXPFILE wt_ex.img
  fi
}





# Run extract_image for either pc or wt cleaned events in that directory
function extract_spectra_all()
{
  # Looking for PC files
  PCFILE=pc_cl.evt

  # Looking for WT files
  WTFILE=wt_cl.evt

  if [ -f $PCFILE ]; then
    rm pc_src.arf
    extract_spectrum "$PCFILE" "pc_src.reg" "pc_src.pha"
    extract_spectrum "$PCFILE" "pc_back.reg" "pc_back.pha"
    xrtmkarf phafile=pc_src.pha srcx=-1 srcy=-1 outfile=pc_src.arf psfflag=yes expofile=pc_ex.img
    group_pha "pc_src.pha" "pc_grp.pha" "pc_back.pha" "pc.rmf" "pc_src.arf"
  fi



  # Extract WT file
  if [ -f $WTFILE ]; then
    rm wt_src.arf
    extract_spectrum "$WTFILE" "wt_src.reg" "wt_src.pha"
    extract_spectrum "$WTFILE" "wt_back.reg" "wt_back.pha"
    xrtmkarf phafile=wt_src.pha srcx=-1 srcy=-1 outfile=wt_src.arf psfflag=yes expofile=wt_ex.img

    # Not needed
    #change_backscale "40" "wt_src.pha" "wt_rescale_src.pha"
    change_backscale "39" "wt_back.pha" "wt_rescale_back.pha"
    group_pha "wt_src.pha" "wt_grp.pha" "wt_rescale_back.pha" "wt.rmf" "wt_src.arf"

  fi
}






function write_offRegionPC()
{
  echo  'icrs;annulus('$RA','$DEC',75",150")' > pc_back.reg
}

function write_RegionsPC()
{
  EXCLUDE=$( bc -l <<<"2.36*$1" )
  ONEDGE=$( bc -l <<<"47 + 2.36*$1" )
  OFFEDGE=$( bc -l <<<"150 + 2.36*$1" )
  echo  'icrs;annulus('$RA','$DEC','$EXCLUDE'",'$ONEDGE'")' > pc_src.reg
  echo  'icrs;annulus('$RA','$DEC',75",'$OFFEDGE'")' > pc_back.reg
}

# Write Regions WT
function write_RegionsWT()
{

  echo  'icrs;circular('$RA','$DEC',47.146")' > wt_src.reg
  echo  'icrs;annulus('$RA','$DEC',188.585",282.877")' > wt_back.reg
}


function correct_pileUP()
{
  COUNTR=1
  ICUT=0

  PCFILE=pc_cl.evt

  if [ -f $PCFILE ]; then

    # While the return of the python scripts is not 0
    while [ $COUNTR -ne 0 ]
    do

      # Create the on region
      write_RegionsPC $ICUT
      # Extract the spectrum
      extract_spectrum pc_cl.evt pc_src.reg pc_src.pha
      # Test the new count rates
      python $SUBDIR/TestCountRate.py pc_src.pha
      COUNTR=$?
      echo $COUNTR
      # Iterate
      ICUT=$[ICUT+1]

    done
  fi
}


# loop over directories
for DIR in $(ls);do

  if [ -d "$DIR" ]; then
    cd $DIR
    echo $DIR
    extract_image_all
    correct_pileUP
    write_RegionsWT
    extract_spectra_all
    cd ../
  fi

  # break

done
