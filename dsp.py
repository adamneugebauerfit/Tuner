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
    complex_spectrum = numpy.fft.rfft(data, config.FFT_SIZE)
    magnitude_spectrum = numpy.abs(complex_spectrum)

    return magnitude_spectrum


def filtering_nonharmonic_frequencies(magnitude_spectrum: numpy.ndarray) -> numpy.ndarray:
    """
    :param magnitude_spectrum: contains the whole frequencies spectrum
    :return: log scores, one per candidate bin from 0 up to len(magnitude_spectrum) // HPS_ACCURACY

    HPS stands for harmonic product spectrum (spektrum alikvotnich tonu (got that from prof. Cernocky :) ))
    which is what this returns.
    For example: when you play the guitar's second string B3, its frequency is 246.94 Hz (f).
    However, f is not the only frequency played. Along with f its harmonic products consisting of
    2*f, 3*f, 4*f, ... are also played.

    For every candidate bin (k) we look at bins 2*k, 3*k,...up to HPS_ACCURACY*k.
    The real harmonic rarely lands exactly on d*k (f sits between bins, and strings play
    higher harmonics slightly sharp), so we take the biggest value within "radius" bins of d*k.
    Each candidate's score is the sum of the logs of these values.
    A missing harmonic gives a huge negative log, which kills that candidate.
    """
    n = len(magnitude_spectrum) // config.HPS_ACCURACY
    k = numpy.arange(n)
    score = numpy.log(magnitude_spectrum[:n] + config.EPS)
    for d in range(2, config.HPS_ACCURACY + 1):
        radius = (d + 1) // 2
        idx = d * k[:, None] + numpy.arange(-radius, radius + 1)[None, :]
        idx = numpy.clip(idx, 0, len(magnitude_spectrum) - 1)
        score += numpy.log(magnitude_spectrum[idx].max(axis=1) + config.EPS)

    return score

    
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

    window = magnitude_spectrum[peak_bin - 3 : peak_bin + 4]
    peak_bin = peak_bin - 3 + numpy.argmax(window)

    a = numpy.log(magnitude_spectrum[peak_bin - 1] + config.EPS)
    b = numpy.log(magnitude_spectrum[peak_bin] + config.EPS)
    c = numpy.log(magnitude_spectrum[peak_bin + 1] + config.EPS)

    denominator = a - (2 * b) + c
    if denominator != 0:
        offset = 0.5 * (a - c) / denominator
        offset = max(-0.5, min(0.5, offset))
    else:
        offset = 0

    peak_frequency = (peak_bin + offset) * config.SAMPLE_RATE / config.FFT_SIZE

    return peak_frequency