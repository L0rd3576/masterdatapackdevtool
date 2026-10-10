#!/usr/bin/env python3
"""Re-check factual claims from knowledge/ against the 26.3 jar output (generated/ + reference/vanilla-data/).

Usage: python tools/verify_knowledge.py        -> prints PASS/FAIL per claim, exit 1 if any FAIL.
Add a claim here whenever you add a checkable fact to knowledge/. Command-syntax claims are checked by
tools/diff_corpus.py against the live server instead.
"""
import json
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REP = os.path.join(ROOT, "generated", "reports")
VAN = os.path.join(ROOT, "reference", "vanilla-data", "minecraft")


def j(*p):
    with open(os.path.join(*p), encoding="utf-8") as f:
        return json.load(f)


DP = j(REP, "datapack.json")
REGS = {k.split(":", 1)[1]: set(x.split(":", 1)[1] for x in v["entries"]) for k, v in j(REP, "registries.json").items()}
CMDS = j(REP, "commands.json")
FOLDERS = {k.split(":", 1)[1] for k, v in DP["registries"].items() if v["elements"]} | set(DP["others"])
_text_cache = {}


def vanilla_text(sub):
    if sub not in _text_cache:
        parts = []
        for d, _, fs in os.walk(os.path.join(VAN, sub)):
            for f in fs:
                if f.endswith(".json"):
                    parts.append(open(os.path.join(d, f), encoding="utf-8").read())
        _text_cache[sub] = "\n".join(parts)
    return _text_cache[sub]


def count(sub, pattern):
    return len(re.findall(pattern, vanilla_text(sub)))


def cmd(*path):
    n = CMDS
    for p in path:
        n = n.get("children", {}).get(p)
        if n is None:
            return False
    return True


def version_json():
    jar = os.path.join(ROOT, "server", "versions", "26.3", "server-26.3.jar")
    with zipfile.ZipFile(jar) as z:
        return json.loads(z.read("version.json"))


V = version_json()


def vanilla_structures_ok():
    """Every vanilla structure: DataVersion 5023, palette entries keyed id/properties (not Name/Properties)."""
    sys.path.insert(0, os.path.join(ROOT, "tools", "mapgen"))
    import nbt
    n = 0
    for d, _, fs in os.walk(os.path.join(VAN, "structure")):
        for f in fs:
            if not f.endswith(".nbt"):
                continue
            root = nbt.to_plain(nbt.read_file(os.path.join(d, f)))
            pals = root.get("palettes") or [root.get("palette", [])]
            if root["DataVersion"] != 5023 or any("Name" in e or "id" not in e for p in pals for e in p):
                return False
            n += 1
    return n > 1000


def mapgen_config_blocks_exist():
    """Every exact block id in tools/mapgen/config.json (palettes + block classes) is a 26.3 block."""
    cfg = j(ROOT, "tools", "mapgen", "config.json")
    ids = set()
    for pal in cfg["palettes"].values():
        for v in pal.values():
            for e in (v if isinstance(v, list) else [v]):
                b = e["block"] if isinstance(e, dict) else e
                if isinstance(b, str) and b.startswith("minecraft:"):
                    ids.add(b.split("[")[0])
    for lst in cfg["blocks"].values():
        if isinstance(lst, list):
            ids |= {b for b in lst if "*" not in b}
    return ids and all(b.split(":", 1)[1] in REGS["block"] for b in ids)
