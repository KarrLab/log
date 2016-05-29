import codecs


class _HandlerInterface:
    """
    the common interface that all handlers must subclass
    """

    def __init__(self, name):
        self.name = name

    def __lt__(self, other):
        return self.name < other.name

    def __le__(self, other):
        return self.name <= other.name

    def __eq__(self, other):
        return self.name == other.name

    def __ge__(self, other):
        return self.name >= other.name

    def __gt__(self, other):
        return self.name >= other.name

    def __hash__(self):
        return super(_HandlerInterface, self).__hash__()

    def write(self, message):
        raise NotImplementedError


class StreamHandler(_HandlerInterface):
    """
    ``StreamHandler`` is useful for writing messages to a stream, i.e. STDOUT or STDERR

    >>> import sys
    >>> handler = StreamHandler(sys.stdout)
    """

    def __init__(self, stream, name=None):
        """
        :param stream: an open stream to write to (most typically sys.stdout)
        :type stream: object

        :param name: the name of the handler
        :type name: str
        """
        super(StreamHandler, self).__init__(name)
        self.stream = stream

    def write(self, message):
        """writes the message to the configured stream

        :param message: what you want logged
        :type message: str
        """
        self.stream.write(message)
        self.stream.flush()


class FileHandler(_HandlerInterface):
    """
    ``FileHandler`` is useful for writing messages to a file.

    >>> fname = '/tmp/test.log'
    >>> handler = FileHandler(fname)
    """

    def __init__(self, filename, mode='a', encoding='utf8', errors='strict', buffering=1, name=None):
        """
        :param filename: the name of the file to write to
        :type filename: str

        :param mode: the write mode
        :type mode: str

        :param encoding: the encoding of the file
        :type encoding: str

        :param errors: the error mode for writing
        :type errors: str

        :param buffering: the buffering level
        :type buffering: int

        :param name: the name of the handler
        :type name: str
        """
        super(FileHandler, self).__init__(name)
        self.fh = codecs.open(filename, mode=mode, encoding=encoding, errors=errors, buffering=buffering)

    def write(self, message):
        """writes the message to the configured file

        :param message: what you want logged
        :type message: str
        """

        self.fh.write(message)
        self.fh.flush()


class SocketHandler(_HandlerInterface):
    """
    SocketHandler is useful for writing logs to a socket. this can be used for network sockets of unix sockets.

    >>> import socket
    >>> net_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    >>> net_addr = ('example.com', 9999)
    >>> net_handler = SocketHandler(net_sock, net_addr)
    >>>
    >>> unix_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    >>> unix_addr = '/tmp/log.sock'
    >>> unix_handler = SocketHandler(unix_sock, unix_addr)
    """

    def __init__(self, socket, address, encoding='utf8', name=None):
        """
        :param socket: the socket to write messages to
        :type socket: socket

        :param address: the socket location
        :type address: str or tuple

        :param encoding: the encoding of the message
        :type encoding: str

        :param name: the name of the handler
        :type name: str
        """
        super(SocketHandler, self).__init__(name)
        self.socket = socket
        self.socket.connect(address)
        self.encoding = encoding

    def write(self, message):
        """writes the message to the configured socket

        :param message: what you want logged
        :type message: str
        """

        self.socket.sendall(bytes(message, self.encoding))
