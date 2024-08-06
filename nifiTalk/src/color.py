from .nifiAPI import nifiAPI
import json

def APIcolorProcessor(nifiAPI : nifiAPI, processorId : str, 
                      colorPatern : dict, verbose : bool = False) -> None:
    payload = nifiAPI.getProcessor(processorId)
    type = payload['component']['type']
    if ('style' in payload['component'].keys() 
        and 'background-color' in payload['component']['style'].keys()
        and payload['component']['style']['background-color'] == colorPatern[type]):
        return type, False, 'Already colored'
    if type in colorPatern.keys():
        color = colorPatern[type]
    elif 'default' in colorPatern.keys():
        color = colorPatern['default']
        if verbose:
            print('using default color for ' + type)    
    else:
        if verbose:
            print('no color for ' + type)
        return type, False, 'No color'
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
        if verbose:
            print('new payload: ' + json.dumps(freshpayload, indent= 2))
        return type, True, 'Colored'
    else:
        raise Exception('invalid color ' + color)

def APIcolorProcessGroup(nifiAPI : nifiAPI, processGroupId : str, colorPatern : dict,
                         recursive : bool = False, verbose : bool = False,
                         results : bool = False) -> dict | None:
    processors = nifiAPI.getProcessorsList(processGroupId, recursive)
    if results:
        dict = {processor : [] for processor in processors}
    for processorId in processors:
        try:
            res = APIcolorProcessor(nifiAPI, processorId, colorPatern, verbose)
            if results:
                dict[processorId] = res
        except Exception as e:
            print('could not color ' + processorId)
            print(e)
            if results:
                dict[processorId] = False, 'Error'
            continue
    return dict if results else None

