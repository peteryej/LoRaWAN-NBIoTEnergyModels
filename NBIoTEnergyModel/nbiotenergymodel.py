
""" NB-IoT Energy Model
The code is mainly derived from the paper,
"Optimized LTE Data Transmission Procedures for IoT: Device Side Energy Consumption Analysis"
Pilar Andres-Maldonado, Pablo Ameigeiras, Jonathan Prados-Garzon, Juan J. Ramos-Munoz
and Juan M. Lopez-Soler

To understand the details of the calculation and model setup, please
refer to the paper.

It calculates the energy per bit of payload and device lifetime based
on the parameters set in the config file and specific NB-IoT transmission
settings, including the P_c, collision probability during RA procedure and P_e,
error probability during CR procedure. The results are also affected by the
data transmission rate, e.g payload size and transmission interval.

Examples:
	nbiot = NBIoTEnergyModel(t_notif=10000000)
	print 'System bandwidth %d MHz' % nbiot.BW_sys
	print 'Energy per Bit is %.3f mJ' % nbiot.calcEnergyperBit()
	print 'Total device lifetime is %.3f years' %nbiot.calcLifetime()

Peter (Jun) Ye
"""


# import libraries
import math

import config

class NBIoTEnergyModel:

	def __init__(self, pl=100, t_notif=1000000, p_c=0, p_e=0):

		self.B_data = pl # (bytes) payload
		self.B_dataCP = self.B_data+44#20 # (bytes) RRC UL transfer + NAS control plane SR + Bdata message size for CP
		self.B_compCP = self.B_dataCP#+9 # (bytes) RRC Setup Complete + NAS control plane SR + Bdata message size for CP
		# system parameters
		self.BW_sys = config.BW_sys
		self.T_RAwin = config.T_RAwin
		self.numofsymbols_PDCCH = config.numofsymbols_PDCCH
		self.format_PDCCH = config.format_PDCCH
		self.th_frag = config.th_frag
		self.numofPreambles = config.numofPreambles
		self.Wc = config.Wc
		self.P_detect = config.P_detect
		self.RAretryMax = config.RAretryMax

		# measured parameters, value varies for different NB-IoT chip
		self.Ps = config.Ps
		self.Pi = config.Pi
		self.P_rx = config.P_rx
		self.P_txMax = config.P_txMax
		self.P_txRB = config.P_txRB
		self.P_txPre = config.P_txPre
		self.T_pre = config.T_pre
		self.T_rxRA = config.T_rxRA
		self.T_rxCR = config.T_rxCR

		self.T_DRXi = config.T_DRXi
		self.T_ond = config.T_ond
		self.T_ls = config.T_ls
		self.T_i = config.T_i
		self.T_wait = config.T_wait

		self.B_RBp = config.B_RBp
		self.B_req = config.B_req
		self.B_comp = config.B_comp
		self.B_scomp = config.B_scomp
		self.B_reconfig = config.B_reconfig

		# battery setting
		self._battery = config._battery
		self._voltage = config._voltage

		self.P_c = p_c
		self.P_e = p_e
		self.IAT = t_notif
		self.R_ave = float(config.N_devices)/self.IAT # average data rate follow Poisson model


	def calcStatesProb(self):
		m = config.N_maxRAtry
		P_fail = 1.0-(1-self.P_e)*(1-self.P_c)

		P_out = P_fail**(m+1) # outage probability

		P_1_tx = math.exp(-self.R_ave*self.T_i)
		P_tx = 1.0-P_1_tx # data transmission probability before Ti expires
		self.P_a = 1.0- math.exp(-self.R_ave*(self.T_DRXi)) # transmission probability before TDRXi expires
		self.P_lc = 1.0- math.exp(-self.R_ave*(self.T_ls + self.T_ond)) # probability of transmission before Tls + Tond expires
		P_on = 1- math.exp(-self.R_ave) # probability of having uplink traffic in a subframe

		self.Nc = math.floor((self.T_i-self.T_DRXi)/(self.T_ls+self.T_ond)) # number of long DRX cycles

		# steady state probability
		k = 0 # kth backoff counter
		i = 0 # ith retransmission

		s = self.P_e*(1-self.P_c) +self.P_c
		aux = 2.0-P_tx + P_tx/(P_1_tx)*(3.0-P_tx+(1.0-self.P_a)*(1.0-(1.0-self.P_lc)**self.Nc)/self.P_lc)

		self.b_off = (1 + P_on*(1+s**(m+1)+(1-s**(m+1))*(1.0-self.P_c)/(1-s)\
		                + s*(1-s**m)*(1+self.Wc)/2/(1-s)+(1-s**(m+1))*aux))**(-1)
		self.b_00 = P_on*self.b_off
		b_i0 = (self.P_e*(1-self.P_c)+self.P_c)**i*self.b_00
		b_ik = (self.Wc-k)/self.Wc*b_i0
		b_CRi = (1-self.P_c)*b_i0
		self.b_drop = (self.P_e*(1-self.P_c)+self.P_c)**(m+1)*self.b_00

		self.b_connect = 0
		for i in range(m):
		    self.b_connect += (1-self.P_e)*(1-self.P_c)*(self.P_e*(1-self.P_c)+self.P_c)**i*self.b_00

		self.b_active = P_tx/(P_1_tx)*self.b_connect
		self.b_tx = self.b_active
		n = 0
		self.b_LCn = (1-self.P_lc)**n*(1-self.P_a)*self.b_active
		self.b_inactive = (P_1_tx)*(self.b_active+self.b_connect)

		self.N_p = self.b_connect*(1+ P_tx/P_1_tx) # number of packets sent while the device is in RRC Connected


	def calcStatesEnergy(self):
		self.calcStatesProb()
		# energy of states
		self.E_off = self.Ps
		self.E_00 = self.T_pre*self.Pi + self.T_rxRA*self.P_rx + self.P_txPre
		self.E_i0 = self.E_00
		self.E_ik = self.Pi
		self.E_CRi = self.T_rxCR*self.P_rx + self.P_txRB*(math.ceil(self.B_req/self.B_RBp)+math.ceil(self.B_compCP/self.B_RBp))
		self.E_connect = 0

		tempSum = 0
		for i in xrange(1, self.T_DRXi):
		    tempSum += math.exp(-self.R_ave*(i-1))*(1-math.exp(-self.R_ave))*i

		self.E_active = (tempSum + math.exp(-self.R_ave*(i-1))*self.T_DRXi)*self.P_rx

		tempSum = 0
		for i in xrange(1, self.T_ls+self.T_ond):
		    tempSum += math.exp(-self.R_ave*(i-1))*(1-math.exp(-self.R_ave))*i*self.Pi

		self.E_LC = tempSum+math.exp(-self.R_ave*(self.T_ls+self.T_ond-1))*(self.T_ls*self.Pi+self.T_ond*self.P_rx)

		self.E_tx = self.P_txRB *(math.ceil(self.B_dataCP/self.B_RBp))
		self.E_inactive = self.T_wait*self.P_rx
		self.E_drop = 0


	def calcEnergyperPacket(self):
		self.calcStatesEnergy()
		# calculate average energy per packet
		E_ave = (self.b_off*self.E_off+self.b_connect*self.E_connect+self.b_drop*self.E_drop+self.b_active*self.E_active+\
		              self.b_00*self.E_00+self.b_inactive*self.E_inactive+self.b_tx*self.E_tx)

		# sum of CR states average energy
		i = 0
		E_CRsum = (1-self.P_c)*self.b_00*self.E_CRi

		for i in range(1, config.N_maxRAtry+1):
		    b_i0 = (self.P_e*(1-self.P_c)+self.P_c)**i*self.b_00
		    b_CRi = (1-self.P_c)*b_i0
		    E_CRsum += b_i0*self.E_i0
		    E_CRsum += b_CRi*self.E_CRi
		    for k in xrange(self.Wc-1):
		        b_ik = (self.Wc-k)/self.Wc*b_i0
		        E_CRsum += b_ik*self.E_ik

		#sum of LC states average energy
		E_LCsum = 0

		for n in xrange(int(self.Nc)):
		    self.b_LCn = (1-self.P_lc)**n*(1-self.P_a)*self.b_active
		    E_LCsum += self.b_LCn*self.E_LC

		E_ave += E_CRsum
		E_ave += E_LCsum
		E_avePacket = E_ave/self.N_p/1000
		return E_avePacket


	def calcEnergyperBit(self):
		E_avePacket = self.calcEnergyperPacket()
		E_aveBit = E_avePacket/(self.B_data)/8
		return E_aveBit

	def calcLifetime(self):
		E_avePacket = self.calcEnergyperPacket()
		E_total = self._battery*self._voltage
		T_total = E_total*3600/E_avePacket*self.IAT/3600000/24/365
		return T_total
