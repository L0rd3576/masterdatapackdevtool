"""Values fixed by Minecraft Java 26.3 itself (not tunable). Everything tunable lives in config.json.

Each constant names its source. [V] = verified this workspace (file or server run), [W] = Minecraft Wiki only.
"""

# [V] every one of the 1511 vanilla structure files in reference/vanilla-data/minecraft/structure/ has DataVersion 5023
DATA_VERSION = 5023

# [V] structure file keys in 26.3 vanilla files: size, entities, blocks, palette (or palettes), DataVersion;
# palette entries are {id, properties} (NOT the pre-26 Name/Properties); blocks are {pos, state, nbt?};
# entities are {pos (doubles), blockPos (ints), nbt}. Checked over all vanilla structures (knowledge/mapgen.md).
PALETTE_ID_KEY = "id"
PALETTE_PROPS_KEY = "properties"

# [V] reference/vanilla-data/minecraft/dimension_type/overworld.json: min_y -64, height 384
OVERWORLD_MIN_Y = -64
OVERWORLD_HEIGHT = 384

# [V] probe on the 26.3 server (knowledge/mapgen.md): attribute base values of a zombie (LivingEntity defaults);
# players use the same defaults for these attributes [W].
STEP_HEIGHT = 0.6
JUMP_STRENGTH = 0.42
GRAVITY = 0.08
SAFE_FALL_DISTANCE = 3.0

# [W] player hitbox (Minecraft Wiki "Player"): 0.6 wide, 1.8 tall (standing)
PLAYER_HEIGHT = 1.8
PLAYER_WIDTH = 0.6

# [V] vertical air drag per tick in LivingEntity travel (0.98) [W]; used only to compute the jump apex below.
VERTICAL_DRAG = 0.98


def jump_apex(jump_strength=JUMP_STRENGTH, gravity=GRAVITY, drag=VERTICAL_DRAG):
    """Max height gained by a standing jump, by simulating the per-tick motion (about 1.2522 blocks)."""
    y, v, best = 0.0, jump_strength, 0.0
    for _ in range(100):
        y += v
        best = max(best, y)
        v = (v - gravity) * drag
        if v <= 0 and y < best:
            break
    return best
