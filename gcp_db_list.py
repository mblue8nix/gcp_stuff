#! /usr/bin/python3

"""
 The purpose of this script is to ineteract with GCP resources to
 gather list of resrouces including: DNS, GCE instances,
 Snapshots, IPs and more. This script is expecting Python 3 and Bash
"""

import time
import os
import argparse
import subprocess


# reads gcloud config project name and used for environment var

proj_env = subprocess.check_output(
    "gcloud info --format=value\(config.project\)", shell=True)
proj_env = proj_env[:-1].decode('utf-8')

# Vars that need values added:


backup_list = "host01, host02, host03" # for snapshots on backup host

# vars for project names outside the main project

dns_zone = "DNS_ZONE"
dns_proj = proj_env # If diferent project us "DNS_PROJECT_NAME" instead

# vars
 
epoch_time = int(time.time())
human_time = time.strftime(
    "%a, %d %b %Y %H:%M:%S %Z", time.localtime(epoch_time))
gcloud_list = "gcloud compute instances list"
gcloud_snap = "gcloud compute snapshots list"
gcloud_csql = "gcloud sql instances list"
gcloud_dns = "gcloud dns record-sets list"
gcloud_lb = "gcloud compute forwarding-rules list"
gcloud_proj = proj_env
db_related = "db|pmm|percona|proxy"
column_ip = "awk '{print $4,\"   >  \", $1, $5}' | sed -e 's/n2//g'"
column_db = "awk '{print $1, $5}' | sed -e 's/16//g; s/32//g'"

# Args

parser = argparse.ArgumentParser()

parser.add_argument('--ip', '-i', help='Run a list for compute \
        in GCP ip only', action="store_true")
parser.add_argument('--databases', '-d', help='Run a list for compute\
        in GCP MySQL Databases only', action="store_true")
parser.add_argument('--down', '-D', help='Run a list of down compute\
        insances in GCP', action="store_true")
parser.add_argument(
    '--search', '-s', nargs='*', dest="search",
    help='Run a list for compute in GCP MySQL Databases filtered')
parser.add_argument('--snapBackups', '-sb', help='Run a list for compute \
        backup snapshots in c1', action="store_true")
parser.add_argument('--snapAll', '-sa', help='Run a list for compute \
        in GCP MySQL Databases filtered', action="store_true")
parser.add_argument('--dns', '-dn', help='Run a list of dns \
        cnames', action="store_true")
parser.add_argument(
    '--loadBalancers', '-l', help='Run a list of Load\
        Balancers', action="store_true")
parser.add_argument(
    '--cluster', '-c', nargs='*', dest="cluster_name",
    help='Run a list for compute in GCP MySQL based off cluster_name \
            Example: --cluster casino02"')
parser.add_argument(
    '--reporting', '-r', help='Run a list for compute in GCP MySQL \
        Reporting servers only', action="store_true")
parser.add_argument(
    '--bucket', '-b', help='Run a list of buckets', action="store_true")

args = (parser.parse_args())

# List of ips and server name of VM Databases only


def ip():
    run = "{0} --project {1} --format='table( NAME, INTERNAL_IP, STATUS)' | \
            egrep '{2}' | sed -e 's/RUNNING/ /g ; s/TERMINATED/\
                   DOWN  /g' | egrep -v \
                    'DOWN'".format(
            gcloud_list, gcloud_proj, db_related)
    os.system(run)
# Need to Include CloudSQL IP
    run = "{2} --project={0} --filter=\"{1}\" \
        --format='table(NAME, PRIVATE_ADDRESS, STATUS)' | \
            sed -e 's/RUNNABLE/ /g' | \
                egrep -v \"PRIVATE_ADDRESS|TERMINATED\"".format(
                gcloud_proj, cluster_name, gcloud_csql)
    os.system(run)

# List Load Balancers'


def loadBalancers():
    print("\n Load Balancers:")
    run = "{0} --project={1} --filter=\"{2}\" | egrep 'pmm|sql' ".format(
        gcloud_lb, gcloud_proj, cluster_name)
    os.system(run)

# List databases only. This is good used in 'for loops'


def databases():
    run = "{0} --project={1} --filter=\"{2}\" --format='table(NAME, STATUS)'\
         | grep '\-db' | sed -e 's/RUNNING/ /g' \
            | egrep -v 'TERMINATED'".format(
                gcloud_list, gcloud_proj, cluster_name)
    os.system(run)
