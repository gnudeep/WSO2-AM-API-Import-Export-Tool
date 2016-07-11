# WSO2 API Manager API Bulk Import Export Tool

This tool helps to export all the created APIs in a WSO2 API Manager deployment in to a set of source file and import it in to a different WSO2 API Manager deployment.

To export APIs, the script uses [API Manager REST API](https://docs.wso2.com/display/AM200/Published+APIs) and the APIs exposed by [api-import-export-2.0.0](https://docs.wso2.com/display/AM200/Migrating+the+APIs+to+a+Different+Environment) web application.

####API Export steps
API Import and Export scripts need OAuth application registered in the API Manager to use Store/Publisher REST API.

#### Create Applicatin for API Manager REST API:
To create a OAuth application Carbon user or Carbon tenant user credentials have to be provided.

OAuth Application Creation Request.
```
curl -X POST -H "Authorization: Basic YWRtaW46YWRtaW4=" -H "Content-Type: application/json" -d @payload.json http://localhost:9763/client-registration/v0.9/register
```

payload.json
```
{
    "callbackUrl": "localhost",
    "clientName": "rest_api_publisher",
    "tokenScope": "Production",
    "owner": "admin",
    "grantType": "password refresh_token",
    "saasApp": true
}
```

Response
```
{"appOwner":null,"clientName":null,"callBackURL":"localhost","isSaasApplication":true,"jsonString":"{\"username\":\"admin\",\"redirect_uris\":\"www.google.lk\",\"client_name\":\"admin_rest_api_publisher\",\"grant_types\":\"urn:ietf:params:oauth:grant-type:saml2-bearer iwa:ntlm implicit refresh_token client_credentials authorization_code password\"}","clientId":"iMWERi0Sg60kV3C1u9Mb0_Q0o74a","clientSecret":"Zm27CVLgUnDQLY8eqlQFgbHf8Ika"}

```

#### Execute the API Export tool
API export script exports the API (download API Zip archive and unzip) to a local folder. If the local folder is a Git repository the script commit new changes and push the new changes to a remote Git repository.

Command syntax to export all the APIs: export-api.py apiKey apiSecret userName password hostName tokenEndpointPort restApiEndpointPort gitRepoPath
```
./export-api.py iMWERi0Sg60kV3C1u9Mb0_Q0o74a Zm27CVLgUnDQLY8eqlQFgbHf8Ika admin admin123 localhost 8243 9443 /tmp/api-repo/
```

Command syntax to export single API: export-api.py apiKey apiSecret userName password hostName tokenEndpointPort restApiEndpointPort gitRepoPath apiName apiVersion
```
./export-api.py iMWERi0Sg60kV3C1u9Mb0_Q0o74a Zm27CVLgUnDQLY8eqlQFgbHf8Ika admin admin123 localhost 8243 9443 /tmp/api-repo/ DEEP-Test 1.0.0
```

For Multi-Tenant environments

Command syntax to export all the APIs: export-api.py apiKey apiSecret userName password hostName tokenEndpointPort restApiEndpointPort gitRepoPath
```
./export-api.py iMWERi0Sg60kV3C1u9Mb0_Q0o74a Zm27CVLgUnDQLY8eqlQFgbHf8Ika admin@mytenant.com mytenant123 localhost 8243 9443 /tmp/api-repo/
```


####API Import steps
Create an OAuth application in the destination API Manager deployment to import APIs. retrieve a access token to communicate with import APIM REST API.

####Execute the API Import tool
API import script updates the local Git repository to get latest changes from the remote Git repo and export all the API in the Git repo to the given APIM deployment.

Command syntax: import-api.py apiKey, apiSecret, userName, password hostName tokenEndpointPort restApiEndpointPort gitRepoPath
```
./import-api.py miFZAyBq46RyVhFwcdspQJc10yMa dZNwt9eC0nNQzfR3uubnqZiVnbUa admin admin localhost 8343 9543 /tmp/api-repo/
```