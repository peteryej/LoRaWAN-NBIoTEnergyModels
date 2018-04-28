# system parameters
BW_sys = 5 # (MHz)
T_RAwin = 40 #5 # (ms)
numofsymbols_PDCCH = 3
format_PDCCH = 0
th_frag = 6 # threshold fragmentation RB pairs
numofPreambles = 54 # number of available preambles
Wc = 20 # (ms) backoff window
P_detect = 1 # probability of error detection
RAretryMax = 9
N_devices = 1

# measured parameters, value varies for different NB-IoT chip
Ps = .0099 #.015 #0.03 (mW)  sleep power
Pi = 19.8 #3.0 #10.0  # (mW) idle power
P_rx = 151.8 #90.0 #100.0  # (mW) rx power
P_txMax = 3300.0 #545.0 #200.0 # (mW) tx max power
P_txRB = 32.18 # (mW) tx power per RB pair
P_txPre = 32.18 # (mW) tx power of sending preamble
T_pre = 2.5 # (ms) time before preamble transmission
T_rxRA = 10.0 # (ms) time of rx in RA
T_rxCR = 16.0 # (ms) time of rx in CR

T_DRXi = 200 # (ms) DRX inactivity timer
T_ond = 5 # 4 (ms) RRC connected on duration timer, 5 NPDCCH periods
T_ls = 2048+1 #80 # (ms) DRX long cycle sleep time, 2.048s+ 1 NPDCCH period
T_i = 10000 # (ms) inactiviy timer
T_wait = 54 # (ms) S1 processing delay

B_RBp = 36 # bytes per RB pair (QPSK mod)
B_req = 7 # (bytes) RRC request msg
B_comp = 20 # (bytes) RRC setup complete msg
B_scomp = 13 # (bytes) RRC security mode complete msg
B_reconfig = 10 # (bytes) RRC reconfiguration complete msg

N_maxRAtry = 9 # max num of retransmissions of RA procedure


# battery setting
_battery = 2400#1515 # (mAh)
_voltage = 3.3  # (V)
