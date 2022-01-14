'''
	Deabsorb x-ray flux for extinction
	Original c++ code provided by Amy
	Shamelessly copyied...
	Translated to python with no secondary checks... use at own risk
'''

import numpy as np



class deabsorb():

	def __init__(self, nH, method = "pha"):
		self.nH = nH
		self.method = method


	def deabsorb(self, en, flux, flux_err = None):
		n = len(flux)
		if flux_err is None:
			flux_err = np.zeros(n)

		unabs_flux = np.zeros(n)
		unabs_flux_err = np.zeros(n)
		if self.method == "pha":
			cross = self.sigma
		elif self.method == "wabs":
			cross = self.get_w_crossec

		for i in range(n):
			unabs_flux[i] = flux[i]*np.exp(self.nH*(1.e22)*cross(en[i]))
			unabs_flux_err[i] = flux_err[i]*np.exp(self.nH*(1.e22)**cross(en[i]))

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


	def pl_abs(self, E, K, alpha, nH, E_norm=1):
		#E has to be in keV
		return np.exp(-nH*self.get_w_crossecs(E)) * K*(E/E_norm)**(-alpha)

	def pl_abs_SED(self, E, K, alpha, nH, E_norm=1):
		#E has to be in keV
		return (np.exp(-nH*self.get_w_crossecs(E)) * K*(E/E_norm)**(-alpha))*E*E*1.6022e-9


	def pl_deabs(self, E, F, dF, nH):
		#E has to be in keV; deabsorption
		return np.exp(nH*self.get_w_crossecs(E)) * F,
		np.exp(nH*get_w_crossecs(E)) * dF



	#Wisconsin photo-electric cross section:
	def crossec(self, c0, c1, c2, E):
		#E has to be in keV, return cm^2
		value=(c0+c1*E+c2*E*E)/E/E/E*1.0e-24
		return value

	def get_w_crossec(self, e):
		#E has to be in keV
		if (e >= 0.03) and (e < 0.1):
			crosssetion = self.crossec(17.3, 608.1, -2150.0, e)
		elif (e >= 0.1) and (e < 0.284):
			crosssetion = self.crossec(34.6, 267.9, -476.1, e)
		elif (e >= 0.284) and (e < 0.4):
			crosssetion = self.crossec(78.1, 18.8, 4.3, e)
		elif (e >= 0.4) and (e < 0.532):
			crosssetion = self.crossec(71.4, 66.8, -51.4, e)
		elif (e >= 0.532) and (e < 0.707):
			crosssetion = self.crossec(95.5, 145.8, -61.1, e)
		elif (e >= 0.707) and (e < 0.867):
			crosssetion = self.crossec(308.9, -380.6, 294.0, e)
		elif (e >= 0.867) and (e < 1.303):
			crosssetion = self.crossec(120.6, 169.3, -47.7, e)
		elif (e >= 1.303) and (e < 1.84):
			crosssetion = self.crossec(141.3, 146.8, -31.5, e)
		elif (e >= 1.84) and (e < 2.471):
			crosssetion = self.crossec(202.7, 104.7, -17.0, e)
		elif (e >= 2.471) and (e < 3.21):
			crosssetion = self.crossec(342.7, 18.7, 0.0, e)
		elif (e >= 3.21) and (e < 4.038):
			crosssetion = self.crossec(352.2, 18.7, 0.0, e)
		elif (e >= 4.038) and (e < 7.111):
			crosssetion = self.crossec(433.9, -2.4, 0.75, e)
		elif (e >= 7.111) and (e < 8.331):
			crosssetion = self.crossec(629.0, 30.9, 0.0, e)
		elif (e >= 8.331) and (e <= 10.0):
			crosssetion = self.crossec(701.2, 25.2, 0.0, e)
		else:
			crosssetion = 0
		return crosssetion