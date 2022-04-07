''' Select mode exposures '''

from astropy.io import fits
import argparse
from pathlib import Path
import sys

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("ReprocessedDir", type=str, help="Reprocessed data directory")
	parser.add_argument("ObsID", type=str, help="Observation ID")
	parser.add_argument("--exposureratio", "-ratio", type=float, help="If the ratio between PC and WT exposures is greater than this number, PC mode is selected, otherwise, WT mode is selected", default=10.)

	args = parser.parse_args()
	ObsID = str(args.ObsID)
	RepDir = args.ReprocessedDir
	input_dir = RepDir + '/' + ObsID
	ratio = args.exposureratio

	if Path(RepDir).is_dir() == False:
		print("DIR NOT FOUND")
		sys.exit()

	file_WT = "/sw" + ObsID + "xwtw2po_cl.evt"
	file_PC2 = "/sw" + ObsID + "xpcw2po_cl.evt"
	file_PC3 = "/sw" + ObsID + "xpcw3po_cl.evt"

	path_to_fWT = Path(input_dir+file_WT)
	path_to_fPC2 = Path(input_dir+file_PC2)
	path_to_fPC3 = Path(input_dir+file_PC3)

	if path_to_fWT.is_file():
		hWT = fits.open(input_dir+file_WT)
		exposure_WT = hWT[0].header["EXPOSURE"]
	else:
		exposure_WT = 0

	if path_to_fPC3.is_file():
		hPC3 = fits.open(input_dir+file_PC3)
		exposure_PC3 = hPC3[0].header["EXPOSURE"]
	else:
		exposure_PC3 = 0

	if path_to_fPC2.is_file():
		hPC2 = fits.open(input_dir+file_PC2)
		exposure_PC2 = hPC2[0].header["EXPOSURE"]
	else:
		exposure_PC2 = 0


	if exposure_WT > 0.:
		if exposure_PC3 > 0.:
			if exposure_PC3/exposure_WT > ratio:
				print(ObsID, "PC")
			else:
				print(ObsID, "WT")
		elif exposure_PC2 > 0.:
			if exposure_PC2/exposure_WT > ratio:
				print(ObsID, "PC")
			else:
				print(ObsID, "WT")
		else:
			print(ObsID, "WT")
	elif exposure_PC3 > 0. or exposure_PC2 > 0.:
		print(ObsID, "PC")
	else:
		print("SKIP")
