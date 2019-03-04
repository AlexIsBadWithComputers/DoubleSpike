"""
This solver implements the double spike equations from the
double-spike toolbox. Other places too, but that's the most popular
reference. Code by Alex Tennant.
Questions to alexpattennant@gmail.com
"""
import numpy as np
from numpy import warnings
from scipy.optimize import fsolve
from scipy.optimize import least_squares
import math

def UseAnneal(Sample, Spike, Standard, Mass, RatioMass, p):
	# print(Sample)
	# print()
	# print(Spike)
	# print()
	# print(Standard)
	# print()
	# print(Mass)
	# print()
	# print(p)
	# print() 

	def equation(x):
		equation = np.array([Standard[i]*(Mass[i]/RatioMass)**(-x[0])*x[2]+
						Spike[i]*(1-x[2])-
						Sample[i]*(Mass[i]/RatioMass)**(-x[1]) for i in range(len(Spike))])
		return equation

	try:
		Result = least_squares(lambda x: equation(x),x0=p)
		x = Result.x
		success = True
		alpha = x[0]
		beta = x[1]
		lamb = x[2]
		return alpha, beta, lamb, success
	except RuntimeWarning:
		alpha= "NoConvergence"
		beta = "No Convergence"
		lamb = "No Convergence"
		success = False
			
		return alpha, beta, lamb, success




def DSpikeSolve(Sample, Spike, Standard, Mass, RatioMass, Anneal=False):

	
	"""
	This solves the non-linear double spike equations and uses
	the linearized method as an intial guess at the system

	Sample is the ratios of the measured sample
	Spike is the known spike ratios,
	Standard is the known standard ratios
	Mass is the known mass of the element,
	Ratio mass is the mass of the denominator in the ratio,
	AmtDS is an optional paramenter of the amount of double spike added
	to calculate concentration of sample by isotope dilution
	"""

	# Linear system first

	A = np.matrix(
		        [[Spike[i] - Standard[i], 
		           -Standard[i] * math.log(Mass[i]/RatioMass), 
		           Sample[i] * math.log(Mass[i]/RatioMass)] for i in range(len(Spike))])

	b = np.array([Sample[i] - Standard[i] for i in range(len(Spike))])
	x = np.linalg.solve(A,b)
	x1 = [x.item(0),x.item(1),x.item(2)]
		# Initial guess
	p = [(x1[1]/(1-x1[0])),x1[2],1-x1[0]]  
	
	# Double Spike equations
	def equation(x):
		equation = np.array([Standard[i]*(Mass[i]/RatioMass)**(-x[0])*x[2]+
						Spike[i]*(1-x[2])-
						Sample[i]*(Mass[i]/RatioMass)**(-x[1]) for i in range(len(Spike))])
		return equation
		
	warnings.simplefilter("error", RuntimeWarning)

	try: 
		# Begin root finding
		
		alpha,beta,lamb = fsolve(lambda x: equation(x),x0=p,xtol=1e-10, maxfev= 10000, factor = 0.5)
		success = True
	
		print(Sample, "I AM SAMPLE")
		print(Standard, "I AM STANDARD")
		print(Spike, "I AM SPIKE")
		print(p, "I AM INITIAL")
		print()
		return alpha, beta, lamb, success
	
	except RuntimeWarning:
		alpha = "No Convergence"
		beta = "No Convergence"
		lamb = "No Convergence"
		success = False
			
		return alpha, beta, lamb, success




def ConcentrationCalculation(alpha, alpha2, Standard, Spike, Mass, RatioMass, ADS, PercentSpike):

	# Add up ratios of standard and spike to calculate our
	# own molar mass.
	S = 1.0
	T = 1.0
	Sample = [0 for i in range(len(Standard))]

	for i in range(len(Standard)):
		S += float(Standard[i])
		T += float(Spike[i])
		Sample[i] = float(Standard[i]) * (float(Mass[i])/float(RatioMass)) ** (-(alpha - alpha2))

	P = [0 for i in range(len(Standard) + 1)]
	for i in range(len(Standard)):
		P[i] = Sample[i] / S

	P[-1] = 1/S

	# Atomic weight
	AW = 0.0 
	for i in range(len(P)-1):
		AW += P[i] * float(Mass[i])
	AW += P[-1] * float(RatioMass)

	# Atomic weight of spike

	DSAW = 0.0
	for i in range(len(Spike)):
		DSAW += float(Spike[i]) * float(Mass[i]) / T
	DSAW += RatioMass / T

	try:
		concentration = (ADS/DSAW) * (1/(PercentSpike ) - 1) * AW
	except RuntimeWarning:
		concentration = "DivByZero"


	return concentration











