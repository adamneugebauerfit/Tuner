import config
import numpy

def calculate_rms(mono_data: numpy.ndarray) -> float:
    """
    :param mono_data: 1D list of float-type frames
    :return: Normalized power that ran through the microphone

    Calculating RMS for further use as a sensitivity threshold.\n
    RMS stands for Root Mean Square [normalized float]
    which is basically the amount of power that runs through the microphone.\n
    RMS = 1.0 means microphone flatted out
    """

    rms = numpy.sqrt(numpy.mean(mono_data ** 2))
    return rms


def apply_window(data_to_frame: numpy.ndarray, hanning: numpy.ndarray) -> numpy.ndarray:
    """
    :param data_to_frame: A 1D list to apply window to
    :param hanning: 1D list of values to multiply data_to_frame by
    :return: data with a fade-in, fade-out effect

    Because the FFT used right after loops the sample it's given, which
    generates "clicks" right when it switches from the end to the start of
    the clip.\n
    Applying window using hanning applies a fade-in and fade-out to the
    data sample, which minimises any click resulting in less fake signals for fft.\n
    """
    return data_to_frame * hanning


def get_magnitude_spectrum(data: numpy.ndarray) -> numpy.ndarray:
    """
    :param data: Array of frames to extract frequencies from
    :return: Spectrum (Array)

    Because we need to convert the data from the stream to a spectrum of
    frequencies, that appear in the sample.\n
    For that we use Fast Fourier Transform with real input (rfft),
    which return a spectrum where each bin represents a frequency
    and the value is the amount of the frequency in the sample.\n
    In complex_spectrum that value is represented by a complex number.
    In magnitude_spectrum the same value is represented by a real number
    """
    complex_spectrum = numpy.fft.rfft(data)
    magnitude_spectrum = numpy.abs(complex_spectrum)

    return magnitude_spectrum


def filtering_nonharmonic_frequencies(magnitude_spectrum: numpy.ndarray) -> numpy.ndarray:
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

    hps = magnitude_spectrum[:len(magnitude_spectrum) // config.HPS_ACCURACY].copy()

    for d in range(2, config.HPS_ACCURACY + 1):
        hps *= magnitude_spectrum[::d][:len(hps)]

    return hps

    
def find_exact_frequency(magnitude_spectrum: numpy.ndarray,
                         hps_list: numpy.ndarray,
                         lowest_possible_bin: int) -> float:
    """
    :param magnitude_spectrum: contains the whole spectrum pre-HPS
    :param hps_list: each frequency scored by how well its harmonics back it up
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

    a = numpy.log(magnitude_spectrum[peak_bin - 1] + config.EPS)
    b = numpy.log(magnitude_spectrum[peak_bin] + config.EPS)
    c = numpy.log(magnitude_spectrum[peak_bin + 1] + config.EPS)

    denominator = a - (2 * b) + c
    if denominator != 0:
        offset = 0.5 * (a - c) / denominator
    else:
        offset = 0

    peak_frequency = (peak_bin + offset) * config.SAMPLE_RATE / config.BLOCK

    return peak_frequency