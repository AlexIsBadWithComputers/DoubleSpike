"""
This code is a remix of the original double spike code I wrote a few years ago.
This one is far superior and likely easier to maintain than the mess that was that first 
GUI. Note that you will require Python 3.x and numpy and scipy in order for this to run correctly.


"""

#!/usr/bin/env python3
from tkinter import * 
from tkinter import filedialog
import glob
import importlib
from DSSolver import *
import re
import tkinter
import itertools
from DoubleSpikeDataBaseCommit import *
import os
class RootWindow(Frame):
	
	"""
	Begin initialization of root window for the GUI
	TODO: Describe what this does here
	"""

	# TODO:
	# Reinitialize the concentration stuff when you open a new directory.
	def __init__(self, parent):
		Frame.__init__(self, parent)

		# Need a canvas so I can have a text box and other widgetds
		# organized by grid in the frame.
	
		self.canvas = Canvas(parent, borderwidth=10)
		self.frame = Frame(self.canvas)
		
		self.canvas.configure(width=1000, height=280)

		self.frame2 = Frame(parent, background = "#ffffff")
		self.TextBox = Text(self.frame2, wrap=NONE)

		# X and Y Scrollbars for text box. Might not need X
		# But someone will complain the one time they need it.

		self.TextScrollY = Scrollbar(self.frame2)
		self.TextScrollX = Scrollbar(self.frame2, orient=HORIZONTAL)
		self.TextScrollY.config(command=self.TextBox.yview)
		self.TextScrollX.config(command=self.TextBox.xview)
		self.TextBox.config(yscrollcommand=self.TextScrollY.set)
		self.TextBox.config(xscrollcommand=self.TextScrollX.set)
		
		self.TextScrollY.pack(side="right",fill="y")
		self.TextScrollX.pack(side="bottom",fill="x")
		self.TextBox.pack(side="bottom",fill="both", expand=True)
		self.frame2.pack(side="bottom",fill='both', expand = True)
		
		#self.vsb.pack(side="right", fill="y")
		self.canvas.pack(side="top", fill='both', anchor=NW)
		
		self.canvas.create_window((4,4), window=self.frame, tags=self.frame, anchor='nw')
		self.frame.bind("<Configure>", self.onFrameConfigure)
		self.parent = parent
		self.BreakChar = "	"

		self.initUI()
	

		# self.initUI()

	def initUI(self):
		"""
		Layout the default window options
		"""

		self.IsobarCorr = BooleanVar()
		self.IsobarCorr.set(False)

		self.parent.title("Double Spike Calculation")
		self.pack(fill=BOTH, expand = 1)

		menubar = Menu(self.parent)
		self.parent.config(menu=menubar)

		TopOptions = Menu(menubar)
		SubTopOptions = Menu(menubar)
		SubTopOptionsOpen =Menu(menubar)
		ViewOptions = Menu(menubar)
		NewOptions = Menu(menubar)
		self.AnalysisOptions = Menu(menubar)
		self.csv = False

		menubar.add_cascade(label = "File", menu=TopOptions)
		TopOptions.add_cascade(label="Save", menu=SubTopOptions)
		SubTopOptions.add_command(label="Output", command=self.OutputSaver)

		TopOptions.add_cascade(label="Open", menu=SubTopOptionsOpen)
		SubTopOptionsOpen.add_command(label="Headers and Constants", command=self.ElementFileOpen)
		SubTopOptionsOpen.add_command(label="Directory", command=lambda: self.onOpen(csv = False))
		SubTopOptionsOpen.add_command(label="CSV File", command= lambda: self.onOpen(csv = True))

		menubar.add_cascade(label="View", menu=ViewOptions)
		ViewOptions.add_command(label="Clear Output", command=self.ClearTextBox)
		menubar.add_cascade(label="Analysis Options", menu=self.AnalysisOptions)

		self.AnalysisOptions.add_command(label="Choose Delta Value", command=self.ChooseDelta)
		self.AnalysisOptions.add_command(label="Concentraition Calculation", command=self.ConcentrationInput)
		self.AnalysisOptions.add_separator()

		self.LeastSquares = BooleanVar()
		self.LeastSquares.set(False)
		self.AnalysisOptions.add_checkbutton(label="Least Squares Solve", variable=self.LeastSquares,
												 onvalue=True, offvalue=False)
		menubar.add_cascade(label="New", menu=NewOptions)
		NewOptions.add_command(label="Headers and Constants", command=self.MakeNewInputFile)
		NewOptions.add_command(label="Inteference Correction", command=self.InterferenceCorrection)
		NewOptions.add_separator()
		NewOptions.add_command(label="Database Entry", command = 	self.ToDataBase)

		self.pastsetup = False
		self.ElementFileOpen()
		self.pastsetup = True

	def onFrameConfigure(self,event):
		self.canvas.configure(scrollregion=self.canvas.bbox("all"))

	def onFrameConfigure2(self,event):
		self.pcanvas.configure(scrollregion=self.pcanvas.bbox("all"))

	@staticmethod
	def GetVarFromFile(filename):
		"""
		Imports data from file
		"""
		global data
		import imp
		
		try:
			f = open(filename, 'r')
		
		except TypeError:
			data = None
			return 
		
		except FileNotFoundError:
			data = None
			return
		
		try:
			data = imp.load_source('data','',f)
			f.close()
		except SyntaxError:
			data = None
			return

	def onOpen(self, csv):
		"""
		This function is uest to select the directory and read
		the ASCII grid exports from thermo software.
		"""
		self.csv = csv
		if hasattr(self, "AmtDS"):
			delattr(self, "AmtDS")

		if hasattr(self,'DSConc'):
			delattr(self, "DSConc")
		
		if self.csv == False:
			ftype = [ ('Data Exports','*.exp'),('All Files','*')]
			self.dlg = filedialog.askdirectory()

			# IF you change directories you need to refresh
			# the concentration vectors to avoid out of
			# range errors caused by irrelevent concentratoins.

			if self.dlg != '':
				self.TextBox.insert(END, "\n Your chosen directory is ")
				self.TextBox.insert(END, self.dlg)
				self.TextBox.insert(END," \n")
				self.TextBox.see(END)

		if self.csv == True:
			
			self.dlg = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
			
			if self.dlg != '':
				self.TextBox.insert(END, "\n Your chosen CSV file is ")
				self.TextBox.insert(END, self.dlg)
				self.TextBox.insert(END," \n************************************************************************\n")
				self.TextBox.insert(END,"\nPLEASE NOTE THAT BACKGROUND SUBTRACTION IS NOT AVAILABLE WITH .CSV FILES")
				self.TextBox.insert(END,"\n   YOU WILL HAVE TO SUBTRACT BACKGROUNDS MANUALLY IF IT IS REQUIRED\n")
				self.TextBox.insert(END," \n************************************************************************\n")
				self.TextBox.see(END)


	def ElementFileOpen(self):
		"""
		This function opens a dialog to open the constant files of the element you're hoping to
		run double spike calculations on. Additonally, it fills the GUI with the data
		relevant to the current evaluation.
		"""

		# If you switch elements while it's still open we don't want 
		# to calculate the wrong delta value used from another 
		# calculation. 
		if hasattr(self, 'DeltaRatio'):
			delattr(self, "DeltaRatio")

		self.labels = ['Column Headers','Mixture Ratio', 'Standard Ratio', 'Spike Ratio', 'Mass','Ratio Mass']
		ftype = (('Python Files', '*.py'))
		if self.pastsetup == True:
			self.fname = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
		else:
			# This is probably universal, but check this on other computers
			self.fname = 'Constants/default.py'

		if str(self.fname) == '':
			return
		
		self.TextBox.insert(END, "\nYou have selected ")
		self.TextBox.insert(END, self.fname)
		self.TextBox.insert(END, " for constants and headers. \n")
		self.TextBox.see(END)
		
		listy = self.frame.grid_slaves()
			# This is in case someone wants to switch the element 
			# while the window is still active.

		for l in listy:
			if int(l.grid_info()["row"]) > 1:
				l.grid_forget()
			
		
		# All this mess does is grab data from files, then place that data in widgets
		# for display and use in the GUI.
		
		# Make sure we don't double dip in optional headers. THis prevents
		# things from existing that shouldn't exist if the method changes.
		# Not the best way, but it's easier to ask forgiviness than permission.
		try:
			if hasattr(data, 'RatioVoltage'):
				delattr(data, "RatioVoltage")
		except NameError:
			pass

		try:
			if hasattr(data, "InterferenceFile"):
				delattr(data, "InterferenceFile")
		except NameError:
			pass
		try:
			if hasattr(data, "isotope"):
				delattr(data, "isotope")
		except NameError:
			pass
		
		if hasattr(self, "RatioVoltage"):
			delattr(self, "RatioVoltage")

		if hasattr(self, "InterferenceFile"):
			delattr(self, "InterferenceFile")

		try:
			self.AnalysisOptions.delete("Subtract Background")
		except tkinter.TclError:
			pass
		try:
			self.AnalysisOptions.delete("Separate Background Files")
		except tkinter.TclError:
			pass

		try:
			self.AnalysisOptions.delete("Inteference Correction")
		except tkinter.TclError:
			pass

		try:
			self.AnalysisOptions.delete("Machine Fractionate Interference")
		except:
			pass

		try:
			self.GetVarFromFile(self.fname)

			if data == None:
				return

			self.MixIN = data.MixIN
			self.StandardIN = data.StandardIN
			self.SpikeIN = data.SpikeIN
			self.Mass = data.Mass
			self.RatioMass = data.RatioMass
			self.columnheaders = data.isotope

			if hasattr(data, 'RatioVoltage'):
				self.RatioVoltage = data.RatioVoltage
			
			if hasattr(data, "InterferenceFile"):
				DoNotGrid = False
				try:
					self.InterferenceFile = open(data.InterferenceFile, 'r')
					self.TextBox.insert(END, "\nInterference correction file: ")
					self.TextBox.insert(END, data.InterferenceFile)
					self.TextBox.insert(END,"\n")
					dicts = []
					for lines in self.InterferenceFile.readlines():
						dicts.append(eval(lines))

					self.DictionaryList = dicts[1]
					self.HeadInterferenceDict = dicts[0]
					self.HeadMassDict = dicts[2]
					self.MassInterferenceDict = dicts[3]
				
				except FileNotFoundError:
					self.TextBox.insert(END, "\nInterference file: ")
					self.TextBox.insert(END, data.InterferenceFile)
					self.TextBox.insert(END," not found.\n")
					DoNotGrid = True


		except AttributeError:
			self.TextBox.insert(END, "\n The file ")
			self.TextBox.insert(END, self.fname)
			self.TextBox.insert(END, " does not contain the appropriate data for double-spike calculations. \n \n")
			return
		except ImportError:
			# This one catches a case where old files are selected, this may never hit htis check.
			self.TextBox.insert(END, "\n The file ")
			self.TextBox.insert(END, self.fname)
			self.TextBox.insert(END, " does not contain the appropriate data for double-spike calculations. \n \n")
			self.TextBox.see(END)
			return

		self.mixgrid = [ None for i in range(len(self.MixIN))]
		self.standardgrid = [ None for i in range(len(self.MixIN))]
		self.massgrid = [ None for i in range(len(self.MixIN))]
		self.headergrid = [ None for i in range(len(self.MixIN))]
		self.spikegrid = [ None for i in range(len(self.MixIN))]

		if len(self.headergrid) < 3:
				self.TextBox.insert(END, "\nNot enough isotopes to run double spike calculation in ")
				self.TextBox.insert(END, self.fname)
				self.TextBox.see(END)
				return

		for i in range(len(self.MixIN)):

			Label(self.frame, text = self.labels[i]).grid(column=i, row = 0)

			self.headergrid[i] = Entry(self.frame)
			self.headergrid[i].grid(column = 0, row = i +1 )
			self.headergrid[i].insert(0,self.columnheaders[i])

			self.mixgrid[i] = Entry(self.frame)
			self.mixgrid[i].grid(column = 1, row = i +1)
			self.mixgrid[i].insert(0,self.MixIN[i])

			self.standardgrid[i] = Entry(self.frame)
			self.standardgrid[i].grid(column = 2, row = i+1 )
			self.standardgrid[i].insert(0,self.StandardIN[i])

			self.spikegrid[i] = Entry(self.frame)
			self.spikegrid[i].grid(column = 3, row = i+1 )
			self.spikegrid[i].insert(0,self.SpikeIN[i])

			self.massgrid[i] = Entry(self.frame)
			self.massgrid[i].grid(column = 4, row = i +1)
			self.massgrid[i].insert(0,self.Mass[i])

		self.ratiogrid = Entry(self.frame)
		self.ratiogrid.grid(column=5, row=1)
		self.ratiogrid.insert(0, self.RatioMass)

		

		if hasattr(self, 'InterferenceFile'):
			# If it didn't work we don't want the options there. 
			if DoNotGrid == False:
				self.IsobarCorr = BooleanVar()
				self.IsobarCorr.set(False)
				
				self.AnalysisOptions.add_checkbutton(label="Inteference Correction", variable=self.IsobarCorr,
												onvalue=True, offvalue=False)
				
				self.MachineFractionateInterference = BooleanVar()
				self.MachineFractionateInterference.set(False)
				
				self.AnalysisOptions.add_checkbutton(label="Machine Fractionate Interference", 
													 variable = self.MachineFractionateInterference,
													 onvalue=True,
													 offvalue=False)
				
	
		if hasattr(self, 'RatioVoltage'):
			Label(self.frame, text="Ratio Header").grid(column=5, row = 5)
			self.ratiovoltagegrid = Entry(self.frame)
			self.ratiovoltagegrid.grid(column=5, row=6)
			self.ratiovoltagegrid.insert(0, self.RatioVoltage)
			
			if self.csv == False:
				self.UniqueBackground = BooleanVar()
				self.UniqueBackground.set(False)

				self.DoSubtraction = BooleanVar()
				self.DoSubtraction.set(True)


				self.AnalysisOptions.add_checkbutton(label="Subtract Background", variable = self.DoSubtraction,
				 							onvalue = True, offvalue = False)

				self.AnalysisOptions.add_checkbutton(label="Separate Background Files", variable=self.UniqueBackground,
												onvalue=True, offvalue=False)

		RunButton = Button(self.frame, text="Calculate", command = self.MethodRun)
		RunButton.grid(column = 2, row = len(self.MixIN) + 4)

		self.Spike1 = StringVar()
		self.Spike2 = StringVar()
		self.Reference = StringVar()

		self.SpikeChoice1 = OptionMenu(self.frame,self.Spike1, *list(self.columnheaders))
		self.SpikeChoice2 = OptionMenu(self.frame,self.Spike2, *list(self.columnheaders))
		self.RefChoice = OptionMenu(self.frame,self.Reference, *list(self.columnheaders))

		Label(self.frame, text ="Spike 1: ").grid(column = 0, row = len(self.MixIN) + 2)
		Label(self.frame, text = "Spike 2: ").grid(column = 0, row = len(self.MixIN) + 3)
		Label(self.frame, text="Unspiked: ").grid(column = 0, row = len(self.MixIN) + 4)

		self.SpikeChoice1.configure(width = 15)
		self.SpikeChoice2.configure(width = 15)
		self.RefChoice.configure(width = 15)

		self.SpikeChoice1.grid(column = 1, row = len(self.MixIN) + 2)
		self.SpikeChoice2.grid(column = 1, row = len(self.MixIN) + 3)
		self.RefChoice.grid(column =1 , row = len(self.MixIN) + 4)



	# This function has gotten out of hand. Rewrite things when possible.	
	def MethodRun(self):
		"""
		This function is used to grab the choice of spikes and reference, and collect
		data about the sample ratios, mixture ratios, spike ratios, and column headers.
		Once it has collected all the data it feeds it into the calculation and prints that 
		information to the textbox. This is essentially " the meat" of the code. 
		MyHeads is the header files,
		RunMix is the mixture values,
		RunStand is the standard values,
		RunMass is the mass and Run Spike is the spike. 
		Positions is an array of indicies that we grab values from contrilled
		by spike/reference choice. 
		"""
		
		# Find which column headers we'll be looking for in each data file
		self.done = False
		if hasattr(self, "dlg") == False:
			self.TextBox.insert(END, "\nYou haven't chosen a directory.")
			return

		self.MyHeads = [
					self.Spike1.get(),
					self.Spike2.get(),
					self.Reference.get()
				  ]
		
		if len(self.MyHeads) != len(set(self.MyHeads)):
			self.TextBox.insert(END, "\n You need three unique ratios, choose new spiked and unspiked ratios.")
			self.TextBox.see(END)
			return	

		# Get index positions 
		try:
			self.Positions = [self.columnheaders.index(self.MyHeads[i]) for i in range(len(self.MyHeads))]

			self.TextBox.insert(END,"\n Using ")
			
			for elements in self.MyHeads: # + [self.ratiovoltagegrid.get()]:
				self.TextBox.insert(END, elements)
				self.TextBox.insert(END, " ")
			
			if hasattr(self, "RatioVoltage"):
				self.TextBox.insert(END, self.ratiovoltagegrid.get())
				self.TextBox.insert(END, " ")
			
			self.TextBox.insert(END, "for double-spike calculation. \n")
			self.TextBox.see(END)
	
		except ValueError:
			self.TextBox.insert(END, "\n You need to choose your spiked and unspiked ratios before analysis.")
			self.TextBox.see(END)
			return

		self.count = 0
		self.AlphaVector = []
		self.BetaVector = []
		self.LambdaVector = []
		self.DeltaVector = []
		self.FileVector = []
		# The second one is for storing the entire file path for data base commitment
		self.FileVector2 = []
		self.ConcentrationVector = []
		escape = False
	
		if hasattr(self, 'RatioVoltage'):
			self.MyHeads = self.MyHeads + [self.ratiovoltagegrid.get()]
		
		if hasattr(self, "subtraction"):
			delattr(self, "subtraction")
		
		if self.csv == False:
			for j, files in enumerate(glob.iglob(self.dlg + '/*.exp')):
				print(files, "I AM FILE")
				self.count += 1					
			    # Constant choices non-convergent. Bail out. 
				if escape == True:
					break
			
				f = open(files,'r')
				
				
			
				for lines in f.readlines():
					# If you want to modify this to use for something either than THERMO files you must modify
					# self.FileSearcher for your input.  
					# These if "STRING" in lines" peices are what you'll need to modify in order 
					# to grab your own data. Unfortunately I don't have access to other data
					# types, so I didn't write those in as an option.

					if hasattr(self, "InterferenceFile"):
						 self.FileSearcher(lines, self.MyHeads, files, GrabIsobar = self.IsobarCorr.get())
					
					else:

						self.FileSearcher(lines, self.MyHeads, files)
					
				
					if len(self.Sample) > 0:
						# This is the background subtraction.
						self.Untouched = self.Sample
						break

				# The above sets up the self.Sample and self.subtraction if applicable and 
				# then CalculateResults performs the calculation
				# print(self.Sample, "HERE")
				
				self.CalculateResults(files)

				f.close()
			if self.count == 0:
				self.TextBox.insert(END, "\n The directory ")
				self.TextBox.insert(END, self.dlg)
				self.TextBox.insert(END, " does not contain any files with the extension *.exp \n")
				self.TextBox.see(END)

		if self.csv == True:
			
			MyCSVFile = open(self.dlg, 'r')

			for i, lines in enumerate(MyCSVFile.readlines()):
				if i == 0:
					self.MakeIndicies(lines, self.MyHeads, InterferenceHeads = self.IsobarCorr.get())
					saveHeads = lines
		
				if i != 0:
					samplename = lines.split(",")[0]
					if self.LeastSquares.get() == False:
						
						self.FileSearcher(lines,self.MyHeads, samplename, GrabIsobar = self.IsobarCorr.get())
						
						self.Untouched = self.Sample
						self.CalculateResults(samplename)

						self.count += 1
					if self.LeastSquares.get() == True:
						
						if hasattr(self, "InterferenceFile"):
							# For CSV files as the headers come from the top of the file, we have to
							# run this twice for method switching. I'm sure I could write this so I dont
							# have to call it twice, but, if I'm being honest, I don't really care to take
							# the time. It's not going to make anything cleaner and it'll just waste 
							# a bunch of time.

							self.MakeIndicies(saveHeads, self.MyHeads, InterferenceHeads = self.IsobarCorr.get())
							self.FileSearcher(lines,self.MyHeads, samplename, GrabIsobar = self.IsobarCorr.get())
							# print(self.Sample)
							
						else:
							self.MakeIndicies(saveHeads, self.MyHeads, InterferenceHeads = self.IsobarCorr.get())
							self.FileSearcher(lines,self.MyHeads, samplename)
						
						self.CalculateResults(samplename, csvLine=lines,saveheads=saveHeads)
						self.count += 1
					


		# Dispaly other values used in calculation in case someone fiddled and you need accountability. 

		if self.count != 0 or self.csv==True:

			self.TextBox.insert(END, "\n \nUsed the following values for standard, mixture, spike, and mass: \n")
			KnownData = []
			KnownData.append(["", 'Standard', 'Mixture', 'Spike', 'Mass'])
			for i in range(len(self.headergrid)):
				KnownData.append([self.headergrid[i].get(), self.standardgrid[i].get(),
						  self.mixgrid[i].get(), self.spikegrid[i].get(), self.massgrid[i].get()])							 
			
			col_width = max(len(word) for row in KnownData for word in row) + 2  # padding
			
			for row in KnownData:
				self.TextBox.insert(END,'\n')
				self.TextBox.insert(END, "".join(word.ljust(col_width) for word in row))
			
			self.TextBox.insert(END, '\n \nRatio Mass: ')
			self.TextBox.insert(END, str(self.ratiogrid.get()))
			self.TextBox.insert(END, '\n \n')
			
			self.DisplayResults()
			
			self.TextBox.insert(END, '\n \n')
			self.TextBox.see(END)

			

		
	def DisplayResults(self):

		Columns = ["File","Alpha","Beta","% Spike"]
		# TODO: Separate wrapper function for this.
		
		# If we calculated a delta value we print out that data as well.
		if hasattr(self, 'DeltaRatio'):
			insert = "Delta" + " (" + str(int(round(self.MassList[self.num.get()]))) + "/" + str(int(round(self.MassList[self.denom.get()]))) +")"
			Columns.append(insert)
		if hasattr(self,'AmtDS') and hasattr(self, 'DSConc'):
			Columns.append("Concentration")
			Columns.append("Spike Added")

		Columns.append("Least Squares")


		if hasattr(self, 'RatioVoltage'):
			Columns.append("Background Subtraction")

		if hasattr(self, "InterferenceFile"):
			Columns.append("Isobar Correction")
			Columns.append("Machine Fractionated")

		if self.csv == False:
			self.TextBox.insert(END, "\nSummary for Directory: ")
			self.TextBox.insert(END, self.dlg)
			self.TextBox.insert(END, '\n')
		else:
			self.TextBox.insert(END, "\nSummary for file: ")
			self.TextBox.insert(END, self.dlg)
			self.TextBox.insert(END, '\n')
		PrintData = [Columns]
		errormessage = False
		for i in range(len(self.FileVector)):
			PrintData.append([self.FileVector[i], str(self.AlphaVector[i]), str(self.BetaVector[i]), str(self.LambdaVector[i])])

			# If we have delta values, add that sucker to the output as well
			if hasattr(self, "DeltaRatio") and hasattr(self,'AmtDS') and hasattr(self, 'DSConc'):
				PrintData[i+1].append(self.DeltaVector[i])
				PrintData[i+1].append(self.ConcentrationVector[i])
				PrintData[i+1].append(str(float(self.AmtDS[i]) * float(self.DSConc)))

			elif (hasattr(self, "DSConc") and hasattr(self,'AmtDS')) and not (hasattr(self, 'DeltaRatio')):
				PrintData[i+1].append(self.ConcentrationVector[i])
				try:
					PrintData[i+1].append(str(float(self.AmtDS[i]) * float(self.DSConc)))
				except TypeError:
					PrintData[i+1].append("No Convergence")
			
			elif (hasattr(self,"DeltaRatio")) and not (hasattr(self, "DSConc") or hasattr(self,'AmtDS')):
				PrintData[i+1].append(self.DeltaVector[i])

			if self.LeastSquares.get() == True:
				PrintData[i+1].append("Yes")
			
			else:
				PrintData[i+1].append("No")

			if hasattr(self, 'RatioVoltage'):
				
				if self.DoSubtraction.get() == True:
					PrintData[i+1].append("Yes")
				
				else:
					PrintData[i+1].append("No")

			if hasattr(self, "InterferenceFile"):
				
				if self.IsobarCorr.get() == True:
					PrintData[i+1].append("Yes")
				
				else:
					PrintData[i+1].append("No")

				if self.MachineFractionateInterference.get() == True:
					
					if hasattr(self, "RatioVoltage"):
						PrintData[i+1].append("N/A")
						
						if errormessage == False and self.IsobarCorr.get() == True:
							self.TextBox.insert(END, "\nMACHINE FRACTIONATION OF INTERFERENCE ONLY AVAILABLE FOR RATIO BASED ANALYSIS.")
							self.TextBox.insert(END, "\nISOBARS WERE SUBTRACTED, BUT NO MASS FRACTIONATION WAS APPLIED.\n")
							errormessage = True
					else:
						PrintData[i+1].append("Yes")
				if self.MachineFractionateInterference.get() == False:
					
					if hasattr(self, "RatioVoltage"):
						PrintData[i+1].append("N/A")
					
					else:
						PrintData[i+1].append("No")

		# Display data with padding
		col_width = max(len(word) for row in PrintData for word in row) + 2

		if len(PrintData) > 1:
		
			for row in PrintData:
					self.TextBox.insert(END,'\n')
					self.TextBox.insert(END, "".join(word.ljust(col_width) for word in row))

		if hasattr(self, "RatioVoltage"):
			if self.DoSubtraction.get() == True:

				self.TextBox.insert(END, "\nUsed background file: ")
				self.TextBox.insert(END, self.BackGroundFile)
				self.TextBox.insert(END, '\n')
				self.TextBox.see(END)

		

	def CalculateResults(self,files,csvLine=None,saveheads=None):

		# Pull other data using the column header order
		
		try:
			RunMix = [float(self.mixgrid[place].get()) for place in self.Positions]
			RunStand = [float(self.standardgrid[place].get())for place in self.Positions]
			RunMass  = [float(self.massgrid[place].get()) for place in self.Positions]
			RunSpike = [float(self.spikegrid[place].get()) for place in self.Positions]
			float(self.ratiogrid.get())
		except ValueError:
			self.TextBox.insert(END, "\nA number in your ratios or masses is not floating point. Please fix it before continuing. \n")
			return


		if hasattr(self, 'RatioVoltage'):
			# Subtract all the voltages from your background. This first bit is to choose a 
			# File for each. Otherwise it's happy to ignore them

			if self.DoSubtraction.get() == True and self.csv == False:
				# Need to do this because I'm an idiot and didn't code smart. 
				SaveSample = self.Sample
				self.subtraction = self.BackGroundSubtraction(files)
				self.Sample = SaveSample
			
				if self.UniqueBackground.get() == False:
					self.done = True
				
				if self.subtraction == None:
					self.TextBox.insert(END, "\n Aborted \n")
					return
			
			if self.DoSubtraction.get() == True and self.csv == False:
				# print(self.subtraction, files)
				# print(self.Sample)
				
				self.Sample = [voltage_sample - voltage_bg for voltage_sample, voltage_bg in zip(self.Sample, self.subtraction)]
				# print(self.Sample)
		
			try:
				
				if self.IsobarCorr.get() == True:
					self.InterferenceSubtraction()
				self.Sample = [self.Sample[i]/self.Sample[-1] for i in range(len(self.Sample) - 1)]
			# This just ignores calculating a delta value for the background file you chose. 
			except ZeroDivisionError:
		
				return

		if hasattr(self,'RatioVoltage') == False:
			if self.IsobarCorr.get() == True:
					self.InterferenceSubtraction()


		try:			
			alpha,beta, lamb, success = DSpikeSolve(self.Sample, 
												RunSpike, 
												RunStand, 
												RunMass,
												float(self.ratiogrid.get()))
		
			alpha2,beta2,lamb2, success2 = DSpikeSolve(RunMix,
												   RunSpike,
												   RunStand,
												   RunMass,
												   float(self.ratiogrid.get()))
		except IndexError:
			return
		# print(alpha, beta, lamb, success, success2)
		if hasattr(self, "InterferenceFile"):
			if self.MachineFractionateInterference.get()==True and self.IsobarCorr.get() == True and self.LeastSquares.get() == False:
			
				if hasattr(self, "RatioVoltage") == True:
					pass
			
				else:
					self.Sample = self.Untouched
					self.InterferenceSubtraction(beta1=beta, bet2=beta, MachineFractionate = True)
					alpha,beta, lamb, success = DSpikeSolve(self.Sample, 
												RunSpike, 
												RunStand, 
												RunMass,
												float(self.ratiogrid.get()))
		
					alpha2,beta2,lamb2, success2 = DSpikeSolve(RunMix,
												   RunSpike,
												   RunStand,
												   RunMass,
												   float(self.ratiogrid.get()))
			AllHeads = [self.headergrid[i].get() for i in range(len(self.headergrid))] 	
		if self.LeastSquares.get() == True and isinstance(alpha,float):
			
			
			# This grabs the interferences. They should already exist from the non-least squares solutions
			if self.csv == False:
				AllHeads = [self.headergrid[i].get() for i in range(len(self.headergrid))] 	
				if hasattr(self, 'RatioVoltage'):
					AllHeads = [self.headergrid[i].get() for i in range(len(self.headergrid))] 
					AllHeads += [self.ratiovoltagegrid.get()]

					if self.DoSubtraction.get() == True:
						SaveSample = self.Sample
						self.subtraction = self.BackGroundSubtraction(files, AllValues = True, AlreadyHasFile=self.BackGroundFile)
						self.Sample = SaveSample

						if self.subtraction == None:
							self.TextBox.insert(END, "\n Aborted \n")
							return
	
				f = open(files, 'r')
				for lines in f.readlines():

					if hasattr(self, "InterferenceFile"):
						self.FileSearcher(lines, AllHeads, files, GrabIsobar = self.IsobarCorr.get())
						self.Untouched = self.Sample
			
					else:
						self.FileSearcher(lines, AllHeads, files)

					if len(self.Sample) > 0:
						MySample = self.Sample
						Unchanged = self.Sample
						# print(MySample)
						break

				
				if hasattr(self, 'RatioVoltage'):
					
					if self.DoSubtraction.get() == True:
					
						self.Sample= [voltage_sample - voltage_bg for voltage_sample, voltage_bg in zip(self.Sample,self.subtraction)]
					
					try:
						if hasattr(self, "InterferenceFile") == True:
							
							self.InterferenceSubtraction(AllValues=True)
				
						self.Sample = [self.Sample[i]/self.Sample[-1] for i in range(len(self.Sample) - 1)]
						MySample = self.Sample
		
					# This just ignores calculating a delta value for the background file you chose. 
					except ZeroDivisionError:
						return

				else:

					if hasattr(self, "InterferenceFile") == True and self.IsobarCorr.get() == True:	
						self.InterferenceSubtraction(AllValues=True)	
			
			if self.csv == True:
				AllHeads = [self.headergrid[i].get() for i in range(len(self.headergrid))] 
				
				self.MakeIndicies(saveheads, AllHeads, InterferenceHeads = self.IsobarCorr.get())
				self.FileSearcher(csvLine, AllHeads, files, GrabIsobar = self.IsobarCorr.get())
			
				if hasattr(self, "InterferenceFile") == True and self.IsobarCorr.get() == True:
					self.Sample = self.Untouched
					self.InterferenceSubtraction(AllValues=True)
					
					if hasattr(self, "RatioVoltage"):
						self.Sample = [self.Sample[i]/self.Sample[-1] for i in range(len(self.Sample) - 1)]
						MySample = self.Sample


			AnnealSpike = [float(self.spikegrid[i].get()) for i in range(len(self.headergrid))]
			AnnealStandard =[float(self.standardgrid[i].get()) for i in range(len(self.headergrid))]
			AnnealMix = [float(self.mixgrid[i].get()) for i in range(len(self.headergrid))]
			AnnealMass = [float(self.massgrid[i].get()) for i in range(len(self.headergrid))]
			p1 = [alpha, beta, lamb]
			p2 = [alpha2, beta2, lamb2]

			alpha, beta, lamb, success = UseAnneal(MySample, 
								AnnealSpike, 
								 AnnealStandard, 
								 AnnealMass, 
								float(self.ratiogrid.get()), 
								p1)
			alpha2, beta2, lamb2, success2 = UseAnneal(AnnealMix, 
									AnnealSpike, 
									AnnealStandard, 
									AnnealMass, 
									float(self.ratiogrid.get()),
									 p2)

			if hasattr(self, "InterferenceFile"):
				if self.MachineFractionateInterference.get()==True and self.IsobarCorr.get() == True:
					if hasattr(self, "RatioVoltage") == True:
							
						pass
					else:
						self.Sample = self.Untouched
						self.InterferenceSubtraction(AllValues = True, MachineFractionate = True, beta1=beta, bet2=beta2)
						# print(self.Sample)
						MySample = self.Sample
						alpha, beta, lamb, success = UseAnneal(MySample, 
											AnnealSpike, 
											AnnealStandard, 
											AnnealMass, 
											float(self.ratiogrid.get()), 
											p1)
						alpha2, beta2, lamb2, success2 = UseAnneal(AnnealMix, 
											AnnealSpike, 
											AnnealStandard, 
											 AnnealMass, 
											 float(self.ratiogrid.get()),
											  p2)
					

		if success ==False and success2== True:
			self.AlphaVector.append(alpha)
			self.BetaVector.append(beta)
			self.LambdaVector.append(lamb)
			# THIS NEEDS TO CHANGE TO \\ IN WINDOWS
			self.FileVector.append(files.split(os.path.sep)[-1])
			
			if hasattr(self, 'DeltaRatio'):
				self.DeltaVector.append("No Convergence")
			if hasattr(self, 'AmtDS'):
				self.ConcentrationVector.append('No Convergence')
		
		if success == True and success2 == True:
			
			self.AlphaVector.append(alpha)
			self.BetaVector.append(beta)
			# THIS NEEDS TO CHANGE TO \\ IN WINDOWS
			self.FileVector.append(files.split(os.path.sep)[-1])
			self.FileVector2.append(files)


			# Calculate percent spike, 1.0 is unitary ratio.
			T = 1.0
			S = 1.0
			for i in range(len(self.spikegrid)):
				T += float(self.spikegrid[i].get())
				S += float(self.standardgrid[i].get())*(float(self.massgrid[i].get()) / float(self.ratiogrid.get())) ** (-(alpha - alpha2))

			PercentSpike = (T * (1.0 - lamb))/(S - S * (1- lamb) + T * (1 - lamb))
			self.LambdaVector.append(PercentSpike * 100)

			if hasattr(self,'DeltaRatio') and success2 == True:
				try:
					self.DeltaVector.append(str((self.DeltaRatio**(-(alpha-alpha2))-1)*1000))
				except RuntimeWarning:
					self.DeltaVector.append(str("Overflow"))
			if hasattr(self, 'AmtDS') and hasattr(self, 'DSConc'):
				conc = ConcentrationCalculation(alpha, 
												alpha2, 
												self.StandardIN, 
												self.SpikeIN, 
												self.Mass, 
												self.RatioMass,
												float(self.AmtDS[self.count-1]) * float(self.DSConc),
												PercentSpike)
				self.ConcentrationVector.append(str(conc))

		else:
			self.TextBox.insert(END,"\n File ")
			self.TextBox.insert(END, files)
			self.TextBox.insert(END, " did not converge.")
			self.TextBox.see(END)
			if success2 == False:
				self.TextBox.insert(END, "\n\nThe current choice of Mixture Ratios, Standard Ratios, and Spike Ratios are non-convergent.")
				self.TextBox.insert(END, "\nYou must choose values that have solutions, or literally nothing can be calculated. \n \n")
				self.TextBox.see(END)
				escape = True
				return

	#TODO: THis is fucked up with the CSV files. figure out why.

	def InterferenceSubtraction(self, AllValues = False, MachineFractionate = False, beta1=0, bet2=0):
		self.IsobaricCorrections = [[] for i in range(len(self.HeadInterferenceDict))]

		if beta1 == "No Convergence" or bet2 == "No Convergence":
			return

		if AllValues == True:
			searchHeads = self.columnheaders
		else:
			searchHeads = self.MyHeads
	
		for i, keys in enumerate(self.HeadInterferenceDict):
		
			KnownAbundance = self.HeadInterferenceDict[keys]
			KnownMass = self.HeadMassDict[keys]
							
			for j, elements in enumerate(searchHeads):
				try:

					self.IsobaricCorrections[i].append((self.DictionaryList[i][elements] / KnownAbundance )* self.MyInterferences[i])

					if MachineFractionate == True and hasattr(self, "RatioVoltage") == False:
						# This only works with ratios, you'll have to set that up yourself after. 
						# Always the last position added thanks to the stuff above.
						
						self.IsobaricCorrections[i][-1] = self.IsobaricCorrections[i][-1] * \
						                                 (self.MassInterferenceDict[i][elements]/float(self.ratiogrid.get()))**(-(beta1 - bet2))
					
				except KeyError:
					self.IsobaricCorrections[i].append(None)
				except AttributeError:
					return

		# print(self.Sample, self.IsobaricCorrections, "LHERELERER")
		for i in range(len(self.IsobaricCorrections)):
			# In terms of ratios this assumes that the denominator is interference free.
			for j in range(len(self.IsobaricCorrections[i])):
				if self.IsobaricCorrections[i][j] == None:
					pass
				else:
					self.Sample[j] = self.Sample[j] - self.IsobaricCorrections[i][j]

	def FileSearcher(self, lines, heads, files, GrabIsobar = False):
		if self.csv == False:
			if "Cycle" in lines:
				self.MakeIndicies(lines, heads, InterferenceHeads = GrabIsobar)
				
				if None in self.FilePositions:
					self.TextBox.insert(END, "\nFile ")
					self.TextBox.insert(END, files)
					self.TextBox.insert(END, " did not contain all your chosen column headers. \n")
					self.TextBox.insert(END, "Found: ")
					self.TextBox.insert(END, self.FilePositions)
					self.TextBox.insert(END, "\nwhere 'None' indicates missing data \n" )
					self.TextBox.see(END)
					Failure = True
					return Failure
				
					
			if "***	Mean" in lines:
				grab = lines.split(self.BreakChar)
				try:
					self.Sample = [float(grab[self.FilePositions[i]]) for i in range(len(self.FilePositions))]
				except TypeError:
					return

				if GrabIsobar == True:
					if hasattr(self, "HeadInterferenceDict"):
					
						try:
							self.MyInterferences = [float(grab[self.InterferencePositions[i]]) for i in range(len(self.InterferencePositions))]
						except TypeError:
							self.TextBox.insert(END, "\nCould not find measured interference with column header(s): ")
							self.TextBox.insert(END, [str(key) for key in self.HeadInterferenceDict])
							self.TextBox.insert(END, "In file: ")
							self.TextBox.insert(END, '\n')
							self.TextBox.insert(END,files)
							self.TextBox.insert(END, '\n')
							self.TextBox.see(END)
							return
				return
			else:
				self.Sample = []
				return

		if self.csv == True:
			grab = lines.split(",")
			if None in self.FilePositions:
					self.TextBox.insert(END, "\nFile ")
					self.TextBox.insert(END, files)
					self.TextBox.insert(END, " did not contain all your chosen column headers. \n")
					self.TextBox.insert(END, "Found: ")
					self.TextBox.insert(END, self.FilePositions)
					self.TextBox.insert(END, "\nwhere 'None' indicates missing data \n" )
					self.TextBox.see(END)
					return
			try:
				self.Sample = [float(grab[self.FilePositions[i]]) for i in range(len(self.FilePositions))]
			except TypeError:
				return


			if GrabIsobar == True:
				if hasattr(self, "HeadInterferenceDict"):
					
					try:
						self.MyInterferences = [float(grab[self.InterferencePositions[i]]) for i in range(len(self.InterferencePositions))]
					except TypeError:
						self.TextBox.insert(END, "\nCould not find measured interference with column header(s): ")
						self.TextBox.insert(END, [str(key) for key in self.HeadInterferenceDict])
						self.TextBox.insert(END, "In file: ")
						self.TextBox.insert(END, '\n')
						self.TextBox.insert(END,files)
						self.TextBox.insert(END, '\n')
						self.TextBox.see(END)
						return
						
		
	def MakeIndicies(self,line, heads, InterferenceHeads = False):
		"""
		This function takes a line of interest and finds the indexes of our column headers 
		for the data we're extracting
		"""
		if self.csv == False:
			BrokenLine = line.split(self.BreakChar)
			
		if self.csv == True:
			BrokenLine = line.split(",")
		
		IndexDictionary = {}
		self.FilePositions = [None for i in range(len(heads))]

		if InterferenceHeads == True:
			if hasattr(self, "HeadInterferenceDict"):
				
				self.InterferencePositions = [None for i in range(len(self.HeadInterferenceDict))]
				InterferenceIndex = {}

				for i, LineStuff in enumerate(BrokenLine):
					for head in self.HeadInterferenceDict:
					#	regex = r'(\s|^|$)' + head + r'(\s|^|$)'
						#match = re.search(regex, LineStuff)

						if head in LineStuff:
							if "/" in LineStuff and "/" not in head:
								pass
							else:
								InterferenceIndex.update({head:i})
				
					for i, elements in enumerate(self.HeadInterferenceDict):
						try:
							self.InterferencePositions[i] = InterferenceIndex[elements]
						except KeyError:
							self.InterferencePositions[i] = None



		# Need regular expressions to prevent matching both
		# 96Mo and 96Mo/95Mo when looking for voltages, for example.
		for i, LineStuff in enumerate(BrokenLine):
			for head in heads:
				# regex = r'\S' + head + r'$' #r'(\s|^|$)' + head + r'(\s|^|$)'
				# match = re.search(regex, LineStuff)
				# print(LineStuff)

				# This distinguishes the ratios from voltages
				if head in LineStuff:
					if "/" in LineStuff and "/" not in head:
						pass
					else:
						print(LineStuff, "SDF")
						IndexDictionary.update({head:i})

		try:
			for i, elements in enumerate(heads):
				self.FilePositions[i] = IndexDictionary[elements]
		except KeyError:
			self.FilePositions[i] = None

	def ConcentrationInput(self):
		"""
		This creates a pop up window to take input for optional concentration calculations
		"""
		#TODO: MODIFY FOR CSV
		self.PopUp = Toplevel()
		self.PopUp.wm_title("Concentration Input")
		
		# Using a canvas so we can have a scroll bar in case a directory has a lot of files in it.

		self.pcanvas = Canvas(self.PopUp, borderwidth=10)
		self.pframe = Frame(self.pcanvas)
		
		self.vsb = Scrollbar(self.PopUp, orient="vertical", command=self.pcanvas.yview)
		self.pcanvas.configure(yscrollcommand=self.vsb.set)
		self.pcanvas.configure(width=450, height=500)

		self.vsb.pack(side="right", fill="y")
		self.pcanvas.pack(side="top", fill='both', anchor=NW)
		
		self.pcanvas.create_window((4,4), window=self.pframe, tags=self.pframe, anchor='nw')
		self.pframe.bind("<Configure>", self.onFrameConfigure2)
		

		# Check to see if values already exist, that way you don't have to type them again.
		
		if hasattr(self,'DSConc'):
			pass
		else:
			self.DSConc = 0.0

		self.ConcRead = Entry(self.pframe)
		self.ConcRead.insert(0, self.DSConc)

		self.lab = Label(self.pframe,text = "Double Spike Concentration: ", font = "bold")
		self.lab.grid(row = 0, column =0)
		self.ConcRead.grid(row=0, column = 1)

		Label(self.pframe, text="").grid(row=1, column=0)
		Label(self.pframe, text="").grid(row=1, column=1)
		Label(self.pframe, text = "File Name", font = "bold").grid(row = 2, column = 0)
		Label(self.pframe, text = "Mass of spike added",font = "bold").grid(row = 2, column = 1)
		
		# Make label and entry boxes, but first count how many things we need.
		if self.csv == False:
			try:
				number = 0
				for i, files in enumerate(glob.iglob(self.dlg + '/*.exp')):
					number +=1
				self.TextBox.insert(END, "\n This window (probably) disabled until concentration input is complete. \n")
				self.TextBox.see(END)
				self.PopUp.grab_set()
			except AttributeError:
				self.TextBox.insert(END,"\n You have not chosen a directory yet.")
				self.TextBox.see(END)
				self.PopUp.grab_release()
				return
		if self.csv == True:
			
			number = 0
			f = open(self.dlg, 'r')
			try:
				for i, lines in enumerate(f.readlines()):
					if i == 0:
						continue
					else:
						number += 1
				self.TextBox.insert(END, "\n This window (probably) disabled until concentration input is complete. \n")
				self.TextBox.see(END)
				self.PopUp.grab_set()
				f.close()
			except AttributeError:
				self.TextBox.insert(END,"\n You have not chosen a CSV file yet.")
				self.TextBox.see(END)
				self.PopUp.grab_release()
				return

		if hasattr(self, 'AmtDS'):
			pass
		else:
			self.AmtDS = [0.0 for i in range(number)]
		
		if len(self.AmtDS) != number: 
			# Changed directory, refresh
			self.AmtDS = [0.0 for i in range(number)]
		
		self.EntryGrid = [None for i in range(number)]
		self.LabelGrid = [None for i in range(number)]

		# Now we're making the entry widgets. 
		if self.csv == False:
			for i, files in enumerate(glob.iglob(self.dlg + '/*.exp')):
				# WINDOWS FLIP SLASH
				myfilename  = files.split(os.path.sep)[-1]
				Label(self.pframe, text = myfilename).grid(row = i + 3, column = 0)
				self.EntryGrid[i] = Entry(self.pframe)
				self.EntryGrid[i].insert(0, self.AmtDS[i])
				self.EntryGrid[i].grid(row = i+3, column = 1)

		if self.csv == True:
			f = open(self.dlg, 'r')
			for i, lines in enumerate(f.readlines()):
					if i == 0:
						continue
					else:
						myfilename = lines.split(",")[0]
						Label(self.pframe, text=myfilename).grid(row=i+3, column=0)
						self.EntryGrid[i-1] = Entry(self.pframe)
						self.EntryGrid[i-1].insert(0, self.AmtDS[i-1])
						self.EntryGrid[i-1].grid(row = i+3, column = 1)
			f.close()




		refresh = Button(self.pframe, text = "Refresh Values", command = self.RefreshConcentration)
		refresh.grid(row = number + 4, column = 0)
		close = Button(self.pframe, text = "Finished", command = self.CloseConcentration)
		close.grid(row = number + 4, column = 1)


	def CloseConcentration(self):
		"""
		This function reads data a pop up toplevel window to read concentration data
		from the user and does not allow them to continue if they've entered a string.
		"""
		escape = True
		# If the user has entered a string, highlight the offending entry
		# widget in red. User shouldn't be able to close the window to get out
		# of it. But if they get frustrated and hit the 'x' in the corner
		# just call that value zero so it doesn't break anything later. 

		#TODO: Change this to .conifgure rather than grid.forget()

		for i in range(len(self.EntryGrid)):
			try:
				self.AmtDS[i] = self.EntryGrid[i].get()
				self.AmtDS[i] = float(self.AmtDS[i])

			except ValueError:

				self.EntryGrid[i].grid_forget()
				self.EntryGrid[i] = Entry(self.pframe, bg = "#ff0000")
				self.EntryGrid[i].insert(0,self.AmtDS[i])
				self.EntryGrid[i].grid(row = i+3, column =1)
				# In case someone decides to close it using the little 'x' 
				# non-numerical values won't break further calculations
				self.AmtDS[i] = 0.0
				escape = False

		try:
			self.DSConc = self.ConcRead.get()
			self.DSConc = float(self.DSConc)
		except ValueError:
			self.ConcRead.grid_forget()
			self.ConcRead = Entry(self.pframe, bg = "#ff0000")
			self.ConcRead.insert(0,self.DSConc)
			self.DSConc = 0.0
			self.ConcRead.grid(row=0,column=1)
			escape = False


		
		if escape == True:
			self.pframe.grab_release()
			self.TextBox.insert(END, "\n Window active. \n")
			self.TextBox.see(END)
			self.PopUp.destroy()

	def RefreshConcentration(self):
		"""
		This function rezeroes the entries of the pop-up window.
		"""
		for i, elment in enumerate(self.AmtDS):
			self.AmtDS[i] = 0.0
			self.EntryGrid[i].delete(0,END)
			self.EntryGrid[i].insert(0, self.AmtDS[i])

		self.ConcRead.delete(0,END)
		self.ConcRead.insert(0, 0.0)

	def ChooseDelta(self):
		"""
		This function allows you to choose the ratios for the delta value calculation
		"""

		self.DeltaPop = Toplevel()
		self.DeltaPop.wm_title("Choose Delta")
		if hasattr(self, 'MassList'):
			checklength = len(self.MassList)

		Label(self.DeltaPop ,text="Choose which masses to use in your delta value calculation. \n These "
			" enter as (Mass1/Mass2)^(alpha_M - alpha_S)",font = "16").grid(row =0, column=0, columnspan =2, rowspan=2)
		Label(self.DeltaPop, text = "Numerator mass",font = "16").grid(row=3, column = 0)
		Label(self.DeltaPop, text = "Denominator mass",font = "16").grid(row=3, column = 1)
		# Use masses for numerator/denominator
		self.MassList = self.Mass + [str(self.RatioMass)]
		
		for i in range(len(self.MassList)):
			self.MassList[i] = float(self.MassList[i])
		self.MassList.sort()
		
	
		NumeratorRadio = [None for i in range(len(self.MassList))]
		DenominatorRadio = [None for i in range(len(self.MassList))]

		# Don't over-write old values if they exist
		if hasattr(self,'num'):
			pass
		else:
			self.num = IntVar()
		
		if hasattr(self,'denom'):
			pass
		else:
			self.denom = IntVar()

		# This is incase someone changes the input element of the 
		# active window. Need to refresh radio button choices
		if 'checklength' in locals():
			if len(self.MassList) != checklength:
				self.num = IntVar()
				self.denom = IntVar()


		# Make radio buttons to choose masses for delta calculation. Note I'm rounding the values so people don't get
		# confused, but the calcultaion used the values placed in the "Mass" array. 
		for i, mass in enumerate(self.MassList):
			NumeratorRadio[i] = Radiobutton(self.DeltaPop, 
											text=int(round(self.MassList[i])), 
											variable=self.num, value=i,font = "16")
			
			DenominatorRadio[i] = Radiobutton(self.DeltaPop, 
											  text=int(round(self.MassList[i])), 
											  variable=self.denom, value=i,font = "16")
			
			NumeratorRadio[i].grid(row=i+4, column=0)
			DenominatorRadio[i].grid(row=i+4, column=1)

		close = Button(self.DeltaPop, text="Done", command=self.CloseChooseDelta)
		close.configure(width = 20)
		close.grid(row=len(self.MassList)+4, column=0, columnspan =2)

	def CloseChooseDelta(self):
		
		"""
		Seeing as I'll have no idea what ratio to use in delta value calculations
		for random elements, take it in as a radio button calculation. This simply chooses the 
		delta value from the radio button input.
		"""

		self.DeltaRatio = float(self.MassList[self.num.get()])/float(self.MassList[self.denom.get()])
		

		self.DeltaPop.destroy()

	def ClearTextBox(self):
		"""
		This function just clears the textbox if you have too much output.
		"""
		self.TextBox.delete('1.0', END)

	def MakeNewInputFile(self):
		"""
		This function opens a dialog for the creation of a new input file.
		It asks the user if how many rows they need, or if they'd like
		to modify an existing file.
		"""

		self.Ask = Toplevel()
		self.Ask.wm_title("New Input")

		Label(self.Ask, text = "How ratios/voltages will you \n "
	 							"have in each data file?").grid(column = 0, row = 0)



		self.NewFileColumnEntry = Entry(self.Ask)
		self.NewFileColumnEntry.configure(width = 25)
		self.NewFileColumnEntry.grid(column = 1, row = 0)
		continuebutton = Button(self.Ask, text = "Accept", command = lambda: self.AskButton(False))
		continuebutton.grid(column = 0, row = 3, columnspan = 3)

		Label(self.Ask, text = "OR").grid(column = 0, row = 4, columnspan = 3)

		modbutton = Button(self.Ask, text = "Modify Existing File", command=lambda: self.AskButton(True))
		modbutton.grid(column = 0, row = 5, columnspan = 3)
		
		self.VoltageInputFile = BooleanVar()
		self.VoltageInputFile.set(False)

		InputCheckButton = Checkbutton(self.Ask, text = "Use Voltages", variable=self.VoltageInputFile,
									   onvalue=True, offvalue=False)
		InputCheckButton.grid(column=2, row = 0)

	def AskButton(self, Modify):
		"""
		This whole function is more or less an error checker. It opens a 
		toplevel window to the specificiations of the MakeNewInputFile function
		then forces the user to sanatize the input, then it calls the 
		function which allows the new data to be saved.
		"""
		ModRatioVoltage = None
		
		if Modify == True:
			self.Ask.destroy()
		if Modify == False:

			try: 
				self.NumberOfEntryRows = int(self.NewFileColumnEntry.get())
				escape = True

			except ValueError:
				self.NewFileColumnEntry.grid_forget()
				self.NewFileColumnEntry = Entry(self.Ask, bg = "#ff0000")
				self.NewFileColumnEntry.configure(width = 25)
				self.NewFileColumnEntry.insert(0, "Require integer")
				self.NewFileColumnEntry.grid(column = 1, row = 0)
				return

			# This is so someone doesn't accidentally enter something ridiculous
			if self.NumberOfEntryRows < 2 or self.NumberOfEntryRows > 12:
				self.NewFileColumnEntry.grid_forget()
				self.NewFileColumnEntry = Entry(self.Ask, bg = "#ff0000")
				self.NewFileColumnEntry.configure(width = 25)
				self.NewFileColumnEntry.insert(0, "Require integer from 2 - 12")
				self.NewFileColumnEntry.grid(column = 1, row = 0)
				escape = False

			if escape == True:
				self.Ask.destroy()
			else:
				return

		if Modify== True:
			self.ModifyFName = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
			
			if len(self.ModifyFName) == 0:
				return
			try:
			# All this mess does is grab data from files, then place that data in widgets
			# for display and use in the GUI.

				self.GetVarFromFile(self.ModifyFName)

				ModMix = data.MixIN
				ModStand = data.StandardIN
				ModSpike = data.SpikeIN
				ModMass = data.Mass
				ModRatioMass = data.RatioMass
				ModHeads = data.isotope
		
				if hasattr(data, "RatioVoltage"):
					ModRatioVoltage = data.RatioVoltage

				self.NumberOfEntryRows = len(ModMix)
			except AttributeError:
				self.TextBox.insert(END,'\n File ')
				self.TextBox.insert(END, self.ModifyFName)
				self.TextBox.insert(END, ' was not formatted correctly for data import.')
				return
			except ImportError:
				self.TextBox.insert(END,'\n File ')
				self.TextBox.insert(END, self.ModifyFName)
				self.TextBox.insert(END, ' was not formatted correctly for data import.')
				return


		self.FileInput = Toplevel()
		self.FileInput.wm_title("New Constant File")
		
		self.newheadergrid = [None for i in range(self.NumberOfEntryRows)]
		self.newmixturegrid = [None for i in range(self.NumberOfEntryRows)]
		self.newstandardgrid = [None for i in range(self.NumberOfEntryRows)]
		self.newspikegrid = [None for i in range(self.NumberOfEntryRows)]
		self.newmassgrid = [None for i in range(self.NumberOfEntryRows)]
		self.newratiogrid = None
		

		for i in range(len(self.labels)):
			Label(self.FileInput, text=self.labels[i]).grid(column = i, row = 0)

		for i in range(self.NumberOfEntryRows):
			self.newheadergrid[i] = Entry(self.FileInput)
			self.newheadergrid[i].configure(width = 20)
			self.newheadergrid[i].grid(column=0, row = i+1)

			self.newmixturegrid[i] = Entry(self.FileInput)
			self.newmixturegrid[i].configure(width = 20)
			self.newmixturegrid[i].grid(column=1, row = i+1)
			
			self.newstandardgrid[i] = Entry(self.FileInput)
			self.newstandardgrid[i].configure(width = 20)
			self.newstandardgrid[i].grid(column=2, row = i+1)
			
			self.newspikegrid[i] = Entry(self.FileInput)
			self.newspikegrid[i].configure(width = 20)
			self.newspikegrid[i].grid(column=3, row = i+1)
			
			self.newmassgrid[i] = Entry(self.FileInput)
			self.newmassgrid[i].configure(width = 20)
			self.newmassgrid[i].grid(column=4, row = i+1)

		self.newratiogrid = Entry(self.FileInput)
		self.newratiogrid.configure(width = 20)
		self.newratiogrid.grid(column =5, row = 1)

		if self.VoltageInputFile.get() == True or ModRatioVoltage != None:

			Label(self.FileInput, text="Ratio Header").grid(column=5, row=2)
			self.newratioheader = Entry(self.FileInput)
			self.newratioheader.grid(column=5, row=4)


		if Modify == True:
			for i in range(self.NumberOfEntryRows):
				self.newheadergrid[i].insert(0, ModHeads[i])
				self.newmixturegrid[i].insert(0,ModMix[i])
				self.newstandardgrid[i].insert(0, ModStand[i])
				self.newspikegrid[i].insert(0, ModSpike[i])
				self.newmassgrid[i].insert(0, ModMass[i])

			if hasattr(self, 'newratioheader'):
				self.newratioheader.insert(0, ModRatioVoltage)
			
			self.newratiogrid.insert(0, ModRatioMass)


		FinishButton = Button(self.FileInput, text = "Create Input File", command = self.FileSave)
		FinishButton.grid(row = self.NumberOfEntryRows + 1, column = len(self.labels)-1)

	# TODO: Clean this up after the deadline for an update. This is embarassing. Although, it didint' take long to
	# write so small victories. 
	# Like it works, but in the same way a penis works if you have ED. Sure, it does the bare minimum it 
	# needs to do to keep you functioning, but you're not going to show it off to anyone. 
	
	def SaveConstantFile(self):
		"""
		This function asks the user where they'd like to save their new constants
		and what to call it. The input should be sanitized before it gets here.
		I haven't been able to break it, but if someone figures out how let me know
		and I'll do my best to fix it.
		"""

		file = filedialog.asksaveasfile(mode='w', defaultextension=".py")

		if file is None:
			return

		SaveMix = []
		SaveStand = []
		SaveSpike = []
		SaveMass = []
		SaveHead = []
		

		for i in range(len(self.newheadergrid)):
			SaveMix.append(self.newmixturegrid[i].get())
			SaveStand.append(self.newstandardgrid[i].get())
			SaveSpike.append(self.newspikegrid[i].get())
			SaveMass.append(self.newmassgrid[i].get())
			SaveHead.append(self.newheadergrid[i].get())

		SaveRatio = self.newratiogrid.get()
		file.write("RatioMass =")
		file.write(SaveRatio)
		file.write('\n')

		file.write("MixIN = [")
		for i in range(len(SaveMix)):
			file.write(SaveMix[i])
			if i != len(SaveMix)-1:
				file.write(", ")
		file.write(']\n')

		file.write("StandardIN = [")
		for i in range(len(SaveMix)):
			file.write(SaveStand[i])
			if i != len(SaveMix)-1:
				file.write(", ")
		file.write(']\n')

		file.write("SpikeIN = [")
		for i in range(len(SaveMix)):
			file.write(SaveSpike[i])
			if i != len(SaveMix)-1:
				file.write(", ")
		file.write(']\n')

		file.write("Mass = [")
		for i in range(len(SaveMix)):
			file.write(SaveMass[i])
			if i != len(SaveMix)-1:
				file.write(", ")
		file.write(']\n')

		file.write("isotope = [" )
		for i in range(len(SaveMix)):
			file.write("'")
			file.write(str(SaveHead[i]))
			file.write("'")
			if i != len(SaveMix)-1:
				file.write(", ")
		file.write(']\n')
		if hasattr(self, "newratioheader"):
			file.write("RatioVoltage = '")
			file.write(self.newratioheader.get())
			file.write("'")
			file.close()

	def FileSave(self):
		"""
		This function forces the input of the new constant file to be appropriate so that it 
		can at least be read by the program. It checks to see if everythign can be
		cast to the appropriate type, and if it can't, it puts a big angry red box around it 
		and won't do anything until the user fixes it. 
		"""

		Save = True

		# Put in matrix so we can modify the grid individually in a nested loop.

		SaveEverything = [self.newmixturegrid, self.newstandardgrid, self.newspikegrid, self.newmassgrid]

		# TODO: Clean this up when you have time after the deadline. 

		# This checks that all input is floating point where necessary and prevents the user from 
		# Saving any files until it's happy. 
		for i in range(len(SaveEverything)):
			for j in range(len(SaveEverything[i])):
				try:
					float(SaveEverything[i][j].get())
					if i == 0:
						self.newmixturegrid[j].configure(bg = "white")
					if i == 1:
						self.newstandardgrid[j].configure(bg = "white")
					if i == 2:
						self.newspikegrid[j].configure(bg = "white")
					if i == 3:
						self.newmassgrid[j].configure(bg = "white")
					
				except ValueError: 
					Save = False
					if i == 0:
						self.newmixturegrid[j].grid_forget()
						self.newmixturegrid[j] = Entry(self.FileInput, bg = "#ff0000")
						self.newmixturegrid[j].configure(width = 20)
						self.newmixturegrid[j].insert(0, SaveEverything[i][j].get())
						self.newmixturegrid[j].grid(column = i+1, row = j +1)
						escape = False
					if i == 1:
						self.newstandardgrid[j].grid_forget()
						self.newstandardgrid[j]= Entry(self.FileInput, bg = "#ff0000")
						self.newstandardgrid[j].configure(width = 20)
						self.newstandardgrid[j].insert(0, SaveEverything[i][j].get())
						self.newstandardgrid[j].grid(column = i+1, row = j +1)
						escape = False
					if i == 2:
						self.newspikegrid[j].grid_forget()
						self.newspikegrid[j]= Entry(self.FileInput, bg = "#ff0000")
						self.newspikegrid[j].configure(width = 20)
						self.newspikegrid[j].insert(0, SaveEverything[i][j].get())
						self.newspikegrid[j].grid(column = i+1, row = j + 1)
						escape = False
					if i == 3:
						self.newmassgrid[j].grid_forget()
						self.newmassgrid[j] = Entry(self.FileInput, bg = "#ff0000")
						self.newmassgrid[j].configure(width = 20)
						self.newmassgrid[j].insert(0, SaveEverything[i][j].get())
						self.newmassgrid[j].grid(column = i+1, row = j + 1)
						escape = False


		try:
			float(self.newratiogrid.get())
			self.newratiogrid.configure(bg = "white")
		except ValueError:
			Save = False
			self.newratiogrid.configure(bg = "#ff0000")

		for i in range(len(self.newheadergrid)):
			
			if len(self.newheadergrid[i].get()) == 0:
				Save = False
				self.newheadergrid[i].configure(bg = "#ff0000")
			else:
				self.newheadergrid[i].configure(bg = "white")

		if self.VoltageInputFile.get() == True:
			if len(self.newratioheader.get()) == 0:
				self.newratioheader.configure(bg="#ff0000")
				Save = False
			else:
				self.newratioheader.configure(bg='white')

		
		if Save == False:
			return

		if Save == True:
			self.SaveConstantFile()
			self.FileInput.destroy()

	def BackGroundSubtraction(self, file, AllValues = False, AlreadyHasFile = None):

		if AlreadyHasFile == None:
		
			if self.UniqueBackground.get() == True:
				mytitle = str("".join(["Background for file ", str(file)]))
				print(mytitle)
				self.BackGroundFile = filedialog.askopenfilename(filetypes=[("Thermo Exports", "*.exp")], 
			                                             title=mytitle)

				self.TextBox.insert(END, '\nWill subtract ')
				self.TextBox.insert(END,self.BackGroundFile)
				self.TextBox.insert(END, " from ")
				self.TextBox.insert(END, file)
				self.TextBox.insert(END, ". \n")
			elif self.UniqueBackground.get() == False and self.done == False:
				self.BackGroundFile = filedialog.askopenfilename(filetypes=[("Thermo Exports", "*.exp")], 
			                                             title="Choose Background File")
				self.done = True
			if self.BackGroundFile == None:
				# print("SDFSDF")
				return



		file = open(self.BackGroundFile, 'r')

		if AllValues == False:
			BackGroundHeads = self.MyHeads #+ [self.ratiovoltagegrid.get()]
		
		else: 
			BackGroundHeads = [self.headergrid[i].get() for i in range(len(self.headergrid))]
			BackGroundHeads = BackGroundHeads + [self.ratiovoltagegrid.get()]
			
		
		for lines in file:
			self.FileSearcher(lines, BackGroundHeads, file)
			if (len(self.Sample) == len(self.MyHeads)) or (len(self.Sample) == len(self.headergrid) + 1):
				subs = self.Sample
				return subs

	def CloseThisWindow(self):
		"""
		This closes the InterferenceCorrection window gracefully.
		"""
		delattr(self, 'N')
		self.InterferenceWindow.destroy()
	
	def InterferenceCorrection(self):
		"""
		This function will be used to make and associate which ratios to use 
		to correct for isobaric interferences.
		"""
		

		if hasattr(self, "N") == False:
			self.N = 0
		else:
			self.N += 1
			if self.N > 5:
				self.TextBox.insert(END, '\nCannot enter more interferences.\n')
				return
		
		if hasattr(self,'AddNewInterference') and self.N != 0:
			self.AddNewInterference.grid_forget()
		if hasattr(self, "AcceptInterferencefile") and self.N != 0:
			self.AcceptInterferencefile.grid_forget()
		

		if self.N == 0:
			try:
				self.ConstantFile = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")],
		                                                 title="Choose Constants to Assosciate")
			except FileNotFoundError:
				self.TextBox.insert(END, "\n File not found.")
				return

			self.InterferenceWindow = Toplevel()
			self.InterferenceWindow.protocol("WM_DELETE_WINDOW", self.CloseThisWindow)
			self.InterferenceWindow.wm_title("Interference Correction Maker")
			self.GetVarFromFile(self.ConstantFile)

			# I don't think it will ever hit this because if you choose wrong it defaults
			# to what it chose earlier. It's like data is a global variable or something...
			try:
				self.InterferenceHeaders = data.isotope
			except AttributeError:
				self.TextBox.insert(END, "\nThat file isn't formatted correctly")
				delattr(self, "N")
				self.InterferenceWindow.destroy()
				return

			if hasattr(data, 'RatioVoltage'):
				self.InterferenceHeaders.append(data.RatioVoltage)
			Label(self.InterferenceWindow,
		      text="Columns of interest in \n chosen data file: ").grid(row=5, column=0, rowspan=2)
			
			for i in range(len(self.InterferenceHeaders)):
				Label(self.InterferenceWindow, text=self.InterferenceHeaders[i]).grid(row=5, column=i+1)

			if self.ConstantFile == None:
				return

			self.InterferenceInFile = []
			self.AbundanceOfMeasuredInterference = []
			self.MassOfMeasuredInterference = []
			self.ListOfAbundances = []
			self.ListOfMasses = []
		
		Label(self.InterferenceWindow, text="Measured Isobar Header: ").grid(row=11*self.N, column=0)
		self.InterferenceInFile.append(Entry(self.InterferenceWindow))
		self.InterferenceInFile[self.N].grid(row=11*self.N, column=1)
		
		Label(self.InterferenceWindow, text="Abundance of Measured Isobar").grid(row=11*self.N+1, column=0)
		self.AbundanceOfMeasuredInterference.append(Entry(self.InterferenceWindow))
		self.AbundanceOfMeasuredInterference[self.N].grid(row=11*self.N+1, column=1)
		
		Label(self.InterferenceWindow, text="Mass of Measured Isobar: ").grid(row=11*self.N+2, column=0)
		self.MassOfMeasuredInterference.append(Entry(self.InterferenceWindow))
		self.MassOfMeasuredInterference[self.N].grid(row=11*self.N+2, column=1)

		# Label(self.InterferenceWindow, text="Abundance of interference").grid(row=11*self.N+4, column=0)
		Label(self.InterferenceWindow, text="Abundance of Isobar: ").grid(row=11*self.N+7, column=0)
		Label(self.InterferenceWindow, text="Mass of Isobar: ").grid(row=11*self.N+8, column=0)
		for i in range(len(self.InterferenceHeaders)):
			self.ListOfAbundances.append(Entry(self.InterferenceWindow))
			self.ListOfMasses.append(Entry(self.InterferenceWindow))

			if self.N == 0:
				self.ListOfAbundances[i].grid(row=11*self.N+7, column=i+1)
				self.ListOfMasses[i].grid(row=11*self.N+8, column=i+1)

			else:
				self.ListOfAbundances[self.N*len(self.InterferenceHeaders)+i].grid(row=11*self.N+7, column=i+1)
				self.ListOfMasses[self.N*len(self.InterferenceHeaders)+i].grid(row=11*self.N+8, column=i+1)

		Label(self.InterferenceWindow, text ="").grid(row=11*self.N+9, column =0, columnspan=len(self.InterferenceHeaders))

		# This adds a new row in case there's multiple interferences. I dont' know if this will be useful, but
		# I put it in anyways.		
		self.AddNewInterference = Button(self.InterferenceWindow, text="New Isobar", command=self.InterferenceCorrection)
		self.AddNewInterference.grid(row = 11*self.N+10, column=len(self.InterferenceHeaders)+1)

		self.AcceptInterferencefile = Button(self.InterferenceWindow, text= "Accept", command=self.MakeInterferenceFile)
		self.AcceptInterferencefile.grid(row=11*self.N+10, column=len(self.InterferenceHeaders)+2)

	def MakeInterferenceFile(self):
		"""
		This checks that input is approprate then saves the new interference file
		"""

		# First, the laborious task of making sure all the input is appropriate.
		
		for i in range(len(self.InterferenceInFile)):
			fail = False
			if self.InterferenceInFile[i].get() == "":
				self.InterferenceInFile[i].configure(bg="#ff0000")
				fail=True

			else:
				self.InterferenceInFile[i].configure(bg="white")
			
			try:
				float(self.AbundanceOfMeasuredInterference[i].get())
				self.AbundanceOfMeasuredInterference[i].configure(bg='white')

			except ValueError:
				self.AbundanceOfMeasuredInterference[i].configure(bg="#ff0000")
				fail = True
			try:
				float(self.MassOfMeasuredInterference[i].get())
				self.MassOfMeasuredInterference[i].configure(bg='white')
			except ValueError:
				self.MassOfMeasuredInterference[i].configure(bg="#ff0000")

		for i in range(len(self.ListOfAbundances)):
			# Empty things are okay
			if self.ListOfAbundances[i].get() == "":
				self.ListOfAbundances[i].configure(bg="white")
				continue
			try:
				float(self.ListOfAbundances[i].get())
				self.ListOfAbundances[i].configure(bg="white")
			except ValueError:
				self.ListOfAbundances[i].configure(bg="#ff0000")
				fail = True

			# Only care if there's a correction on that mass
			if self.ListOfAbundances[i].get() != "":
				try:
					float(self.ListOfMasses[i].get())
					self.ListOfMasses[i].configure(bg='white')
				except ValueError:
					self.ListOfMasses[i].configure(bg="#ff0000")
					fail = True

				
		# Okay so that wasn't that labourious.

		
		if fail == True:
			return

		# If the input is good, let's start building some dictionaries.
		# First, let's split all the entry chunks into their own lists.

		Abundances = ['' for i in range(len(self.ListOfAbundances))]
		for i in range(len(self.ListOfAbundances)):
			Abundances[i] = self.ListOfAbundances[i].get()

		Masses = ['' for i in range(len(self.ListOfMasses))]
		for i in range(len(self.ListOfMasses)):
			Masses[i] = self.ListOfMasses[i].get()

		if self.N == 0:
			MyAbundanceList = Abundances
			MyMassList = Masses
		else:
			width = len(self.InterferenceHeaders)
			MyAbundanceList = [Abundances[i:i+width] for i in range(0,len(Abundances), width)]
			MyMassList = [Masses[i:i+width] for i in range(0,len(Masses), width)]
		# Now, let's associate each with their own dictionary. 

		HeadInterferenceDict = {}
		HeadMassDict = {}
		for i in range(len(self.InterferenceInFile)):
			HeadInterferenceDict.update({self.InterferenceInFile[i].get():float(self.AbundanceOfMeasuredInterference[i].get())})
			HeadMassDict.update({self.InterferenceInFile[i].get():float(self.MassOfMeasuredInterference[i].get())})

		if self.N == 0:
			DictionaryList = [{}]
			MassDictionaryList = [{}]
		else:	
			DictionaryList = [{} for i in range(self.N+1)]
			MassDictionaryList = [{} for i in range(self.N+1)]

		# Associate each abundace with the ratio/voltage it will be correcting for.
		if len(DictionaryList) == 1:
			for i in range(len(self.InterferenceHeaders)):
				# Skip entries which we're not correcting for. 
				if MyAbundanceList[i] == '':
					pass
				else:
					DictionaryList[0].update({self.InterferenceHeaders[i]:float(MyAbundanceList[i])})
				if MyMassList[i] == '':
					pass
				else:
					MassDictionaryList[0].update({self.InterferenceHeaders[i]:float(MyMassList[i])})


		
		elif len(DictionaryList) > 1:
			for i in range(len(DictionaryList)):
				for j in range(len(self.InterferenceHeaders)):
					if MyAbundanceList[i][j] == '':
						pass
					else:
						DictionaryList[i].update({self.InterferenceHeaders[j]:float(MyAbundanceList[i][j])})
					if MyMassList[i][j] == "":
						pass
					else:
						MassDictionaryList[i].update({self.InterferenceHeaders[j]:float(MyMassList[i][j])})
				

		# Now, we save the interferences to a file

		import json
		file = filedialog.asksaveasfile(mode='w', defaultextension=".py")
		file.write(json.dumps(HeadInterferenceDict))
		file.write('\n')
		file.write(json.dumps(DictionaryList))
		file.write('\n')
		file.write(json.dumps(HeadMassDict))
		file.write('\n')
		file.write(json.dumps(MassDictionaryList))
		file.write('\n')
		file.close()

		# Make sure we don't get multiple correction files.
		file2 = open(self.ConstantFile, 'r+')
		Check = file2.readlines()
		file2.seek(0)
		for lines in Check:
			if "InterferenceFile = " not in lines:
				file2.write(lines)
			
		file2.truncate()
		file2.close()
		file2 = open(self.ConstantFile, 'a')

		file2.write("InterferenceFile = ")
		file2.write("'")
		file2.write(str(file.name))
		file2.write("'")
		file2.write("\n")

		self.InterferenceWindow.destroy()

		# In case someone wants to make multiple interferences at once

		delattr(self, 'N')

	def OutputSaver(self):
		"""
		This saves the contents of the text box to a text file.
		"""

		savefile = filedialog.asksaveasfile(mode='w', defaultextension=".txt")

		if savefile == None:
			return

		with open(savefile.name, 'w') as output:
			output.write(self.TextBox.get(1.0, "end-1c"))

	def ToDataBase(self):
		"""
		Excuse this mess, it was a last minute request that could have been better 
		integrated elsewhere. Basically this preps input so we can shove it into
		the database.


		"""

		CorrectPassword = 'a'
		self.password = None
		self.TextBox.delete("1.0",END)
		self.GetPassword()
		if self.password != CorrectPassword:
			self.TextBox.delete("1.0",END)
			self.TextBox.insert(END, "I can't let you do that Dave. That is not the correct password. \n")
			return
		else:
			self.TextBox.delete("1.0",END)
			self.TextBox.insert(END, "Password accepted \n")

		DataBlock = []

		try:
			DataBlock.append(self.FileVector2)
		except AttributeError:
			self.TextBox.insert(END, "You need to perform analysis before committing to database")
			return

		DataBlock.append(self.AlphaVector)
		DataBlock.append(self.BetaVector)
		DataBlock.append(self.LambdaVector)

		BulkNo = ["No" for i in range(len(self.FileVector2))]
		BulkYes = ["Yes" for i in range(len(self.FileVector2))]
		BulkNone = [None for i in range(len(self.FileVector2))]
		NotApplicable = ["N/A" for i in range(len(self.FileVector2))]
		

		

		if hasattr(self, "DeltaVector") and hasattr(self, "MassList"):
			DataBlock.append(self.DeltaVector)
			MassesUsed = str(int(round(self.MassList[self.num.get()]))) + "/" + str(int(round(self.MassList[self.denom.get()]))) 
			bulk = [str(MassesUsed) for i in range(len(self.FileVector2))]
			DataBlock.append(bulk)

		else:
			DataBlock.append(BulkNone)
			DataBlock.append(BulkNone)

		if hasattr(self, "AmtDS"):
			DataBlock.append(self.ConcentrationVector)
			DataBlock.append(self.AmtDS)
		
		else:
			DataBlock.append(BulkNone)
			DataBlock.append(BulkNone)

		if self.LeastSquares.get() == True:
			DataBlock.append(BulkYes)
		
		else:
			DataBlock.append(BulkNo)

		if hasattr(self, "InterferenceFile"):
			
			if self.IsobarCorr.get() == True and self.csv == False:
				DataBlock.append(BulkYes)
				if hasattr(self, "RatioVoltage") == False and self.MachineFractionateInterference.get() == True:
					DataBlock.append(BulkYes)
			
			elif self.IsobarCorr.get() == False and self.csv == False:
				DataBlock.append(BulkNo)
				if hasattr(self, "RatioVoltage") == False:
					DataBlock.append(BulkNo)

			if hasattr(self, "RatioVoltage"):
				DataBlock.append(NotApplicable)
		
			
		
		else:
			DataBlock.append(BulkNone)
			DataBlock.append(BulkNone)

		if hasattr(self, "RatioVoltage"):
			
			if self.DoSubtraction.get() == True:
				DataBlock.append(BulkYes)
			
			if self.DoSubtraction.get() == False:
				DataBlock.append(BulkNo)
		
		else:
			DataBlock.append(NotApplicable)

		

		DataBlock.append([self.Spike1.get() for i in range(len(self.FileVector2))])
		DataBlock.append([self.Spike2.get() for i in range(len(self.FileVector2))])
		DataBlock.append([self.Reference.get() for i in range(len(self.FileVector2))])

		# Because it's (almost) never going to be square
		NewThing = list(itertools.zip_longest(*DataBlock))

		InsertChunk(NewThing)

		self.TextBox.insert(END, "\n Successfully updated database")

	def GetPassword(self):
		self.wait_window(PasswordDialog(self))
		return self.password



class PasswordDialog(Toplevel):
    def __init__(self, parent2):
        Toplevel.__init__(self)
        self.parent2 = parent2
        self.label = Label(self,text="Please Enter Password")
        self.label.pack()
        self.entry = Entry(self, show='*')
        self.entry.bind("<KeyRelease-Return>", self.StorePassEvent)
        self.entry.pack()
        self.button = Button(self)
        self.button["text"] = "Submit"
        self.button["command"] = self.StorePass
        self.button.pack()


    def StorePassEvent(self, event):
        self.StorePass()

    def StorePass(self):
        self.parent2.password = self.entry.get()
        self.destroy()
      
        return self.parent2.password


def main():
	root = Tk()
	ex = RootWindow(root)
	#root.geometry("1200x450")
	root.mainloop()

if __name__ == '__main__':
	main()
