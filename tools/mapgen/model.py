"""In-memory block grid: sparse blocks (full block-state strings), block entities and entities.

Coordinates are local, 0 <= x < size[0] etc. A cell that was never set is "untouched": the structure writer
writes it as air when config structure.fill_air is true (so placing the map also clears leftovers, which the
restore logic relies on), otherwise leaves it out (structure void).
Block states are validated against the 26.3 block report and stored with every property filled in.
"""
import blocks

ROT_FACING = {"north": "east", "east": "south", "south": "west", "west": "north"}  # 90 degrees clockwise
MIRROR_X = {"east": "west", "west": "east"}       # flip along x (Minecraft Mirror.FRONT_BACK)
MIRROR_Z = {"north": "south", "south": "north"}   # flip along z (Minecraft Mirror.LEFT_RIGHT)


class Model:
    def __init__(self, size):
        if len(size) != 3 or min(size) < 1:
            raise ValueError(f"bad model size {size}")
        self.size = tuple(int(v) for v in size)
        self.blocks = {}          # key(x,y,z) -> full state string
        self.block_entities = {}  # key -> nbt-like dict (plain python, see structure_writer)
        self.entities = []        # [(x, y, z) floats, nbt dict]
        self._norm = {}

    # ------------------------------------------------------------------ basics
    def key(self, x, y, z):
        return (y * self.size[2] + z) * self.size[0] + x

    def unkey(self, k):
        sx, sz = self.size[0], self.size[2]
        return k % sx, k // (sx * sz), (k // sx) % sz

    def inside(self, x, y, z):
        return 0 <= x < self.size[0] and 0 <= y < self.size[1] and 0 <= z < self.size[2]

    def normalize(self, state):
        s = self._norm.get(state)
        if s is None:
            name, props = blocks.parse_state(state)
            errs = blocks.validate_state(name, props)
            if errs:
                raise ValueError("; ".join(errs))
            s = blocks.state_string(name, blocks.full_state(name, props))
            self._norm[state] = s
        return s

    def set(self, x, y, z, state, clip=False):
        if not self.inside(x, y, z):
            if clip:
                return
            raise IndexError(f"({x},{y},{z}) outside model size {self.size}")
        k = self.key(x, y, z)
        self.blocks[k] = self.normalize(state)
        self.block_entities.pop(k, None)

    def get(self, x, y, z):
        """Full state string, or None for an untouched cell (also outside the model)."""
        if not self.inside(x, y, z):
            return None
        return self.blocks.get(self.key(x, y, z))

    def name_at(self, x, y, z):
        s = self.get(x, y, z)
        return None if s is None else s.split("[", 1)[0]

    def clear(self, x, y, z):
        k = self.key(x, y, z)
        self.blocks.pop(k, None)
        self.block_entities.pop(k, None)

    def set_block_entity(self, x, y, z, nbt):
        k = self.key(x, y, z)
        if k not in self.blocks:
            raise ValueError("set the block before its block entity")
        self.block_entities[k] = nbt

    def add_entity(self, pos, nbt):
        self.entities.append((tuple(float(v) for v in pos), nbt))

    def positions(self):
        """All set positions in a stable order (y, then z, then x)."""
        return [self.unkey(k) for k in sorted(self.blocks)]

    # ------------------------------------------------------------------ operations
    @staticmethod
    def _span(a, b):
        return range(min(a, b), max(a, b) + 1)

    def fill(self, p1, p2, state, clip=False):
        s = self.normalize(state)
        for y in self._span(p1[1], p2[1]):
            for z in self._span(p1[2], p2[2]):
                for x in self._span(p1[0], p2[0]):
                    self.set(x, y, z, s, clip)

    def hollow(self, p1, p2, state, interior="minecraft:air", clip=False):
        """Shell of `state` (like /fill ... hollow); interior set to `interior` (None = leave as is)."""
        xs, ys, zs = self._span(p1[0], p2[0]), self._span(p1[1], p2[1]), self._span(p1[2], p2[2])
        for y in ys:
            for z in zs:
                for x in xs:
                    edge = x in (xs[0], xs[-1]) or y in (ys[0], ys[-1]) or z in (zs[0], zs[-1])
                    if edge:
                        self.set(x, y, z, state, clip)
                    elif interior is not None:
                        self.set(x, y, z, interior, clip)

    def walls(self, p1, p2, state, clip=False):
        """Vertical walls of a box (no floor or ceiling)."""
        xs, zs = self._span(p1[0], p2[0]), self._span(p1[2], p2[2])
        for y in self._span(p1[1], p2[1]):
            for z in zs:
                for x in xs:
                    if x in (xs[0], xs[-1]) or z in (zs[0], zs[-1]):
                        self.set(x, y, z, state, clip)

    def line(self, p1, p2, state, clip=False):
        """3D line (integer DDA, inclusive of both ends)."""
        n = max(abs(p2[i] - p1[i]) for i in range(3))
        for t in range(n + 1):
            pos = [p1[i] + (round((p2[i] - p1[i]) * t / n) if n else 0) for i in range(3)]
            self.set(*pos, state, clip)

    def column(self, x, z, y_top, top_state, fill_state, y_bottom=0, clip=True):
        """Column from y_bottom up to y_top (inclusive): fill_state below, top_state at the top."""
        for y in range(y_bottom, y_top):
            self.set(x, y, z, fill_state, clip)
        self.set(x, y_top, z, top_state, clip)

    def heightmap(self, heights, top_state, fill_state, y_bottom=0, origin=(0, 0)):
        """heights[z][x] = surface y; fills every column (clipped to the model)."""
        for dz, row in enumerate(heights):
            for dx, h in enumerate(row):
                self.column(origin[0] + dx, origin[1] + dz, int(h), top_state, fill_state, y_bottom)

    def transformed(self, rotation=0, mirror="none"):
        """Copy rotated clockwise (seen from above) by 0/90/180/270 after mirroring ("none", "x", "z").
        Rotates/mirrors `facing`, `axis` and `rotation` (0-15) block properties; other directional
        properties (e.g. stair `shape`, fence connections) are kept as is."""
        if rotation % 90 or mirror not in ("none", "x", "z"):
            raise ValueError("rotation must be a multiple of 90, mirror none/x/z")
        turns = (rotation // 90) % 4
        sx, sy, sz = self.size
        nsize = (sz, sy, sx) if turns % 2 else (sx, sy, sz)
        out = Model(nsize)

        def tpos(x, z):
            if mirror == "x":
                x = sx - 1 - x
            elif mirror == "z":
                z = sz - 1 - z
            w, d = sx, sz
            for _ in range(turns):
                x, z = d - 1 - z, x
                w, d = d, w
            return x, z

        def tstate(s):
            if "[" not in s:
                return s
            name, props = blocks.parse_state(s)
            if "facing" in props:
                f = props["facing"]
                f = (MIRROR_X if mirror == "x" else MIRROR_Z if mirror == "z" else {}).get(f, f)
                for _ in range(turns):
                    f = ROT_FACING.get(f, f)
                props["facing"] = f
            if "axis" in props and turns % 2 and props["axis"] in ("x", "z"):
                props["axis"] = "z" if props["axis"] == "x" else "x"
            if "rotation" in props and props["rotation"].isdigit():
                r = int(props["rotation"])
                if mirror == "x":
                    r = (16 - r) % 16
                elif mirror == "z":
                    r = (8 - r) % 16
                props["rotation"] = str((r + 4 * turns) % 16)
            return blocks.state_string(name, props)

        for k, s in self.blocks.items():
            x, y, z = self.unkey(k)
            nx, nz = tpos(x, z)
            out.blocks[out.key(nx, y, nz)] = tstate(s)
            if k in self.block_entities:
                out.block_entities[out.key(nx, y, nz)] = self.block_entities[k]
        for (x, y, z), nbt in self.entities:
            # entity positions are continuous: map the block cell, keep the offset inside the cell
            bx, bz = int(x // 1), int(z // 1)
            nx, nz = tpos(bx, bz)
            out.entities.append(((nx + (x - bx), y, nz + (z - bz)), nbt))
        return out

    def stamp(self, other, origin, rotation=0, mirror="none", skip_untouched=True, clip=False):
        """Copy `other` (optionally rotated/mirrored) into this model with its min corner at origin."""
        src = other.transformed(rotation, mirror) if (rotation or mirror != "none") else other
        ox, oy, oz = origin
        for k, s in src.blocks.items():
            x, y, z = src.unkey(k)
            if not self.inside(ox + x, oy + y, oz + z):
                if clip:
                    continue
                raise IndexError(f"stamp at {origin} leaves the model at ({ox + x},{oy + y},{oz + z})")
            nk = self.key(ox + x, oy + y, oz + z)
            self.blocks[nk] = s
            self.block_entities.pop(nk, None)
            if k in src.block_entities:
                self.block_entities[nk] = src.block_entities[k]
        for (x, y, z), nbt in src.entities:
            self.entities.append(((ox + x, oy + y, oz + z), nbt))

    # ------------------------------------------------------------------ queries used by validators/renderers
    def top_y(self, x, z, ignore=("minecraft:air",)):
        """Highest y whose block is set and not in `ignore`, or None."""
        for y in range(self.size[1] - 1, -1, -1):
            n = self.name_at(x, y, z)
            if n is not None and n not in ignore:
                return y
        return None
