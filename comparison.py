# compare energy consumption of Nb-IoT and LoRaWAN

# import libraries
import matplotlib.pyplot as plt

from LoRaWANEnergyModel.lorawanenergymodel import LoRaWANEnergyModel
from NBIoTEnergyModel.nbiotenergymodel import NBIoTEnergyModel


lorawanModel = LoRaWANEnergyModel(dr=0, ackmode=1, pl=1, p_c=0.00001, t_notif=6000000)
nbiotModel = NBIoTEnergyModel()

print "LoRaWAN total device lifetime is %.3f year" % lorawanModel.calcLifetime()
print 'NB-IoT total device lifetime is %.3f years' % nbiotModel.calcLifetime()
print "LoRaWAN energy per bit is %.3f mJ" % lorawanModel.calcEnergyperBit()
print 'Nb-IoT energy per bit is %.3f mJ' % nbiotModel.calcEnergyperBit()

N_devices = range(1, 600, 50)
Payload = range(10, 250, 10)
T_notif = [i*10**exp for exp in range(1, 5) for i in range(1, 10)]
#T_notif = range(1,26,1)
P_collision =[i*.00001 for i in range(0, 30, 1)]
DRs = range(0, 6, 1)
# DR0Lifetime = []
# DR5Lifetime = []
# DR0MaxPLLifetime = []
DR5MaxPLLifetime = []
loraWANLifetime = []
loraWANEnergy20 = []
loraWANEnergy200 = []
loraWANCapacity1Min = []
loraWANCapacity10Min = []
loraWANCapacity100Min = []
loraWANCapacity1000Min = []
nbiotLifetime = []
nbiotEnergy20 = []
nbiotEnergy200 = []
notifPeriod = 60000
#for P_c in P_collision:
#for devices in N_devices:
#for payload in Payload:
for notifPeriod in T_notif:
#for DR in DRs:

    # lorawanModelDR0 = LoRaWANEnergyModel(dr=0, ackmode=1, pl=1, p_c=0.00001, t_notif=notifPeriod*60000)
    # lorawanModelDR5 = LoRaWANEnergyModel(dr=5, ackmode=1, pl=1, p_c=0.00001, t_notif=notifPeriod*60000)
    # lorawanModelDR0MaxPL = LoRaWANEnergyModel(dr=0, ackmode=1, pl=51, p_c=0.00001, t_notif=notifPeriod*60000)
    # lorawanModelDR5MaxPL = LoRaWANEnergyModel(dr=5, ackmode=1, pl=242, p_c=0.00001, t_notif=notifPeriod*60000)
    # loraWANModel1Min = LoRaWANEnergyModel(dr=DR, ackmode=1, pl=50, N_dev=1, p_c=0, t_notif=notifPeriod)
    # loraWANModel10Min = LoRaWANEnergyModel(dr=DR, ackmode=1, pl=50, N_dev=1, p_c=0, t_notif=notifPeriod*10)
    # loraWANModel100Min = LoRaWANEnergyModel(dr=DR, ackmode=1, pl=50, N_dev=1, p_c=0, t_notif=notifPeriod*100)
    loraWANModel200 = LoRaWANEnergyModel(dr=5, ackmode=1, pl=200, N_dev=1, p_c=0, t_notif=notifPeriod*1000)
    nbiotModel200 = NBIoTEnergyModel(pl=200, t_notif=notifPeriod*1000, p_e=0, p_c =0)
    loraWANModel20 = LoRaWANEnergyModel(dr=5, ackmode=1, pl=20, N_dev=1, p_c=0, t_notif=notifPeriod*1000)
    nbiotModel20 = NBIoTEnergyModel(pl=20, t_notif=notifPeriod*1000, p_e=0, p_c =0)
    # loraWANModel = LoRaWANEnergyModel(dr=5, ackmode=1, pl=200, p_c=0, t_notif=notifPeriod*1000)

    # DR0Lifetime.append(lorawanModelDR0.calcLifetime())
    # DR5Lifetime.append(lorawanModelDR5.calcLifetime())
    # DR0MaxPLLifetime.append(lorawanModelDR0MaxPL.calcLifetime())
    # DR5MaxPLLifetime.append(lorawanModelDR5MaxPL.calcLifetime())
    nbiotEnergy20.append(nbiotModel20.calcLifetime())
    loraWANEnergy20.append(loraWANModel20.calcLifetime())
    nbiotEnergy200.append(nbiotModel200.calcLifetime())
    loraWANEnergy200.append(loraWANModel200.calcLifetime())
    # nbiotEnergy200.append(nbiotModel200.calcEnergyperBit())
    # loraWANEnergy200.append(loraWANModel200.calcEnergyperBit())
    # nbiotEnergy20.append(nbiotModel20.calcEnergyperBit())
    # loraWANEnergy20.append(loraWANModel20.calcEnergyperBit())
    # loraWANCapacity1Min.append(loraWANModel1Min.calcAlohaCapcity())
    # loraWANCapacity10Min.append(loraWANModel10Min.calcAlohaCapcity())
    # loraWANCapacity100Min.append(loraWANModel100Min.calcAlohaCapcity())
    # loraWANCapacity1000Min.append(loraWANModel1000Min.calcAlohaCapcity())



