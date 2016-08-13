#!/usr/bin/python
import sys
import requests
import os
import zipfile
import git
import glob
import json
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def main(argv):
    apiKey = argv[0]
    apiSecret = argv[1]
    userName = argv[2]
    userPassword = argv[3]
    hostName = argv[4]
    tokenEndpointPort = argv[5]
    restApiEndpointPort = argv[6]
    gitRepoPath = argv[7]
    if len(sys.argv) > 9:
        apiName = argv[8]
        apiVersion = argv[9]

    #List APIs
    scope = 'apim:api_view apim:subscription_view apim:subscribe apim:api_create apim:api_publish'
    (accessToken, expiresIn, refreshToken) = getAccessToken(apiKey, apiSecret, userName, userPassword, hostName, tokenEndpointPort,scope)

    apiList = []
    if len(sys.argv) > 9 and len(apiName) and len(apiVersion):
        apiList = getApiId(hostName,restApiEndpointPort, accessToken, apiName, apiVersion)
    else:
        apiList = getAllApis(hostName, restApiEndpointPort, accessToken)

    #Delete all subscription
    subsList = getAllSubscriptions(hostName,restApiEndpointPort, accessToken, apiList)
    deleteAllSubscriptions(hostName,restApiEndpointPort,accessToken,subsList)

    #Delete all APIS
    deleteAllApis(hostName,restApiEndpointPort, accessToken, apiList)

    #Update the Git repository
    dir_list = os.walk(gitRepoPath).next()[1]
    if '.git' in dir_list:
         gitPullAllApis(gitRepoPath)

    #Archive APIs
    zipAllFiles(gitRepoPath)

    if len(sys.argv) > 9 and len(apiName) and len(apiVersion):
        importSingleApi(userName, userPassword, hostName, restApiEndpointPort, gitRepoPath, apiName, apiVersion)
        apiList = getApiId(hostName,restApiEndpointPort, accessToken, apiName, apiVersion)
    else:
        importAllApis(userName, userPassword, hostName, restApiEndpointPort, gitRepoPath)
        #Get updated API list.
        apiList = getAllApis(hostName, restApiEndpointPort, accessToken)

    if apiList:
        publishAllApis(hostName,restApiEndpointPort, accessToken, apiList)
    else:
        print "Empty API list received"

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

def getApiId(hostName, restApiEndpointPort, accessToken, apiName, apiVerison):
    stsUrl = getRestApiEndpoint(hostName, restApiEndpointPort) + "/" + "apis"
    headers = {'Authorization': 'Bearer ' + accessToken}
    response = requests.get(stsUrl, headers=headers, verify=False)
    data = json.loads(response.text)
    apiList = []
    for x in range(0, data['count']):
        if data['list'][x]['name'] == apiName and data['list'][x]['version'] == apiVerison:
            apiList.append((data['list'][x]['name'], data['list'][x]['id']))
    return apiList

def getAllApis(hostName, restApiEndpointPort, accessToken):
    stsUrl = getRestApiEndpoint(hostName, restApiEndpointPort) + "/" + "apis"
    headers = {'Authorization': 'Bearer ' + accessToken}
    response = requests.get(stsUrl, headers=headers, verify=False)
    data = json.loads(response.text)
    apiList = []
    for x in range(0, data['count']):
        apiList.append((data['list'][x]['name'], data['list'][x]['id']))
    return apiList

def deleteAllSubscriptions(hostName, restApiEndpointPort, accessToken,subsList):
    baseUrl = getRestStoreApiEndpoint(hostName, restApiEndpointPort) + "/" + "subscriptions"
    headers = {'Authorization': 'Bearer ' + accessToken}
    for x in range(0, len(subsList)):
        stsUrl = baseUrl + "/" + subsList[x][1]
        response = requests.delete(stsUrl, headers=headers, verify=False)
        if response.status_code == 200:
            print "Successfully deleted the subscription: " + subsList[x][0] + " : " + subsList[x][0]
        else:
            print "Error in deleting the subscriptions :" + subsList[x][1]
    return

