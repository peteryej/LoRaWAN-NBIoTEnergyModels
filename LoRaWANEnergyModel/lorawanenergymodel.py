
""" LoRaWAN Energy Model
The code is mainly derived from the paper,
"Modeling the Energy Performance of LoRaWAN"
Lluis Casals ID , Bernat Mir ID , Rafael Vidal ID and Carles Gomez

To understand the details of the calculation and model setup, please
refer to the paper.

It calculates the energy per bit of payload and device lifetime based
on the parameters set in the config file and specific LoRa transmission
settings, including SF, BW, CR. The results are also affected by the
data transmission rate, e.g payload size and transmission interval.

Note:
	LoRaWAN Data Rate setting is EU specific

Examples:
	lora = LoRaWANEnergyModel(dr=0, ackmode=1, pl=1, p_c=0, t_notif=6000000)
	print lora._SF
	print lora._BW
	print "Expected data delivered is %d bytes" % lora.getdataDelivered()
	print "Average current is %.3f mA" % lora.calcAveCurrent()
	print "Total device lifetime is %.3f year" % lora.calcLifetime()
	print "Energy per bit is %.3f mJ" % lora.calcEnergyperbit()

Peter (Jun) Ye
"""


# import libraries
import math
import random

import config

class LoRaWANEnergyModel:

	def __init__(self, dr=3, cr=.8, pl=3, t_notif=3600000, p_c=.0001, ackmode=1):
		assert(dr <= 6 and dr >= 0), "DR values only from 0 to 6 are supported"
		self.DR = dr 		# data rate
		if self.DR <= 5:
			self._SF = 12 - self.DR   # valid values are 7,8,9,10,11,12
			self._BW = 125   # (KHz)
		elif self.DR == 6:
			self._SF = 7
			self._BW = 250   # (KHz)
		self._CR = cr   # 4/5, 4/6, 4/7, 4/8
		self._PL = pl   # (bytes) max 242 for SF 7-8, 115 for SF 9, 51 for SF 10-12
		self._acknowledgement = ackmode # 1 for with acknowledgement, 0 for wihtout ack
		self.P_c = p_c  # collision probability
		self.T_notif = t_notif

		self.I_sleep  		= config.I_sleep # all current value is in mA
		self.I_wakeup 		= config.I_wakeup
		self.I_radioPrep 	= config.I_radioPrep
		self.I_trans 		= config.I_trans
		self.I_delay1	 	= config.I_delay1
		self.I_delay2 		= config.I_delay2
		self.I_recv1 		= config.I_recv1
		self.I_recv2 		= config.I_recv2
		self.I_radioOff 	= config.I_radioOff
		self.I_postproc 	= config.I_postproc
		self.I_turnoff 		= config.I_turnoff

		self.T_wakeup 		= config.T_wakeup  # all time value is in ms
		self.T_radioPrep 	= config.T_radioPrep
		self.T_radioOff 	= config.T_radioOff
		self.T_postproc 	= config.T_postproc
		self.T_turnoff 		= config.T_turnoff

		# battery setting
		self._battery 		= config._battery # (mAh)
		self._voltage 		= config._voltage # (V)

		# LoRaWAN setting
		self.CRC 			= config.CRC    # wheather cyclic redundancy check
		 								    # exists in physical layer message
		self.BER 			= config.BER      # bit error rate
		self.receive_delay1 = config.receive_delay1  # (ms)
		self.receive_delay2 = config.receive_delay2  # (ms)
		self.numofPreambleSymbols = config.numofPreambleSymbols

		self.T_txMin = {12:991.8, 11:577.5, 10:288.7, 9:144.4, 8:72.2, 7:41.2}

		assert(self._SF <= 12 and self._SF >= 7), "valid SF values are 7,8,9,10,11,12"

		if self._SF > 9:
		    assert(self._PL <= 51), "max PL bytes 242 for SF 7-8, 115 for SF 9, 51 for SF 10-12"
		elif self._SF > 8:
		    assert(self._PL <= 115), "max PL bytes 242 for SF 7-8, 115 for SF 9, 51 for SF 10-12"
		elif self._SF > 6:
		    assert(self._PL <= 242), "max PL bytes 242 for SF 7-8, 115 for SF 9, 51 for SF 10-12"

		if (self._SF>10):
		    self.DE = 1  # drift correction is used
		    self.numofRecvSymbols = 8
		else:
		    self.DE = 0 # drift correction is not used
		    self.numofRecvSymbols = 12


		self.physicalPL = self._PL +13
		self.totalData = self.physicalPL + 2*self.CRC + 2.5

		self.numofMessageSymbols = 8 + max(math.ceil((28+8*self.physicalPL+16*\
								self.CRC-4*self._SF)/float(4*(self._SF-2*\
								self.DE)))*(self._CR+4), 0)
		self.timeperSymbol = float(2**self._SF)/self._BW
		self.timeofPreamble = (self.numofPreambleSymbols+4.25)*self.timeperSymbol
		self.timeofMessage = self.numofMessageSymbols*self.timeperSymbol

		self.dataDelivered = self._PL*((1-self.BER)**(self.totalData))*(1-self.P_c)


		self.T_trans = self.timeofMessage+self.timeofPreamble  # measured 52 ms
		self.T_delay1 = self.receive_delay1
		self.T_recv1 = self.timeperSymbol*self.numofRecvSymbols # measured 24 ms
		self.T_delay2 = 1000 - self.T_recv1
		self.T_recv2 = float(2**self._SF+32)/self._BW
		self.T_recv2NoAck = self.T_recv2

		self.I_ack1 = 0
		self.T_active1 = 0
		self.I_ack2 = 0
		self.T_active2 = 0


	def calcAveCurrentandActiveTime(self, T_recv1=None, T_recv2=None,\
								T_radioOff = None,I_delay2 = None,T_delay2 = None ):
		if T_recv1 == None:
			T_recv1 = self.T_recv1
		if T_recv2 == None:
			T_recv2 = self.T_recv2
		if T_radioOff == None:
			T_radioOff = self.T_radioOff
		if T_delay2 == None:
			T_delay2 = self.I_delay2
		if I_delay2 == None:
			I_delay2 = self.T_delay2

		# calculate average current per notification without acknowledgement
		T_active = self.T_wakeup + self.T_radioPrep + self.T_trans + \
						self.T_delay1 + T_delay2 + T_recv1 + T_recv2 +\
		             	T_radioOff + self.T_postproc + self.T_turnoff

		T_sleep = self.T_notif - T_active

		I_aveNotif = (self.T_wakeup*self.I_wakeup + self.T_radioPrep*self.I_radioPrep +\
		 			self.T_trans*self.I_trans + self.T_delay1*self.I_delay1 + \
					T_delay2*I_delay2 + T_recv1*self.I_recv1 +\
		            T_recv2*self.I_recv2 + T_radioOff*self.I_radioOff +\
					self.T_postproc*self.I_postproc + self.T_turnoff*self.I_turnoff +\
					T_sleep*self.I_sleep)/self.T_notif
		return I_aveNotif, T_active


	def calcACandAT(self, ackmode):
		if (ackmode):
			self.I_ack1, self.T_active1 = self.calcAveCurrentandActiveTime(T_recv1=self.T_txMin[self._SF],\
										T_recv2=0, T_radioOff = config.T_radioOffAck,\
										I_delay2 = self.I_radioOff, T_delay2 = 0)
			self.I_ack2, self.T_active2 = self.calcAveCurrentandActiveTime(T_radioOff=config.T_radioOffAck,\
										T_recv2 = self.T_txMin[self._SF])

			I_aveNotif = config.P_recv1*self.I_ack1 + config.P_recv2*self.I_ack2
			T_active = config.P_recv1*self.T_active1 + config.P_recv2*self.T_active2
		else:
			I_aveNotif, T_active = self.calcAveCurrentandActiveTime()

		return I_aveNotif, T_active

	def calcAveCurrent(self):
		if (self._acknowledgement):
			I_aveNotif = self.calcAveCurrentAck()
		else:
			I_aveNotif, T_active = self.calcACandAT(ackmode=0)
		return I_aveNotif

	def calcAveCurrentAck(self):
		random.seed()

		k = 0  # number of retransmissions
		numofRetransMax = config.numofRetransMax # default is set as 7

		totalDataAmt = self.physicalPL + 4.5  # (bytes)
		totalAckAmt = 14.5 # (bytes)

		P_dataErr = self.P_c + (1-self.P_c)*(1-(1-self.BER)**totalDataAmt)
		P_1winErr = config.P_recv1*(1-P_dataErr)*(1-(1-self.BER)**totalAckAmt)
		P_2winErr = config.P_recv2*(1-P_dataErr)*(1-(1-self.BER)**totalAckAmt)

		P_0 = ((1-self.BER)**totalDataAmt)**((1-self.BER)**totalAckAmt)*(1-self.P_c) # probablility without retransmission
		P_k = ((1-P_0)**k)*P_0

		I_ackTO = self.I_delay1
		T_ackTO = random.randint(1000,3000)

		I_aveNotifAck, T_activeAck = self.calcACandAT(ackmode=1)
		# print I_aveNotifAck, T_activeAck
		I_aveNotifNoAck, T_activeNoAck = self.calcACandAT(ackmode=0)
		# print I_aveNotifNoAck, T_activeNoAck

		T_ok = T_activeAck
		I_ok = (I_aveNotifAck*self.T_notif-(self.T_notif-T_ok)*self.I_sleep)/T_ok

		I_dataErr = I_aveNotifNoAck
		I_1winErr = (self.I_ack1*self.T_notif-(self.T_notif-T_ok)*self.I_sleep)/T_ok
		I_2winErr = (self.I_ack2*self.T_notif-(self.T_notif-T_ok)*self.I_sleep)/T_ok

		T_dataErr = T_activeNoAck
		T_1winErr = self.T_active1
		T_2winErr = self.T_active2


		T_act = 0
		I_act = 0
		Topsumk =0
		Bottomsumk =0
		self.dataDelivered = 0
		for k in range(numofRetransMax):
			for i in range(k):
			    Topsumk += (I_ackTO*(T_ackTO-self.T_recv2NoAck)+(I_dataErr*T_dataErr*P_dataErr + I_1winErr*T_1winErr*P_1winErr \
			                                                + I_2winErr*T_2winErr*P_2winErr)/(P_dataErr+P_1winErr+P_2winErr))
			    Bottomsumk += (T_ackTO-self.T_recv2NoAck)+(T_dataErr*P_dataErr+T_1winErr*P_1winErr+T_2winErr*P_2winErr)/ \
			                                                (P_dataErr+P_1winErr+P_2winErr)

			P_k = ((1-P_0)**k)*P_0
			T_k = T_ok+Bottomsumk
			I_k = (I_ok*T_ok+Topsumk)/T_k
			I_act += I_k*P_k
			T_act += T_k*P_k
			self.dataDelivered += (((1-self.P_c)*(1-(1-self.BER)**self.totalData)+self.P_c)**k)*\
									(1-self.P_c)*(1-self.BER)**self.totalData
			Topsumk = 0
			Bottomsumk = 0

		self.dataDelivered += self._PL*self.dataDelivered
		I_aveAck = (I_act*T_act+self.I_sleep*(self.T_notif-T_act))/self.T_notif
		return I_aveAck

	def getdataDelivered(self):
		if (self._acknowledgement):
			self.calcAveCurrentAck()
		return self.dataDelivered

	def calcEnergyperbit(self):
		I_aveNotif = self.calcAveCurrent()
		E_perBit = I_aveNotif*self._voltage*self.T_notif/self.dataDelivered/1000.0/8.0
		return E_perBit

	def calcLifetime(self):
		I_aveNotif = self.calcAveCurrent()
		T_lifetime = self._battery/I_aveNotif/24.0/365.0
		return T_lifetime
