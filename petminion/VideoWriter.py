
import abc

import av
import cv2
import imageio
import numpy as np
import pygifsicle


class VideoWriter:
    """
    A class for writing video files.

    Attributes:
        filename (str): The name of the output video file.

    """

    def __init__(self, filename, metaclass=abc.ABCMeta):
        """
        Initializes a VideoWriter object.

        Args:
            filename (str): The name of the output video file.
            metaclass (type, optional): The metaclass of the VideoWriter class. Defaults to abc.ABCMeta.

        """
        self.filename = filename

    @abc.abstractmethod
    def add_frame(self, frame: np.ndarray):
        """
        Adds a frame to the video file.

        Args:
            frame (np.ndarray): The frame to be added, represented as a NumPy array.

        """
        pass

    @abc.abstractmethod
    def close(self):
        """
        Closes the video file.
        """
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        """For use with with statements."""
        # flush
        self.close()


class MP4Writer(VideoWriter):
    """
    A class for writing MP4 files.

    Args:
        filename (str): The name of the output video file.

    Attributes:
        output (av.OutputContainer): The output container for the video file.
        stream (av.VideoStream): The video stream for encoding frames.

    """

    def __init__(self, filename, frame_rate=24):
        """
        Initializes a VideoWriter object.

        Args:
            filename (str): The name of the output video file. such as foo.mp4

        """
        super().__init__(filename)
        self.output = output = av.open(filename, 'w')
        self.stream = stream = output.add_stream('h264', frame_rate)
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

    def close(self):
        """
        Closes the video file.
        """
        packet = self.stream.encode(None)
        self.output.mux(packet)
        self.output.close()


class GIFWriter(VideoWriter):
    """
    A class for writing GIF files.

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
        super().__init__(filename)
        self.output = imageio.get_writer(filename, mode='I')

    def add_frame(self, frame: np.ndarray):
        """
        Adds a frame to the video file.

        Args:
            frame (np.ndarray): The frame to be added, represented as a NumPy array.

        """
        self.output.append_data(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    def close(self):
        """
        Closes the video file.
        """
        self.output.close()
        # if you really need gifs even smaller add: colors=16 and options "--use-colormap", "web",
        # we use -l to loop
        pygifsicle.optimize(self.filename, colors=256, options=["--lossy=70", "-O3", "-l",
                                                                "--resize-width", "320"])
