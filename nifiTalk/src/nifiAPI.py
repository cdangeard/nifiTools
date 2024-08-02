import requests
import json
import uuid

# disable warnings
requests.packages.urllib3.disable_warnings()

class nifiAPI:
    def __init__(self, host : str, client : str = None, verbose : bool = False) -> None:
        if host[-1] != "/":
            host = host + "/"
        self.host = host + "nifi-api"
        self.verbose = verbose
        if client:
            self.client = self.callAPI('/flow/client-id', type='GET', payload=None)
        else:
            self.client = str(uuid.uuid4())
            print('generated client id: ' + self.client)


    def makeRequest(self, url, headers, payload, type : str):
        """
        Makes an API call
        
        Parameters
        ----------
        url : url to call
        headers : headers to send
        payload : body to send
        """
        return requests.request(type, url, headers=headers, data=payload, verify=False)

    def callAPI(self, endpoint : str, type : str, payload : dict):
        """
        Makes an API call
        
        Parameters
        ----------
        endpoint : str - API endpoint
        type : str - GET, POST, PUT, DELETE
        payload : dict - json payload
        """
        headers = {
        'Content-Type': 'application/json'
        }
        if endpoint[0] != "/":
            endpoint = "/" + endpoint
        url = self.host + endpoint
        if self.verbose:
            print("calling " + url)
            if payload is not None:
                print("with payload: " + json.dumps(payload, indent= 2))
        response = self.makeRequest(url, headers, json.dumps(payload), type)
        if response.status_code != 200:
            print(response.text)
            raise Exception(f"API call failed with status code: {response.status_code}\n {response.text}")
        try:
            jsonResponse = response.json()
        except json.decoder.JSONDecodeError:
            jsonResponse = response.text
        return jsonResponse

    def makeProcessorRevision(self, processorId : str) -> dict:
        """
        Return

        Parameters
        ----------
        processorId : str uuid of processor
        """
        oldPayload = self.getProcessor(processorId)
        if 'clientId' not in oldPayload['revision'].keys():
            return {'revision': {
                        'clientId' : self.client,
                        'version' : 0
                        }}
        return {'revision': {
                    'clientId' : oldPayload['revision']['clientId'],
                    'version' : oldPayload['revision']['version'] + 1
                }}

################################## PUTs #######################################
    class processor:
        def modifyProcessor(self, processorId : str, changes : dict) -> dict:
            """
            Pushes changes to a processor
            Manage versions of processors

            Parameters
            ----------
            processorId : uuid of processor
            changes : dict
                
                for format see : 
                    https://nifi-python-swagger-client.readthedocs.io/en/latest/ProcessorEntity/
                
                ex :
                    {
                        'component' : {...}
                    }
            """
            payload = self.makeProcessorRevision(processorId) | changes
            payload['component']['id'] = processorId
            
            if self.verbose:
                print('Modifying processor ' + processorId 
                    + ' with payload: \n' + json.dumps(payload, indent= 2))
            
            jsonPayload = json.dumps(payload, indent= 2)
            return self.callAPI(f"/processors/{processorId}", "PUT", jsonPayload)

################################## RUNs #######################################
    def runOnceProcessor(self, processorId : str):
        """
        Run a processor once
        """
        changes = self.makeProcessorRevision(processorId) | {"state" : "RUN_ONCE"}
        return self.callAPI(f"/processors/{processorId}/run-status", "PUT", changes)
      
