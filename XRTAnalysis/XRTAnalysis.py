import numpy as np
# For fitting intrinsic power law
from scipy.optimize import curve_fit
from .__deabsorb import deabsorb as deab
import matplotlib.pyplot as plt
from astropy.table import Table
from astropy import units as u
# Checking if xspec can be imported
# PyXSpec can be installed with heasoft!
try :
    import xspec
except ImportError as e:
    print ("%s\nHave you initialised heasoft?")


class XRT_Analysis():

    def __init__(self, igrouped = None):

        # Name of the pha file to be analysed
        self.grpFileName = igrouped
        if igrouped != None:
            self._initializeXSpec()

        # Model Specific things
        self.modelType = 0
        self.dof = 0
        self.chi2 = 0

        # for Swift-XRT
        self.emin = 0.3
        self.emax = 10.0

        # N_h, defaulted to galactic value
        # 2.56e20
        self.abs = "pha"
        self.nH = 2.56


        # Energy Spectral Points
        # Energy in keV
        self.energy = 0
        self.energy_err = 0
        # Observed
        # E2dnde in keV cm^-2 s^-1
        self.e2dnde = 0
        self.e2dnde_err = 0

        # Intrinsic
        # E2dnde in keV cm^-2 s^-1
        self.e2dnde_deabsorbed = 0
        self.e2dnde_err_deabsorbed = 0

        # Specific binning for the model flux estimate
        self.modelEnergy = 0
        self.model_e2dnde = 0

        self.intrinsicModel = 0
        self.fluxCorrection = 0

        # Model Handler
        self.model = 0
        self.modelType = 0
        self.modelIntrinsic = 0


        self.ifcFlux = True
        xspec.Fit.statMethod = 'chi'


    # Function to initialize XSpec
    def _initializeXSpec(self):
        # Clearing any previous states
        xspec.AllData.clear()
        xspec.AllData.show()
        # load in the group pha file
        self.spec = xspec.Spectrum(self.grpFileName)
        # For plotting
        xspec.Plot.xAxis = "kev"
        xspec.Plot.setRebin(10,10)
        # Ignoring invalid data chanels
        xspec.AllData.ignore("bad")
        xspec.AllData.ignore("**-0.3 10.-**")

        self.m1 = 0


    # Use C-Statistics in fitting
    def setCStat(self):
        xspec.Fit.statMethod = "cstat"


    # Set the grouped PHA file
    def setGroupedPHA(self, igrpFile):
        self.grpFileName = igrpFile
        self._initializeXSpec()

    # Setting the min/max of the Fit
    def setcfluxMinMax(self, emin, emax):
        self.emin = emin
        self.emax = emax


    # Define the model, asuming one is using cflux
    def setModel(self, imodel = "pwl", cflux = True, absorb = None):

        self.ifcFlux  = cflux
        if cflux:
            str_cflux = "*cflux"
        else:
            str_cflux = ""

        if absorb is None:
            # Default what ever was previously defined
            absorb = self.abs
        else:
            self.abs = absorb

        if imodel.lower() == "pwl":
            mod = "*po"
            self.modelIntrinsic = "pwl"
        elif imodel.lower() == "logpar":
            mod = "*logpar"
            self.modelIntrinsic = "logpar"

        else :
            print ("Model unknown. Feel free to add it.\n defaulting to a power law")
            self.setModel("pwl")

        # power law model
        # if imodel == "pwl":
        #     if self.ifcFlux :
        #         self.modelType = "pha*cflux*po"
        #         self.m1 = xspec.Model(self.modelType)
        #         self.m1.powerlaw.norm.frozen = True
        #     else :
        #         self.modelType = "pha*po"
        #         self.m1 = xspec.Model(self.modelType)
        self.modelType = absorb + str_cflux + mod
        self.m1 = xspec.Model(self.modelType)
        
        # # # log parabola model
        # # elif imodel == "logpar":
        # #     if self.ifcFlux :
        # #         self.modelType = "pha*cflux*logpar"
        # #         self.m1 = xspec.Model(self.modelType)
        # #         self.m1.logpar.norm.frozen = True

        # #     else :
        # #         self.modelType = "pha*logpar"
        # #         self.m1 = xspec.Model(self.modelType)
        # #         self.m1.logpar.norm.frozen = False

        # else :
        #     print ("Model unknown. Feel free to add it.\n defaulting to a power law")
        #     self.setModel("pwl")

        if imodel.lower() == "pwl":
            self.m1.powerlaw.norm.frozen = cflux
        elif imodel.lower() == "logpar":
            self.m1.logpar.norm.frozen = cflux


        if self.ifcFlux :
            self.m1.cflux.Emin = self.emin
            self.m1.cflux.Emax = self.emax
        self.setNH(self.nH)

    # Setting the Column Density
    def setNH(self, i_nH, i_fixed = True):
        self.nH = i_nH
        if (self.abs == "pha"):
            self.m1.phabs.nH = i_nH
            self.m1.phabs.nH.frozen = i_fixed
        elif (self.abs == "wabs"):
            self.m1.wabs.nH = i_nH
            self.m1.wabs.nH.frozen = i_fixed

    # Appling the fit and doing some inital Corrections
    def doFit(self):

        xspec.Fit.nIterations = 10000
        # xspec.Fit.statMethod = 'chi'
        xspec.Fit.perform()
        self.writeModel()

    '''
        With cflux we have the intrinsic integral flux and spectral parameters
        This is similar to PowerLaw2
        In the case of a PowerLaw2:

        dN/dE = N(gamma+1)E^gamma / (Emax^(gamma+1) - Emin^(gamma+1))

    '''
    def __intrinsicPowerLaw(self, energy, emin, emax, integral, index ):

        intspec = integral*(-index + 1) * energy ** (-index)
        intspec /= ( emax ** (-index +1) - emin ** (-index +1) )
        return intspec

    def __pwl(self, e, norm):
        return norm*e**(-self.index)

    # Writing results to a dictionary
    def writeModel(self):
        self.modelDict = {}

        self.modelDict["Chi2"] = xspec.Fit.statistic
        self.modelDict["DOF"] = xspec.Fit.dof

        # Plotting energy bins
        xspec.Plot("data eeufspec model")
        self.modelDict["Energy [keV]"] = np.array(xspec.Plot.x(1,2))
        self.modelDict["e2dnde [keV cm^-2 s^-1]"] = np.array(xspec.Plot.y(1,2))
        self.modelDict["Energy_err [keV]"] = np.array(xspec.Plot.xErr(1,2))
        self.modelDict["e2dnde_err [keV cm^-2 s^-1]"] = np.array(xspec.Plot.yErr(1,2))

        if self.abs == "wabs":
            d = deab(self.nH, method = "wabs")
        else:
            d = deab(self.nH)
        self.modelDict["e2dnde_deabsorbed [keV cm^-2 s^-1]"], \
        self.modelDict["e2dnde_deabsorbed_err [keV cm^-2 s^-1]"] = \
                    d.deabsorb(
                                self.modelDict["Energy [keV]"],
                                self.modelDict["e2dnde [keV cm^-2 s^-1]"],
                                self.modelDict["e2dnde_err [keV cm^-2 s^-1]"])


        if (self.modelIntrinsic == "pwl") :

            # Checking if fit is valid
            if (self.modelDict["Chi2"] / self.modelDict["DOF"] > 2. ):
                self.index = float(self.m1.powerlaw.PhoIndex)
                index_err = [0,0]

            else:
                # getting 1 sigma error instead of default 95%
                if (self.ifcFlux):
                    xspec.Fit.error("1. 4")  # cflux
                    xspec.Fit.error("1. 5")  # index
                    self.index = float(self.m1.powerlaw.PhoIndex)
                    index_err = xspec.AllModels(1)(5).error
                else:
                    xspec.Fit.error("1. 3")  # norm
                    xspec.Fit.error("1. 2")  # index
                    self.index = float(self.m1.powerlaw.PhoIndex)
                    index_err = xspec.AllModels(1)(2).error




            self.modelDict["Index"] = self.index
            self.modelDict["Index_errl"] = self.index - float(index_err[0])
            self.modelDict["Index_erru"] = float(index_err[1]) - self.index

        elif (self.modelIntrinsic == "logpar") :


            # Checking if fit is valid
            if (self.modelDict["Chi2"] / self.modelDict["DOF"] > 2. ):
                # getting 1 sigma error instead of default 95%


                alpha = float(self.m1.logpar.alpha)
                beta = float(self.m1.logpar.beta)

                alpha_err = [0,0]
                beta_err = [0,0]

            else:
                # getting 1 sigma error instead of default 95%
                xspec.Fit.error("1. 4")  # cflux
                xspec.Fit.error("1. 5")  # alpha
                xspec.Fit.error("1. 6")  # beta

                alpha = float(self.m1.logpar.alpha)
                beta = float(self.m1.logpar.beta)

                alpha_err = xspec.AllModels(1)(5).error
                beta_err = xspec.AllModels(1)(6).error

            self.modelDict["Alpha"] = alpha
            self.modelDict["Alpha_errl"] = alpha - float(alpha_err[0])
            self.modelDict["Alpha_erru"] = float(alpha_err[1]) - alpha

            self.modelDict["Beta"] = beta
            self.modelDict["Beta_errl"] = beta - float(beta_err[0])
            self.modelDict["Beta_erru"] = float(beta_err[1]) - beta


        # Getting integral flux and 1 sigma error
        if (self.ifcFlux):


            print ("Getting Flux")
            # print (np.power(10., self.m1.cflux.lg10Flux.values[0]))
            # print (np.power(10., self.m1.cflux.lg10Flux.values[0] - self.m1.cflux.lg10Flux.sigma))
            # print (np.power(10., self.m1.cflux.lg10Flux.values[0] + self.m1.cflux.lg10Flux.sigma))
            try:
                err = xspec.Fit.error("1. 4")
            
                par4 = self.m1.cflux.lg10Flux.error
                print (self.m1.cflux.lg10Flux.sigma)
                print (par4)
            except Exception as e:

                print("Problem getting error. Chi^2 greater than 2? \n\t%s"%e)
                err = -999
                par4 = [0, 0]
            # print (self.m1.cflux.lg10Flux.er)
            # print (par4.error)
            print (np.power(10., self.m1.cflux.lg10Flux.values[0]),
                    np.power(10, par4[0]),
                    np.power(10, par4[1]))

            print (self.m1.cflux.lg10Flux.sigma)
            print (self.m1.cflux.lg10Flux.values[0] + self.m1.cflux.lg10Flux.sigma)
            print (self.m1.cflux.lg10Flux.values[0] - self.m1.cflux.lg10Flux.sigma)
            self.modelDict["Flux [erg cm^-2 s^-1]"] = np.power(10., self.m1.cflux.lg10Flux.values[0])
            self.modelDict["Flux_errl [erg cm^-2 s^-1]"] = np.power(10., self.m1.cflux.lg10Flux.values[0] - self.m1.cflux.lg10Flux.sigma)
            self.modelDict["Flux_erru [erg cm^-2 s^-1]"] = np.power(10., self.m1.cflux.lg10Flux.values[0] + self.m1.cflux.lg10Flux.sigma)

        else :
            iflux = xspec.AllModels.calcFlux("2. 10.0")
            iflux_err = xspec.AllModels.calcFlux("2. 10.0 err")
            iflux_err2 = xspec.AllModels.calcFlux("2. 10.0 1 err")

            iflux = xspec.AllData(1).flux
            # iflux = float(iflux.split()[4].replace("(",""))
            # iflux_errl = float(iflux.split()[4].replace("(",""))
            # iflux_errh = float(iflux.split()[4].replace("(",""))
            self.modelDict["Flux [erg cm^-2 s^-1]"] = iflux[0]
            self.modelDict["Flux_errl [erg cm^-2 s^-1]"] = iflux[0] - iflux[1]
            self.modelDict["Flux_erru [erg cm^-2 s^-1]"] = iflux[2] - iflux[0]

        # Plotting model
        xspec.Plot("model")

        modelenergies = np.array(xspec.Plot.x(1))

        # masking out bad channels
        rangemask = ( modelenergies >= 0.3 ) & ( modelenergies <= 10.0 )

        self.modelDict["modelEnergy [keV]"] = modelenergies[rangemask]
        self.modelDict["model_e2dnde [keV cm^-2 s^-1]"] = modelenergies[rangemask] \
                                                          * modelenergies[rangemask] \
                                                          * np.array(xspec.Plot.model())[rangemask]

        # Obtaining deabsorb model
        intrinspec = d.deabsorb(self.modelDict["modelEnergy [keV]"],
                                self.modelDict["model_e2dnde [keV cm^-2 s^-1]"])


        self.modelDict["model_intrinsic_e2dnde [keV cm^-2 s^-1]"] = np.array(intrinspec[0])



    # Return the dict of results
    def getFitResults(self):
        return self.modelDict


    # Return the flux and the error
    def getFlux(self):
        # print self.
        return self.modelDict["Flux [erg cm^-2 s^-1]"], \
               self.modelDict["Flux_errl [erg cm^-2 s^-1]"], \
               self.modelDict["Flux_erru [erg cm^-2 s^-1]"]



    # Return chi^2 and NDF
    # Allow the user to check the model is sensible
    def getChi2NDF(self):
        return self.modelDict["Chi2"], \
               self.modelDict["DOF"]


    # Plot the energy Spectrum
    # bintrinsic = False, only plot the observed spectrum
    # bintrinsic = True, also plot the deabsorbed spectrum
    def plotEnergySpectrum(self, data = None, bintrinsic = True):

        if (data == None):
            tmpPlotData = self.modelDict
        else :
            print ("XRT_Analysis::plotEnergySpectrum Plotting passed data...")
            tmpPlotData = data

        # create new figure
        fig = plt.figure(figsize=(11,6))
        # Plotting energy points
        plt.errorbar(tmpPlotData["Energy [keV]"],
                     tmpPlotData["e2dnde [keV cm^-2 s^-1]"],
                     xerr = tmpPlotData["Energy_err [keV]"],
                     yerr = tmpPlotData["e2dnde_err [keV cm^-2 s^-1]"],
                     fmt = "C0o", label = "Observed Data")

        plt.plot(tmpPlotData["modelEnergy [keV]"],
                 tmpPlotData["model_e2dnde [keV cm^-2 s^-1]"],
                 "C0--", label = "Observed Model")

        plt.xlim(0.3,10.)
        plt.ylim( 0.75 * np.min(tmpPlotData["e2dnde [keV cm^-2 s^-1]"]),
                  1.75 * np.max(tmpPlotData["e2dnde [keV cm^-2 s^-1]"]) )

        if bintrinsic:
            plt.errorbar(tmpPlotData["Energy [keV]"],
                         tmpPlotData["e2dnde_deabsorbed [keV cm^-2 s^-1]"],
                         xerr = tmpPlotData["Energy_err [keV]"],
                         yerr = tmpPlotData["e2dnde_deabsorbed_err [keV cm^-2 s^-1]"],
                         fmt = "C2s", label = "Deabsorbed Data")

            plt.plot(tmpPlotData["modelEnergy [keV]"],
                     tmpPlotData["model_intrinsic_e2dnde [keV cm^-2 s^-1]"],
                     "C2--", label = "Deabsorbed Model")

            plt.ylim( 0.75 * np.min(tmpPlotData["e2dnde_deabsorbed [keV cm^-2 s^-1]"]),
                      1.75 * np.max(tmpPlotData["e2dnde_deabsorbed [keV cm^-2 s^-1]"]) )


        plt.grid(True,which="both",ls="--")
        plt.xlabel(r"Energy [keV]", fontsize = 16)
        plt.ylabel(r"E$^2$ dN/dE [keV cm$^{-2}$ s$^{-1}$]", fontsize = 16)

        plt.tick_params(axis = "both", which = "major", labelsize = "large")
        plt.tick_params(axis = "both", which = "major", length = 8)
        plt.tick_params(axis = "both", which = "minor", length = 6)

        plt.xscale('log')
        plt.yscale('log')

        plt.legend(fontsize = 16)

        return fig


    # Get fTest probability of two fits
    def fTest(self, chi2_a,  dof_a, chi2_b, dof_b ):
        return xspec.Fit.ftest(chi2_a, dof_a, chi2_b, dof_b)



    def writeSpecTable(self):

        cols = [ self.modelDict["Energy [keV]"] * u.keV,
                self.modelDict["Energy_err [keV]"] * u.keV,
                self.modelDict["e2dnde [keV cm^-2 s^-1]"] * u.keV / u.cm / u.cm / u.s ,
                self.modelDict["e2dnde_err [keV cm^-2 s^-1]"] * u.keV / u.cm / u.cm / u.s,
                self.modelDict["e2dnde_deabsorbed [keV cm^-2 s^-1]"] * u.keV / u.cm / u.cm / u.s,
                self.modelDict["e2dnde_deabsorbed_err [keV cm^-2 s^-1]"] * u.keV / u.cm / u.cm / u.s
                ]

        colnam = ["Energy", "EnergyErr", "E2dNdE", "E2dNdEErr", "E2dNdE_deabsorbed", "E2dNdEErr_deabsorbed"]

        tabl = Table(cols, names = colnam)
        return tabl
