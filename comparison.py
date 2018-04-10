# compare energy consumption of Nb-IoT and LoRaWAN

# import libraries
import matplotlib.pyplot as plt

from LoRaWANEnergyModel.lorawanenergymodel import LoRaWANEnergyModel
from NBIoTEnergyModel.nbiotenergymodel import NBIoTEnergyModel


lorawanModel = LoRaWANEnergyModel(dr=0, ackmode=1, pl=1, p_c=0.00001, t_notif=6000000)
nbiotModel = NBIoTEnergyModel()

print "LoRaWAN total device lifetime is %.3f year" % lorawanModel.calcLifetime()
print 'NB-IoT total device lifetime is %.3f years' % nbiotModel.calcLifetime()
print "LoRaWAN energy per bit is %.3f mJ" % lorawanModel.calcEnergyperbit()
print 'Nb-IoT energy per bit is %.3f mJ' % nbiotModel.calcEnergyperBit()

#T_notif = range(.1, 25*60, 10)
T_notif = [i*10**exp for exp in range(-1, 3) for i in range(1, 10)]
DR0Lifetime = []
DR5Lifetime = []
for notifPeriod in T_notif:
    lorawanModelDR0 = LoRaWANEnergyModel(dr=0, ackmode=1, pl=1, p_c=0.00001, t_notif=notifPeriod*60000)
    lorawanModelDR5 = LoRaWANEnergyModel(dr=5, ackmode=1, pl=1, p_c=0.00001, t_notif=notifPeriod*60000)
    DR0Lifetime.append(lorawanModelDR0.calcLifetime())
    DR5Lifetime.append(lorawanModelDR5.calcLifetime())


plt.plot(T_notif, DR0Lifetime, 'r+-', label='LoRAWAN DR0')
plt.plot(T_notif, DR5Lifetime, 'go-', label='LoRAWAN DR5')
plt.xlabel('Notification Period (min)')
plt.ylabel('Device lifetime (year)')
plt.xscale('log')
plt.title('Device lifetime vs. Notification Period')
plt.legend()
plt.show()
