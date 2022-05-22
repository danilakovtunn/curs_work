import requests
import os
import sys
import json
import numpy as np
import pandas as pd


def GetMetrixNames(url):
    return [
        'libvirt_domain_block_stats_flush_requests_total',
        'libvirt_domain_block_stats_flush_time_seconds_total',
        'libvirt_domain_block_stats_read_bytes_total',
        'libvirt_domain_block_stats_read_requests_total',
        'libvirt_domain_block_stats_read_time_seconds_total',
        'libvirt_domain_block_stats_write_bytes_total',
        'libvirt_domain_block_stats_write_requests_total',
        'libvirt_domain_block_stats_write_time_seconds_total',
        'libvirt_domain_info_cpu_time_seconds_total',
        'libvirt_domain_info_memory_usage_bytes',
        'libvirt_domain_interface_stats_receive_bytes_total',
        'libvirt_domain_interface_stats_receive_drops_total',
        'libvirt_domain_interface_stats_receive_errors_total',
        'libvirt_domain_interface_stats_receive_packets_total',
        'libvirt_domain_interface_stats_transmit_bytes_total',
        'libvirt_domain_interface_stats_transmit_drops_total',
        'libvirt_domain_interface_stats_transmit_errors_total',
        'libvirt_domain_interface_stats_transmit_packets_total ',
        'libvirt_domain_memory_stats_disk_cache_bytes',
        'libvirt_domain_memory_stats_major_fault_total',
        'libvirt_domain_memory_stats_minor_fault_total',
        'libvirt_domain_memory_stats_rss_bytes',
        'libvirt_domain_memory_stats_unused_bytes',
        'libvirt_domain_memory_stats_usable_bytes',
        'libvirt_domain_memory_stats_used_percent',
        'libvirt_domain_vcpu_cpu',
        'libvirt_domain_vcpu_time_seconds_total'
    ]

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
