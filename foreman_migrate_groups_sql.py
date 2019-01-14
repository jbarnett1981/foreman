'''
Created `05/21/2014 02:50`

@author jbarnett

Script to pull node/hostgroup info from one puppet/foreman db and configure hosts that have been migrated to another puppet/foreman server with the same hostgroups.
'''

from getpass import getpass
import psycopg2
from foreman.client import Foreman
import csv, time

# create log file
logfile = "log" + time.strftime("_%m_%d_%Y-%H_%M_%S") + ".csv"
with open(logfile, "w") as f:
    writer = csv.writer(f)
    writer.writerow(["hostname", "hostgroup"])

# create connection object to foreman and object for all nodes
username = raw_input("Enter username: ")
f = Foreman('http://puppet.dev.tsi.lan:3000', (username, getpass()))
nodes = f.index_hosts(per_page=10000)

# create dict for host group names to id mappings
group_dict = {}
hostgroups = f.index_hostgroups()
for hostgroup in hostgroups:
    group_dict[hostgroup[u'hostgroup'][u'name']] = hostgroup[u'hostgroup'][u'id']

# create connection to old puppetdb (where foreman db is stored)
conn = psycopg2.connect("dbname='puppetdb' user='puppetdb' host='devitpuppet.tsi.lan' password='puppetdb'")
cur = conn.cursor()
cur.execute("""select h.name,hg.name from hosts h left join hostgroups hg on h.hostgroup_id=hg.id""")
rows = cur.fetchall()

# iterate through foreman nodes and add to necessary hostgroup
for node in nodes:
    nodename = node[u'host'][u'name']
    if node[u'host'][u'hostgroup_id'] == None:
        for row in rows:
            if row[0] == nodename and row[1] == None:
                f.update_hosts(id=node[u'host'][u'id'], host={'hostgroup_id': group_dict[row[1]]})
                print('{0} added to {1}').format(node[u'host'][u'name'], row[1].strip())
                with open(logfile, "a") as f:
                    writer = csv.writer(f)
                    writer.writerow([str(nodename), row[1]])