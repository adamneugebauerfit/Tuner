import sounddevice as sd
import numpy
import dsp
import config


def main():

    hanning_window = numpy.hanning(config.BLOCK)

    low_bin = int(config.LOWEST_FREQ * config.BLOCK / config.SAMPLE_RATE)


    with sd.InputStream(samplerate=config.SAMPLE_RATE, channels=1, dtype="float32", blocksize=config.BLOCK) as stream:

        #Program loop
        while True:
            stream_data, _ = stream.read(config.BLOCK)

            #since we work with mono audio, second column of data
            #is pointless so this turns data from 2D to 1D array
            stream_data = stream_data[:, 0]

            rms = dsp.calculate_rms(stream_data)

            #sensitivity threshold
            if rms < config.RMS_GATE:
                continue

            stream_data = dsp.apply_window(stream_data, hanning_window)

            magnitude = dsp.get_magnitude_spectrum(stream_data)

            hps = dsp.filtering_nonharmonic_frequencies(magnitude)

            peak_freq = dsp.find_exact_frequency(magnitude, hps, low_bin)

            print(f"Freq: {peak_freq:6.3f} Hz", end="\r")

        
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted")
