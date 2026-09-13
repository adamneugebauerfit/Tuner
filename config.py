BLOCK = 4096

SAMPLE_RATE = 15000

#How many matches must the harmonic product spectrum hit
#Lower than 4 might result in unwanted behaviour in some frequencies
HPS_ACCURACY = 6

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
    "C":    16.352,
    "C#":   17.324,
    "D":    18.354,
    "D#":   19.445,
    "E":    20.602,
    "F":    21.827,
    "F#":   23.125,
    "G":    24.500,
    "G#":   25.957,
    "A":    27.500,
    "A#":   29.135,
    "B":    30.868
}

names = list(notes)