################################## GETs #######################################

    def getRootProcessGroup(self) -> str:
        """
        Get id of root process group
        """
        return self.callAPI("/flow/process-groups/root", "GET", None)['processGroupFlow']['id']
    def getProcessor(self, processorId : str) -> dict:
        """
        Get details of a processor

        Parameters
        ----------
        processorId : str uuid of processor
        """
        return self.callAPI(f"/processors/{processorId}", "GET", None)
  
    def getProcessGroupList(self, processGroupId : str, recursive : bool = False) -> list:
        """
        Get id of process group contained in a process group

        Parameters
        ----------
        
        processorId : uuid of processor
        recursive : True if you want to get the process group containing
                    the processor in all process groups
        """
        response = self.callAPI(f"/process-groups/{processGroupId}/process-groups",
                                type =  "GET", payload = None)
        sortie = [pg['id'] for pg in response['processGroups']]
        if recursive:
            for pgId in sortie:
                sortie.extend(self.getProcessGroupList(pgId, recursive))
        return sortie
    
    def getProcessGroupsInfosList(self, processGroupId : str, recursive : bool = False) -> list:
        """
        Get 
            - name
            - id 
        of process group contained in a process group

        Parameters
        ----------
        
        processorId : uuid of processor
        recursive : True if you want to get the process group containing
                    the processor in all process groups
        """
        response = self.callAPI(f"/process-groups/{processGroupId}/process-groups",
                                type =  "GET", payload = None)
        sortie = [{'id' :pg['id'], 
                   'name' : pg['component']['name']} 
                   for pg in response['processGroups']]
        if recursive:
            for pgId in sortie:
                sortie.extend(self.getProcessGroupsInfosList(pgId['id'], recursive))
        return sortie
    
    def getProcessGroupsInfos(self, processGroupId: str, recursive : bool = False) -> dict:
        """
        """
        response = self.callAPI(f"/process-groups/{processGroupId}/process-groups",
                                type =  "GET", payload = None)
        sortie = {pg['id'] : {'parentGroupId' : processGroupId, 
                              'name' : pg['component']['name']} 
                              for pg in response['processGroups']}
        if recursive:
            for pgId in [id for id in sortie.keys()]:#avoid changing dic size during iteration
                pgSortie = self.getProcessGroupsInfos(pgId, recursive)
                sortie.update(pgSortie)
        return sortie

    def getProcessorsList(self, processGroupId : str, recursive : bool = False) -> list:
        """
        Get id of all processors in a process group
        
        Parameters
        ----------
        
        processGroupId : uuid of process group
        recursive : True if you want to get all processors in all process groups
        """
        response = self.callAPI(f"/process-groups/{processGroupId}/processors", "GET", None)
        sortie = [proc['id'] for proc in response['processors']]
        if recursive:
            #get all process groups
            pgs = self.getProcessGroupList(processGroupId, recursive = False)
            for pgId in pgs['processGroups']:
                pgSortie = self.getProcessorsList(pgId, recursive)
                sortie.extend(pgSortie)
        return sortie
    
    def getProcessorsInfos(self, processGroupId : str, recursive : bool = False) -> dict:
        """
        return dict of processor ;
            - id
            - name
            - type
            - parentGroupId
            - state

        Parameters
        ----------
        processGroupId : uuid of process group
        recursive : True if you want to get all processors in all process groups
        """

        response = self.callAPI(f"/process-groups/{processGroupId}/processors", "GET", None)
        sortie = {proc['id'] : {'name' : proc['component']['name'],
                                'type' : proc['component']['type'], 
                                'parentGroupId' : proc['component']['parentGroupId'],
                                'state' : proc['component']['state']
                                }
                 for proc in response['processors']}
        sortie[processGroupId] = {}
        if recursive:
            #get all process groups
            pgs = self.getProcessGroupList(processGroupId, recursive = False)
            for pg in pgs:
                pgSortie = self.getProcessorsInfos(pg, recursive)
                pgSortie[pg] = {'parentGroupId' : processGroupId}
                sortie.update(pgSortie)
        return  sortie
   
    def getConnectionsList(self, processGroupId : str, recursive : bool = False) -> list:
        """
        Get id of all connections in a process group
        
        Parameters
        ----------
        
        processGroupId : uuid of process group
        recursive : True if you want to get all connections in all process groups
        """
        response = self.callAPI(f"/process-groups/{processGroupId}/connections",
                                type = "GET", payload = None)
        sortie = [conn['id'] for conn in response['connections']]
        if recursive:
            #get all process groups
            pgs = self.getProcessGroupList(processGroupId, recursive = False)
            for pgId in pgs:
                pgSortie = self.getConnectionsList(pgId, recursive)
                sortie.extend(pgSortie)
        return sortie
       
    def getProcessGroupStatus(self, processGroupId : str) -> dict:
        """
        Get status of a process group
        
        Parameters
        ----------
        processGroupId : uuid of process group
        """
        return self.callAPI(f"flow/process-groups/{processGroupId}/status",
                            type = "GET", payload = None)

    def getControlerServices(self, processGroupId : str,
                                  recursive : bool = False) -> dict:
        """
        Get ids and status & info of all controlers services in a process group
        
        Parameters
        ----------
        
        processGroupId : uuid of process group
        recursive : True if you want to get all controlers in all process groups
        """
        res = self.callAPI(endpoint=f'/flow/process-groups/{processGroupId}/controller-services',
                            type='GET',payload= None)
        sortie =  {ctrl['id'] : {'parentGroupId' : ctrl['parentGroupId'],
                                        'name' : ctrl['component']['name'], 
                                        'state' : ctrl['component']['state'],
                                        'type' : ctrl['component']['type'], 
                                        }
                        for ctrl in res['controllerServices']}
        if recursive:
            #get all process groups
            pgs = self.getProcessGroupList(processGroupId, recursive = False)
            for pgId in pgs:
                pgSortie = self.getControlerServices(pgId, recursive)
                sortie.update(pgSortie)
        return sortie

