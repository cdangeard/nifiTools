from .nifiAPI import nifiAPI
import pandas as pd
import time
import re
from typing import Union

UUID_PATTERN = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)

class Monitor:
    def __init__(self, nifiAPI : nifiAPI, verbose : bool = False) -> None:
        self.nifiAPI = nifiAPI
        self.verbose = verbose

    def getPGstatus_info(self, processGroupId : str) -> dict:
        res = self.nifiAPI.getProcessGroupStatus(processGroupId)
        sortie = {proc['id'] : int(proc['connectionStatusSnapshot']['queuedCount']) for proc in 
               res['processGroupStatus']['aggregateSnapshot']['connectionStatusSnapshots']}
        sortie[processGroupId] = int(res['processGroupStatus']['aggregateSnapshot']['queuedCount'])
        sortie['timestamp'] = time.time()
        return sortie
    
    def observePG(self, processGroupId : str, rate : float = 1.0, maxDuration : int = 10) -> pd.DataFrame:
        """
        return a DataFrame with the status of the process group
        asynchronously waiting for each intervalSeconds
        infos : 
            - queue count

        Parameters
        ----------
        processGroupId : uuid of process group
        rate : number of calls maximum per second
        maxDuration : maximum duration of observation in seconds
        """
        intervalSeconds = 1/rate
        numberOfData = int(rate*maxDuration)
        data = {k : {} for k in range(0, numberOfData, 1)}
        #list of process groups inside the PG
        PGs = self.nifiAPI.getProcessGroupsList(processGroupId=processGroupId, recursive=True)
        PGs.append(processGroupId)
        for i in range(0, numberOfData, 1):
            start = time.perf_counter()
            cycleData = {}
            for pg in PGs:
                cycleData = cycleData | self.getPGstatus_info(pg)
            data[i] = cycleData
            elapsed = time.perf_counter() - start
            time.sleep(max(0.0, intervalSeconds - elapsed))
        return data
    
    def monitor_PG(self, processGroupId : str, 
                rate : float = 1.0, maxDuration : int = 10,
                start :  str = 'auto', verbose : bool = False) -> pd.DataFrame:
        """
        return a DataFrame with the status of the process group
        asynchronously waiting for each intervalSeconds
        infos : 
            - queue count

        Parameters
        ----------
        processGroupId : uuid of process group
        rate : number of calls maximum per second
        maxDuration : maximum duration of observation in seconds
        start : uuid of the source processor or 'auto' or None/'manual'
        """
        # Resolve start if auto
        if start == 'auto':
            sources = self.nifiAPI.findSourceProcessor(processGroupId=processGroupId)
            if len(sources) == 1:
                start = sources[0]
                if verbose:
                    print('Starter Found :', start)
            else:
                raise Exception(ValueError, 'No source processor found')
        elif re.match(UUID_PATTERN, start):
            start = start
        elif start == 'manual' or start == None or not(start):
            start = False
        else:
            raise Exception(ValueError, 'Wrong start parameter')
        if start:
            if verbose:
                print('Running once :', start)
            self.nifiAPI.runOnceProcessor(processorId=start)
        # Start monitoring
        if verbose:
            print('Start monitoring')
        return self.observePG(processGroupId=processGroupId, rate=rate, maxDuration=maxDuration)
