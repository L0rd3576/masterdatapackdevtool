"""Model <-> 26.3 structure template (.nbt) conversion, plus tiling of large models.

Layout copied from the vanilla 26.3 files (see constants.py): root {size, entities, blocks, palette, DataVersion},
palette entries {id, properties?}, blocks {pos:[I;x,y,z as TAG_List of Int], state, nbt?},
entities {pos:[doubles], blockPos:[ints], nbt:{id,...}}.
Output is deterministic: palette in first-use order over positions sorted (y, z, x); gzip mtime 0.
"""
import blocks
import constants
import nbt
from model import Model


def plain_to_nbt(v):
    """Plain JSON-like value -> typed NBT (int->Int, float->Double, bool->Byte). Typed values pass through."""
    if isinstance(v, (nbt._Num, nbt.ByteArray, nbt.IntArray, nbt.LongArray)):
        return v
    if isinstance(v, bool):
        return nbt.Byte(1 if v else 0)
    if isinstance(v, int):
        return nbt.Int(v)
    if isinstance(v, float):
        return nbt.Double(v)
    if isinstance(v, str):
        return v
    if isinstance(v, dict):
        return {k: plain_to_nbt(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return nbt.List([plain_to_nbt(x) for x in v])
    raise TypeError(f"cannot convert {v!r} to NBT")


def to_nbt(model, fill_air=True, box=None):
    """Structure compound for the whole model or a sub-box ((x0,y0,z0),(x1,y1,z1) inclusive)."""
    (x0, y0, z0), (x1, y1, z1) = box or ((0, 0, 0), tuple(s - 1 for s in model.size))
    size = (x1 - x0 + 1, y1 - y0 + 1, z1 - z0 + 1)
    air = model.normalize("minecraft:air")
    palette, pidx, blist = [], {}, nbt.List(elem=nbt.TAG_COMPOUND)
    for y in range(y0, y1 + 1):
        for z in range(z0, z1 + 1):
            for x in range(x0, x1 + 1):
                k = model.key(x, y, z)
                s = model.blocks.get(k)
                if s is None:
                    if not fill_air:
                        continue
                    s = air
                i = pidx.get(s)
                if i is None:
                    i = pidx[s] = len(palette)
                    palette.append(s)
                entry = {"pos": nbt.List([nbt.Int(x - x0), nbt.Int(y - y0), nbt.Int(z - z0)]), "state": nbt.Int(i)}
                if k in model.block_entities:
                    entry["nbt"] = plain_to_nbt(model.block_entities[k])
                blist.append(entry)
    pal = nbt.List(elem=nbt.TAG_COMPOUND)
    for s in palette:
        name, props = blocks.parse_state(s)
        e = {constants.PALETTE_ID_KEY: name}
        if props:
            e[constants.PALETTE_PROPS_KEY] = {k: props[k] for k in sorted(props)}
        pal.append(e)
    ents = nbt.List(elem=nbt.TAG_COMPOUND)
    for (x, y, z), data in model.entities:
        if not (x0 <= x < x1 + 1 and y0 <= y < y1 + 1 and z0 <= z < z1 + 1):
            continue
        lx, ly, lz = x - x0, y - y0, z - z0
        ents.append({
            "pos": nbt.List([nbt.Double(lx), nbt.Double(ly), nbt.Double(lz)]),
            "blockPos": nbt.List([nbt.Int(int(lx // 1)), nbt.Int(int(ly // 1)), nbt.Int(int(lz // 1))]),
            "nbt": plain_to_nbt(data),
        })
    return {
        "size": nbt.List([nbt.Int(v) for v in size]),
        "entities": ents,
        "blocks": blist,
        "palette": pal,
        "DataVersion": nbt.Int(constants.DATA_VERSION),
    }


def write(model, path, fill_air=True, box=None):
    root = to_nbt(model, fill_air, box)
    nbt.write_file(path, root)
    return root


def from_nbt(root):
    """Structure compound -> Model (first palette if the file has several). Air is kept as set cells."""
    size = [v.v for v in root["size"]]
    m = Model(size)
    pal = root["palette"] if "palette" in root else root["palettes"][0]
    states = []
    for e in pal:
        name = e.get(constants.PALETTE_ID_KEY) or e.get("Name")  # Name/Properties = pre-26 files
        props = e.get(constants.PALETTE_PROPS_KEY) or e.get("Properties") or {}
        states.append(blocks.state_string(name, dict(props)))
    for b in root["blocks"]:
        x, y, z = (v.v for v in b["pos"])
        m.set(x, y, z, states[b["state"].v])
        if "nbt" in b:
            m.block_entities[m.key(x, y, z)] = nbt.to_plain(b["nbt"])
    for e in root["entities"]:
        m.entities.append((tuple(v.v for v in e["pos"]), nbt.to_plain(e["nbt"])))
    return m


def read(path):
    return from_nbt(nbt.read_file(path))


def tiles(size, tile):
    """Split a size into boxes of at most tile[0] x tile[1] x tile[2], bottom layer first (y, z, x order)."""
    out = []
    for y in range(0, size[1], tile[1]):
        for z in range(0, size[2], tile[2]):
            for x in range(0, size[0], tile[0]):
                out.append(((x, y, z), (min(x + tile[0], size[0]) - 1, min(y + tile[1], size[1]) - 1,
                                         min(z + tile[2], size[2]) - 1)))
    return out
