from argparse import ArgumentParser, Namespace
from pprint import pprint
import json
import requests
import os
import sys
from logging import Logger, Formatter, StreamHandler
from logging.handlers import RotatingFileHandler

logger = Logger(__name__)
filehandler = RotatingFileHandler('konohana.log', maxBytes = 10**6)
streamhandler = StreamHandler(sys.stdout)
formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s')
filehandler.setFormatter(formatter)
streamhandler.setFormatter(formatter)
logger.addHandler(filehandler)
logger.addHandler(streamhandler)

NODE_TYPES = ['ricefield', 'herbs', 'empty']

def dispatch_request(func):
	def wrapper(**kwargs):
		try:
			r = func(**kwargs)
			return r
		except requests.ConnectionError:
			logger.error('Could not connect to server')
		except Exception, e:
			logger.error('Something went wrong!: %s, %s'%(e, type(e)))
	return wrapper

class Konohana(object):
	@classmethod
	def confirm_destroy(satoyama_type, mid, **kwargs):
		invalid_choice = True
		while invalid_choice:
			choice = raw_input('Are you sure that you want to destroy %s %s and all data it owns? [Y/n]? '%(satoyama_type, mid))
			if choice in ['Y', 'y', 'Yes', 'yes']:
				print 'Destroyed %s %s'%(satoyama_type, mid)
				return True
			elif choice in ['n', 'N', 'no', 'No']:
				return False
			else:
				print 'Please choose yes or no :)'
	
	@staticmethod
	def handle_response(response):
		if not response.ok: 
			logger.info('Failed to complete request. Got HTTP code: %s'%response.status)
		else:
			try:
				return json.loads(response.text)
			except Exception:
				logger.exception('Could not parse the API response.')
				return {}

	@classmethod
	def send_raw_input(**args):
		pass

	@staticmethod
	@dispatch_request
	def sites(**kwargs):
		r = requests.get(URL + 'sites')
		sites = json.loads(r.text)['objects']
		# pprint(sites)
		pprint(map(lambda s: 'id: %s, alias: %s, nodes: %s\n'%(s['id'], s['alias'], len(s['nodes'])), sites))


	@staticmethod
	@dispatch_request
	def nodes(**kwargs):
		r = requests.get(URL + 'nodes')
		nodes = json.loads(r.text)['objects']
		# pprint(nodes)
		pprint(map(lambda n: 'id: %s, alias: %s, sensors: %s\n'%(n['id'], ['alias'], len(n['sensors'])), nodes))

	
	@staticmethod
	@dispatch_request
	def create_node(**kwargs):
		fields = ['alias', 'site_id', 'node_type']
		node_fields = dict(zip(fields, map(lambda k: kwargs.get(k, None), fields)))
		print node_fields
		api_response = Konohana.handle_response(requests.post(URL + 'node', data = node_fields))
		if len(api_response.get('errors', [])) == 0: 
			logger.info('Node created!')
			logger.info(api_response['objects'])
		else: 
			logger.error('Could not create node!')
			for e in api_response['errors']: logger.error('%s'%e)
		
	@staticmethod
	@dispatch_request
	def destroy_node(**kwargs):
		node_id = kwargs.get('id')
		api_response = Konohana.handle_response(requests.delete(URL + 'node/%s'%node_id))
		if len(api_response.get('errors', [])) == 0: 
			logger.info('Node destroyed!')
			logger.info(api_response['objects'])
		else: 
			logger.error('Could not destroy node!')
			for e in api_response['errors']: logger.error(e)

	@staticmethod
	@dispatch_request
	def create_site(**kwargs):
		fields = ['alias']
		site_fields = dict(zip(fields, map(lambda k: kwargs.get(k, None), fields)))
		if kwargs.get('nodes', None):
			nodes = kwargs['nodes']
			l = [z.split(':') for z in nodes.split(',')]
			node_dict = dict(zip([x[0] for x in l], [x[1] for x in l]))
		
		api_response = Konohana.handle_response(requests.post(URL + 'site', data = site_fields))

		if len(api_response.get('errors', [])) == 0: 
			logger.info('Site created!')
			logger.info(api_response['objects'])
			site_id = api_response['objects'][0]['id']
		else: 
			logger.error('Could not create site!')
			for e in api_response['errors']: logger.error('%s'%e)
			site_id = None
		
		if site_id and kwargs.get('nodes', None):
			for node_type, n_nodes in node_dict.items():
				for i in xrange(int(n_nodes)):
					Konohana.create_node(site = site_id, node_type = node_type)

	@staticmethod
	def destroy_site(**kwargs):
		site_id = kwargs.get('id')
		api_response = Konohana.handle_response(requests.delete(URL + 'site/%s'%site_id))
		if len(api_response.get('errors', [])) == 0: 
			logger.info('Site destroyed!')
			logger.info(api_response['objects'])
		else: 
			logger.error('Could not destroy site!')
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
	parser.add_argument('--host', default = '127.0.0.1', help = 'Server IP address e.g., 107.170.251.142')
	parser.add_argument('--port', type = int, default = 8080, help = 'Port on the server (usually 80)')
	subparsers = parser.add_subparsers(help='sub-command help', dest = 'action')

	
	###
	### Subparser for listing sites and nodes
	###
	parser_create_node = subparsers.add_parser('sites', help='Get a list of the ids of all existing sites')
	parser_create_node = subparsers.add_parser('nodes', help='Get a list of the ids of all existing nodes')
	
	###
	### Subparser for create node
	###
	parser_create_node = subparsers.add_parser('create_node', help='Create a site or node')
	parser_create_node.add_argument('--node_type', '-nt', choices = NODE_TYPES, required = True)
	parser_create_node.add_argument('--site_id', '-s', type = int, required = True, help = 'The id of the site that the node belongs to')
	parser_create_node.add_argument('--alias', type = str, required = False, help = 'The name of the node (e.g. "ricefield_small_waterlevel")')
	parser_create_node.add_argument('--latitude', '-ltt', required = False, type = float, help = 'The latitude of the node')
	parser_create_node.add_argument('--longitude', '-lgt', required = False, type = float, help = 'The latitude of the node')

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

	URL = 'http://%s:%s/'%(HOST, PORT)

	# print vars(args)
	getattr(Konohana, args.action)(**vars(args))

	# print action, model
	
