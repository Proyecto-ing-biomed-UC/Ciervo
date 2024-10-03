import argparse
import logging
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import time
from paho.mqtt import client as mqtt_client
import ciervo.parameters as p
import numpy as np

# Import SciPy signal processing functions
from scipy.signal import iirnotch, butter, sosfilt, tf2sos

class Publish:
    def __init__(self, board_shim):
        self.board_id = board_shim.get_board_id()
        self.board_shim = board_shim
        self.exg_channels = BoardShim.get_exg_channels(self.board_id)
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        self.update_speed_ms = 50
        self.window_size = 4
        self.num_points = int(self.window_size * self.sampling_rate)

        self.marker = -1

        # Initialize filters
        self.mains = 50  # Notch filter frequency (Hz)
        self.band_low = 0.5  # Lower cutoff frequency for band-pass filter (Hz)
        self.band_high = 10  # Upper cutoff frequency for band-pass filter (Hz)

        # Design notch filter
        b_notch, a_notch = iirnotch(w0=self.mains / (self.sampling_rate / 2), Q=30)
        self.sos_notch = tf2sos(b_notch, a_notch)

        # Design band-pass filter
        self.sos_bp = butter(
            N=4,
            Wn=[self.band_low / (self.sampling_rate / 2), self.band_high / (self.sampling_rate / 2)],
            btype='bandpass',
            output='sos'
        )

        # Initialize filter states for each EEG channel
        self.num_eeg_channels = len(self.exg_channels)
        self.zi_bp = []
        self.zi_notch = []
        for _ in range(self.num_eeg_channels):
            self.zi_bp.append(np.zeros((self.sos_bp.shape[0], 2)))
            self.zi_notch.append(np.zeros((self.sos_notch.shape[0], 2)))

        # MQTT
        self.broker = p.BROKER_HOST
        self.port = p.BROKER_PORT
        self.topic = p.TOPIC
        self.client = mqtt_client.Client(client_id='openbci')
        self.client.on_connect = on_connect
        self.client.on_message = self.on_message

        self.client.connect(self.broker, self.port)
        self.client.subscribe('marker')  # Subscribe to marker topic
        self.client.loop_start()

        self.update()
        self.client.loop_stop()
    
    def on_message(self, client, userdata, msg):
        self.marker = int(msg.payload.decode('utf-8'))
        
    def update(self):
        # Initialize start_time
        data = self.board_shim.get_board_data(self.num_points)
        start_time = data[p.SYN_TIME_CHANNEL, 0]
        while True:
            time.sleep(2 / self.sampling_rate)  # Wait for at least 2 samples
            data = self.board_shim.get_board_data(self.num_points)  # np.float64 default
            data[p.SYN_TIME_CHANNEL, :] -= start_time

            # Check if there is a marker
            if self.marker != -1:
                data[p.SYN_MARKER_CHANNEL, :] = self.marker

            data = data[p.SYN_ALL_CHANNELS, :]


            # Apply filters to EEG channels
            for idx, channel in enumerate(range(8)):
                # Get data for this channel
                channel_data = data[channel, :] - 2250

                # Apply the band-pass filter with state
                filtered_bp, self.zi_bp[idx] = sosfilt(
                    self.sos_bp, channel_data, zi=self.zi_bp[idx]
                )

                # Apply the notch filter with state
                filtered_data, self.zi_notch[idx] = sosfilt(
                    self.sos_notch, filtered_bp, zi=self.zi_notch[idx]
                )

                # Assign filtered data back to data array
                data[channel, :] = filtered_data

            # Convert data to desired precision and publish
            data = data.astype(p.PRECISION)
            data_bytes = data.tobytes()

            self.client.publish(self.topic, data_bytes, qos=1)

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

def main():
    BoardShim.enable_dev_board_logger()
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    # Use docs to check which parameters are required for specific board, e.g., for Cyton - set serial port
    parser.add_argument('--timeout', type=int, help='timeout for device discovery or connection', required=False,
                        default=0)
    parser.add_argument('--ip-port', type=int, help='ip port', required=False, default=0)
    parser.add_argument('--ip-protocol', type=int, help='ip protocol, check IpProtocolType enum', required=False,
                        default=0)
    parser.add_argument('--ip-address', type=str, help='ip address', required=False, default='')
    parser.add_argument('--serial-port', type=str, help='serial port', required=False, default='/dev/cu.usbserial-DN0094LC')
    parser.add_argument('--mac-address', type=str, help='mac address', required=False, default='')
    parser.add_argument('--other-info', type=str, help='other info', required=False, default='')
    parser.add_argument('--streamer-params', type=str, help='streamer params', required=False, default='streaming_board://225.1.1.1:6677')
    parser.add_argument('--serial-number', type=str, help='serial number', required=False, default='')
    parser.add_argument('--board-id', type=int, help='board id, check docs to get a list of supported boards',
                        required=False, default=BoardIds.SYNTHETIC_BOARD)
    parser.add_argument('--file', type=str, help='file', required=False, default='')
    parser.add_argument('--master-board', type=int, help='master board id for streaming and playback boards',
                        required=False, default=BoardIds.SYNTHETIC_BOARD)
    args = parser.parse_args()

    params = BrainFlowInputParams()
    params.ip_port = args.ip_port
    params.serial_port = args.serial_port
    params.mac_address = args.mac_address
    params.other_info = args.other_info
    params.serial_number = args.serial_number
    params.ip_address = args.ip_address
    params.ip_protocol = args.ip_protocol
    params.timeout = args.timeout
    params.file = args.file
    params.master_board = args.master_board
    params.ip_address_aux = "225.1.1.2"
    params.ip_port_aux = 6678

    board_shim = BoardShim(args.board_id, params)
    try:
        board_shim.prepare_session()
        board_shim.add_streamer(args.streamer_params)
        board_shim.start_stream(250 * 10)
        Publish(board_shim)
    except BaseException:
        logging.warning('Exception', exc_info=True)
    finally:
        logging.info('End')
        if board_shim.is_prepared():
            logging.info('Releasing session')
            board_shim.release_session()

if __name__ == '__main__':
    from pprint import pprint
    board_id = BoardIds.SYNTHETIC_BOARD.value
    pprint(BoardShim.get_board_descr(board_id))

    main()
