#!/usr/bin/python
import sys
import requests
import json
import os
import zipfile
import git
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

    #List all APIs
    (accessToken, expiresIn, refreshToken) = getAccessToken(apiKey, apiSecret, userName, userPassword, hostName, tokenEndpointPort)
    apiList = getAllApis(hostName,restApiEndpointPort, accessToken)

    #Export APIs
    if len(sys.argv) > 9 and len(apiName) and len(apiVersion):
        print "Exporting API : " + apiName + "-" + apiVersion
        zipFilePath = exportSingleApi(hostName, restApiEndpointPort, userName, userPassword,apiName, apiVersion, gitRepoPath)
        unzipSingleFile(gitRepoPath, zipFilePath);
    else:
        print "Exporting All APIs"
        exportAllApis(hostName, restApiEndpointPort, userName, userPassword, apiList, gitRepoPath)
        unzipAllFiles(gitRepoPath)    

    #Push to a Git Repository
    dir_list = os.walk(gitRepoPath).next()[1]
    if '.git' in dir_list:
        gitPushAllApis(gitRepoPath)
        print "All APIs exported and saved in " + gitRepoPath + "and pushed to remote git repository."
    else:
        print "All APIs exported and saved in " + gitRepoPath
        return

def getAccessToken(apiKey, apiSecret, userName, userPassword, hostName, tokenEndpointPort):
    stsUrl = getTokenEndpoint(hostName, tokenEndpointPort)
    payload= {'client_id' : apiKey,'client_secret':apiSecret, 'username':userName, 'password':userPassword, 'grant_type':'password', 'scope':'apim:api_view'}
    
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
        apiList.append((data['list'][x]['name'], data['list'][x]['version']))
    return apiList

def exportSingleApi(hostName, port, userName, userPassword, apiName, apiVersion, gitRepoPath):
    zipFilePath = gitRepoPath + "/" + apiName + "-" + apiVersion + ".zip"
    importExportEndpoint = getImpExpEndpoint(hostName, port)
    exportUrl = importExportEndpoint + '?name=' + apiName + '&version=' + apiVersion + '&provider=' + userName
    basicAuth = getAuthHeaders(userName, userPassword)
    with open(zipFilePath, 'wb') as handle:
        response = requests.get(exportUrl, auth=basicAuth, verify=False, stream=True)
        if not response.ok:
            print response
        for block in response.iter_content(1024):
            handle.write(block)
    return zipFilePath

def exportAllApis(hostName, port, userName, userPassword, apiList, gitRepoPath):
    for x in range(0, len(apiList)):
        zipFilePath = gitRepoPath + "/" + apiList[x][0] + "-" + apiList[x][1] + ".zip"
        importExportEndpoint = getImpExpEndpoint(hostName, port)
        exportUrl = importExportEndpoint + '?name=' + apiList[x][0] + '&version=' + apiList[x][1] + '&provider=' + userName
        basicAuth = getAuthHeaders(userName, userPassword)
        with open(zipFilePath, 'wb') as handle:
            response = requests.get(exportUrl, auth=basicAuth, verify=False, stream=True)
            if not response.ok:
                print response
            for block in response.iter_content(1024):
                handle.write(block)
    return

def unzipAllFiles(gitRepoPath):
    for item in os.listdir(gitRepoPath):
        filePath = os.path.abspath(os.path.join(gitRepoPath, item))
        unzipAndRemoveFile(filePath, gitRepoPath)
    return

def unzipSingleFile(gitRepoPath, zipFilePath):
    filePath = os.path.abspath(zipFilePath)
    unzipAndRemoveFile(filePath, gitRepoPath)
    return

def unzipAndRemoveFile(filePath, targetDirectory):
    os.chdir(targetDirectory)
    extension = ".zip"
    if filePath.endswith(extension):
        zip_ref = zipfile.ZipFile(filePath)
        zip_ref.extractall()
        zip_ref.close()
        os.remove(filePath)
    return

def gitPushAllApis(gitRepoPath):
    repo = git.Repo(gitRepoPath)
    repo.git.add('*')
    gitStatus = repo.git.status()
    if gitStatus.find("nothing to commit") > -1:
        repo.git.push()
    else:
        repo.git.commit( m='Added new API Changes' )
        repo.git.push()
    print repo.git.status()

    return True

def getImpExpEndpoint(hostName, restApiEnpointPort):
    endPoint = 'https://' + hostName + ':' + restApiEnpointPort + '/api-import-export-2.0.0-SNAPSHOT-v0/export-api'
    return endPoint

def getRestApiEndpoint(hostName, restApiEnpointPort):
    endPoint = 'https://' + hostName + ':' + restApiEnpointPort + '/api/am/publisher/v0.9/'
    return endPoint

def getTokenEndpoint(hostName, tokenEnpointPort):
    endPint = 'https://' + hostName + ':' + tokenEnpointPort + '/token'
    return endPint

def getAuthHeaders(userName, userPassword):
    return HTTPBasicAuth(userName, userPassword)

if __name__ == '__main__':
    if len(sys.argv) < 9:
        print "Usage: python export-api.py apiKey, apiSecret, userName, password hostName tokenEndpointPort restApiEndpointPort stagingDir apiName apiVersion"
        print "Example: ./export-api.py iMWERi0Sg60kV3C1u9Mb0_Q0o74a Zm27CVLgUnDQLY8eqlQFgbHf8Ika admin admin localhost 8243 9443 /tmp/api-repo/ ERP 1.0.1"
        sys.exit(1)
    main(sys.argv[1:])