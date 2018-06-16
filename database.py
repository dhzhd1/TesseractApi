from pymongo import MongoClient, errors
from api_env import db_structure


class Database():
	def __init__(self):
		try:
			self.conn = MongoClient()
			self.db = self.conn[db_structure.keys()[0]]
			create_list = list(set(db_structure[db_structure.keys()[0]]) - set(self.db.collection_names()))
			try:
				for coll_name in create_list:
					self.db.create_collection(coll_name)
			except Exception as e1:
				print "Create collection failed! " + e1.message
		except Exception as e2:
			print "Connect to Database Failed! " + e2.message


