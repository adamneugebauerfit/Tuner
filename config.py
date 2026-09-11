BLOCK = 4096

SAMPLE_RATE = 48000

#How many matches must the harmonic product spectrum hit
#Lower than 4 might result in unwanted behaviour in some frequencies
HPS_ACCURACY = 4

#Required in this version of the script because
#otherwise very low unwanted frequencies get in the way
LOWEST_FREQ = 70

#Epsilon used to avoid log(0) err
EPS = 1e-12

#Sensitivity threshold, below this there is no note being played
#Measured room noise peaks at around 0.005
RMS_GATE = 0.01