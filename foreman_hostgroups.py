#!/usr/bin/env python

'''
Created `01/08/2016 02:44`

@author jbarnett@tableau.com
@version 0.1

foreman_hostgroup.py:

Adds and removes systems to specified foreman/puppet hostgroup.

changelog:

0.1
---
First draft
'''

from getpass import getpass
from foreman.client import Foreman, ForemanException
import csv, time, argparse, sys
import requests

def get_args():
    '''
    Supports the command-line arguments listed below.
    '''
    parser = argparse.ArgumentParser(description='Process for adding hosts to specific hostgroups in Foreman')

    credentials_parser = parser.add_argument_group('required login arguments')
    credentials_parser.add_argument('--username', required=True, help='username to authenticate to Foreman')
    credentials_parser.add_argument('--password', required=True, help='password to authenticate to Foreman')
    credentials_parser.add_argument('--apiurl', required=True, help='API URL to authenticate to Foreman')

    subparsers = parser.add_subparsers(help='commands')

    list_parser = subparsers.add_parser('list', help='list command. Prints to stdout')
    list_parser.set_defaults(which='list')
    list_parser.add_argument('groups', help='List Foreman hostgroups')

    add_parser = subparsers.add_parser('add', help='list command. Prints to stdout')
    add_parser.set_defaults(which='add')
    add_parser.add_argument('--hostname', required=True, help='hostname to modify')
    add_parser.add_argument('--hostgroup', required=True, help='Foreman hostgroup')

    args = vars(parser.parse_args())

    return args

def get_host_id(foreman, hostname):
    '''
    Function that returns Foreman id from hostname string
    '''
    try:
        hostid = foreman.show_hosts(hostname)['host']['id']
        return hostid
    except TypeError:
        sys.exit("\nInvalid hostname. Please check hostname and try again.")


def get_groupid(foreman, group):
    '''
    Function that returns Foreman id from hostgroup string
    '''
    try:
        for hg in foreman.index_hostgroups():
            if hg['hostgroup']['name'] == group:
                return hg['hostgroup']['id']
    except TypeError:
        sys.exit("\nInvalid hostgroup name. Please check hostgroup and try again.")

def is_number(num):
    ''' Test if value can be converted to a number and if so return True '''
    try:
        int(num)
        return True
    except ValueError:
        return False

def main():
    args = get_args()
    # from requests.auth import HTTPBasicAuth
    requests.packages.urllib3.disable_warnings()

    # create connection object to foreman and nodes object
    f = Foreman(args['apiurl'], (args['username'], args['password']))

    if args['which'] == 'list' and args['groups']:
    # list hostgroups within Foreman
        group_dict = {}
        hostgroups = f.index_hostgroups()
        print("\n{0:40}{1}".format("Hostgroup", "ID"))
        print("{0:40}{1}".format("---------", "--\n"))
        for hostgroup in hostgroups:
            group_dict[hostgroup[u'hostgroup'][u'name']] = hostgroup[u'hostgroup'][u'id']
            print("{0:40}{1}".format(hostgroup[u'hostgroup'][u'name'],hostgroup[u'hostgroup'][u'id']))

    if args['which'] == 'add':
        # add specified host to specified hostgroup
        hostid = get_host_id(f, args['hostname'])
        groupname = args['hostgroup']
        if not is_number(groupname):
            groupid = get_groupid(f, groupname)
        try:
            f.update_hosts(id=hostid, host={'hostgroup_id':groupid})
            print("Host successfully added to %s hostgroup" % groupname)
        except ForemanException, e:
            sys.exit(str(e) + ', see error description above')

if __name__ == "__main__":
    main()