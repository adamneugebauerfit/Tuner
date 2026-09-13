import numpy
import config

def match_freq_to_tone(frequency: float) -> tuple[str, int]:

    fractional_octave = numpy.log2(frequency/config.notes["C"] + config.EPS)

    semitones = round(12 * fractional_octave)
    index = semitones % 12
    exact_octave = semitones // 12

    closest_tone = config.names[index]


    closest_freq_in_original = config.notes[f"{closest_tone}"] * (2**exact_octave)

    cents = 1200 * numpy.log2(frequency / closest_freq_in_original)
    cents = numpy.round(cents)
    

    return f"{closest_tone}{exact_octave}", int(cents)