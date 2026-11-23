# Tuner

A small command-line tuner written in Python.

It listens to your microphone, finds the note being played and shows
how far off from that note you are, measured in cents.

```
....|.....E2.......... Freq:   81.000 Hz
==========A2========== Freq:  110.000 Hz
..........E2......|... Freq:   84.000 Hz
```


## Installation

Because the script needs to talk to the microphone, it uses `sounddevice`,
which on Linux also needs the PortAudio library installed on the system.

```bash
#Fedora
sudo dnf install portaudio

#Debian / Ubuntu
sudo apt install libportaudio2
```

Then create a virtual environment and install the two Python packages:

```bash
python3 -m venv .venv && .venv/bin/pip install sounddevice numpy
```

Python 3.9 or newer is required.


## Usage

```bash
.venv/bin/python tuner.py
```

Play a note and watch the line update. Press `Ctrl+C` to stop.

If nothing shows up, the input is probably too quiet, see `RMS_GATE` below.


## Reading the cent meter

The note in the middle is the closest note to what you are playing,
the number after it is the octave.\
Each dot on either side stands for 5 cents (100 cents = 1 semitone),
so the meter reaches 50 cents to each side. Further than that and a
different note would be closer.

- `|` left of the note - you are flat (too low), tune up
- `|` right of the note - you are sharp (too high), tune down
- `=` everywhere - you are in tune (less than 2.5 cents off)

The frequency on the right is the exact frequency that was detected.


## How it works

Every loop `tuner.py` reads one block of audio from the microphone and
sends it through these steps:

1. `dsp.calculate_rms` - Measures how loud the block is.
   If it is quieter than `RMS_GATE`, the block is skipped, because
   nothing is being played and we would only be tuning room noise.
2. `dsp.apply_window` - Applies a Hanning window, which is a fade-in
   and fade-out on the block, so the FFT does not hear a "click"
   where the end of the block loops back to the start.
3. `dsp.get_magnitude_spectrum` - Turns the audio into a spectrum using
   FFT, where each bin is a frequency and its value is how much of
   that frequency is in the block.
4. `dsp.filtering_nonharmonic_frequencies` - Because the loudest frequency
   is not always the note being played, Harmonic Product Spectrum (HPS)
   scores each frequency by how well its harmonics (2x, 3x, 4x ...)
   back it up. The real note has all of them, the fake ones do not.
5. `dsp.find_exact_frequency` - Because the real frequency usually sits
   between two bins, we fit a parabola through the peak and its two
   neighbours (in log space) to find exactly where it is.
6. `tones.match_freq_to_tone` - Turns the frequency into the closest
   note name, its octave and how many cents it is off by.

The whole explanation of each step is in the docstring of its function.


## Configuration

All the settings live in `config.py`.

| Name           | Default | What it does                                                                           |
|----------------|---------|----------------------------------------------------------------------------------------|
| `BLOCK`        | `4096`  | How many samples are read at once. Bigger is more precise, but slower to react         |
| `SAMPLE_RATE`  | `15000` | Samples per second taken from the microphone                                           |
| `HPS_ACCURACY` | `6`     | How many harmonics must back up a frequency. Lower than 4 might misbehave              |
| `LOWEST_FREQ`  | `70`    | Anything below this (in Hz) is ignored, otherwise low unwanted frequencies get in the way |
| `EPS`          | `1e-12` | Tiny number added to avoid `log(0)` errors                                             |
| `RMS_GATE`     | `0.01`  | Loudness below which nothing is considered played. Room noise peaks around `0.005`     |
| `notes`        |         | Frequencies of all 12 notes in octave 0, every other octave is calculated from these  |

With the default values the tuner hears roughly from 70 Hz up to about 1250 Hz,
because HPS only keeps the bottom `1 / HPS_ACCURACY` part of the spectrum.\
One FFT bin is `SAMPLE_RATE / BLOCK` ≈ 3.66 Hz wide.


## Files

- `tuner.py` - The main program loop and the cent meter print
- `dsp.py` - Signal processing, from raw audio to the exact frequency
- `tones.py` - Matching the frequency to a note and cents
- `config.py` - Settings and note frequencies


## TODO

- The detected note can jump between octaves too easily
