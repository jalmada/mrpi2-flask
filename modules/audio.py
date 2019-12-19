import pyaudio
import logging


class Audio:

    FORMAT = pyaudio.paInt32
    CHANNELS = 1
    RATE = 44100
    CHUNK = 4096
    BITS_PER_SAMPLE = 32
    INPUT_DEVICE_INDEX = 2

    def __init__(self):
        self.audio1 = pyaudio.PyAudio()
        self.wav_header = self.genHeader(self.RATE, self.BITS_PER_SAMPLE, self.CHANNELS)
        self.stream = self.audio1.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True,input_device_index=self.INPUT_DEVICE_INDEX, frames_per_buffer=self.CHUNK)


    def genHeader(self, sampleRate, bitsPerSample, channels):
        datasize = 2000*10**6
        o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
        o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
        o += bytes("WAVE",'ascii')                                              # (4byte) File type
        o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
        o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
        o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
        o += (channels).to_bytes(2,'little')                                    # (2byte)
        o += (sampleRate).to_bytes(4,'little')                                  # (4byte)
        o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
        o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
        o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
        o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
        o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
        return o

    def sound(self):
        try:
            yield(self.wav_header)
            while True:
                data = self.stream.read(self.CHUNK, exception_on_overflow = False)
                yield (data)
        except Exception as e:
            logging.warning(e)
    
