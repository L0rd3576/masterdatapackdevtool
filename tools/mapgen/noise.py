"""Seeded 2D value noise and fractal (fBm) noise, implemented from scratch (no external packages).

Lattice values come from rng.mix(seed, ix, iz) so the result depends only on seed and coordinates.
"""
import math

from rng import mix, seed_from


def _lattice(seed, ix, iz):
    return (mix(seed, ix, iz) >> 11) / float(1 << 53)  # [0, 1)


def _smooth(t):
    return t * t * t * (t * (t * 6 - 15) + 10)  # quintic fade


def value2d(seed, x, z):
    """Smooth value noise in [0, 1) at real coordinates (lattice spacing 1)."""
    ix, iz = math.floor(x), math.floor(z)
    fx, fz = x - ix, z - iz
    a = _lattice(seed, ix, iz)
    b = _lattice(seed, ix + 1, iz)
    c = _lattice(seed, ix, iz + 1)
    d = _lattice(seed, ix + 1, iz + 1)
    u, v = _smooth(fx), _smooth(fz)
    return (a + (b - a) * u) * (1 - v) + (c + (d - c) * u) * v


def fbm2d(seed, x, z, octaves=4, lacunarity=2.0, gain=0.5):
    """Fractal sum of value noise octaves, normalized to [0, 1)."""
    seed = seed_from(seed)
    total, amp, freq, norm = 0.0, 1.0, 1.0, 0.0
    for o in range(octaves):
        total += amp * value2d(mix(seed, o), x * freq, z * freq)
        norm += amp
        amp *= gain
        freq *= lacunarity
    return total / norm


def heightfield(seed, width, depth, scale, octaves, lacunarity, gain):
    """[z][x] grid of fbm values in [0, 1)."""
    return [[fbm2d(seed, x / scale, z / scale, octaves, lacunarity, gain) for x in range(width)]
            for z in range(depth)]
