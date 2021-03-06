# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 10:58:28 2017

@author: AustinPeel
"""

import requests
import zipfile
from io import BytesIO
import pandas as pd 
from pandas.io.json import json_normalize


apitoken = "INSERT HERE"
#update baseUrl
baseurl = "https://INSERT.qualtrics.com/API/v3/"

class qualtrics:

    # https://api.qualtrics.com/docs/response-exports
    def __init__(self,survey=""):
        self.apiToken = apitoken
        self.surveyId = survey 
        self.baseUrl = baseurl
        self.headers = {"content-type": "application/json","x-api-token": self.apiToken,}
    def getProgressID(self):
        downloadRequestUrl = self.baseUrl + "responseexports/"
        #downloadRequestPayload = '{"format":"' + self.fileFormat + '","surveyId":"' + self.surveyId  + '","lastResponseId":"' + self.lastID  + '","useLabels":' + self.label+  '}'
        downloadRequestResponse = requests.request("POST", downloadRequestUrl, data=self.payload, headers=self.headers)
        progressId = downloadRequestResponse.json()["result"]["id"]
        print(downloadRequestResponse.text)
        return progressId

    # https://api.qualtrics.com/docs/get-response-export-progress
    def checkProgress(self):
        self.progressId = self.getProgressID()
        requestCheckProgress = 0
        while requestCheckProgress < 100:
          requestCheckUrl = self.baseUrl + "responseexports/" + self.progressId
          requestCheckResponse = requests.request("GET", requestCheckUrl, headers=self.headers)
          requestCheckProgress = requestCheckResponse.json()["result"]["percentComplete"]
          print("Download is " + str(requestCheckProgress) + " complete")
        return requestCheckProgress
    
    def buildPayload(self,**kwargs):
        long = '"'
        for key, value in kwargs.items():
             short =   key +'":"' + value + '","'
             long =  long + short
        payload = '{"format":"' + self.fileFormat + '","surveyId":"' + self.surveyId  +'",' + long  + 'useLabels":' + self.label+  '}'  
        return payload

    # https://api.qualtrics.com/docs/get-response-export-file
    def downloadExtractZip(self,fileFormat="csv",label="true",**kwargs):
        self.fileFormat = fileFormat
        self.label = label
        self.payload = self.buildPayload(**kwargs)
        prog = self.checkProgress()  
        if prog == 100:
            requestDownloadUrl = self.baseUrl + "responseexports/" + self.progressId + '/file'
            requestDownload = requests.request("GET", requestDownloadUrl, headers=self.headers)
            print(requestDownload.status_code)
            z = zipfile.ZipFile(BytesIO(requestDownload.content))
            z.extractall()
        else:
            print("something went wrong with download")
        
    # https://api.qualtrics.com/docs/get-distributions
    def getListDistributions(self):
        url = self.baseUrl +"distributions?" + "surveyId=" + self.surveyId
        distributions = requests.request("GET", url, headers=self.headers)
        return distributions.json()
    
    # https://api.qualtrics.com/docs/get-distribution
    def getDistributions(self,distributionId):
        url = self.baseUrl +"distributions/" + distributionId + "?surveyId=" + self.surveyId
        distributions = requests.request("GET", url, headers=self.headers)
        return distributions.json()
    
    # https://api.qualtrics.com/docs/get-mailing-list
    def getContacts(self,mailingId):
        url = self.baseUrl +"mailinglists/" + mailingId + "/contacts"
        contacts = requests.request("GET", url, headers=self.headers)
        return contacts.json()
    
    # gets the first page of the distribution contacts
    # https://api.qualtrics.com/docs/get-distribution-links
    def getDistributionByContact(self,distributionId):
        url = self.baseUrl +"distributions/" + distributionId + "/links?surveyId=" + self.surveyId
        distributions = requests.request("GET", url, headers=self.headers)
        return distributions.json()
    
    # iterates over DistributionsByContact and return all in a df
    # status column is currently broken
    def getAllContacts(self,distributionId):
        jsonData = self.getDistributionByContact(distributionId)
        df = json_normalize(jsonData['result']['elements'])
        num = 100
        while True:
            nextPage = jsonData['result']['nextPage']
            if not nextPage:
                break
            else:
                distributions = requests.request("GET", nextPage, headers=self.headers)
                jsonData = distributions.json()
                df2 = json_normalize(jsonData['result']['elements'])
                df =df.append(df2)
                print(str(num) + " rows")
                num += 100
        return df
