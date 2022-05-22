import requests
import os
import sys
import json
import numpy as np
import pandas as pd


def GetMetrixNames(url):
    response = requests.get('{0}/api/v1/label/__name__/values'.format(url))
    names = response.json()['data']    #Return metrix names
    return names

def main():    
    if len(sys.argv) < 2:
        print('Usage: {0} http://localhost:9090'.format(sys.argv[0]))
        sys.exit(1)
    
    metrixNames = GetMetrixNames(sys.argv[1])

    dataframes = {}
    for metrixName in metrixNames:
        response = requests.get(
            '{0}/api/v1/query'.format(sys.argv[1]), 
            params={'query': metrixName+'[10h]'}
        )
        results = response.json()['data']['result']
        
        if len(results) == 0 or 'domain' not in results[0]['metric'].keys():
            continue
        
        data = {}
        for result in results:
            if 'target_device' in result['metric']:
                if result['metric']['name'] not in data.keys():
                    data[result['metric']['name']] = np.array(result['values'])[:, 1].astype(np.float64)
                else:
                    data[result['metric']['name']] += np.array(result['values'])[:, 1].astype(np.float64)
            else:
                data[result['metric']['name']] = np.array(result['values'])[:, 1].astype(np.float64)
        
        for i in data.keys():
            if i not in dataframes.keys():
                dataframes[i] = pd.DataFrame()
            dataframes[i][metrixName] = data[i]
   
    if not os.path.exists('data'):
        os.makedirs('data')
    for i in dataframes.keys():   
        dataframes[i].to_csv('data/' + i + '.csv')

if __name__ == '__main__':
    main()    
