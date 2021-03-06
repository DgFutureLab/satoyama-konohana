from argparse import ArgumentParser, Namespace
from pprint import pprint
import json
import requests
import os
import sys
from logging import Logger, Formatter, StreamHandler
from logging.handlers import RotatingFileHandler
from termcolor import colored
logger = Logger(__name__)
filehandler = RotatingFileHandler('konohana.log', maxBytes = 10**6)
streamhandler = StreamHandler(sys.stdout)
formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s')
filehandler.setFormatter(formatter)
streamhandler.setFormatter(formatter)
logger.addHandler(filehandler)
logger.addHandler(streamhandler)


def dispatch_request(func):
	def wrapper(**kwargs):
		try:
			r = func(**kwargs)
			return r
		except requests.ConnectionError:
			logger.error('Could not connect to server')
		except Exception, e:
			print e
			logger.error('Something went wrong!: %s, %s'%(e, type(e)))
	return wrapper

def debug(msg):
	colored(msg, 'red')

class Konohana(object):


	@staticmethod
	def confirm_destroy(satoyama_type, model_id, **kwargs):
		invalid_choice = True
		while invalid_choice:
			choice = raw_input('Are you sure that you want to destroy %s %s and all data it owns? [Y/n]? '%(satoyama_type, model_id))
			if choice in ['Y', 'y', 'Yes', 'yes']:
				print 'Destroyed %s %s'%(satoyama_type, model_id)
				break
			elif choice in ['n', 'N', 'no', 'No']:
				os._exit(0)
			else:
				print 'Please choose yes or no :)'
	
	@staticmethod
	def handle_response(response):
		debug(response.status_code)
		if response.ok: 
			try:
				return json.loads(response.text)
			except Exception:
				logger.exception('Could not parse the API response.')
				return False
		else:
			logger.info(colored('Failed to complete request. Got HTTP code: %s'%response.status_code, 'red'))
			return False

			

	@classmethod
	def send_raw_input(**args):
		pass

	@staticmethod
	@dispatch_request
	def sites(**kwargs):
		r = requests.get(URL + 'sites')
		sites = json.loads(r.text)['objects']
		pprint(map(lambda s: 'id: %s, alias: %s, nodes: %s'%(s['id'], s['alias'], len(s['nodes'])), sites))

	@staticmethod
	@dispatch_request
	def nodes(**kwargs):
		fields = ['site_id']
		node_fields = dict(zip(fields, map(lambda k: kwargs.get(k, None), fields)))
		r = requests.get(URL + 'nodes', data = node_fields)
		nodes = json.loads(r.text)['objects']
		# pprint(nodes)
		pprint(map(lambda n: 'id: %s, alias: %s, sensors: %s'%(n['id'], n['alias'], len(n['sensors'])), nodes))

	@staticmethod
	@dispatch_request
	def node(**kwargs):
		r = requests.get(URL + 'node/' + str(kwargs['id']))
		pprint(json.loads(r.text)['objects'])

	@staticmethod
	@dispatch_request
	def site(**kwargs):
		r = requests.get(URL + 'site/' + str(kwargs['id']))
		pprint(json.loads(r.text)['objects'])


	@staticmethod
	@dispatch_request
	def nodetypes(**kwargs):
		r = requests.get(URL + 'nodetypes')
		nodetypes = json.loads(r.text)['objects'][0]
		if kwargs['verbose']:
			pprint(nodetypes)
		else:	
			pprint(nodetypes.keys())
	
	@staticmethod
	@dispatch_request
	def create_node(**kwargs):
		fields = ['alias', 'site_id', 'node_type', 'latitude', 'longitude', 'populate']
		node_fields = dict(zip(fields, map(lambda k: kwargs.get(k, None), fields)))
		api_response = Konohana.handle_response(requests.post(URL + 'node', data = node_fields))
		if api_response: 
			logger.info(colored('Node created! Node data printed below.', 'green'))
			pprint(api_response['objects'])
		else: 
			logger.error(colored('Could not create node!', 'red'))
			if isinstance(api_response, dict):
				for e in api_response['errors']: 
					logger.error(colored('%s'%e, 'red'))
		
	@staticmethod
	@dispatch_request
	def destroy_node(**kwargs):
		node_id = kwargs.get('id')
		Konohana.confirm_destroy('node', node_id)
		api_response = Konohana.handle_response(requests.delete(URL + 'node/%s'%node_id))
		if api_response: 
			logger.info(colored('Node destroyed!', 'green'))
			logger.info(api_response['objects'])
		else: 
			logger.error(colored('Could not destroy node!', 'red'))
			if isinstance(api_response, dict):
				for e in api_response['errors']: 
					logger.error(colored(e, 'red'))

	@staticmethod
	@dispatch_request
	def create_site(**kwargs):
		fields = ['alias']
		site_fields = dict(zip(fields, map(lambda k: kwargs.get(k, None), fields)))
		if kwargs.get('nodes', None):
			nodes = kwargs['nodes']
			l = [z.split(':') for z in nodes.split(',')]
			node_dict = dict(zip([x[0] for x in l], [x[1] for x in l]))
		# response = requests.post(URL + 'site', data = site_fields)
		# print response.text

		api_response = Konohana.handle_response(requests.post(URL + 'site', data = site_fields))

		if len(api_response.get('errors', [])) == 0: 
			try:
				site_id = api_response['objects'][0]['id']
				logger.info(colored('Site created! Site data printed below.', 'green'))
				logger.info(api_response['objects'])
			except Exception:
				site_id = None
				logger.error(colored('Could not create site!', 'red'))
			
		else: 
			logger.error(colored('Could not create site!', 'red'))
			for e in api_response['errors']: logger.error('%s'%e)
			site_id = None
		
		if site_id and kwargs.get('nodes', None):
			for node_type, n_nodes in node_dict.items():
				for i in xrange(int(n_nodes)):
					Konohana.create_node(site = site_id, node_type = node_type)

	@staticmethod
	def destroy_site(**kwargs):
		site_id = kwargs.get('id')
		Konohana.confirm_destroy('site', site_id)
		api_response = Konohana.handle_response(requests.delete(URL + 'site/%s'%site_id))
		if len(api_response.get('errors', [])) == 0: 
			logger.info(colored('Site destroyed!', 'green'))
			logger.info(api_response['objects'])
		else: 
			logger.error(colored('Could not destroy site!', 'red'))
			for e in api_response['errors']: logger.error(e)

	@staticmethod
	def info(**kwargs):
		raise Exception('Not implemented')

