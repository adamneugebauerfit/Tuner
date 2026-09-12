import numpy
import config

def match_freq_to_tone(frequency: float) -> tuple[str, int]:

    fractional_octave = numpy.log2(frequency/config.C0)

    semitones = round(12 * fractional_octave)
    index = semitones % 12
    exact_octave = semitones // 12

    closest_tone = config.notes[index]

    closest_freq_in_0 = config.notes["{closest_tone}"]

    if closest_tone == "C":
        pass
    else:
        closest_tone_octave = exact_octave
    

    return "something", int(frequency)