# Need to Include CloudSQL IP
    run = "{2} --project={0} --filter=\"{1}\" \
        --format='table(PRIVATE_ADDRESS, STATUS)' | \
            sed -e 's/RUNNABLE/ /g' | \
                egrep -v \"PRIVATE_ADDRESS|TERMINATED\"".format(
                gcloud_proj, cluster_name, gcloud_csql)
    os.system(run)


def reporting():
    run = "{0} --project={1} --filter=\"{2}\" --format='table(NAME, STATUS)' \
        | grep '\-w1' | sed -e 's/RUNNING/ /g' \
            | egrep -v 'TERMINATED'".format(
                gcloud_list, gcloud_proj, cluster_name)
    os.system(run)

# List DNS


def dns():
    print("\n DNS: Cnames")
    run = "--project={0} --zone={2} {1} --filter=\"{3}\" --format=list | \
        egrep  \"name|type|rrdatas\" | \
            egrep \"\-db\" | \
        ".format(gcloud_dns, dns_proj, dns_zone, cluster_name)
    os.system(run)
    print("")

# List Downed Servers


def down():
    run = "{0} --project={1} --format='table(NAME, STATUS)'| grep '\-db' | \
        sed -e 's/RUNNING/ /g ; s/TERMINATED/DOWN/g' \
            | grep -i \"DOWN\" ".format(gcloud_list, gcloud_proj)
    os.system(run)

# Snapshots From Backup Clusters
# will show last snapshot


def snapBackups():
    print(
        "Curent Epoch Time:\n", epoch_time, "\nCurrent Human Time:\n",
        human_time, "\n")
    if args.cluster_name:
        cluster_name = ' '.join(args.cluster_name)
        print("Last Snapshot URI for", cluster_name, ":")
        cluster_name = cluster_name + "-db01-w1"
        run = "{0} --project={1} --filter=\"{2}\" --uri | grep cron|\
             grep -v manual| tail -1".format(
                gcloud_snap, gcloud_proj, cluster_name)
        os.system(run)
    else:
        cluster_name = ""
        print("Last Snapshot URI for\n")
        run = "for i in {0} ; do echo \"$i:\";\
                {1} --project={2} --filter=\"{3}\" --uri | egrep $i| \
                    grep -v manual | tail -1 ; done".format(
                    backup_list, gcloud_snap, gcloud_proj, cluster_name)
        os.system(run)
    print("\n\n Run: (epoch_con <uri_epoch_time>) to convert the URI epoch \
date to verify it's within the hour \n")

# Shows all snapshots with the options of search
# --search will grep for a string ie:  --search percona


def snapAll():
    if args.search:
        search = ' '.join(args.search)
        run = "{0} --project={1} --uri | grep {2}".format(
            gcloud_snap, gcloud_proj, search)
        os.system(run)
    else:
        run = "{0} --project={1} --uri".format(gcloud_snap, gcloud_proj)
        os.system(run)

# This shows all GCE resources


def default():
    print(
        "GCP Resources related to Databases in: ", gcloud_proj,
        "\n\n GCE Instances:")

    run = "{0} --project={1} --filter=\"{3}\"| egrep '{2}'".format(
        gcloud_list, gcloud_proj, db_related, cluster_name)
    os.system(run)


def csql():
    print("\n Google Cloud SQL:")
    run = "{0} --project={1} --filter=\"{2}\"".format(
        gcloud_csql, gcloud_proj, cluster_name)
    os.system(run)


def storage():
    print("\n Storage Buckets:")
    run = "gcloud alpha storage ls --project={0}".format(gcloud_proj)
    os.system(run)

# If your searching for a cluster ie: --cluster casino03
# Otherwise it's blank


if args.cluster_name:

    cluster_name = ' '.join(args.cluster_name)

else:

    cluster_name = " "

if args.ip:
    ip()

elif args.databases:
    databases()

elif args.bucket:
    storage()

elif args.down:
    down()

elif args.reporting:
    reporting()

elif args.snapBackups:
    snapBackups()

elif args.snapAll:
    snapAll()

elif args.loadBalancers:
    loadBalancers()

elif args.dns:
    dns()

# If no argument then shows all Resources releated to Databases
else:
    default()
    csql()
    loadBalancers()
    dns()
    print("")
