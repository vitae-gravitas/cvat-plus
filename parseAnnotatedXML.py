try:
    import xml.etree.cElementTree as et
except ImportError:
    import xml.etree.ElementTree as et
import sys

class XMLParser(object):
	@staticmethod
	def getVideoNameFromXML(xml_file):
		xml_tree = et.parse(xml_file)
		for elem in xml_tree.iter():
			if elem.tag == "name":
				return elem.text

	@staticmethod
	def getNumberOfFrames(xml_file):
		xml_tree = et.parse(xml_file)
		for elem in xml_tree.iter():
			if elem.tag == "stop_frame":
				return int(elem.text) + 1


	@staticmethod
	def isValidXMLAnnotation(xml_file):

		try:
			masterFrame = XMLParser.getFrameNumber(xml_file)
			totFrames = XMLParser.getNumberOfFrames(xml_file)
			if isinstance(masterFrame, bool) and masterFrame == False:
				return False, "file was not annotated"
			elif masterFrame >= totFrames or masterFrame < 0:
				return False, "the master frame is not in range"
			else:
				return True, "master frame is " + str(masterFrame)
		except et.ParseError:
			return False, "not valid xml file"
		except Exception as e:
			return False, str(e)

	@staticmethod
	def getTuriCreateAnnotationsFromXML(xml_file):
		xmlFormatBBoxes = XMLParser.getBBoxesFromXML(xml_file)
		annotations = []
		for bb in xmlFormatBBoxes:
			initBBox = (bb['xtl'], bb['ytl'], bb['xbr'] - bb['xtl'], bb['ybr'] - bb['ytl'])
			annotations.append(XMLParser.getTCAnnotationFromBB(initBBox, bb['label'], bb['objectID']))
		return annotations

	@staticmethod
	def getTCAnnotationFromBB(xywhBB, label, objId):
	    return {
	        'coordinates':
	        {
	            'x': xywhBB[0] + xywhBB[2]/2,
	            'width': xywhBB[2],
	            'y': xywhBB[1] + xywhBB[3]/2,
	            'height': xywhBB[3]
	        },
	        'label': label,
	        'objectID': objId
	    }

	@staticmethod
	def getBBoxesFromXML(xml_file):
		xml_tree = et.parse(xml_file)
		bboxes = []

		frameNumber = XMLParser.getFrameNumber(xml_file)

		parent_map = dict((c, p) for p in xml_tree.iter() for c in p)


		for elem in xml_tree.iter():
			if elem.tag == "box" and float(elem.get("frame")) == frameNumber:
				bb = {"xtl": float(elem.get("xtl")), "ytl": float(elem.get("ytl")), 
				"xbr": float(elem.get("xbr")), "ybr" : float(elem.get("ybr")), 
				"label": parent_map[elem].get("label"), "objectID": parent_map[elem].get("id"), "frame": int(elem.get("frame"))}
				bboxes.append(bb)

		return bboxes

	@staticmethod
	def getFrameNumber(xml_file):
		xml_tree = et.parse(xml_file)
		lowestNum = False
		for elem in xml_tree.iter():
			if elem.tag == "box":
				if isinstance(lowestNum, bool) or int(elem.get("frame")) < lowestNum:
					lowestNum = int(elem.get("frame"))
		return lowestNum


if __name__ == "__main__":
	print(XMLParser.getBBoxesFromXML(sys.argv[1]))