CLAIMS = [
    ("pack-format.md", "26.3 data pack format is 121.0", lambda: (V["pack_version"]["data_major"], V["pack_version"]["data_minor"]) == (121, 0)),
    ("pack-format.md", "26.3 resource pack format is 97.1", lambda: (V["pack_version"]["resource_major"], V["pack_version"]["resource_minor"]) == (97, 1)),
    ("pack-format.md", "26.3 needs Java 25", lambda: V["java_version"] == 25),
    ("datapack-structure.md", "folder 'function' (singular) is valid; 'functions' is not", lambda: "function" in FOLDERS and "functions" not in FOLDERS),
    ("datapack-structure.md", "'loot_table','item_modifier','predicate','advancement','recipe' folders valid", lambda: {"loot_table", "item_modifier", "predicate", "advancement", "recipe"} <= FOLDERS),
    ("datapack-structure.md", "worldgen/feature + worldgen/carver exist; configured_feature/configured_carver do not", lambda: {"worldgen/feature", "worldgen/carver"} <= FOLDERS and not {"worldgen/configured_feature", "worldgen/configured_carver"} & FOLDERS),
    ("datapack-structure.md", "new element registries slot_source, context_int_provider, context_float_provider, world_clock, timeline, villager_trade, trade_set", lambda: {"slot_source", "context_int_provider", "context_float_provider", "world_clock", "timeline", "villager_trade", "trade_set"} <= FOLDERS),
    ("datapack-structure.md", "no 'number_provider' folder in 26.3", lambda: "number_provider" not in FOLDERS),
    ("commands.md", "gamerule IDs are snake_case: spawn_mobs/advance_time/keep_inventory exist, doMobSpawning/keepInventory do not", lambda: cmd("gamerule", "spawn_mobs") and cmd("gamerule", "advance_time") and cmd("gamerule", "keep_inventory") and not cmd("gamerule", "doMobSpawning") and not cmd("gamerule", "keepInventory")),
    ("commands.md", "new commands exist: compute, posteffect, swing, stopwatch, waypoint, dialog, fetchprofile", lambda: all(cmd(c) for c in ("compute", "posteffect", "swing", "stopwatch", "waypoint", "dialog", "fetchprofile"))),
    ("commands.md", "'item fill', 'item override' and 'execute if slots' exist", lambda: cmd("item", "fill") and cmd("item", "override") and cmd("execute", "if", "slots")),
    ("commands.md", "'tick' requires permission level admins (not usable in functions)", lambda: CMDS["children"]["tick"]["permissions"]["permission"]["level"] == "admins"),
    ("loot-predicates.md", "loot conditions: match_block, int_value_check, float_value_check exist; block_state_property, value_check, reference do not", lambda: {"match_block", "int_value_check", "float_value_check"} <= REGS["loot_condition_type"] and not {"block_state_property", "value_check", "reference"} & REGS["loot_condition_type"]),
    ("loot-predicates.md", "number providers: add/mul/min/max/avg exist, sum/product do not", lambda: {"add", "mul", "min", "max", "avg"} <= REGS["context_float_provider_type"] and not {"sum", "product"} & REGS["context_float_provider_type"]),
    ("loot-predicates.md", "vanilla loot tables never use keys 'functions'/'conditions'/'function'", lambda: count("loot_table", r'"(functions|conditions|function)"\s*:') == 0),
    ("loot-predicates.md", "vanilla loot tables use 'condition' and 'modifier'", lambda: count("loot_table", r'"condition"\s*:') > 100 and count("loot_table", r'"modifier"\s*:') > 100),
    ("loot-predicates.md", "loot 'tag' entries use 'items' (not 'name')", lambda: all('"items"' in m for m in re.findall(r'\{[^{}]*"type": "minecraft:tag"[^{}]*\}', vanilla_text("loot_table")))),
    ("loot-predicates.md", "entity predicates use 'minecraft:entity_type' and 'minecraft:type_specific/*' keys", lambda: count("advancement", r'"minecraft:entity_type"') > 0 and count("advancement", r'"minecraft:type_specific/') > 0),
    ("advancements.md", "recipe_unlocked trigger uses 'recipes'", lambda: count("advancement", r'"recipes"') > 0 and count("advancement", r'"recipe"\s*:') == 0),
    ("advancements.md", "advancement icons use 'id' (no 'item' key in vanilla advancements)", lambda: count("advancement", r'"icon":\s*\{\s*"item"') == 0 and count("advancement", r'"icon":\s*\{\s*"(count|components|id)"') > 0),
    ("item-components.md", "components attack_animation, interact_animation, block_transformer, cooking_fuel, brewing_fuel exist; swing_animation, map_color do not", lambda: {"attack_animation", "interact_animation", "block_transformer", "cooking_fuel", "brewing_fuel"} <= REGS["data_component_type"] and not {"swing_animation", "map_color"} & REGS["data_component_type"]),
    ("item-components.md", "custom_data, custom_name, item_name, lore, unbreakable, enchantments, attribute_modifiers, tooltip_display, item_model, consumable, food exist", lambda: {"custom_data", "custom_name", "item_name", "lore", "unbreakable", "enchantments", "attribute_modifiers", "tooltip_display", "item_model", "consumable", "food"} <= REGS["data_component_type"]),
    ("recipes.md", "only minecraft:brewing recipes use {\"item\": ...} objects (input/output); others use plain-string ingredients", lambda: all('"minecraft:brewing"' in t for t in vanilla_text("recipe").split("\n}\n") if re.search(r'\{\s*"(item|tag)"\s*:', t))),
    ("recipes.md", "recipe results use 'id'", lambda: count("recipe", r'"result":\s*\{\s*"(count|id|components)"') > 500),
    ("recipes.md", "26.3 adds recipe type minecraft:brewing", lambda: "brewing" in REGS["recipe_serializer"]),
    ("registries.md", "attribute IDs have no 'generic.' prefix", lambda: "max_health" in REGS["attribute"] and not any(a.startswith("generic.") for a in REGS["attribute"])),
    ("registries.md", "item 'iron_chain' exists and 'chain' does not", lambda: "iron_chain" in REGS["item"] and "chain" not in REGS["item"]),
    ("registries.md", "trim_material uses 'palette_id' (not 'asset_name')", lambda: count("trim_material", r'"palette_id"') > 0 and count("trim_material", r'"asset_name"') == 0),
    ("registries.md", "every vanilla timeline has a 'clock'", lambda: all('"clock"' in open(os.path.join(VAN, "timeline", f), encoding="utf-8").read() for f in os.listdir(os.path.join(VAN, "timeline")))),
    ("text-components.md", "vanilla data uses click_event/hover_event, never clickEvent/hoverEvent", lambda: count("dialog", r'"(clickEvent|hoverEvent)"') + count("advancement", r'"(clickEvent|hoverEvent)"') == 0),
    ("registries.md", "overworld dimension_type has attributes/timelines/default_clock and no effects/ultrawarm/piglin_safe", lambda: (lambda d: {"attributes", "timelines", "default_clock"} <= set(d) and not {"effects", "ultrawarm", "piglin_safe"} & set(d))(j(VAN, "dimension_type", "overworld.json"))),
    ("registries.md", "enchantment sharpness keys match the documented list", lambda: set(j(VAN, "enchantment", "sharpness.json")) == {"anvil_cost", "description", "effects", "exclusive_set", "max_cost", "max_level", "min_cost", "primary_items", "slots", "supported_items", "weight"}),
    ("functions.md", "commands needing admins/owners include tick, op, stop", lambda: all(CMDS["children"][c]["permissions"]["permission"]["level"] in ("admins", "owners") for c in ("tick", "op", "stop"))),
    ("loot-predicates.md", "item_modifier 'sequence' and number provider 'constant'/'storage' types exist", lambda: "sequence" in REGS["loot_function_type"] and {"constant", "storage"} <= REGS["context_float_provider_type"]),
    ("advancements.md", "trigger types tick, using_item, inventory_changed, impossible exist", lambda: {"tick", "using_item", "inventory_changed", "impossible"} <= REGS["trigger_type"]),
    ("advancements.md", "vanilla root advancements (no parent, with display) all have a background", lambda: all("background" in a["display"] for a in (j(d, f) for d, _, fs in os.walk(os.path.join(VAN, "advancement")) for f in fs) if "parent" not in a and "display" in a)),
    ("datapack-structure.md", "tags exist for function, block, item, entity_type, damage_type, enchantment", lambda: all(DP["registries"].get("minecraft:" + r, {}).get("tags") for r in ("block", "item", "entity_type", "damage_type", "enchantment")) and DP["others"]["function"]["tags"]),
    # mapgen / framework (knowledge/mapgen.md, knowledge/framework-contract.md)
    ("mapgen.md", "all vanilla structures: DataVersion 5023, palette entries {id, properties}", vanilla_structures_ok),
    ("mapgen.md", "overworld dimension_type min_y -64, height 384 (constants.py)", lambda: (lambda d: (d["min_y"], d["height"]) == (-64, 384))(j(VAN, "dimension_type", "overworld.json"))),
    ("mapgen.md", "'place template', 'forceload add' and 'schedule function' exist", lambda: cmd("place", "template") and cmd("forceload", "add") and cmd("schedule", "function")),
    ("mapgen.md", "no vanilla fake-player command: no 'player' root command", lambda: not cmd("player")),
    ("mapgen.md", "'dimension' is a datapack folder; biome the_void exists", lambda: "dimension" in FOLDERS and "the_void" in REGS.get("worldgen/biome", set()) | {f[:-5] for f in os.listdir(os.path.join(VAN, "worldgen", "biome"))}),
    ("mapgen.md", "flat world_preset generator: type minecraft:flat, settings biome/features/lakes/layers", lambda: (lambda g: g["type"] == "minecraft:flat" and {"biome", "features", "lakes", "layers"} <= set(g["settings"]))(j(VAN, "worldgen", "world_preset", "flat.json")["dimensions"]["minecraft:overworld"]["generator"])),
    ("mapgen.md", "attributes step_height, jump_strength, gravity, safe_fall_distance exist", lambda: {"step_height", "jump_strength", "gravity", "safe_fall_distance"} <= REGS["attribute"]),
    ("framework-contract.md", "entity types text_display, armor_stand, marker exist (labels, test stand-ins)", lambda: {"text_display", "armor_stand", "marker"} <= REGS["entity_type"]),
    ("framework-contract.md", "statistic 'minecraft.mined' criteria type exists (block_brawl wool counters)", lambda: "mined" in REGS["stat_type"]),
    ("mapgen.md", "every exact block id in tools/mapgen/config.json is a 26.3 block", mapgen_config_blocks_exist),
]


def main():
    bad = 0
    for i, (where, text, check) in enumerate(CLAIMS, 1):
        try:
            ok = bool(check())
        except Exception as e:  # noqa: BLE001
            ok = False
            text += f"  [error: {e}]"
        bad += not ok
        print(f"{'PASS' if ok else 'FAIL'} {i:2} [{where}] {text}")
    print(f"verify_knowledge: {len(CLAIMS) - bad}/{len(CLAIMS)} claims verified")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
