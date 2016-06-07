#!/usr/bin/python
import sys
import requests
import os
import zipfile
import git
import glob
import base64


def main(argv):

    userName = argv[0]
    userPassword = argv[1]
    hostName = argv[2]
    restApiEndpointPort = argv[3]
    gitRepoPath = argv[4]

    gitPullAllApis(gitRepoPath)
    zipAllFiles(gitRepoPath)
    importAllApis(userName, userPassword, hostName, restApiEndpointPort, gitRepoPath)

def gitPullAllApis(gitRepoPath):
    repo = git.Repo( gitRepoPath )
    print repo.git.status()
    print repo.git.pull()

    return True

def zipAllFiles(gitRepoPath):
    dir_list = os.walk(gitRepoPath).next()[1]
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
                print 'zipping %s as %s' % (os.path.join(root, file), arcname)
                ziph.write(absname, arcname)
        ziph.close()
    return True

def getAllApiKeys():

    return True

def deletAllApis():

    return True;

def getImpExpEndpoint(hostName, port):
    endPint = 'https://' + hostName + ':' + port + '/api-import-export-2.0.0-SNAPSHOT/import-api'
    return endPint

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
    if len(sys.argv) != 6:
        print "Usage: python import-api.py userName, password hostName restApiEndpointPort gitRepoPath"
        print "Example: ./import-api.py admin admin localhost 9543 /tmp/api-repo"
        sys.exit(1)
    main(sys.argv[1:])
