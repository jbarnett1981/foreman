'''
Created `05/21/2014 02:50`

@author jbarnett

Script to pull node/hostgroup info from one puppet/foreman db and configure hosts that have been migrated to another puppet/foreman server with the same hostgroups.
'''

from getpass import getpass
from foreman.client import Foreman
import csv, time, argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', "--inputfile", help="example: --inputfile hgdump.csv")
    args = parser.parse_args()
    if args.inputfile:
        # create connection object to foreman and nodes object
        username = raw_input("Enter username: ")
        f = Foreman('http://puppet.dev.tsi.lan:3000', (username, getpass()))
        nodes = f.index_hosts(per_page=10000)

        # create dict for host group names to id mappings
        group_dict = {}
        hostgroups = f.index_hostgroups()
        for hostgroup in hostgroups:
            group_dict[hostgroup[u'hostgroup'][u'name']] = hostgroup[u'hostgroup'][u'id']

        # create log file
        logfile = "log" + time.strftime("_%m_%d_%Y-%H_%M_%S") + ".csv"
        with open(logfile, "w") as mylog:
            writer = csv.writer(mylog)
            writer.writerow(["hostname", "hostgroup"])

        # function to write to node/hostgroup info to logfile
        def writelog(logfile, mylog, nodename, row):
            with open(logfile, "a") as mylog:
                writer = csv.writer(mylog)
                writer.writerow([str(nodename), row[1]])

        # iterate through foreman nodes and add to necessary hostgroup from hgdump.csv (puppetdb/foreman db dump)
        for node in nodes:
            nodename = node[u'host'][u'name']
            if node[u'host'][u'hostgroup_id'] == None:
                with open(args.inputfile, "r") as myfile:
                    reader = csv.reader(myfile, delimiter=',')
                    for row in reader:
                        if row[0] == nodename and row[1] != '':
                            try:
                                f.update_hosts(id=node[u'host'][u'id'], host={'hostgroup_id': group_dict[row[1].strip()]})
                                print('{0} added to {1}'.format(node[u'host'][u'name'], row[1].strip()))
                                writelog(logfile, mylog, nodename, row)
                            except KeyError, e:
                                print("Error. KeyError: %s" % str(e))
                        elif row[0] == nodename and row[1] == '':
                            print('{0} added to {1}'.format(node[u'host'][u'name'], row[1].strip()))
                            writelog(logfile, mylog, nodename, row)
