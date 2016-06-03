#!/usr/bin/python
import sys
import requests
import os
import zipfile
import git
import glob


def main(argv):

    userName = argv[0]
    userPassword = argv[1]
    hostName = argv[2]

    gitPullAllApis()
    zipAllFiles()
    importAllApis()

def gitPullAllApis():

    repo = git.Repo( '/tmp/api-repo-import' )
    print repo.git.status()
    print repo.git.pull()

    return True

def zipAllFiles():

    rootdir = '/tmp/api-repo-import'

    dir_list = os.walk(rootdir).next()[1]
    dir_list.remove('.git')
    for dir in dir_list:
        zipFileName = rootdir + "/" + dir + ".zip"
        zipFolderName = rootdir + "/" + dir
        abszipFolderName = os.path.abspath(rootdir)
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

def importAllApis():
    importUrl = 'https://172.17.42.1:9543/api-import-export-2.0.0-SNAPSHOT/import-api'
    headers = {'Authorization': 'Basic YWRtaW46YWRtaW4='}
    rootdir = '/tmp/api-repo-import'
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
    if len(sys.argv) != 4:
        print "Usage: python import-api.py userName, password hostName"
        sys.exit(1)
    main(sys.argv[1:])
