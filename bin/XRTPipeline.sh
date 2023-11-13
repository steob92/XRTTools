#!/bin/bash

#'''
#    Script to process level 1 fits XRT data
#    Both PC and WT modes
#'''

function usage()
{
  echo "Usage: ./XRTPipeline.sh -r SourceRA -d SourceDec -f /Path/To/Data/Files"
  echo "Example: ./XRTPipeline.sh -r 356.77015 -d 51.70497 -f /1ES2344/Swift-XRT/"
  echo -e "\t /1ES2344/Swift-XRT/ is expected to have a Data/ directory"
  echo -e "\t where Data/ contains OBS_ID/xrt/ and OBS_ID/auxil/"
  echo -e "\t and RA and Dec are in degrees"
  echo -e "\t Outputs are written to /1ES2344/Swift-XRT/Reprocessed/"
  exit
}

RA=-1
DEC=-1

while getopts ":r:d:p:f:?h" opt; do
  case ${opt} in
    r )
      RA=${OPTARG}
      ;;
    d )
      DEC=${OPTARG}
      ;;
    f )
      SRCDIR=${OPTARG}
      ;;
    h|? )
      usage
      ;;
  esac
done

# All pars are required
if [[ -z "$RA" ]] || [[ -z "$DEC" ]] || [[ -z "$SRCDIR" ]]
then
  usage
  exit
fi


# Check if data directory exists
DATADIR=$SRCDIR/Data

if [ -d $DATADIR ]; then
  echo "RA: $RA"
  echo "DEC: $DEC"
  echo "Data: $DATADIR"
else
  echo "ERROR: \"$DATADIR\" doesn't exist.."
  usage
  exit
fi

function run_xrtpipeline()
{
  INDIR=$DATADIR/$1
  OUTDIR=$SRCDIR/Reprocessed/$1
  echo "#######################################"
  echo "Running xrtpipeline for obs $1 "
  echo "#######################################"
  xrtpipeline indir=$INDIR outdir=$OUTDIR steminputs=sw$1 srcra=$RA srcdec=$DEC pntra=$RA pntdec=$DEC exprpcgrade="0-12" exprwtgrade="0-2" exprpdgrade="0-2" clobber=yes createexpomap=yes  >> xrtpipeline_$1.log
  mv xrtpipeline_$1.log $OUTDIR
}


echo "Looping"
# loop over directories
for DIR in $(ls $DATADIR); do
  #echo $DATADIR/$DIR
  if [ -d "$DATADIR/$DIR" ]; then
    cd $DATADIR
    run_xrtpipeline $DIR
  else
    echo "$DATADIR/$DIR not found..."
    echo "pwd: $(pwd)"
  fi
  cd -
done
