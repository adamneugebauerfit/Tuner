import numpy
import config

def match_freq_to_tone(frequency: float) -> tuple[str, int]:
    """
    :param frequency: Frequency of the tone registered by the microphone
    :return: Tuple of string "{note}{octave number}", number of cents the freqeuncy
    is above (+) or below (-) by from the exact note returned in string

    Because noone remembers the frequencies of all the tones.\n
    This function turns the frequency in a tone context of the closest note
    while the gap between them is measured in cents (log space).\n

    To calculate the closest tone we:\n
    First need to calculate the octave the input is in
    which is done by: log2(freq/C0 freq).\n
    Then we multiply it by 12, because an octave holds 12 semitones,
    which turns it into how many semitones the input sits above C0.\n
    Rounding that gives us the closest semitone, and the fraction we
    throw away is exactly how out of tune the input is.\n
    From the rounded number % 12 tells us which of the 12 names it is
    and // 12 tells us the octave, so the two can never disagree with
    each other and a note like B0 cannot leak into the next octave.\n
    Last we rebuild the frequency of that closest note and compare the
    input to it in log space, because pitch is logarithmic - an octave
    is always double the frequency, never a fixed number of Hz.\n
    We multiply by 1200 because an octave holds 1200 cents
    (12 semitones * 100), so the result is never further than 50 cents
    from 0, otherwise a different note would have been closer.\n
    Positive cents mean the input is sharp, negative mean it is flat.
    """

    fractional_octave = numpy.log2(frequency/config.notes["C"] + config.EPS)

    semitones = round(12 * fractional_octave)
    index = semitones % 12
    exact_octave = semitones // 12

    closest_tone = config.names[index]


    closest_freq_in_original = config.notes[f"{closest_tone}"] * (2**exact_octave)

    cents = 1200 * numpy.log2(frequency / closest_freq_in_original)
    cents = numpy.round(cents)
    

    return f"{closest_tone}{exact_octave}", int(cents)