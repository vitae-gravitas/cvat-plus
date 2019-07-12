import requests
import pickle
from tqdm import tqdm
from config import config
from parseAnnotatedXML import XMLParser
import os
import argparse
from validate_annotations import Validator
import sys
from requestUtils import *
from load import Loader



class Downloader(object):

	server = 'http://localhost:8080'
	api = '/api/v1'
	tasks = '/tasks'
	users = '/users'
	

	def __init__(self):
		self.auth = (config["user"], config["password"])
		self.cache = Loader.getCache()

	def downloadTask(self, taskName):
		taskId = self.cache[taskName]

		reqURL = "http://localhost:8080/api/v1/tasks/{0}/annotations/{0}_{1}".format(taskId, taskName)
		makeRequest(reqURL, 201, requests.get, maxIterations = 45)

		reqURL = "http://localhost:8080/api/v1/tasks/{0}/annotations/{0}_{1}?action=download".format(taskId, taskName)
		response = makeRequest(reqURL, 200, requests.get, maxIterations = 1)


		# # response = requests.get("http://localhost:8080/api/v1/tasks/{0}/annotations/{0}_{1}?format=api".format(taskId, taskName), auth = self.auth)
		# response = requests.get("http://localhost:8080/api/v1/tasks/{0}/annotations/{0}_{1}".format(taskId, taskName), auth = self.auth)
		# while response.status_code != 201:
		# 	response = requests.get("http://localhost:8080/api/v1/tasks/{0}/annotations/{0}_{1}".format(taskId, taskName), auth = self.auth)
		# 	# print(response.status_code)
		# response = requests.get("http://localhost:8080/api/v1/tasks/{0}/annotations/{0}_{1}?action=download".format(taskId, taskName), auth = self.auth)
		# # print(response.text)
		# if response.status_code != 200:
		# 	print(response.status_code, taskName) 


		annotationFileName = "./annotations" + "/{0}.xml".format(taskName.split(".")[0])
		file = open(annotationFileName, "w")
		file.write(response.text)
		file.close()


	def downloadAllTasks(self):
		for fname in tqdm(sorted(self.cache.keys(), key = lambda fname: int(fname.split(".")[0].split("video")[1]))):
			self.downloadTask(fname)
		Validator.validateAllAnnotations("./annotations")
			
if __name__ == "__main__":

	downloadObject = Downloader()
	downloadObject.downloadAllTasks()

	
	







