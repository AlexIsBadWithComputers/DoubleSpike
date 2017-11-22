"""
THis is the program that will commit the data to the data base. Hooray. 
"""
from DataBaseEnterer import *
from MySQLdb import IntegrityError, OperationalError
from tkinter import messagebox

def InsertChunk(data):
	db = Database()
	AlreadyAsked = False
	Command = ("INSERT INTO DoubleSpikeTable (FilePath, alpha, beta, percentspike, delta, deltaratio, concentration, spikeadded,"
				 "leastsquares, InterferenceCorrection, MachineFractionate, BackGroundSub, spike1, spike2, refference) VALUES"
					"(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

	PossibleCommand = """INSERT INTO MainTable (FilePath) VALUES (%s) """

	for rows in data:

		DataToCommit = tuple(rows)

		try: 
			MainTableCommit = tuple([rows[0]])
			if MainTableCommit == tuple([None]):
				continue 
			else:
				print(MainTableCommit)
				db.insert(PossibleCommand, MainTableCommit)

		# This data has already been put in the main table. Pass
		except IntegrityError as e:
			pass

		try: 
			print(DataToCommit)
			db.insert(Command, DataToCommit)
		except IntegrityError as e:
			print(rows)
			if AlreadyAsked == False:
				Continue = messagebox.askyesno("Whoopsie Daisy!", "These files are already in the database. Would you like to update them?")
				AlreadyAsked = True
				
			if Continue == True:
				query1 = Command.replace("INSERT", "REPLACE")
				db.insert(query1, DataToCommit)

			else:
				db.rollypolly()
				return


					




