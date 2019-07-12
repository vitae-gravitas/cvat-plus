
from tqdm import tqdm


import os
import argparse
from parseAnnotatedXML import *
import turicreate as tc
from tqdm import tqdm 
import numpy as np

try:
    import xml.etree.cElementTree as et
except ImportError:
    import xml.etree.ElementTree as et

class EvaluationSFrame(object):
	def getSFrame(xml_file, image_folder):
		IMAGE = ('.ras', '.xwd', '.bmp', '.jpe', '.jpg', '.jpeg', '.xpm', '.ief', '.pbm', '.tif', '.gif', '.ppm', '.xbm', '.tiff', '.rgb', '.pgm', '.png', '.pnm')
		xml_tree = et.parse(xml_file)

		data = {
			'image' : [],
			'annotations': []
		}

		for elem in tqdm(xml_tree.iter()):
			if elem.tag == "image":
				annotation = []
				for child in elem.iter():
					if child.tag == "box":
						xtl = float(child.get('xtl')) 
						ytl = float(child.get('ytl'))
						width = float(child.get('xbr')) - float(child.get('xtl'))
						height = float(child.get('ybr')) - float(child.get('ytl'))
						initBBox = (xtl, ytl, width, height)
						annotation.append(XMLParser.getTCAnnotationFromBB(initBBox, child.get('label'), None))
				image = tc.Image(os.path.join(image_folder, elem.get("name")))
				data['annotations'].append(annotation)
				data['image'].append(image)
		# print(data)
		return tc.SFrame(data)
						



			
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Creates an sframe of evaluation set')
	parser.add_argument('--image_folder', required = True,
	                    help='path to folder of all images')
	parser.add_argument('--xml_file', required = True, help = 'path to xml file')
	# parser.add_argument('--mask', required = False, help = 'path to folder of all xml annotations')


	args = parser.parse_args()

	sf = EvaluationSFrame.getSFrame(args.xml_file, args.image_folder)
	print("total number of images in sframe: " + str(len(sf)))
	# sf.print_rows(num_rows= len(sf))
	sf.save(str(len(sf)) + "evaluationSet.sframe")


	







