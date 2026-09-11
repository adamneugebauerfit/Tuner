import sounddevice as sd
import numpy

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



def filtering_nonharmonic_frequencies (magnitude_spectrum: numpy.ndarray):
    """
    :param magnitude_spectrum: contains the whole frequencies spectrum
    :return: a shortened list where each frequency is scored by how well its harmonics back it up

    Because the loudest frequency is not always the right one.\n
    For example the low E on a typical guitar is 82.0 Hz but this is not the
    only frequency that is being played and its multiples are registered too
    such as 164, 246, 328 ... Hz.\n
    Using HPS we can filter out the unwanted frequencies.\n
    HPS stands for harmonic product spectrum which is exactly what this function returns.\n
    We find these harmonic products by copying the beginning of the magnitude_spectrum to a new list,
    extracting every "d"th element from the magnitude_spectrum, and multiplying the new list by it
    as many times as we want (HPS_ACCURACY).\n
    This ensures that any zero in the process kills the whole frequency, because a missing
    harmonic means it is not the real note.\n

    """

    hps = magnitude_spectrum[:len(magnitude_spectrum) // HPS_ACCURACY].copy()

    for d in range(2, HPS_ACCURACY + 1):
        hps *= magnitude_spectrum[::d][:len(hps)]

    return hps



    
def find_exact_frequency (magnitude_spectrum: numpy.ndarray,
                                      hps_list: numpy.ndarray,
                                      lowest_possible_bin: int) -> float:
    """
    :param magnitude_spectrum: contains the whole spectrum pre-HPS
    :param hps_list: contains only the harmonic product frequencies (the ones we want)
    :param lowest_possible_bin: given by LOWEST_FREQ, refers to hps_list elements
    :return: The exact frequency played

    Because the magnitude_spectrum list might look something like this:\n
    110 Hz: ############\n
    120 Hz: ##################\n
    130 Hz: #####\n
    In this case the frequency we want to find is between 110 and 120 Hz.\n

    We use interpolation of the magnitude_spectrum values to calculate the exact frequency
    using log space because FFT peak is bell-shaped, which after log gives a parabola.\n
    We use magnitude_spectrum instead of hps_list because HPS distorts the peak shape.\n
    We use the parabola to calculate the offset from the peak_bin frequency using following formula:\n
    offset = 0.5 * (a - c) / (a - 2 * b + c)
    """

    #peak_bin refers to the bin with the highest value in the hps_list
    #using the same example as in the function comment, this will calculate
    #the index of 120Hz bin
    peak_bin = lowest_possible_bin + numpy.argmax(hps_list[lowest_possible_bin:])

    a = numpy.log(magnitude_spectrum[peak_bin - 1] + EPS)
    b = numpy.log(magnitude_spectrum[peak_bin] + EPS)
    c = numpy.log(magnitude_spectrum[peak_bin + 1] + EPS)

    denominator = a - (2 * b) + c
    if denominator != 0:
        offset = 0.5 * (a - c) / denominator
    else:
        offset = 0

    peak_frequency = (peak_bin + offset) * SAMPLE_RATE / BLOCK

    return peak_frequency


def main ():

    notes = {
        "C": 16.35,
        "C#": 17.32,
        "D": 18.35,
        "D#": 19.45,
        "E": 20.60,
        "F": 21.83,
        "F#": 23.12,
        "G": 24.50,
        "G#": 25.96,
        "A": 27.50,
        "A#": 29.14,
        "B": 30.87
    }

    hanning = numpy.hanning(BLOCK)
    low_bin = int(LOWEST_FREQ * BLOCK / SAMPLE_RATE)


    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32", blocksize=BLOCK) as stream:

        #Program loop
        while True:
            data, _ = stream.read(BLOCK)

            #since we work with mono audio, second column of data
            #is pointless so this turns data from 2D to 1D array
            data = data[:, 0]

            #RMS stands for Root Mean Square [float32 0.00 - 1.00]
            #which is basically the amount of power that runs through the
            #microphone so it's used as a volume threshhold
            rms = numpy.sqrt(numpy.mean(data ** 2))

            #using the RMS as a volume threshhold
            #if the sound is not loud enough, does not
            #calculate and print stays from previous recorded frequency
            if rms < 0.01:
                continue

            #FFT method which is used to find the pitch
            #loops the data it's given which makes a "click"
            #when the end of the clip meets the start of the same clip
            #hanning is like a fade-in fade-out, which ensures
            #no "click" and no fake signals
            data = data * hanning

            #fft.rfft is a fast fourier tranformation for real numbers
            #returns an 1D array of complex numbers, each container
            #represents a frequency and each value in the container
            #represents the amount of the frequency in the sample
            spectrum = numpy.fft.rfft(data)

            #because spectrum contains complex numbers, with .abs()
            #they're turned into plain positive number values
            magnitude = numpy.abs(spectrum)

            hps = filtering_nonharmonic_frequencies(magnitude)

            peak_freq = find_exact_frequency(magnitude, hps, low_bin)

            print(f"Freq: {peak_freq:6.3f} Hz", end="\r")

        
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted")
