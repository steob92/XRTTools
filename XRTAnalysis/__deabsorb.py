'''
	Deabsorb x-ray flux for extinction
	Original c++ code provided by Amy
	Shamelessly copyied...
	Translated to python with no secondary checks... use at own risk
'''

import numpy as np



class deabsorb():

	def __init__(self, nH):
		self.nH = nH


	def deabsorb(self, en, flux, flux_err = None):
		n = len(flux)
		if flux_err is None:
			flux_err = np.zeros(n)

		unabs_flux = np.zeros(n)
		unabs_flux_err = np.zeros(n)

		for i in range(n):
			unabs_flux[i] = flux[i]*np.exp(self.nH*(1.e22)*self.sigma(en[i]))
			unabs_flux_err[i] = flux_err[i]*np.exp(self.nH*(1.e22)**self.sigma(en[i]))

		return unabs_flux, unabs_flux_err


	def sigma(self, energy):
		c0 = 0
		c1 = 0
		c2 = 0

		if(energy<=0.4):
			c0 = 78.1
			c1 = 18.8
			c2 = 4.3

		elif(0.4<energy<=0.532):
			c0 = 71.4
			c1 = 66.8
			c2 = -51.4

		elif(0.532<energy<=0.707):
			c0 = 95.5
			c1 = 145.8
			c2 = -61.1

		elif(0.707<energy<=0.867):
			c0 = 308.9
			c1 = -380.6
			c2 = 294.0

		elif(0.867<energy<=1.303):
			c0 = 120.6
			c1 = 169.3
			c2 = -47.7

		elif(1.303<energy<=1.840):
			c0 = 141.3
			c1 = 146.8
			c2 = -31.5

		elif(1.840<energy<=2.471):
			c0 = 202.7
			c1 = 104.7
			c2 = -17.0

		elif(2.471<energy<=3.210):
			c0 = 342.7
			c1 = 18.7
			c2 = 0.0

		elif(3.210<energy<=4.038):
			c0 = 352.2
			c1 = 18.7
			c2 = 0.0

		elif(4.038<energy<=7.111):
			c0 = 433.9
			c1 = -2.4
			c2 = 0.75

		elif(7.111<energy<=8.331):
			c0 = 629.0
			c1 = 30.9
			c2 = 0.0

		elif(8.331<energy<=10.0000):
			c0 = 701.2
			c1 = 25.2
			c2 = 0.0

		# For model fit this just generates a load of junk output
		# else:
		#	print("Out of Range!")

		sig = (c0+c1*energy+c2*energy*energy)
		sig /= (energy*energy*energy)
		sig *= 1.e-24

		return sig
		# return ((c0+c1*energy+c2*energy*energy)/(energy*energy*energy))*TMath::Power(10,-24)
