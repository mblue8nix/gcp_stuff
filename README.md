# gcp_stuff

Wrapper around gcloud to list db resources in the GCP env.

## gcp-dblist.py

### Usage:

```
 gcp-dblist -h
usage: dblist [-h] [--ip] [--databases] [--down]
              [--search [SEARCH [SEARCH ...]]] [--snapBackups] [--snapAll]
              [--dns] [--loadBalancers]
              [--cluster [CLUSTER_NAME [CLUSTER_NAME ...]]] [--reporting]
              [--bucket]

optional arguments:
  -h, --help            show this help message and exit
  --ip, -i              Run a list for compute in GCP ip only
  --databases, -d       Run a list for compute in GCP MySQL Databases only
  --down, -D            Run a list of down compute insances in GCP
  --search [SEARCH [SEARCH ...]], -s [SEARCH [SEARCH ...]]
                        Run a list for compute in GCP MySQL Databases filtered
  --snapBackups, -sb    Run a list for compute backup snapshots in c1
  --snapAll, -sa        Run a list for compute in GCP MySQL Databases filtered
  --dns, -dn            Run a list of dns cnames
  --loadBalancers, -l   Run a list of Load Balancers
  --cluster [CLUSTER_NAME [CLUSTER_NAME ...]], -c [CLUSTER_NAME [CLUSTER_NAME ...]]
                        Run a list for compute in GCP MySQL based off
                        cluster_name Example: --cluster casino02"
  --reporting, -r       Run a list for compute in GCP MySQL Reporting servers
                        only
  --bucket, -b          Run a list of buckets
  ```

List of just databases:
- Usefull for loop scripts
```
gcp-dblist.py -d

test01-db01-c1
test02-db01-c1
test03-db01-c1
test04-db01-c1
test05-db01-c1
test06-db01-c1
test01-db02-c1
test02-db02-c1
test03-db02-c1
test04-db02-c1
test05-db02-c1
test06-db02-c1
test01-db01-w1
test02-db01-w1
test03-db01-w1
test04-db01-w1
test05-db01-w1
test06-db01-w1
tests07-db01-cloudsql-c1
tests07-db02-cloudsql-c1
tests07-db01-cloudsql-w1
```

List of databases for a specific cluster:

```
gcp-dblist.py -d -c test03
test03-db01-c1
test03-db02-c1
test03-db01-w1

```

Find snapshot uri for a cluster:

```
$ gcp-dblist -sb -c test03
Curent Epoch Time:
 1672559747
Current Human Time:
 Sun, 01 Jan 2023 07:55:47 UTC

Last Snapshot URI for test03-db01-w1 :
https://www.googleapis.com/compute/v1/projects/blue-test-hab7/global/snapshots/test03-db01-w1-us-west1-1671040741-cron


 Run: (epoch_con <uri_epoch_time>) to convert the URI epoch date to verify it's within the hour
```

If you run gcp-dblist by itself you will get a full list of GCE, Load balancers, DNS, CloudSQL resourses for the projectt.
