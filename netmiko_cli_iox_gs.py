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

def pprint(json_data):
    """
    Pretty print JSON formatted data
    :param json_data:
    :return:
    """

    print(json.dumps(json_data, indent=4, separators=(' , ', ' : ')))


def main():

    date_time = str(datetime.datetime.now().replace(microsecond=0))

    print('\n\nBegin of application run at this time ', date_time)
    print('\nDevice information: ')
    pprint(DEVICE_INFO)

    # connect to device using ssh/netmiko
    net_connect = ConnectHandler(**DEVICE_INFO)
    command_output = net_connect.find_prompt()
    print('\nPrompt of the connected device: ', command_output)

    # define the config command sets to be sent to device.
    # the commands will configure iox, vpg, nat, guest shell
    config_commands = ['hostname GS-Gabi', 'line vty 0 15',
                       'transport input ssh',
                       'iox', 'aaa new-model',
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
    # send config commands to device
    commands_output = net_connect.send_config_set(config_commands)
    print('IOX and GS CLI configs: ', commands_output)

    # time delay to wait for iox caf to be enabled
    print('Wait 30 seconds for IOX to be enabled')
    time.sleep(30)

    # create a new connection to device to avoid the session timeouts
    net_connect.disconnect()
    net_connect = ConnectHandler(**DEVICE_INFO)

    # save the run config
    # command_output = net_connect.save_config()
    # print(command_output)

    # show iox
    command_output = net_connect.send_command('show iox')
    print(command_output)

    # enable Guest shell
    command_output = net_connect.send_command('guestshell enable')
    print('Enable Guest Shell: ', command_output)

    # time delay to wait for guest shell to be enabled
    print('Wait 15 seconds for Guest Shell to complete configuration')
    time.sleep(15)

    # create a new connection to device to avoid the session timeouts
    net_connect.disconnect()
    net_connect = ConnectHandler(**DEVICE_INFO)

    # verify connectivity
    command_output = net_connect.send_command('guestshell run ping 10.1.1.1 -c 5')
    print('\nPing to VPG IP address: \n', command_output)

    # install bind-utils
    command_output = net_connect.send_command('guestshell run sudo yum install bind-utils -y')
    print('\nbind-utils installation: \n', command_output)
    command_output = net_connect.send_command('guestshell run nslookup www.cisco.com')
    print('\nwww.cisco.com nslookup: \n ', command_output)

    # create a new connection to device to avoid the session timeouts
    net_connect.disconnect()
    net_connect = ConnectHandler(**DEVICE_INFO)

    # update guest shell os
    command_output = net_connect.send_command('guestshell run sudo yum update -y')
    print('\nCent OS update: \n ', command_output)



    date_time = str(datetime.datetime.now().replace(microsecond=0))

    print('\n\nEnd of application run at this time ', date_time)


if __name__ == '__main__':
    main()
