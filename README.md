# WSO2-AM-API-Import-Export-Tool

This tool helps to export all the created APIs in a WSO2 API Manager deployment in to a set of source file and export it in to a different WSO2 API Manager deployment.

To export APIs user has to use APIM REST API and the APIs exposed by api-import-export-2.0.0 web application.

####API Export steps

####Create Applicatin for APIM REST API:
```
curl -X POST -H "Authorization: Basic YWRtaW46YWRtaW4=" -H "Content-Type: application/json" -d @payload.json http://localhost:9763/client-registration/v0.9/register

{
    "callbackUrl": "localhost",
    "clientName": "rest_api_publisher",
    "tokenScope": "Production",
    "owner": "admin",
    "grantType": "password refresh_token",
    "saasApp": true
}
```

####Get Access Token
User the consumer key and secret to retrieve the access token.
```
curl -k -d "grant_type=password&username=admin&password=admin&scope=apim:api_view" -H "Authorization: Basic aU1XRVJpMFNnNjBrVjNDMXU5TWIwX1Ewbzc0YTpabTI3Q1ZMZ1VuRFFMWThlcWxRRmdiSGY4SWth" https://127.0.0.1:8243/token
```

#### Execute the API Export tool.
API export script exports the API to a local git repo and commit the new changes to the remote git repository.

Command syntax:


####API Import steps
Create Application in the APIM deployment in the API import APIM deployment following the steps explained in the Create Application section and retrieve a access token to communicate with import APIM REST API.

####Execute the API Import tool
API import script updates the local Git repository to get latest chages from the remote Git repo and export all the API in the Git repo to the given APIM deployment.

