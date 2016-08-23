#!/usr/bin/python
import os, sys, syslog, mysql.connector, re, urllib
from pymongo import MongoClient
from datetime import datetime
from galintools.settings import *

class MySQL():
	
	def __init__(self, logger):
		self.logger = logger

	def mysql_connect(self, host, user, password):

		self.db_conn = None
		
		self.logger.info("Connecting to MySQL server: %s" % (host))

		try:
			self.db_conn = mysql.connector.connect(host=host,
												   user=user,
												   password=password)
		except Exception, e:
			self.logger.error("Error connecting to MySQL server: %s. Details: %s" % (host, e))
		
		return self.db_conn

	def escape_str(self,string):
		return "`" + string + "`"

	def set_cursor(self,raw=True):
		return self.db_conn.cursor(raw=raw,buffered=True)

	def close_cursor(self, cursor):
		cursor.close()
		cursor = None

	def get_databases(self, search=None):
		cursor = self.set_cursor()
		databases = []
		cursor.execute("SHOW DATABASES")

		if search:
			regexp = re.compile(search)
			for database in cursor:
				if regexp.search(database[0]):
					databases.append(database[0])
			self.close_cursor(cursor)
			return databases
		else:
			databases = [ database for database, in cursor ]
			self.close_cursor(cursor)
			return databases


	def get_table_list(self):
		cursor = self.set_cursor()
		cursor.execute("SHOW TABLES")
		tables = [ table for table, in cursor ]
		self.close_cursor(cursor)
		return tables

	def get_table_schema(self, table):
		cursor = self.set_cursor()
		cursor.execute("SHOW CREATE TABLE %s" % (self.escape_str(table)))
		table_schema = cursor.fetchone()[1]
		self.close_cursor(cursor)
		return table_schema

	def get_structure_sql(self,table):
		schemas = {}
		schemas[table] = self.get_table_schema(table)
		return schemas

	def get_column_names(self, table):
		cursor = self.set_cursor()
		cursor.execute("DESCRIBE %s" % (self.escape_str(table)))
		column_names = [ self.escape_str(row[0]) for row in cursor ]
		self.close_cursor(cursor)
		return column_names

	def set_database(self, db):
		db = self.escape_str(db)
		self.db_name = db
		self.db_conn.database = db


class MongoDB():
	def __init__(self, logger):
		self.logger = logger

	def mongodb_connect(self, host, port=27017, user=None, password=None):
		self.db_conn = None
		
		self.logger.info("Connecting to MongoDB server: %s" % (host))

		if user or password:
			password = urllib.quote_plus(password)
			mongodb_uri = 'mongodb://' + user + ':' + password + '@' + host + ':' + str(port)
		else:
			mongodb_uri = 'mongodb://' + host + ':' + str(port)

		try:
			self.db_conn = MongoClient(mongodb_uri)
		except Exception, e:
			self.logger.error("Error openning connection to mongo: %s. Details: %s" % (host, e))

		return self.db_conn

	def get_databases(self, search=None):
		databases = self.db_conn.database_names()

		if search:
			regexp = re.compile(search)
			for database in databases:
				if not regexp.search(database):
					databases.remove(database)

		return databases
