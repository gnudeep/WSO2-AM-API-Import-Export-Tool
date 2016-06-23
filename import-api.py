#!/usr/bin/python
import sys
import requests
import os
import zipfile
import git
import glob
import base64
import json


def main(argv):

    apiKey = argv[0]
    apiSecret = argv[1]
    userName = argv[2]
    userPassword = argv[3]
    hostName = argv[4]
    tokenEndpointPort = argv[5]
    restApiEndpointPort = argv[6]
    gitRepoPath = argv[7]

    #Delete subscription

    #Delete APIS
    scope = 'apim:api_view'
    (accessToken, expiresIn, refreshToken) = getAccessToken(apiKey, apiSecret, userName, userPassword, hostName, tokenEndpointPort,scope)
    apiList = getAllApis(hostName, restApiEndpointPort, accessToken)
    # scope = 'apim:api_create'
    # (accessToken, expiresIn, refreshToken) = getAccessToken(apiKey, apiSecret, userName, userPassword, hostName, tokenEndpointPort,scope)
    # deleteAllApis(hostName,restApiEndpointPort, accessToken, apiList)

    #Import APIs
    # dir_list = os.walk(gitRepoPath).next()[1]
    # if '.git' in dir_list:
    #     gitPullAllApis(gitRepoPath)
    # zipAllFiles(gitRepoPath)
    # importAllApis(userName, userPassword, hostName, restApiEndpointPort, gitRepoPath)

    #Publish Apis
    scope = 'apim:api_publish'
    (accessToken, expiresIn, refreshToken) = getAccessToken(apiKey, apiSecret, userName, userPassword, hostName, tokenEndpointPort,scope)
    publishAllApis(hostName,restApiEndpointPort, accessToken, apiList)

def getAccessToken(apiKey, apiSecret, userName, userPassword, hostName, tokenEndpointPort, scope):
    stsUrl = getTokenEndpoint(hostName, tokenEndpointPort)
    payload= {'client_id' : apiKey,'client_secret':apiSecret, 'username':userName, 'password':userPassword, 'grant_type':'password', 'scope':scope}

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

def getAllApis(hostName, restApiEndpointPort, accessToken):
    stsUrl = getRestApiEndpoint(hostName, restApiEndpointPort) + "/" + "apis"
    headers = {'Authorization': 'Bearer ' + accessToken}
    response = requests.get(stsUrl, headers=headers, verify=False)
    data = json.loads(response.text)
    apiList = []
    for x in range(0, data['count']):
        apiList.append((data['list'][x]['name'], data['list'][x]['id']))
    return apiList

def deleteAllApis(hostName, restApiEndpointPort, accessToken, apiList):
    baseUrl = getRestApiEndpoint(hostName, restApiEndpointPort) + "/" + "apis"
    headers = {'Authorization': 'Bearer ' + accessToken}
    for x in range(0, len(apiList)):
        print "Deleting API: " + apiList[x][0]
        stsUrl = baseUrl + "/" + apiList[x][1]
        response = requests.delete(stsUrl, headers=headers, verify=False)
        if response.status_code == 200:
            print "Successfully deleted API: " + apiList[x][0]
        else:
            print "Error in deleting API :" + apiList[x][1]
    return True

def publishAllApis(hostName, restApiEndpointPort, accessToken, apiList):
    baseUrl = getRestApiEndpoint(hostName, restApiEndpointPort) + "/" + "apis/change-lifecycle?apiId="
    headers = {'Authorization': 'Bearer ' + accessToken}
    for x in range(0, len(apiList)):
        print "Updatinging API: " + apiList[x][0]
        stsUrl = baseUrl + apiList[x][1] + "&action=Publish"
        print stsUrl
        response = requests.post(stsUrl, headers=headers, verify=False)
        if response.status_code == 200:
            print "Successfully published API: " + apiList[x][0]
        else:
            print "Error in publishing API :" + apiList[x][1]
    return True

def gitPullAllApis(gitRepoPath):
    repo = git.Repo( gitRepoPath )
    print repo.git.status()
    print repo.git.pull()

    return True

def zipAllFiles(gitRepoPath):
    dir_list = os.walk(gitRepoPath).next()[1]
    if '.git' in dir_list:
        dir_list.remove('.git')
    for dir in dir_list:
        zipFileName = gitRepoPath + "/" + dir + ".zip"
        zipFolderName = gitRepoPath + "/" + dir
        abszipFolderName = os.path.abspath(gitRepoPath)
        ziph = zipfile.ZipFile(zipFileName, 'w', zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(zipFolderName):
            for file in files:
                absname = os.path.abspath(os.path.join(root, file))
                arcname = absname[len(abszipFolderName) + 1:]
                # DEBUG: print 'zipping %s as %s' % (os.path.join(root, file), arcname)
                ziph.write(absname, arcname)
        ziph.close()
    return True

def getImpExpEndpoint(hostName, port):
    endPint = 'https://' + hostName + ':' + port + '/api-import-export-2.0.0-SNAPSHOT/import-api'
    return endPint

def getRestApiEndpoint(hostName, restApiEnpointPort):
    endPoint = 'https://' + hostName + ':' + restApiEnpointPort + '/api/am/publisher/v0.9'
    return endPoint

def getTokenEndpoint(hostName, tokenEnpointPort):
    endPint = 'https://' + hostName + ':' + tokenEnpointPort + '/token'
    return endPint

def getAuthHeaders(userName, userPassword):
    headerValue = base64.b64encode(userName + ':' + userPassword)
    headers = "{'Authorization': u'Basic " + headerValue + "'}"
    return headers

def getAuthHeaders(userName, userPassword):
    headerValue = base64.b64encode(userName + ':' + userPassword)
    headers = "{'Authorization': 'Basic " + headerValue + "'}"
    headers = {'Authorization': 'Basic YWRtaW46YWRtaW4='}
    return headers


def importAllApis(userName, userPassword, hostName, port, gitRepoPath):
    importUrl = getImpExpEndpoint(hostName,port)
    headers = getAuthHeaders(userName, userPassword)
    rootdir = gitRepoPath
    os.chdir(rootdir)
    for file in glob.glob("*.zip"):
        fileName = rootdir + "/" + file
        print fileName
        with open(fileName, 'rb') as f:
            response = requests.post(importUrl, headers=headers, verify=False, files={'file': f})
            if not response.ok:
                print response
    return True

if __name__ == '__main__':
    if len(sys.argv) != 9:
        print "Usage: python import-api.py apiKey, apiSecret, userName, password hostName tokenEndpointPort restApiEndpointPort gitRepoPath"
        print "Example: ./import-api.py miFZAyBq46RyVhFwcdspQJc10yMa dZNwt9eC0nNQzfR3uubnqZiVnbUa admin admin localhost 8343 9543 /tmp/api-repo/"
        sys.exit(1)
    main(sys.argv[1:])
