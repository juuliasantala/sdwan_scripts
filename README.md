# SD-WAN scripts

## unlock.py

Script to unlock a user in vManage using admin credentials. Requires an environment variable `PW` to be set to vManage `admin` account's password.

The script is created for a situation where there are multiple vManage pods from which to choose the correct IP address to be targeted. The IP addresses of the pods are defined in the `pods.yaml`. If you only have one vManage, update the pods.yaml to include only one list element and while running the script, choose to target pod number 1.

The script pulls the usernames from the vManage and provides you an option to choose which one of them you want to unlock.

## Author

Juulia Santala, jusantal@cisco.com

## License
This project is licensed to you under the terms of the [Cisco Sample Code License](LICENSE).