if __name__ == "__main__":
	parser = ArgumentParser()

	###
	### Main parser
	###
	parser.add_argument('-y', action='store_true', help='If specified, Konohana will not ask for confirmation when destroying Satoyama entities.')
	parser.add_argument('--host', default = 'satoyamacloud.com', help = 'Server hostname or IP address e.g., 107.170.251.142')
	parser.add_argument('--port', type = int, default = 80, help = 'Port on the server (usually 80)')
	subparsers = parser.add_subparsers(help='sub-command help', dest = 'action')

	
	###
	### Subparser for listing sites and nodes
	###
	subparsers.add_parser('sites', help='Get a list of the ids of all existing sites')
	nodes_parser = subparsers.add_parser('nodes', help='Get a list of the ids of all existing nodes')
	nodes_parser.add_argument('--site_id', '-s', required = False, type = int, help = 'Get all nodes belonging to this site.')

	node_parser = subparsers.add_parser('node', help='Get verbose information about a single node')
	node_parser.add_argument('--id', required = True, type = int)
	
	nodetype_parser = subparsers.add_parser('nodetypes', help='Get a list of the ids of all existing node types')
	nodetype_parser.add_argument('--verbose', '-v', action = 'store_true')

	site_parser = subparsers.add_parser('site', help='Get verbose information about a single site')
	site_parser.add_argument('--id', required = True, type = int)
	
	###
	### Subparser for create node
	###
	parser_create_node = subparsers.add_parser('create_node', help='Create a site or node')
	parser_create_node.add_argument('--node_type', '-nt', required = True, help='To know which node types are available, use konohana nodetypes command')
	parser_create_node.add_argument('--site_id', '-s', type = int, required = True, help = 'The id of the site that the node belongs to')
	parser_create_node.add_argument('--alias', type = str, required = False, help = 'The name of the node (e.g. "ricefield_small_waterlevel")')
	parser_create_node.add_argument('--latitude', '-ltt', required = False, type = float, help = 'The latitude of the node')
	parser_create_node.add_argument('--longitude', '-lgt', required = False, type = float, help = 'The latitude of the node')
	parser_create_node.add_argument('--populate', '-pop', required = False, type = int, help = 'Populates the node with one week of sample data')

	###
	### Subparser for destroy node
	###
	parser_destroy_node = subparsers.add_parser('destroy_node', help='Destroy a node')
	parser_destroy_node.add_argument('--id', type = int, required = True, help = 'The id of the node you want to destroy')
	parser_destroy_node.add_argument('--erase_data', '-E', action = 'store_true', help = 'Set this flag to erase all sensor data generated by sensors in the node')

	###
	### Subparser for create site
	###
	parser_create_site = subparsers.add_parser('create_site', help='Create a new site')
	parser_create_site.add_argument('--nodes', '-nn', type = str, required = False, help = 'Specify which and how many nodes the site should contain. For example, to create a site with 10 ricefield nodes and 5 herb nodes, use --nodes ricefield:10,herb:5')
	parser_create_site.add_argument('--alias', type = str, required = False, help = 'The name of the site (e.g. "Hackerfarm")')

	###
	### Subparser for destroy site
	###
	parser_destroy_site = subparsers.add_parser('destroy_site', help='Destroy a site')
	parser_destroy_site.add_argument('--id', type = int, help = 'The id of the node you want to destroy')
	parser_destroy_site.add_argument('--erase_data', '-E', action = 'store_true', help = 'Set this flag to erase all sensor data generated by sensors in the node')

	args = parser.parse_args()	

	HOST = args.host
		
	try:
		PORT = int(args.port)
	except ValueError:
		print "Please specify a port with an integer"
		os._exit(1)

	URL = 'http://%s:%s/'%(HOST.strip('http://'), PORT)

	print URL 

	getattr(Konohana, args.action)(**vars(args))


	