#################################### FINDs ####################################
    def findSourceProcessor(self, processGroupId : str, recursive : bool = True) -> dict:
        """
        Find source processor in a process group

        Parameters
        ----------
        processGroupId : uuid of process group
        """
        subProcessGroup = self.getProcessGroupList(processGroupId, recursive=True)
        starter = []
        for sub in subProcessGroup + [processGroupId]:
            a = self.callAPI(f"/process-groups/{sub}/connections", "GET", None)
            connexions = a['connections']
            destinations = [conn['component']['destination'] for conn in connexions]
            sources = [conn['component']['source'] for conn in connexions]
            origin = set(s['id'] for s in sources 
                         if s not in destinations and s['type'] == 'PROCESSOR')
            starter.extend(origin)
        return starter
    

###############################################################################
class nifiAPI_userAuth(nifiAPI):
    def __init__(self, host : str, username : str, password : str,
                  client : str = None, verbose : bool = False) -> None:
        self.username = username
        self.password = password
        self.verbose = verbose
        if host[-1] != "/":
            host = host + "/"
        self.host = host + "nifi-api"
        self.fetchToken()
        if client is None:
            self.client = str(uuid.uuid4())
            print('generated client id: ' + self.client)
        else:
            self.client = self.callAPI('/flow/client-id', type='GET', payload=None)
    def fetchToken(self):
        """
        Fetches a new token with username and password
        """
        payload=f'username={self.username}&password={self.password}'
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }
        urlToken = self.host + "/access/token"
        print('fetching new token at ' + urlToken)
        response = requests.request("POST", urlToken, headers=headers,
                                    data=payload, verify=False)
        if response.status_code not in [200, 201]:
            raise Exception("Failed getting token: " + str(response.status_code))
        self.token = response.text
        print("new token: " + self.token)

    def makeRequest(self, url, headers, payload, type : str):
        """
        Makes a request to the API
        use stored Bearer token
        
        Parameters
        ----------
        url : url to call
        headers : headers to send
        payload : body to send
        """
        headers['Authorization'] = 'Bearer ' + self.token
        response = requests.request(type, url, headers=headers,
                                     data=payload, verify=False)
        if response.status_code == 401:
            self.fetchToken()
            response = requests.request("POST", url, headers=headers,
                                         data=payload, verify=False)
        return response      

###############################################################################
class nifiAPI_certAuth(nifiAPI):
    def __init__(self, host : str, pemPath : str, certPath : str, keyPath : str,
                 client : str = None, verbose : bool = False) -> None:
        self.pem = pemPath
        self.cert = certPath
        self.key = keyPath
        super().__init__(host, client, verbose)

    def makeRequest(self, url, headers, payload, type : str):
        """
        Makes a request to the API
        uses certificates
        
        Parameters
        ----------
        url : url to call
        headers : headers to send
        payload : body to send
        """
        response = requests.request(type, url, headers=headers,
                                    data=payload, verify=self.pem, 
                                    cert=(self.cert, self.key))
        if response.status_code != 200:
            print(response.text)
            raise Exception("API call failed with status code: " +
                             str(response.status_code))
        return response