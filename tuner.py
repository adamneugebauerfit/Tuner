import sounddevice as sd
import numpy

BLOCK = 4096
SAMPLE_RATE = 48000
    

def main():

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


    #Initializing inputstream for real-time recording
    #channel=1 means mono
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32", blocksize=BLOCK) as stream:

        #Program loop
        while True:
            data, overflowed = stream.read(BLOCK)

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
            if rms < 0.02:
                continue
            else:

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

                #because spectrum conatins complex numbers, with .abs()
                #they're turned into whole number values
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