def getAllSubscriptions(hostName, restApiEndpointPort, accessToken, apiList):
    baseUrl = getRestApiEndpoint(hostName, restApiEndpointPort) + "/" + "subscriptions?apiId="
    headers = {'Authorization': 'Bearer ' + accessToken}
    subsList = []
    for x in range(0, len(apiList)):
        stsUrl = baseUrl + apiList[x][1]
        response = requests.get(stsUrl, headers=headers, verify=False)
        if response.status_code == 200:
            print "Successfully received subscriptions for: " + apiList[x][0]
            #Loop over list of subscription and delete subscription
            data = json.loads(response.text)
            for x in range(0, data['count']):
                subsList.append((data['list'][x]['apiIdentifier'], data['list'][x]['subscriptionId']))
        else:
            print "Error in getting subscriptions: " + apiList[x][1]
    return subsList

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
        response = requests.post(stsUrl, headers=headers, verify=False)
        if response.status_code == 200:
            print "Successfully published API: " + apiList[x][0]
        else:
            print "Error in publishing API :" + apiList[x][1]
    return

def gitPullAllApis(gitRepoPath):
    repo = git.Repo( gitRepoPath )
    print repo.git.status()
    print repo.git.pull()
    return

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
    #Preserve provider set to false to support new environments
    endPoint = 'https://' + hostName + ':' + port + '/api-import-export-2.0.0-v0/import-api?preserveProvider=false'
    return endPoint

def getRestApiEndpoint(hostName, restApiEnpointPort):
    endPoint = 'https://' + hostName + ':' + restApiEnpointPort + '/api/am/publisher/v0.10'
    return endPoint

def getRestStoreApiEndpoint(hostName, restApiEnpointPort):
    endPoint = 'https://' + hostName + ':' + restApiEnpointPort + '/api/am/store/v0.10'
    return endPoint

def getTokenEndpoint(hostName, tokenEnpointPort):
    endPint = 'https://' + hostName + ':' + tokenEnpointPort + '/token'
    return endPint

def getAuthHeaders(userName, userPassword):
    return HTTPBasicAuth(userName, userPassword)

def importSingleApi(userName, userPassword, hostName, port, gitRepoPath, apiName, apiVersion):
    importUrl = getImpExpEndpoint(hostName,port)
    basicAuth = getAuthHeaders(userName, userPassword)
    rootdir = gitRepoPath
    fileName = rootdir + "/" + apiName + "-" + apiVersion + ".zip"
    with open(fileName, 'rb') as f:
        response = requests.post(importUrl, auth=basicAuth, verify=False, files={'file': f})
        if not response.ok:
            print response
    return

def importAllApis(userName, userPassword, hostName, port, gitRepoPath):
    importUrl = getImpExpEndpoint(hostName,port)
    basicAuth = getAuthHeaders(userName, userPassword)
    rootdir = gitRepoPath
    os.chdir(rootdir)
    for file in glob.glob("*.zip"):
        fileName = rootdir + "/" + file
        print "Importing API Archive: " + file
        with open(fileName, 'rb') as f:
            response = requests.post(importUrl, auth=basicAuth, verify=False, files={'file': f})
            if not response.ok:
                print response
    return

if __name__ == '__main__':
    if len(sys.argv) < 9:
        print "Usage: python import-api.py apiKey, apiSecret, userName, password hostName tokenEndpointPort restApiEndpointPort gitRepoPath apiName apiVersion"
        print "Example: ./import-api.py miFZAyBq46RyVhFwcdspQJc10yMa dZNwt9eC0nNQzfR3uubnqZiVnbUa admin admin localhost 8343 9543 /tmp/api-repo/ ERP 1.0.1"
        sys.exit(1)
    main(sys.argv[1:])
