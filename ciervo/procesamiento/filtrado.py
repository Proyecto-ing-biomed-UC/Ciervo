from scipy import signal



class ButterLowpassFilter:
    """
    Butterworth lowpass filter.

    Args:
        cutoff (float): The cutoff frequency of the filter.
        fs (float, optional): The sampling frequency. Defaults to 250.
        order (int, optional): The order of the filter. Defaults to 2.

    Attributes:
        cutoff (float): The cutoff frequency of the filter.
        fs (float): The sampling frequency.
        order (int): The order of the filter.
        normal_cutoff (float): The normalized cutoff frequency.
        b (ndarray): The numerator coefficients of the filter.
        a (ndarray): The denominator coefficients of the filter.

    Methods:
        apply(data): Applies the lowpass filter to the input data.

    """

    """
    Initialize the ButterLowpassFilter.

    Args:
        cutoff (float): The cutoff frequency of the filter.
        fs (float, optional): The sampling frequency. Defaults to 250.
        order (int, optional): The order of the filter. Defaults to 2.
    """

    """
    Applies the lowpass filter to the input data.

    Args:
        data (ndarray): The input data to be filtered.

    Returns:
        ndarray: The filtered output data.
    """
    def __init__(self, cutoff, fs=250, order=2):
        self.cutoff = cutoff
        self.fs = fs
        self.order = order
        self.normal_cutoff = cutoff / (0.5 * fs)
        self.b, self.a = signal.butter(order, self.normal_cutoff, btype='low', analog=False)

    def apply(self, data):
        y = signal.filtfilt(self.b, self.a, data, axis=0)
        return y


class ButterHighpassFilter:
    """
    Initializes a Butterworth highpass filter.

    Parameters:
    - cutoff (float): The cutoff frequency of the filter.
    - fs (int, optional): The sampling frequency of the input data. Defaults to 250.
    - order (int, optional): The order of the filter. Defaults to 2.
    """

    """
    Applies the Butterworth highpass filter to the input data.

    Parameters:
    - data (ndarray): The input data to be filtered.

    Returns:
    - ndarray: The filtered data.
    """
    def __init__(self, cutoff, fs=250, order=2):
        self.cutoff = cutoff
        self.fs = fs
        self.order = order
        self.normal_cutoff = cutoff / (0.5 * fs)
        self.b, self.a = signal.butter(order, self.normal_cutoff, btype='high', analog=False)

    def apply(self, data):
        y = signal.filtfilt(self.b, self.a, data, axis=0)
        return y


class ButterBandpassFilter:
    """
    Initializes a Butterworth bandpass filter.

    Args:
        lowcut (float): The lower cutoff frequency of the filter.
        highcut (float): The upper cutoff frequency of the filter.
        fs (int, optional): The sampling frequency of the input data. Defaults to 250.
        order (int, optional): The order of the filter. Defaults to 2.
    """
    

    """
    Applies the Butterworth bandpass filter to the input data.

    Args:
        data (array-like): The input data to be filtered.

    Returns:
        array-like: The filtered output data.
    """

    def __init__(self, lowcut, highcut, fs=250, order=2):
        self.lowcut = lowcut
        self.highcut = highcut
        self.fs = fs
        self.order = order
        nyq = 0.5 * fs
        self.low = lowcut / nyq
        self.high = highcut / nyq
        self.b, self.a = signal.butter(order, [self.low, self.high], btype='band', analog=False)

    def apply(self, data):
        y = signal.filtfilt(self.b, self.a, data, axis=0)
        return y
