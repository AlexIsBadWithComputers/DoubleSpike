import MySQLdb

class Database():
	"""
	This class will be used to insert data into the database using 
	the DataBaseEntry GUI.
	"""

	host = 'localhost'
	user = 'GuiUpload'
	password = ''
	db = 'TestBase'

	def __init__(self):
		self.connection = MySQLdb.connect(self.host, self.user, self.password, self.db)
		self.cursor = self.connection.cursor()

	def insert(self, query, data):
		#try:
			self.cursor.execute(query, data)
			self.connection.commit()
		#except:
			#print("UHOH!")
		#	self.connection.rollback()
	def deleteinsert(self,query):
		self.cursor.execute(query)
		self.connection.commit()


	def query(self, query):
		cursor = self.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute(query)

		return cursor.fetchall()
	def rollypolly(self):
		self.connection.rollback()

	def __del__(self):
		self.connection.close()