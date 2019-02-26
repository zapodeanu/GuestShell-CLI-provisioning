#!/usr/bin/env python3


# developed by Gabi Zapodeanu, TSA, GPO, Cisco Systems


# import Python packages


import urllib3
import requests
import json
import datetime
import netmiko
import time


# import functions modules

from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings
from requests.auth import HTTPBasicAuth  # for Basic Auth
from netmiko import ConnectHandler

from config import DEVICE_IP, DEVICE_TYPE, USER, PASS

urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings


DEVICE_INFO = {
    'device_type': DEVICE_TYPE,
    'host': DEVICE_IP,
    'username': USER,
    'password': PASS,
    }


def main():

    print(DEVICE_INFO)

    net_connect = ConnectHandler(**DEVICE_INFO)
    command_output = net_connect.find_prompt()

    print('\nConnected to device: ', command_output)


    config_commands = ['iox', 'aaa new-model',
                       'aaa authentication login default local',
                       'aaa authorization exec default local',
                       'ip name-server 208.67.222.222',
                       'interface VirtualPortGroup0',
                       'ip address 10.1.1.1 255.255.255.0',
                       'description used_for_GS_access',
                       'ip nat inside',
                       'interface GigabitEthernet1',
                       'ip nat outside',
                       'ip access-list standard GS_NAT_ACL',
                       'permit 10.1.1.0 0.0.0.255',
                       'ip nat inside source list GS_NAT_ACL interface GigabitEthernet1 overload',
                       'app-hosting appid guestshell',
                       'vnic gateway1 virtualportgroup 0 guest-interface 0 guest-ipaddress 10.1.1.2 netmask 255.255.255.0 gateway 10.1.1.1 name-server 208.67.222.222',
                       'end'
                       ]
    commands_output = net_connect.send_config_set(config_commands)

    print('IOX and GS CLI configs: ', commands_output)
    time.sleep(60)

    net_connect = ConnectHandler(**DEVICE_INFO)
    # save the run config
    command_output = net_connect.save_config()
    print(command_output)

    # show iox
    command_output = net_connect.send_command('show iox')
    print(command_output)

    # enable Guest shell
    command_output = net_connect.send_command('guestshell enable')

    print('Enable Guest Shell: ', command_output)

    date_time = str(datetime.datetime.now().replace(microsecond=0))

    print('\n\nEnd of application run at this time ', date_time)


if __name__ == '__main__':
    main()
