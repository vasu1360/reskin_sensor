import argparse
import time

from reskin_sensor import ReSkinProcess

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test code to run a ReSkin streaming process in the background. Allows data to be collected without code blocking"
    )
    # fmt: off
    parser.add_argument("-p", "--port", type=str, help="port to which the microcontroller is connected", default= "/dev/ttyACM0",)
    parser.add_argument("-pp", "--press_port", type=str, help="port to which the pressure microcontroller is connected", default= "/dev/ttyACM1",)
    parser.add_argument("-b", "--baudrate", type=str, help="baudrate at which the microcontroller is streaming data", default=115200,)
    parser.add_argument("-n", "--num_mags", type=int, help="number of magnetometers on the sensor board", default=7,)
    parser.add_argument("-np", "--num_press", type=int, help="number of PneuNets connected to Teensy", default=4,)
    parser.add_argument("-tf", "--temp_filtered", action="store_true", help="flag to filter temperature from sensor output",)
    # parser.add_argument("-p", "--press_port", type=str, help="port to which the pressure sensor Teensy is connected", default= "/dev/ttyACM1",)
    # fmt: on

    args = parser.parse_args()

    # Create sensor stream
    sensor_stream = ReSkinProcess(
        num_mags=args.num_mags,
        port=args.port,
        baudrate=args.baudrate,
        burst_mode=True,
        device_id=1,
        temp_filtered=args.temp_filtered,
        press_port=args.press_port,
        num_press=args.num_press
    )

    # Start sensor stream
    sensor_stream.start()
    time.sleep(0.1)

    # Buffer data for two seconds and return buffer
    if sensor_stream.is_alive():
        sensor_stream.start_buffering()
        buffer_start = time.time()
        time.sleep(2.0)

        sensor_stream.pause_buffering()
        buffer_stop = time.time()

        # Get buffered data
        buffered_data = sensor_stream.get_buffer()

        if buffered_data is not None:
            print(
                "Time elapsed: {}, Number of datapoints: {}".format(
                    buffer_stop - buffer_start, len(buffered_data)
                )
            )

        # Get a specified number of samples
        test_samples = sensor_stream.get_data(num_samples=28)
        print(
            "Columns: ",
            ", \t".join(
                [
                    "T{0}, \tBx{0}, \tBy{0}, \tBz{0}".format(ind)
                    for ind in range(args.num_mags)
                ]
            ),
        )
        for sid, sample in enumerate(test_samples):
            print(
                "Sample {}: ".format(sid + 1)
                + str(["{:.2f}".format(d) for d in sample.data])
            )

        # Pause sensor stream
        sensor_stream.pause_streaming()

        sensor_stream.join()
