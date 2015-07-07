#!/usr/bin/python
import os, sys, syslog, mysql.connector, re
from datetime import datetime
from galintools.settings import *

class MySQL():
	
	def __init__(self, logger, host, user, password, raw=True):
		self.logger = logger

		self.logger.info("Connecting to server MySQL server: %s" % (host))

		self.db_conn = mysql.connector.connect(host=host,
							 				   user=user,
							 				   password=password)

		self.host = host
		self.raw = raw
		self.dateformat = "%d/%m/%Y %H:%M:%S"

	def escape_str(self,string):
		return "`" + string + "`"

	def set_cursor(self):
		return self.db_conn.cursor(raw=self.raw,buffered=True)

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
