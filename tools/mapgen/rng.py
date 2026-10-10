"""Seeded, platform-independent RNG (SplitMix64). Generators must use this, never the `random` module,
`hash()`, time, or set iteration order: same seed + params must give byte-identical output on any machine."""
import hashlib

MASK = (1 << 64) - 1


def seed_from(value):
    """Map an int or string seed to a 64-bit int (strings via SHA-256, stable across runs)."""
    if isinstance(value, bool):
        raise TypeError("seed must be int or string")
    if isinstance(value, int):
        return value & MASK
    return int.from_bytes(hashlib.sha256(str(value).encode("utf-8")).digest()[:8], "big")


def mix(*values):
    """Stateless 64-bit hash of integers (used for lattice noise)."""
    h = 0x9E3779B97F4A7C15
    for v in values:
        h = _splitmix((h ^ (v & MASK)) & MASK)
    return h


def _splitmix(z):
    z = (z + 0x9E3779B97F4A7C15) & MASK
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
    return z ^ (z >> 31)


class Rng:
    def __init__(self, seed):
        self.state = seed_from(seed)

    def next_u64(self):
        z = self.state
        self.state = (z + 0x9E3779B97F4A7C15) & MASK
        return _splitmix(z)

    def random(self):
        """Float in [0, 1)."""
        return (self.next_u64() >> 11) / float(1 << 53)

    def randint(self, a, b):
        """Integer in [a, b] (inclusive), unbiased via rejection."""
        if b < a:
            raise ValueError(f"randint({a}, {b})")
        n = b - a + 1
        limit = (1 << 64) - ((1 << 64) % n)
        while True:
            r = self.next_u64()
            if r < limit:
                return a + r % n

    def chance(self, p):
        return self.random() < p

    def choice(self, seq):
        return seq[self.randint(0, len(seq) - 1)]

    def weighted(self, items):
        """items: list of (value, weight>=0); returns a value."""
        total = sum(w for _, w in items)
        if total <= 0:
            raise ValueError("all weights are 0")
        r = self.random() * total
        for v, w in items:
            r -= w
            if r < 0:
                return v
        return items[-1][0]

    def shuffle(self, seq):
        for i in range(len(seq) - 1, 0, -1):
            j = self.randint(0, i)
            seq[i], seq[j] = seq[j], seq[i]

    def fork(self, label):
        """Independent child stream (so adding draws in one feature does not shift another)."""
        return Rng(mix(self.state, seed_from(str(label))))
