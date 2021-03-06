import io
import asyncio
import urllib.parse


CONCURRENCY_MAP = {
    io: "syncio",
    "io": "syncio",
    "syncio": "syncio",
    asyncio: "asyncio",
    "asyncio": "asyncio"
}


class Serial:

    def __init__(self, url, *args, **kwargs):
        import serial
        self.eol = kwargs.pop("eol", b"\n")
        self.serial = serial.serial_for_url(url, *args, **kwargs)

    def read(self, size=1):
        return self.serial.read(size)

    def write(self, data):
        return self.serial.write(data)

    def readline(self, eol=None):
        return self.serial.read_until(terminator=eol or self.eol)

    def write_readline(self, data, eol=None):
        self.write(data)
        return self.readline(eol=eol)


def connection_for_url(url, *args, **kwargs):
    url_result = urllib.parse.urlparse(url)
    concurrency = CONCURRENCY_MAP[kwargs.pop("concurrency", "asyncio")]
    scheme = url_result.scheme
    if scheme == "serial":
        # local serial line
        if concurrency is "syncio":
            return Serial(url[9:], *args, **kwargs)
    elif scheme == "rfc2217":
        if concurrency is "syncio":
            return Serial(url, *args, **kwargs)
        elif concurrency is "asyncio":
            import serialio.aio.rfc2217
            return serialio.aio.rfc2217.Serial(url, *args, **kwargs)
    elif scheme == "tcp":
        host, port = url_result.netloc.split(":", 1)
        port = int(port)
        if concurrency is "syncio":
            import sockio.sio
            return sockio.sio.TCP(host, port, *args, **kwargs)
        elif concurrency is "asyncio":
            import sockio.aio
            return sockio.aio.TCP(host, port, *args, **kwargs)
    raise RuntimeError(
        "unsupported concurrency model {!r} for {}".format(concurrency, scheme)
    )
