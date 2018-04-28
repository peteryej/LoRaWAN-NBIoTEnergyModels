"""
model for calculating NB-IoT outage probablity which
show the coverage of NB-IoT
"""
import math
import matplotlib.pyplot as plt

N_frag = 6.0
B_data = 100.0
B_comp = 20.0
B_RAR = 8.0 # number of bytes used for the RAR message
B_conn = 38.0 # size of RRC connect message in bytes
B_RB = 36.0 # number of bytes per resource block
B_req = 7.0 # size of RRC request message in bytes
T_pre = 2.5
m = 9.0 # maximum retransmission
d = 54.0 # number of preambles

N =1.0
R_ave = 2.0
R_1 = N*R_ave
R_t = 18.4
T_RAO = 5.0


def calcP_c(R_t):
    P_c = 1.0-(1.0-1.0/d)**(R_t*T_RAO-1.0)
    return P_c

def calcP_e(R_t):
    R_pre = R_t*T_RAO/d
    R_s = R_pre*math.exp(-R_pre)*d/T_RAO
    R_a = (1-math.exp(-R_pre))*d/T_RAO

    R_PDCCH = (1-math.exp(-R_t*T_RAO))/T_RAO+R_s*(2+math.ceil(B_data/(N_frag*B_RB)))
    N_PDCCH = 3.0 #  number of PDCCH pointers per subframe
    T_PDCCH = 10.0

    R_PDSCH = math.ceil(R_a*B_RAR/B_RB)+R_s*(math.ceil(B_conn/B_RB))
    N_PDSCH  = 3.0 # number of resource blocks in PDSCH
    T_PDSCH = 40.0


    R_PUSCH = R_a*math.ceil(B_req/B_RB) + R_s*(math.ceil(B_comp/B_RB)+math.ceil(B_data/B_RB))
    N_ULRB = 6*168 # 6 or 21 RBs and 168 REs per RB
    N_PUSCH = N_ULRB-6*10.0/T_RAO # number of resource blocks in PUSCH
    T_PUSCH = 40.0


    P_qPDCCH = calP_q(R_PDCCH, N_PDCCH, T_PDCCH)
    P_qPDSCH = calP_q(R_PDSCH, N_PDSCH, T_PDSCH)
    P_qPUSCH = calP_q(R_PUSCH, N_PUSCH, T_PUSCH)

    P_e = 1-(1-P_qPDCCH)*(1-P_qPDSCH)*(1-P_qPUSCH)
    return P_e

def calcR_tTest(P_e, P_c, R_ave):
    R_tTest = R_ave*(1-(P_e*(1-P_c)+P_c)**(m+1))/(1-(P_e*(1-P_c)+P_c))
    return R_tTest

def calcP_out(P_e, P_c):
    P_out = (P_e*(1-P_c)+P_c)**(m+1)
    return P_out

def calP_q(R, N, T):
  p = R/N
  T_d = T-(1.0/N)
  omega = math.exp(-N*(1-p)*T_d)
  return (1-p)*p*omega/(1-p**2*omega)

P_outs = []

R_aves = [.1*x for x in range(1, 40, 1)]
for R_ave in R_aves:
    R_t = R_ave +.001
    P_e = calcP_e(R_t)
    P_c = calcP_c(R_t)
    while calcR_tTest(P_e, P_c, R_ave)-R_t > .1:
        R_t += .001
        P_e = calcP_e(R_t)
        P_c = calcP_c(R_t)

    print R_ave
    print P_c
    print P_e
    print R_t
    P_outs.append(calcP_out(P_e, P_c))
R_aves = [x*1000 for x in R_aves]
plt.plot(R_aves, P_outs, 'yx-', label='NB-IoT 1.4MHz')
plt.xlabel('Arrivals/s')
plt.ylabel('Outage Probability')
plt.title('NB-IoT Outage Probability vs Arrival Rate')
plt.ylim(-.01,.5)
plt.legend()
plt.show()
