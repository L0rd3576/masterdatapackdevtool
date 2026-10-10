"""Minimal, deterministic NBT reader/writer (Java Edition, big-endian), stdlib only.

Tag values are plain Python objects wrapped in small typed classes so the writer knows the exact tag type:
    Byte(1), Short(2), Int(3), Long(4), Float(5), Double(6), ByteArray(7), str (8), List(9), Compound=dict (10),
    IntArray(11), LongArray(12)
A Python `str` is a TAG_String and a `dict` is a TAG_Compound (key order is preserved, so output is stable).
Structure files are gzip-compressed with an unnamed root compound; `write_file`/`read_file` handle that.
gzip header mtime is fixed to 0 so equal data gives byte-identical files.
"""
import gzip
import io
import struct

TAG_END, TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG, TAG_FLOAT, TAG_DOUBLE = 0, 1, 2, 3, 4, 5, 6
TAG_BYTE_ARRAY, TAG_STRING, TAG_LIST, TAG_COMPOUND, TAG_INT_ARRAY, TAG_LONG_ARRAY = 7, 8, 9, 10, 11, 12


class _Num:
    __slots__ = ("v",)
    tag = None

    def __init__(self, v):
        self.v = v

    def __eq__(self, o):
        return type(o) is type(self) and o.v == self.v

    def __hash__(self):
        return hash((self.tag, self.v))

    def __repr__(self):
        return f"{type(self).__name__}({self.v!r})"


class Byte(_Num):
    tag = TAG_BYTE


class Short(_Num):
    tag = TAG_SHORT


class Int(_Num):
    tag = TAG_INT


class Long(_Num):
    tag = TAG_LONG


class Float(_Num):
    tag = TAG_FLOAT


class Double(_Num):
    tag = TAG_DOUBLE


class ByteArray(list):
    tag = TAG_BYTE_ARRAY


class IntArray(list):
    tag = TAG_INT_ARRAY


class LongArray(list):
    tag = TAG_LONG_ARRAY


class List(list):
    """TAG_List; `elem` is the element tag id (needed for empty lists)."""
    tag = TAG_LIST

    def __init__(self, items=(), elem=None):
        super().__init__(items)
        self.elem = elem


def tag_of(v):
    if isinstance(v, bool):
        raise TypeError("use Byte(0/1) for booleans")
    if isinstance(v, (_Num, ByteArray, IntArray, LongArray, List)):
        return v.tag
    if isinstance(v, str):
        return TAG_STRING
    if isinstance(v, dict):
        return TAG_COMPOUND
    if isinstance(v, list):
        return TAG_LIST
    raise TypeError(f"not an NBT value: {v!r}")


_FMT = {TAG_BYTE: ">b", TAG_SHORT: ">h", TAG_INT: ">i", TAG_LONG: ">q", TAG_FLOAT: ">f", TAG_DOUBLE: ">d"}


# ----------------------------------------------------------------------------------------------- writing
def _w_str(out, s):
    b = s.encode("utf-8")  # modified UTF-8 differs only for NUL and supplementary chars; not used here
    out.write(struct.pack(">H", len(b)))
    out.write(b)


def _w_payload(out, t, v):
    if t in _FMT:
        out.write(struct.pack(_FMT[t], v.v))
    elif t == TAG_STRING:
        _w_str(out, v)
    elif t == TAG_BYTE_ARRAY:
        out.write(struct.pack(">i", len(v)))
        out.write(struct.pack(f">{len(v)}b", *v))
    elif t == TAG_INT_ARRAY:
        out.write(struct.pack(">i", len(v)))
        out.write(struct.pack(f">{len(v)}i", *v))
    elif t == TAG_LONG_ARRAY:
        out.write(struct.pack(">i", len(v)))
        out.write(struct.pack(f">{len(v)}q", *v))
    elif t == TAG_LIST:
        elem = getattr(v, "elem", None)
        if v:
            elem = tag_of(v[0])
        elem = elem if elem is not None else TAG_END
        out.write(struct.pack(">bi", elem, len(v)))
        for item in v:
            if tag_of(item) != elem:
                raise TypeError(f"mixed list element types: {v!r}")
            _w_payload(out, elem, item)
    elif t == TAG_COMPOUND:
        for k, item in v.items():
            it = tag_of(item)
            out.write(struct.pack(">b", it))
            _w_str(out, k)
            _w_payload(out, it, item)
        out.write(b"\x00")
    else:
        raise TypeError(t)


def dumps(root, name=""):
    """Uncompressed NBT bytes for a root compound."""
    out = io.BytesIO()
    out.write(struct.pack(">b", TAG_COMPOUND))
    _w_str(out, name)
    _w_payload(out, TAG_COMPOUND, root)
    return out.getvalue()


def write_file(path, root):
    raw = dumps(root)
    with open(path, "wb") as f:
        f.write(gzip_bytes(raw))


def gzip_bytes(raw):
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="") as g:
        g.write(raw)
    return buf.getvalue()


# ----------------------------------------------------------------------------------------------- reading
class _R:
    def __init__(self, data):
        self.d, self.i = data, 0

    def take(self, n):
        b = self.d[self.i:self.i + n]
        if len(b) != n:
            raise ValueError("truncated NBT")
        self.i += n
        return b

    def unpack(self, fmt):
        return struct.unpack(fmt, self.take(struct.calcsize(fmt)))[0]

    def string(self):
        n = self.unpack(">H")
        return self.take(n).decode("utf-8", "replace")


_CLS = {TAG_BYTE: Byte, TAG_SHORT: Short, TAG_INT: Int, TAG_LONG: Long, TAG_FLOAT: Float, TAG_DOUBLE: Double}


def _r_payload(r, t):
    if t in _FMT:
        return _CLS[t](r.unpack(_FMT[t]))
    if t == TAG_STRING:
        return r.string()
    if t in (TAG_BYTE_ARRAY, TAG_INT_ARRAY, TAG_LONG_ARRAY):
        n = r.unpack(">i")
        code = {TAG_BYTE_ARRAY: "b", TAG_INT_ARRAY: "i", TAG_LONG_ARRAY: "q"}[t]
        vals = struct.unpack(f">{n}{code}", r.take(n * struct.calcsize(code)))
        return {TAG_BYTE_ARRAY: ByteArray, TAG_INT_ARRAY: IntArray, TAG_LONG_ARRAY: LongArray}[t](vals)
    if t == TAG_LIST:
        elem = r.unpack(">b")
        n = r.unpack(">i")
        return List([_r_payload(r, elem) for _ in range(n)], elem=elem)
    if t == TAG_COMPOUND:
        out = {}
        while True:
            it = r.unpack(">b")
            if it == TAG_END:
                return out
            k = r.string()
            out[k] = _r_payload(r, it)
    raise ValueError(f"bad tag id {t}")


def loads(data):
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    r = _R(data)
    t = r.unpack(">b")
    if t != TAG_COMPOUND:
        raise ValueError("root is not a compound")
    r.string()
    return _r_payload(r, TAG_COMPOUND)


def read_file(path):
    with open(path, "rb") as f:
        return loads(f.read())


def to_plain(v):
    """NBT value -> plain JSON-able Python (for printing/inspection)."""
    if isinstance(v, _Num):
        return v.v
    if isinstance(v, dict):
        return {k: to_plain(x) for k, x in v.items()}
    if isinstance(v, list):
        return [to_plain(x) for x in v]
    return v
