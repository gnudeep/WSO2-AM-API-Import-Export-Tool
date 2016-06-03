#!/usr/bin/python
import sys
import requests
import datetime
import time
import json
import os
import zipfile
import git

def main(argv):
    apiKey = argv[0]
    apiSecret = argv[1]
    userName = argv[2]
    userPassword = argv[3]
    hostName = argv[4]
    
    (accessToken, expiresIn, refreshToken) = getAccessToken(apiKey, apiSecret, userName, userPassword, hostName)
    apiList = getAllApis(accessToken)
    exportAllApis(apiList)
    unzipAllFile()
    gitPushAllApis()


def getAccessToken(apiKey, apiSecret, user, password, hostName):
    stsUrl = 'https://' + hostName + ':8243/token'
    payload= {'client_id' : apiKey,'client_secret':apiSecret, 'username':user, 'password':password, 'grant_type':'password', 'scope':'apim:api_view'}
    
    response = requests.post(stsUrl, data=payload, verify=False)
    if response.status_code == 200:
        data = json.loads(response.text)
        accessToken = data['access_token']
        expiresIn = data['expires_in'] #in seconds
        refreshToken = data['refresh_token']
        return (accessToken, expiresIn, refreshToken)
    else:
        print 'Failed to obtain access token, status code ' + str(response.status_code)
        return ('', '0', '')


def getAllApis(hostName, accessToken):
    stsUrl = 'http://' + hostName + ':9763/api/am/publisher/v0.9/apis'
    headers = {'Authorization': 'Bearer ' + accessToken}

    response = requests.get(stsUrl, headers=headers)
    data = json.loads(response.text)
    apiList = []
    for x in range(0, data['count']):
        apiList.append((data['list'][x]['name'], data['list'][x]['version']))
    return apiList


def exportAllApis(hostName, apiList):
    for x in range(0, len(apiList)):
        zipFileName = "/tmp/api-repo/" + apiList[x][0] + "-" + apiList[x][1] + ".zip"
        exportUrl = 'https://' + hostName + ':9443/api-import-export-2.0.0-SNAPSHOT/export-api?name=' + apiList[x][0] + '&version=' + apiList[x][1] + '&provider=admin'
        headers = {'Authorization': 'Basic YWRtaW46YWRtaW4='}
        with open(zipFileName, 'wb') as handle:
            response = requests.get(exportUrl, headers=headers, verify=False, stream=True)
            if not response.ok:
                print response

            for block in response.iter_content(1024):
                handle.write(block)

    return True

def unzipAllFile():
    dir_name = '/tmp/api-repo/'
    extension = ".zip"
    os.chdir(dir_name)
    for item in os.listdir(dir_name):
        if item.endswith(extension):
            file_name = os.path.abspath(item)
            zip_ref = zipfile.ZipFile(file_name)
            zip_ref.extractall(dir_name)
            zip_ref.close()
            os.remove(file_name)
    return True

def gitPushAllApis():
    repo = git.Repo( '/tmp/api-repo' )
    repo.git.add('*')
    gitStatus = repo.git.status()
    print gitStatus

    if gitStatus.find("nothing to commit") > -1:
        repo.git.push()
    else:
        repo.git.commit( m='Added new API Changes' )
        repo.git.push()
    print repo.git.status()

    return True

def getApimPubliherEndpoint():

    return True

def getApimImportExportEndpoint():

    return True

if __name__ == '__main__':
    if len(sys.argv) != 6:
        print "Usage: python export-api.py apiKey, apiSecret, userName, password hostName"
        sys.exit(1)
    main(sys.argv[1:])
