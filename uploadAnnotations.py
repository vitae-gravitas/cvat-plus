import requests
import pickle
from tqdm import tqdm
from config import config
from parseAnnotatedXML import XMLParser
import os
import argparse
from requestUtils import *


class AnnotationUploader(object):
	server = 'http://localhost:8080'
	api = '/api/v1'
	tasks = '/tasks'
	users = '/users'


	def getTaskData(taskID):

		reqURL = "http://localhost:8080/api/v1/tasks/{0}".format(taskID)
		response = makeRequest(reqURL, 200, requests.get)
		return response.json()

	def uploadAnnotationFromXML(taskID, xml_file):

		validBool, message = XMLParser.isValidXMLAnnotation(xml_file)

		if not validBool:
			print(xml_file + ": " + message)
			return

		def getLabelNumberFromName(taskData, labelName):
			for labelDict in taskData['labels']:
				if labelDict['name'] == labelName:
					return labelDict['id']
			raise Exception

		data = {"version": 1, "tags": [], "shapes": [], "tracks": []}
		taskData = AnnotationUploader.getTaskData(taskID)
		bboxes = XMLParser.getBBoxesFromXML(xml_file)

		for bb in bboxes:
			shape = {
				"type": "rectangle",
				"occluded": False,
				"z_order": 0,
				"points": [
					bb['xtl'],
					bb['ytl'],
					bb['xbr'],
					bb['ybr']
				],
				# "id": 1178,
				"frame": XMLParser.getFrameNumber(xml_file),
				"label_id": getLabelNumberFromName(taskData, bb['label']),
				"group": 0,
				"attributes": []
			}

			data['shapes'].append(shape)
		# print(data)

		


		reqURL = "http://localhost:8080/api/v1/tasks/{0}/annotations".format(taskID)

		response = makeRequest(reqURL, 200, requests.put, maxIterations = 1, json = data)

		# print(response.text)

if __name__ == "__main__":
	AnnotationUploader.uploadAnnotationFromXML(1336, "/Users/tejasvikothapalli/Desktop/cvat-plus/annotations/video58.xml")
	# print(l)



	
	







