
import sounddevice as sd
import numpy

def main():

    hanning = numpy.hanning(4096)

    with sd.InputStream(samplerate=48000, channels=1, dtype="float32", blocksize=4096) as stream:
        while True:
            data, overflowed = stream.read(4096)
            data = data[:, 0]
            

            rms = numpy.sqrt(numpy.mean(data ** 2))

            if rms < 0.01: 
                continue
            else:
                data = data * hanning

                spectrum = numpy.fft.rfft(data)

                magnitude = numpy.abs(spectrum)
                
                hps = magnitude[:len(magnitude) // 5].copy()
                for d in range(2, 6):
                    hps *= magnitude[::d][:len(hps)]

               
                peak_bin = numpy.argmax(hps)
                a = numpy.log(magnitude[peak_bin - 1])
                b = numpy.log(magnitude[peak_bin])
                c = numpy.log(magnitude[peak_bin + 1])
                offset = 0.5 * (a - c) / (a - 2*b + c)
                peak_freq = (peak_bin + offset) * 48000 / 4096


            print(f"Freq: {peak_freq:6.1f} Hz", end="\r")

        
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted")
