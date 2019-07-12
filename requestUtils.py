import requests
from config import config
from parseAnnotatedXML import XMLParser
import os
import argparse
import sys


server = 'http://localhost:8080'
api = '/api/v1'
tasks = '/tasks'
users = '/users'
auth = (config["user"], config["password"])


def makeRequest(requestURL, status_code, requestMethod, maxIterations = 30, data = None, json = None):
    
    response = requestMethod(requestURL, data = data,  auth = auth, json = json)

    count = 1
    while response.status_code != status_code and count < maxIterations:
        response = requestMethod(requestURL, data = data,  auth = auth, json = json)
        count += 1

    if response.status_code != status_code:
        print(requestURL, response.text, response.status_code)

    return response

def validateAuth():
    response = requests.get(server + api, auth = auth)
    if response.status_code == 403:
        print(response.text)
        sys.exit()
    return response.status_code

validateAuth()