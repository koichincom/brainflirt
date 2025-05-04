from pylsl import StreamInlet, resolve_streams
import numpy as np

_inlet = None # global variable to store the inlet

'''
get the inlet from the stream
'''
def get_inlet():
    global _inlet
    if _inlet is None:
        print("Resolving streams")
        streams = resolve_streams(wait_time=1)
        eeg_stream = None

        for stream in streams:
            if stream.name() == 'PetalStream_eeg':
                eeg_stream = stream
                break

        if eeg_stream is None:
            print("No EEG stream found")
            exit(1)

        print("Inlet created")
        _inlet = StreamInlet(eeg_stream)

    return _inlet


def get_raw_eeg_all_channels(duration_sec=10, fs=256):
    inlet = get_inlet()
    n_samples = int(duration_sec * fs)
    data = []
    timestamps = []

    for _ in range(n_samples):
        try:
            sample, timestamp = inlet.pull_sample(timeout=0.1)
            if sample is not None:
                data.append(sample)
                timestamps.append(timestamp)
        except Exception as e:
            print(f"Error pulling sample: {e}")

    if not data:
        print("WARNING: No data received. Check the connection.")
        return None, None

    return np.array(data), np.array(timestamps)  # [tp9, af7, af8, tp10], timestamps