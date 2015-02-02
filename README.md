satoyama-konohana
=================

Satoyama-konohana is a command line tool for easily managing Satoyama Cloud sensor networks. In order to use this command line tool you need to have a  <a href="https://github.com/DgFutureLab/satoyama-api">satoyama-api</a> server up and running. With these tools you can create sites and nodes.

# Requirements
1. Python 2.7
2. A python virtualenv

# Installation
1. Clone this repository
2. Install requirements: $pip install -r satoyama-konohana/requirements.txt

# Usage
To get an overview of the tool, run it with the --help flag:

  `$python konohana.py --help`
  
The tool has several subcommands: nodes, sites, create_node, create_site, destroy_site, destroy_node. To get help for a particular subcommand, run the script with that subcommand and set the help flag. Like so:

  `$ python konohana.py nodes --help`

After running a command successfully, you will see a json dump of the response. For instance, if you create a site and the response has an 'id' key, then that is the id of the site you just created.
  
## Commands

Get a list of all sites in the database:

  `$ python konohana.py sites`

Get a list of all nodes in the database:

  `$ python konohana.py nodes`
  
Create a new site called 'mysite':

  `$ python konohana.py create_site --alias mysite`

Create new site specifying the host for satoyama-api:

  `$ python konohana.py --host 128.199.191.249 --port 80 create_site --alias mysite`

Create a new ricefield node at site 1:

`$ python konohana.py create_node --node_type ricefield --site_id 1 --alias kamogawa1`

Create a new ricefield node at site 1 specifying the host for satoyama-api:

`$ python konohana.py --host 128.199.191.249 --port 80 create_node --node_type ricefield --site_id 1`

Create a new ricefield node at site 1 specifying the host for satoyama-api and the geolocation of the node:

`$ python konohana.py --host 128.199.191.249 --port 80 create_node --latitude 35.144828 --longitude 139.962516 --node_type ricefield --site_id 1 --alias garden`

Destroy site 1:

  `$ python konohana.py destroy_site --id 1`
  
Destroy node 1:

  `$ python konohana.py destroy_node --id 1`

## The MIT License (MIT)

Satoyama Cloud is an open source framework to setup and manage sensor networks built by <a href="http://www.fljapan.com">Future Lab</a> & <a href="http://freaklabs.org/">Hacker Farm</a>.
