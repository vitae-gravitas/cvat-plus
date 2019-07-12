import requests
import pickle
from tqdm import tqdm
from config import config
import sys

import argparse
from requestUtils import *
from uploadAnnotations import *



class Loader(object):

    # First set up server api variables
    server = 'http://localhost:8080'
    api = '/api/v1'
    tasks = '/tasks'
    users = '/users'

    def __init__(self):
        self.auth = (config["user"], config["password"])

        # get all files mounted on share
        req = Loader.server + Loader.api + '/server/share?directory=/'
        response = requests.get(req, auth = self.auth)
        # print(response.json())
        # print('shared file get result: {}'.format(response))
        self.shared_fnames = [ res['name'] for res in response.json() if res['name'] != '.DS_Store']
        self.shared_fnames.sort(key = lambda fname: int(fname.split(".")[0].split("video")[1]), reverse=True)
        self.cache = Loader.getCache()

    


    def uploadDataToTask(self, fname):
        task_id = self.cache[fname]
        # print(task_id)

        data = {'server_files[0]': fname}
        req = Loader.server + Loader.api + Loader.tasks + '/{0}/data'.format(task_id)
        # print(req)
        # print("task data request for {0}: {1}".format(fname, req))
        response = requests.post(req, data = data, auth = self.auth)
        # print("task data response for {0}: {1}".format(fname, response.text))

    
    def ensureTaskDataHasBeenUploaded(self, fname, currentIteration, maxIteration = 30):
        task_id = self.cache[fname]
        status = Loader.server + Loader.api + Loader.tasks + f'/{task_id}/status'
        statusResponse = requests.get(status, auth = self.auth)
        
        while statusResponse.json()['state'] != 'Finished' and statusResponse.json()['state'] != 'Failed':
            statusResponse = requests.get(status, auth = self.auth)
            # print("status response for {0}: {1}".format(fname, statusResponse.json()['state']))

        if statusResponse.json()['state'] == 'Failed' and currentIteration <= maxIteration:
            # print("status response for {0}: {1}".format(fname, statusResponse.json()['state']))
            self.uploadDataToTask(fname)
            self.ensureTaskDataHasBeenUploaded(fname, currentIteration + 1)

    def createTask(self, fname):
        create_task_data = {
            "name": fname,
            "overlap": 0,
            "z_order": False,
            "image_quality": 95,
            "labels": [{"name": "mainPlate"}, {"name": "otherPlate"}],
        }

        # create tasks

        req = Loader.server + Loader.api + Loader.tasks
        response = requests.post(req, json=create_task_data, auth=self.auth)

        if response.status_code == 403:
            print(response.text)
            return None, response.status_code
        # print("task create response for {0}: {1}".format(fname, response.json()))

        # print(response.json())
     
        # send data to task
        task_id = response.json()['id']

        return task_id

    def loadData(self, xml_folder = None):
        for fname in tqdm(self.shared_fnames):
            if fname in self.cache.keys():
                print(fname + " already is a task")  
            else:
                self.cache[fname] = self.createTask(fname)
                self.uploadDataToTask(fname)


        Loader.saveCache(self.cache)

        print()
        print("All the videos have been uploaded to the GUI. The videos that caused problems originally will be uploaded through brute force. If annotation folder was provided, annotations will be uploaded as well This may take a while, but you can begin annotating now!")
        print()
  

        for fname in tqdm(self.shared_fnames):
            self.ensureTaskDataHasBeenUploaded(fname, 0)
            
            if xml_folder:
                xml_file_name = os.path.splitext(fname)[0] + ".xml"
                xml_file_path = os.path.join(xml_folder, xml_file_name)
                AnnotationUploader.uploadAnnotationFromXML(self.cache[fname], xml_file_path)

    @staticmethod
    def getCache():
        try:
            fileObject = open("cache", 'rb')
            cache = pickle.load(fileObject)
            fileObject.close()
            return cache
        except OSError:
            return {}

    @staticmethod
    def saveCache(cache):
        fileObject = open("cache",'wb')  
        pickle.dump(cache, fileObject)   
        fileObject.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='loads data into cvat server')
    parser.add_argument('--xml_folder', required = False,
                        help='path to folder of xml files for annotation upload')
    args = parser.parse_args()

    validateAuth()
    ld = Loader()
    ld.loadData(xml_folder = args.xml_folder)











   






