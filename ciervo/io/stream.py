import os; os.system('clear')
import argparse
import logging
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import time
from paho.mqtt import client as mqtt_client
import ciervo.parameters as p
import serial
import sys
import glob
from pprint import pprint
from ciervo.aux_tools import Buffer
import numpy as np
from time import sleep

# Import SciPy signal processing functions
from scipy.signal import iirnotch, butter, sosfilt, tf2sos

def create_channel_setting_command(channel, power_down, gain_set, input_type_set, bias_set, srb2_set, srb1_set, daisy_module=False):
    """
    Generate the channel setting command string.
    """
    if not (1 <= channel <= 16):
        raise ValueError("Channel must be between 1 and 16.")
    
    # Determine channel letter/number based on board or daisy module
    if channel <= 8:
        channel_str = str(channel)
    else:
        channel_str = chr(ord('Q') + (channel - 9))  # 'Q' to 'I' for daisy module channels

    # Construct the command string
    command = f"x{channel_str}{power_down}{gain_set}{input_type_set}{bias_set}{srb2_set}{srb1_set}x"

    return command

def find_openbci():
    """ Lists serial port names """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # Exclude current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass

    open_bci_ports = [port for port in result if 'usb' in port.lower()]
    #print(open_bci_ports)
    #open_bci_ports = ['/dev/ttyAMA1']

    assert len(open_bci_ports) > 0, 'No se encontraron dispositivos OpenBCI'
    assert len(open_bci_ports) == 1, 'Se encontraron varios dispositivos OpenBCI'

    print(f"OpenBCI en puerto {open_bci_ports[0]}")

    return open_bci_ports[0]

class Publish:
    def __init__(self, board_shim):
        self.board_id = board_shim.get_board_id()
        self.board_shim = board_shim
        self.exg_channels = BoardShim.get_exg_channels(self.board_id)
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        self.update_speed_ms = 50
        self.window_size = 5
        self.num_points = self.window_size * self.sampling_rate

        self.marker = -1
        self.buffer = Buffer(self.window_size, roll=True)


        # Initialize filters using SciPy
        self.mains = 50  # Notch filter frequency (Hz)
        self.band_low = 20  # Lower cutoff frequency for band-pass filter (Hz)
        self.band_high = 120  # Upper cutoff frequency for band-pass filter (Hz)

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
        self.topic = 'data'
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, client_id='openbci')
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
        target_set = set(list(range(256)))
        start_time = None
        while True:
            time.sleep(8 / self.sampling_rate)  # Wait for at least 2 samples
            data = self.board_shim.get_board_data(self.num_points)  # np.float64 default
            if data.shape[1] == 0:
                continue

            if start_time is None:
                start_time = data[p.TIME_CHANNEL, 0]
            data[p.TIME_CHANNEL, :] -= start_time

            if self.marker != -1:
                data[p.MARKER_CHANNEL, :] = self.marker
            data = data[p.ALL_CHANNELS, :]

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

            
            obtain_set = set(data[12, :])

            if not obtain_set.issubset(target_set):
                print("Reiniciando")
                self.board_shim.release_session()
                self.board_shim.prepare_session()
                self.board_shim.start_stream()



            
            
             

            self.client.publish(self.topic, data_bytes, qos=0)

def on_connect(client, userdata, flags, rc, properties):
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
    parser.add_argument('--mac-address', type=str, help='mac address', required=False, default='')
    parser.add_argument('--other-info', type=str, help='other info', required=False, default='')
    parser.add_argument('--streamer-params', type=str, help='streamer params', required=False, default='streaming_board://225.1.1.1:6677')
    parser.add_argument('--serial-number', type=str, help='serial number', required=False, default='')
    parser.add_argument('--board-id', type=int, help='board id, check docs to get a list of supported boards',
                        required=False, default=BoardIds.CYTON_BOARD)
    parser.add_argument('--file', type=str, help='file', required=False, default='')
    parser.add_argument('--master-board', type=int, help='master board id for streaming and playback boards',
                        required=False, default=BoardIds.CYTON_BOARD)
    args = parser.parse_args()

    params = BrainFlowInputParams()
    params.ip_port = args.ip_port
    params.serial_port = find_openbci()
    params.mac_address = args.mac_address
    params.other_info = args.other_info
    params.serial_number = args.serial_number
    params.ip_address = args.ip_address
    params.ip_protocol = args.ip_protocol
    params.timeout = args.timeout
    params.file = args.file
    params.master_board = args.master_board
    #params.ip_address_aux = "225.1.1.2"
    #params.ip_port_aux = 6678

    board_shim = BoardShim(args.board_id, params)

    try:
        board_shim.prepare_session()
        # Configure OpenBCI
        # x (CHANNEL, POWER_DOWN, GAIN_SET, INPUT_TYPE_SET, BIAS_SET, SRB2_SET, SRB1_SET) X

        for i in range(1, 4):
            ch = create_channel_setting_command(channel=i,
                                                power_down=0,
                                                gain_set=6,
                                                input_type_set=0,
                                                bias_set=1,
                                                srb2_set=1,
                                                srb1_set=0)

            board_shim.config_board(ch)
            sleep(0.1)

        #board_shim.add_streamer(args.streamer_params)
        board_shim.start_stream()
        Publish(board_shim)
    except BaseException:
        logging.warning('Exception', exc_info=True)
    finally:
        logging.info('End')
        if board_shim.is_prepared():
            logging.info('Releasing session')
            board_shim.release_session()

if __name__ == '__main__':
    board_id = BoardIds.CYTON_BOARD.value
    pprint(BoardShim.get_board_descr(board_id))

    main()
