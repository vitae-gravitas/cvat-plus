
from tqdm import tqdm


import os
import argparse
import cv2
from parseAnnotatedXML import *
import turicreate as tc
from tqdm import tqdm 
import numpy as np

class MasterSFrame(object):
	@staticmethod
	def getMasterSframe(video_folder, xml_folder):
		data = {
			'image': [],
			'annotations': [],
			'name': []
		}
		annotationFiles = os.listdir(xml_folder)
		if ".DS_Store" in annotationFiles:
			annotationFiles.remove(".DS_Store")
		for fname in tqdm(sorted(annotationFiles, key = lambda fname: int(fname.split(".")[0].split("video")[1])), desc = "frames parsed"):
			annotation_filepath = os.path.join(xml_folder, fname)
			video_filepath = os.path.join(video_folder, "{0}.mp4".format(fname.split(".")[0]))
			validBool, message = XMLParser.isValidXMLAnnotation(annotation_filepath)
			if validBool:
				data['name'].append(fname)
				data['image'].append(MasterSFrame.getTuriCreateMasterImage(video_filepath, XMLParser.getFrameNumber(annotation_filepath)))
				data['annotations'].append(XMLParser.getTuriCreateAnnotationsFromXML(annotation_filepath))

		return tc.SFrame(data)

	def getTuriCreateMasterImage(video_file, frameNumber):
		frame = MasterSFrame.getAllFrames(video_file)[frameNumber]
		assert (isinstance(frame, np.ndarray)), 'Image is not of type numpy.ndarray.'
		RAW_FORMAT = 2
		return tc.Image(_image_data=frame.tobytes(), 
			_width=frame.shape[1],
			_height=frame.shape[0],
			_channels=frame.shape[2],
			_format_enum=RAW_FORMAT,
			_image_data_size=frame.size)

	def getAllFrames(video_file):
		frames = []
		v = cv2.VideoCapture(video_file)
		while True:
			frame = v.read()[1]
			if frame is None:
				break
			else:
				frames.append(frame)
		return frames


	@staticmethod
	def oneMainPlate(SFrame_dir):
		SFrame = tc.SFrame(SFrame_dir)


		for row in tqdm(SFrame, "updating to only one main plate"):
			# print(row['annotations'])
			maxMainPlateArea = 0
			maxMainPlateID = None
			for bb in row['annotations']:
				if bb['label'] == "mainPlate":
					# print(bb)
					area = bb['coordinates']['height'] * bb['coordinates']['width']
					if area > maxMainPlateArea:
						maxMainPlateArea = area
						maxMainPlateID = bb['objectID']

			if maxMainPlateID != None:
				for bb in row['annotations']:
					if bb['label'] == "mainPlate" and bb['objectID'] != maxMainPlateID:
						bb['label'] = "otherPlate"
			# print(row['annotations'])

		return SFrame

	@staticmethod
	def secondMainPlate(SFrame_dir):
		SFrame = tc.SFrame(SFrame_dir)


		for row in tqdm(SFrame, "updating to have a second main plate"):
			# print(row['annotations'])
			maxMainPlateArea = 0
			maxMainPlateID = None
			for bb in row['annotations']:
				if bb['label'] == "mainPlate":
					# print(bb)
					area = bb['coordinates']['height'] * bb['coordinates']['width']
					if area > maxMainPlateArea:
						maxMainPlateArea = area
						maxMainPlateID = bb['objectID']

			if maxMainPlateID != None:
				for bb in row['annotations']:
					if bb['label'] == "mainPlate" and bb['objectID'] != maxMainPlateID:
						bb['label'] = "secondMainPlate"
			# print(row['annotations'])
		return SFrame


			
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Creates an sframe of all the master frames')
	parser.add_argument('--video_folder', required = True,
	                    help='path to folder of all videos')
	parser.add_argument('--xml_folder', required = True, help = 'path to folder of all xml annotations')
	# parser.add_argument('--mask', required = False, help = 'path to folder of all xml annotations')


	args = parser.parse_args()

	sf = MasterSFrame.getMasterSframe(args.video_folder, args.xml_folder)
	print("total number of frames in sframe: " + str(len(sf)))
	sf.save(str(len(sf)) + "masterFrames.sframe")

	oneMainPlateSF = MasterSFrame.oneMainPlate("masterFrames.sframe")
	oneMainPlateSF.save(str(len(sf)) + "oneMainPlate.sframe")

	secondMainPlateSF = MasterSFrame.secondMainPlate("masterFrames.sframe")
	oneMainPlateSF.save(str(len(sf)) + "secondMainPlate.sframe")
	
	







