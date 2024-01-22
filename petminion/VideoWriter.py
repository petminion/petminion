import av
import numpy as np


class VideoWriter:
    """
    A class for writing video files using the av library.

    Args:
        filename (str): The name of the output video file.

    Attributes:
        output (av.OutputContainer): The output container for the video file.
        stream (av.VideoStream): The video stream for encoding frames.

    """

    def __init__(self, filename):
        """
        Initializes a VideoWriter object.

        Args:
            filename (str): The name of the output video file. such as foo.mp4

        """
        self.output = output = av.open(filename, 'w')
        self.stream = stream = output.add_stream('h264', 24)
        stream.bit_rate = 2000000  # 8000000, 2mbps is a low bitrate per https://www.videoproc.com/media-converter/bitrate-setting-for-h264.htm

    def add_frame(self, frame: np.ndarray):
        """
        Adds a frame to the video file.

        Args:
            frame (np.ndarray): The frame to be added, represented as a NumPy array.

        """
        f = av.VideoFrame.from_ndarray(frame, format='bgr24')
        packet = self.stream.encode(f)
        self.output.mux(packet)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        """For use with with statements."""
        # flush
        packet = self.stream.encode(None)
        self.output.mux(packet)
        self.output.close()
