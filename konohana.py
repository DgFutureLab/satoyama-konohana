from argparse import ArgumentParser, Namespace
from pprint import pprint
import json
import requests
verbs = {
	'create' : 'created',
	'destroy': 'destroyed'
}

NODE_TYPES = ['ricefield', 'herbs', 'empty']

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

	@classmethod
	def send_raw_input(**args):
		requsts.post

	# @classmethod
	# def create_node(alias, node_type, short_address, site = None):
	# 	print'ADSASD'

	@staticmethod
	def nodes(**kwargs):
		r = requests.get('http://localhost:8080/nodes')
		nodes = json.loads(r.text)['objects']
		pprint(map(lambda n: {'id': n['id'], 'alias':n['alias'], 'sensors': len(n['sensors'])}, nodes))

	@staticmethod
	def sites(**kwargs):
		r = requests.get('http://localhost:8080/sites')
		sites = json.loads(r.text)['objects']
		pprint(map(lambda s: {'id': s['id'], 'alias': s['alias'], 'nodes': len(s['nodes'])}, sites))

	@staticmethod
	def create_node(alias, node_type, short_address, site = None, **kwargs):
		print'ADSASD'
		print alias
		print node_type
		print short_address




if __name__ == "__main__":
	parser = ArgumentParser()

	parser.add_argument('-y', action='store_true', help='If specified, Konohana will not ask for confirmation when destroying Satoyama entities.')
	subparsers = parser.add_subparsers(help='sub-command help', dest = 'action')

	parser_create_node = subparsers.add_parser('sites', help='Get a list of the ids of all existing sites')
	parser_create_node = subparsers.add_parser('nodes', help='Get a list of the ids of all existing nodes')
	

	parser_create_node = subparsers.add_parser('create_node', help='Create a site or node')
	parser_create_node.add_argument('alias', type = str, help = 'The name of the node (e.g. "ricefield_small_waterlevel")')
	parser_create_node.add_argument('--node_type', '-t', choices = NODE_TYPES, required = True)
	parser_create_node.add_argument('--short_address', '-a', type = int, help = 'The Chibi short adress of the node', required = True)
	parser_create_node.add_argument('--site', '-s', type = int, help = 'The id of the site that the node belongs to', required = True)
	parser_create_node.add_argument('--latitude', type = float, help = 'The latitude of the node', required = False)
	parser_create_node.add_argument('--longitude', type = float, help = 'The latitude of the node', required = False)

	parser_destroy_node = subparsers.add_parser('destroy-node', help='Destroy a node')
	parser_destroy_node.add_argument('id', type = int, help = 'The id of the node you want to destroy')
	parser_destroy_node.add_argument('--erase_data', '-E', action = 'store_true', help = 'Set this flag to erase all sensor data generated by sensors in the node')

	parser_create_site = subparsers.add_parser('create-site', help='create a site')
	parser_create_site.add_argument('name', type = str, help = 'The name of the site (e.g. "Hackerfarm")')

	parser_destroy_site = subparsers.add_parser('destroy-site', help='Destroy a site')
	parser_destroy_site.add_argument('id', type = int, help = 'The id of the node you want to destroy')
	parser_destroy_site.add_argument('--erase_data', '-E', action = 'store_true', help = 'Set this flag to erase all sensor data generated by sensors in the node')

	args = parser.parse_args()	
	print vars(args)
	getattr(Konohana, args.action)(**vars(args))

	# print action, model
	
