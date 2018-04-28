# measured parameters, value varies for different LoRa chip
I_sleep = .0001 # .045 # all current is in mA
I_wakeup = 1.4 # 22.1
I_radioPrep = 0.0015 # 13.3
I_trans = 90.0 # 83.0
I_delay1 = 1.4 #27.0
I_delay2 = I_delay1
I_recv1 =  10.8 #38.0
I_recv2 = I_recv1
I_radioOff = 0.0015 #13.0
I_postproc = 1.4 # 21.0
I_turnoff = 0.0015 # 13.0

T_wakeup = 168.2  # all time is in ms
T_radioPrep = 83.8
T_radioOff = 147.0
T_postproc = 268.0
T_turnoff = 38.0


# battery setting
_battery = 2400 # (mAh)
_voltage = 3.3  # (V)


# LoRaWAN setting
CRC = 1       # wheather cyclic redundancy check exists in physical layer message
BER = 0.00001      # bit error rate
receive_delay1 = 1000.0  # (ms)
receive_delay2 = receive_delay1 + 1000.0  # (ms)
numofPreambleSymbols = 8.0
numof125KHzChannels = 6.0

# for acknowledgement mode
P_recv1 = .5
P_recv2 = 1 - P_recv1
T_radioOffAck = 337.8

numofRetransMax = 7 # default is set as 7
