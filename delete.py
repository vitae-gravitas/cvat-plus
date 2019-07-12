import requests
from tqdm import tqdm
import pickle
from config import config
from load import *
import sys

import argparse
from requestUtils import *


class Deleter(object):


	# First set up server api variables
	server = 'http://localhost:8080'
	api = '/api/v1'
	tasks = '/tasks'
	users = '/users'

	def __init__(self):
		self.auth = (config["user"], config["password"])
		self.cache = Loader.getCache()

	def deleteTask(self, fname):
		reqURL = Deleter.server + Deleter.api + Deleter.tasks + "/" + str(self.cache[fname])
		makeRequest(reqURL, 204, requests.delete, maxIterations = 1)
		
		

	def deleteAllTasks(self):
		for fname in tqdm(self.cache.keys()):
			self.deleteTask(fname)
			

		Loader.saveCache({})

	def deleteRangeOfTasks(self, startInclusive, endExclusive):
		for i in tqdm(range(startInclusive, endExclusive)):
			taskName = "video" + str(i) + ".mp4"
			if taskName in self.cache:
				self.deleteTask("video" + str(i) + ".mp4")
				del self.cache["video" + str(i) + ".mp4"]
			# print("video" + str(i) + ".mp4")
		Loader.saveCache(self.cache)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='delete tasks')
	parser.add_argument('--start', type=int)
	parser.add_argument('--end', type=int)
	parser.add_argument('--deleteAll')

	args = parser.parse_args()


	if args.start and args.end:
		Deleter().deleteRangeOfTasks(args.start, args.end)
	elif args.deleteAll:
		Deleter().deleteAllTasks()
	else:
		print("no flags were given in terminal argument")
	