#!/bin/bash

#'''
#    Script to test XRT data reduction
#    and generate a run selection list with OBSID and modes based on exposure times
#'''

function usage()
{
  echo -e "Usage: TestReduction.sh -f /Path/To/Reduced/Files"
  echo -e "Example: TestReduction.sh -f ./Reprocessed"
  echo -e "\t ./Reprocessed contains OBS_ID/swOBD_ID*cl.evt"
  echo
  exit
}

while getopts ":f:?h" opt; do
  case ${opt} in
    f )
      DATADIR=${OPTARG}
      ;;
    h )
      usage
      ;;
    \? ) usage
      ;;
  esac
done

if [[ -z "$DATADIR" ]]
then
  usage
fi

echo "DATADIR: $DATADIR"
cd $DATADIR
if [ -f $DATADIR/run_selection.dat ]; then
  rm run_selection.dat
fi
touch run_selection.dat
for DIR in $(ls $DATADIR);do
  echo "$DATADIR/$DIR"
  if [ -d $DATADIR/$DIR ]; then
    MODE=`python /afs/ifh.de/group/cta/scratch/pedroivo/Software/XRTTools/bin/TestExposure.py $DATADIR $DIR | awk '{print $2}'`
    echo "MODE: $MODE"
    cd $DATADIR/$DIR
    if [[ "$MODE" == "PC" ]]; then
      if [[ -f "./pc_src.pha" ]] && [[ -f "./pc_back.pha" ]] && [[ -L "./pc.rmf" ]] && [[ -f "./pc_src.arf" ]] && [[ -f "./pc_grp.pha" ]]
      then
        echo "$DIR: PC REDUCTION SUCCEEDED"
        python /afs/ifh.de/group/cta/scratch/pedroivo/Software/XRTTools/bin/TestExposure.py $DATADIR $DIR >> $DATADIR/run_selection.dat
      else
        echo "$DIR: PC REDUCTION FAILED"
      fi
    elif [[ "$MODE" == "WT" ]]; then
      if [[ -f "./wt_src.pha" ]] && [[ -f "./wt_rescale_back.pha" ]] && [[ -L "./wt.rmf" ]] && [[ -f "./wt_src.arf" ]] && [[ -f "./wt_grp.pha" ]]
      then
        echo "$DIR: WT REDUCTION SUCCEEDED"
        python /afs/ifh.de/group/cta/scratch/pedroivo/Software/XRTTools/bin/TestExposure.py $DATADIR $DIR >> $DATADIR/run_selection.dat
      else
        echo "$DIR: WT REDUCTION FAILED"
      fi
    else
      echo "MODE NOT FOUND"
    fi
  else
    echo "Not a directory, skipping to next one"
  fi
done
