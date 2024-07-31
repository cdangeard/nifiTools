from .nifiAPI import nifiAPI
import json

def APIcolorProcessor(nifiAPI : nifiAPI, processorId : str, colorPatern : dict, verbose : bool = False) -> None:
    payload = nifiAPI.getProcessor(processorId)
    type = payload['component']['type']
    if type in colorPatern.keys():
        color = colorPatern[type]
    elif 'default' in colorPatern.keys():
        color = colorPatern['default']
        if verbose:
            print('using default color for ' + type)    
    else:
        if verbose:
            print('no color for ' + type)
        return None
    
    # verify input color
    if color[0] ==  '#' and all(c in '0123456789abcdef' for c in color[1:]) and len(color) == 7 :
        if verbose:
            print('coloring ' + processorId + ' with ' + color)
        freshpayload = {
            'revision': {
                'version': payload['revision']['version'] + 1
            },
            'component' : {
                'id': processorId,
                'style': {
                    'background-color': color
                }
            }         
        }
        if 'clientId' in payload['revision'].keys():
            freshpayload['revision']['clientId'] = payload['revision']['clientId']
        else :
            freshpayload['revision']['clientId'] = nifiAPI.client
            freshpayload['revision']['version'] = 0
        print('new payload: ' + json.dumps(freshpayload['revision'], indent= 2))
        return nifiAPI.callAPI(f"/processors/{processorId}", "PUT", json.dumps(freshpayload, indent= 2))
    else:
        print('invalid color ' + color)
        return None

def APIcolorProcessGroup(nifiAPI : nifiAPI, processGroupId : str, colorPatern : dict, recursive : bool = False, verbose : bool = False) -> None:
    processors = nifiAPI.getProcessorsIdInPG(processGroupId, recursive)
    for processorId in processors:
        APIcolorProcessor(nifiAPI, processorId, colorPatern, verbose)