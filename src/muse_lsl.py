from pylsl import StreamInlet, resolve_streams
import numpy as np
from scipy.signal import welch  # for band‑power extraction
CHANNEL_NAMES = ["TP9", "AF7", "AF8", "TP10"]  # Muse 2 default order

_inlet = None # global variable to store the inlet

'''
get the inlet from the stream
'''
def get_inlet(timeout=3):
    """
    Resolve an EEG stream (type=='EEG') and return a cached StreamInlet.

    The first stream that has 4 channels (Muse 2) is used.
    """
    global _inlet
    if _inlet is not None:
        return _inlet

    print("Resolving EEG streams…")
    streams = resolve_streams(wait_time=timeout)
    print(f"Found {len(streams)} streams:")
    
    eeg_stream = None
    for i, st in enumerate(streams):
        print(f"Stream {i}: type={st.type()}, name={st.name()}, channels={st.channel_count()}")
        if st.type() == "EEG" and st.channel_count() == 4:
            eeg_stream = st
            break

        if eeg_stream is None:
            raise RuntimeError("No 4‑channel EEG stream found. Is Muse 2 LSL running?")

    _inlet = StreamInlet(eeg_stream)
    print(f"Inlet created → {eeg_stream.name()}")
    return _inlet


def get_raw_eeg_all_channels(duration_sec=10, fs=256):
    """
    Pull raw Muse2 EEG samples for `duration_sec` seconds.

    Returns
    -------
    data : np.ndarray, shape (n_samples, 4)
        Columns are TP9, AF7, AF8, TP10.
    ts   : np.ndarray
        Timestamps for each sample.
    """
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

# ------------------------------------------------------------------------
# Feature extraction helpers
# ------------------------------------------------------------------------

_BANDS = {
    "delta": (0.5, 4),
    "theta": (4, 8),
    "alpha": (8, 13),
    "beta":  (13, 30),
}

def _band_power(signal, fs, band):
    """Compute band power via Welch PSD (µV² / Hz)."""
    fmin, fmax = _BANDS[band]
    freqs, psd = welch(signal, fs=fs, nperseg=fs*2)
    idx = np.logical_and(freqs >= fmin, freqs <= fmax)
    return np.trapz(psd[idx], freqs[idx])

def get_current_features(duration_sec: int = 2, fs: int = 256) -> np.ndarray:
    """
    Capture `duration_sec` of data and return a 28‑dim feature vector:

        4 channels × (mean, std, alpha, beta, theta, delta, max–min)

    Returns
    -------
    np.ndarray shape (28,)
    """
    raw, _ = get_raw_eeg_all_channels(duration_sec, fs)
    if raw is None:
        return np.zeros(28)

    feats = []
    for ch in range(raw.shape[1]):
        sig = raw[:, ch]
        feats.extend([
            np.mean(sig),
            np.std(sig),
            _band_power(sig, fs, "alpha"),
            _band_power(sig, fs, "beta"),
            _band_power(sig, fs, "theta"),
            _band_power(sig, fs, "delta"),
            np.max(sig) - np.min(sig),
        ])
    return np.array(feats, dtype=np.float32)