# plt.plot(T_notif, DR0Lifetime, 'ro-', label='LoRAWAN DR0 1 byte')
# plt.plot(T_notif, DR5Lifetime, 'go-', label='LoRAWAN DR5 1 byte')
# plt.plot(T_notif, DR0MaxPLLifetime, 'rD-', label='LoRAWAN DR0 MaxPL')
# plt.plot(T_notif, DR5MaxPLLifetime, 'go-', label='LoRAWAN DR5')
#plt.plot(N_devices, nbiotLifetime, 'yx-', label='NB-IoT')
#plt.plot(N_devices, loraWANLifetime, 'go-', label='LoRaWAN DR5')
#plt.plot(P_collision, loraWANLifetime, 'go-', label='LoRaWAN DR5, PL 100 bytes,\nT_notif 1h, with acknowledgement')
# plt.plot(DRs, loraWANCapacity1Min, 'go-', label='T_notif 1 Min')
# plt.plot(DRs, loraWANCapacity10Min, 'ro-', label='T_notif 10 Min')
# plt.plot(DRs, loraWANCapacity100Min, 'yo-', label='T_notif 100 Min')
# plt.plot(DRs, loraWANCapacity1000Min, 'bo-', label='T_notif 1000 Min')
#plt.plot(T_notif, nbiotLifetime, 'yx-', label='NB-IoT')
#plt.plot(P_collision, nbiotLifetime, 'yx-', label='NB-IoT')
#plt.plot(T_notif, loraWANLifetime, 'go-', label='LoRaWAN DR5')
plt.plot(T_notif, nbiotEnergy20, 'yx-', label='NB-IoT 20 bytes')
plt.plot(T_notif, loraWANEnergy20, 'gx-', label='LoRaWAN DR5 20 bytes')
plt.plot(T_notif, nbiotEnergy200, 'yo-', label='NB-IoT 200 bytes')
plt.plot(T_notif, loraWANEnergy200, 'go-', label='LoRaWAN DR5 200 bytes')
plt.xlabel('Notification Period (s)')
#plt.xlabel('Collision Probability')
#plt.xlabel('Number of Devices in One Gateway')
# plt.xlabel('Data Rate')
# plt.ylabel('Number of Devices in One Gateway')
plt.ylabel('Device lifetime (year)')
#plt.xlabel('Payload (bytes)')
#plt.ylabel('Energy/bit (mJ)')
plt.xscale('log')
#plt.yscale('log')
#plt.title('LoRaWAN Capacity vs Data Rate')
#plt.title('Device lifetime vs. Collision Probability')
#plt.title('Device lifetime vs. Number of Devices')
plt.title('Device lifetime vs. Notification Period')
#plt.title('Energy/Bit vs. Payload Size with Notification Period of 200 s')
#plt.title('Energy/Bit vs. Notification Period')
#plt.figtext(0, 0, '*the setting is PL 200 bytes, P_c 0' )
#use 6 125-KHz Channels with acknowledgement mode', horizontalalignment='left')
plt.ylim(-5, 100)
# plt.xlim(7, 2*10**4)
plt.legend()
plt.show()
