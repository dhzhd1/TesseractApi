from pymongo import MongoClient, errors
from api_env import db_structure


class Database:
	def __init__(self):
		try:
			self.conn = MongoClient()
			self.db = self.conn[db_structure.keys()[0]]
			create_collections = list(set(db_structure[db_structure.keys()[0]]) - set(self.db.collection_names()))
			try:
				for coll_name in create_collections:
					self.db.create_collection(coll_name)
			except Exception as e1:
				print "Create collection failed! " + e1.message
		except Exception as e2:
			print "Connect to Database Failed! " + e2.message


	def document_add(self, collection_name, records_list):
		return self.db[collection_name].insert_many(records_list)

	def document_remove(self, collection_name, filter_list):
		for filter_key in filter_list:
			self.db[collection_name].delete_many(filter_key)

	def document_search(self, collection_name, search_dict):
		# TODO: implement the operator($gt, $eq, $gte, $in, $lt, $lte, $ne, $nin)
		# https://docs.mongodb.com/manual/reference/operator/query-comparison/
		# https://docs.mongodb.com/manual/reference/method/db.collection.find/
		return self.db[collection_name].find(search_dict)