#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Script to unlock a user account in vManage.

Copyright (c) 2022 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
'''

import os
import requests
import urllib3
import yaml
import pprint

urllib3.disable_warnings()

__author__ = "Juulia Santala <jusantal@cisco.com>"
__copyright__ = "Copyright (c) 2022 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

class vManage():
    '''
    Class to manage vManage connection.

    Methods:
        get_cookie
        get_xsrf_token
    '''
    authentication_cookie = None
    xsrf_token = None
    users = []

    def __init__(self,
                ip_address: str,
                username: str,
                password: str,
                port: int = 443,
                verify: bool = False):

        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.verify = verify # False if self-signed certificate
        self.base_url = f"https://{ip_address}:{port}"

        self.get_cookie()
        self.get_xsrf_token()
        self.get_users()

    def get_cookie(self) -> None:
        '''
        Function to authenticate, called automatically when the object is
        created.
        Saves authentication cookie in object property "authentication_cookie".
        '''
        url = f"{self.base_url}/j_security_check"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        body = {
            "j_username": self.username,
            "j_password": self.password
        }

        print("Authenticating...")
        response = requests.post(url, headers=headers, data=body, verify=self.verify)
        print(f"Response status code: {response.status_code}")
        if response.status_code != 200:
            print(f"Error:\n{response.text}")
        else:
            self.authentication_cookie = response.cookies

    def get_xsrf_token(self) -> None:
        '''
        Get a cross-site request forgery prevention token,
        which is required for most POST operations.
        Requires authentication_cookie to authenticate, and saves the returned
        XSRF token in object property "xsrf_token".
        Called automativally when the object is created.
        '''
        url = f"{self.base_url}/dataservice/client/token"

        print("Requesting XSRF token...")
        response = requests.get(url, cookies=self.authentication_cookie, verify=self.verify)
        print(f"Response status code: {response.status_code}")
        if response.status_code != 200:
            print(f"Error:\n{response.text}")
        else:
            self.xsrf_token = response.text

    def get_users(self) -> None:
        url = f"{self.base_url}/dataservice/admin/user"
        headers = {"Content-Type":"application/json", "X-XSRF-TOKEN": self.xsrf_token}
        response = requests.get(url, headers=headers,
                                cookies=self.authentication_cookie, verify=self.verify)
        if response.status_code != 200:
            print(f"Error:\n{response.text}")
        else:
            self.users = [user["userName"] for user in response.json()["data"]]


def unlock_user(pod: vManage, user: str = "netadmin") -> None:
    '''
    Unlock a user of the vManage.

    Paramerers:
        pod (vManage): The vManage object that you want to target
        user (str): The user to be unlocked in the vManage, default "netadmin"
    '''

    url = f"{pod.base_url}/dataservice/admin/user/reset"
    headers = {"Content-Type":"application/json", "X-XSRF-TOKEN": pod.xsrf_token}
    body = {
        "userName": user
    }
    response = requests.post(url, headers=headers, json=body,
                            cookies=pod.authentication_cookie, verify=pod.verify)
    if response.status_code == 200:
        print(f"User {user} unlocked successfully!")
    else:
        print(f"Status code: {response.status_code}")
        print(f"Error description: {response.text}")

def get_pod_ips(filename:str) -> list:
    '''
    Load pod IPs from a YAML file.
    The structure of pod yaml file should have a key "Pods" pointing to a list
    containing all the IP addresses. For example:
        Pods:
            - 1.1.1.1
            - 2.2.2.2
    
    Parameters:
        filename (str): the name of the YAML file
    
    Returns:
        pods (list): the list of Pod IP addresses
    '''
    with open(filename, encoding="utf8") as file:
        pods = yaml.load(file, Loader=yaml.loader.SafeLoader)
    return pods["Pods"]

if __name__ == "__main__":
    print("You are about to unlock a user account in vManage.")
    pods = get_pod_ips("./pods.yaml")
    while True:
        selection = input("\nType the number of your pod: ")
        try:
            pod = pods[int(selection)-1]
        except ValueError:
            print(f"> '{selection}' is not a number!")
        except IndexError:
            print(f"> '{selection}' is not a valid pod number!")
            print("> Please recheck your Pod number from 'Self Serve Labs' GUI")
        else:
            verify = input(f"You have selected pod {selection} ({pod}). Is that correct (Y/N)? ")
            if verify.upper() == "Y" or verify.upper() == "YES":
                break
            elif verify.upper() == "N" or verify.upper() == "NO":
                continue
            else:
                print("Not a valid option.")
                continue

    print("*"*30)
    print(f"Your are about to connect to pod {selection} in {pod}")
    my_vmanage = vManage(pod, "admin", os.getenv("PW"))
    users = my_vmanage.users

    print("*"*30)
    while True:
        print(f"\nThe users of pod {selection}:")
        for i,user in enumerate(users):
            print(f"{i+1}. {user}", end=" ")
        selection = input("\nType the number of the user that you want to unlock: ")
        try:
            user = users[int(selection)-1]
        except ValueError:
            print(f"> '{selection}' is not a number!")
        except IndexError:
            print(f"> '{selection}' is not a valid user number!")
            print("> Please recheck your User's number from the list")
        else:
            verify = input(f"You are about to unlock user {user}. Is that correct (Y/N)? ")
            if verify.upper() == "Y" or verify.upper() == "YES":
                break
            elif verify.upper() == "N" or verify.upper() == "NO":
                continue
            else:
                print("Not a valid option.")
                continue

    print("*"*30)

    print("Starting to unlock...\n")
    unlock_user(my_vmanage, user=user)
