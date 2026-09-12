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



#Frequency of a C0 tone in Hz
C0 = 16.352

notes = {
    "C":    16.35,
    "Cs":   17.32,
    "D":    18.35,
    "Ds":   19.45,
    "E":    20.60,
    "F":    21.83,
    "Fs":   23.12,
    "G":    24.50,
    "Gs":   25.96,
    "A":    27.50,
    "As":   29.14,
    "B":    30.87
}

names = list(notes)