import requests
import pickle
from tqdm import tqdm
from config import config
from parseAnnotatedXML import XMLParser
import os
import argparse



class Validator(object):

	@staticmethod
	def validateAllAnnotations(validate_folder):

		annotationFiles = os.listdir(validate_folder)
		if ".DS_Store" in annotationFiles:
			annotationFiles.remove(".DS_Store")
		# print(annotationFiles)

		for fname in sorted(annotationFiles, key = lambda fname: int(fname.split(".")[0].split("video")[1])):
			annotationFileName = os.path.join(validate_folder, "{0}.xml".format(fname.split(".")[0]))
			Validator.validateAnnotation(annotationFileName)

	@staticmethod
	def validateAnnotation(annotationFile):
		validBoolean, message = XMLParser.isValidXMLAnnotation(annotationFile)
		print(os.path.basename(annotationFile) + ": " + message)
			
if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='validate xml annotations')
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('--xml_folder', help='path to folder of annotations')
	group.add_argument('--xml_file', help='path to annotation file' )

	args = parser.parse_args()

	if args.xml_folder:
		Validator.validateAllAnnotations(args.xml_folder)
	else:
		Validator.validateAnnotation(args.xml_folder)

	
	







