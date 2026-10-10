"""Writes the slice's *.test.json files (kept as a script so coordinates and helpers stay consistent).
Run: python examples/slice/tests/_make_tests.py   (then rebuild with tools/build_pack.py)"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def w(name, d):
    with open(os.path.join(HERE, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(d, indent=2) + "\n")


def stands(n):
    return [f'summon minecraft:armor_stand {2 * i} -60 2 {{Tags:["t.p"]}}' for i in range(n)] + \
        ["execute as @e[tag=t.p] run function slice:queue/join"]


CLEAN = ["kill @e[tag=t.p]", "scoreboard players reset * slice.coins", "tag @e remove slice.queued"]

w("a_registry.test.json", {
    "description": "build_pack compiled the pool: per-count candidate lists respect tags and player ranges; maps/games are in storage",
    "steps": [
        {"assert_data": {"source": "storage slice:registry", "path": "maps.shared_court.needs_restore", "equals": "1b"}},
        {"assert_data": {"source": "storage slice:registry", "path": "maps.duel_pit.origin", "equals": "{x:0,y:64,z:0}"}},
        {"assert_data": {"source": "storage slice:registry", "path": "games.pvp_arena.variants.pvp_quick.settings.kit", "equals": '"axe"'}},
        {"assert_data": {"source": "storage slice:registry", "path": "games.pvp_arena.variants.default.rules_lib.gamemode", "equals": '"adventure"'}},
        {"assert_data": {"source": "storage slice:registry", "path": "games.block_brawl.variants.default.rules_lib.gamemode", "equals": '"survival"'}},
        {"assert": 'unless data storage slice:registry by_count.n10[{value:{game:"pvp_arena"}}]'},
        {"assert": 'if data storage slice:registry by_count.n10[{value:{map:"maze_rooms"}}]'},
        {"assert": 'unless data storage slice:registry by_count.n3[{value:{map:"maze_rooms"}}]'},
        {"assert": 'unless data storage slice:registry by_count.n8[{value:{map:"duel_pit"}}]'},
        {"assert": 'if data storage slice:registry by_count.n6[{value:{map:"duel_pit",preset:"pvp_quick"}}]'},
        {"assert": "unless data storage slice:registry by_count.n2"},
        {"assert": "unless data storage slice:registry by_count.n11"},
        {"assert_output": {"command": "execute if data storage slice:registry by_count.n3[]", "contains": "Count: 5"}},
        {"assert_score": {"target": "#tiles_per_tick", "objective": "slice.cfg", "equals": 2}},
    ]})

w("b_pvp_round.test.json", {
    "description": "pvp_arena on duel_pit with 4 stand-ins: map placed over ticks, rules applied, teleported to spawns, "
                   "last standing wins, linear payout by participant count, rules reverted, stand-ins returned",
    "setup": ["gamerule keep_inventory false"] + stands(4),
    "steps": [
        {"run": 'function slice:round/start_with {game:"pvp_arena",map:"duel_pit",preset:"default"}'},
        {"assert_score": {"target": "#state", "objective": "slice.round", "equals": 1}},
        {"ticks": 4},
        {"assert_score": {"target": "#state", "objective": "slice.round", "equals": 2}},
        {"assert": "in slice:arena if block 0 64 0 minecraft:smooth_stone"},
        {"assert": "in slice:arena if block 0 65 0 minecraft:stone_bricks"},
        {"assert_output": {"command": "execute in slice:arena positioned 0 65 0 if entity @e[tag=t.p,dx=20,dy=1,dz=20]", "contains": "Count: 4"}},
        {"assert_output": {"command": "gamerule keep_inventory", "contains": "true"}},
        {"assert_score": {"target": "#n", "objective": "slice.round", "equals": 4}},
        {"assert_output": {"command": "scoreboard players get #global slice.rtimer", "matches": "has 2[0-9]{3} "}},
        {"run": "execute as @e[tag=t.p,limit=2] run function slice:round/eliminate"},
        {"ticks": 1},
        {"assert_score": {"target": "#state", "objective": "slice.round", "equals": 2}},
        {"run": "execute as @e[tag=t.p,tag=slice.alive,limit=1] run function slice:round/eliminate"},
        {"ticks": 1},
        {"assert_score": {"target": "#state", "objective": "slice.round", "equals": 0}},
        {"assert_output": {"command": "execute if entity @e[tag=t.p,scores={slice.coins=32}]", "contains": "Count: 1"}},
        {"assert_output": {"command": "execute if entity @e[tag=t.p,scores={slice.coins=2}]", "contains": "Count: 3"}},
        {"assert_output": {"command": "execute positioned 0 -60 2 if entity @e[tag=t.p,dx=8,dy=1,dz=0]", "contains": "Count: 4"}},
        {"assert_output": {"command": "gamerule keep_inventory", "contains": "false"}},
        {"assert": "if entity @e[tag=t.p] unless entity @e[tag=slice.in_round]"},
        {"assert_score": {"target": "#placed.duel_pit", "objective": "slice.round", "equals": 1}},
    ],
    "teardown": CLEAN})

w("c_brawl_restore.test.json", {
    "description": "block_brawl on shared_court: broken and placed blocks are restored after the round, dropped items "
                   "cleared, highest score wins the pot (10 x 3 participants), participation paid to all",
    "setup": stands(3),
    "steps": [
        {"run": 'function slice:round/start_with {game:"block_brawl",map:"shared_court",preset:"default"}'},
        {"ticks": 4},
        {"assert_score": {"target": "#state", "objective": "slice.round", "equals": 2}},
        {"assert": "in slice:arena if block 269 64 13 minecraft:gold_block"},
        {"run": "execute in slice:arena run setblock 269 64 13 minecraft:air"},
        {"run": "execute in slice:arena run setblock 261 65 5 minecraft:white_wool"},
        {"run": 'execute in slice:arena run summon minecraft:item 262 65 6 {Item:{id:"minecraft:white_wool",count:1}}'},
        {"assert": "in slice:arena if block 269 64 13 minecraft:air"},
        {"run": "scoreboard players set @e[tag=t.p,limit=1] slice.score 5"},
        {"run": "function slice:round/end"},
        {"assert_score": {"target": "#state", "objective": "slice.round", "equals": 4}},
        {"assert_output": {"command": "execute if entity @e[tag=t.p,scores={slice.coins=31}]", "contains": "Count: 1"}},
        {"assert_output": {"command": "execute if entity @e[tag=t.p,scores={slice.coins=1}]", "contains": "Count: 2"}},
        {"assert": "in slice:arena unless entity @e[type=minecraft:item,x=256,y=64,z=0,dx=26,dy=6,dz=26]"},
        {"ticks": 4},
        {"assert_score": {"target": "#state", "objective": "slice.round", "equals": 0}},
        {"assert": "in slice:arena if block 269 64 13 minecraft:gold_block"},
        {"assert": "in slice:arena if block 261 65 5 minecraft:air"},
    ],
    "teardown": CLEAN})

w("d_random_select.test.json", {
    "description": "round/start picks only compatible combinations for the queued count (10 -> block_brawl only, "
                   "3 -> never maze_rooms) and fails cleanly when nothing fits (2)",
    "setup": ["scoreboard objectives add t.s dummy"] + stands(10),
    "steps": [
        {"run": "function slice:round/start"},
        {"assert": 'if data storage slice:round current.game{id:"block_brawl"}'},
        {"assert_score": {"target": "#n", "objective": "slice.round", "equals": 10}},
        {"ticks": 4},
        {"run": "function slice:round/abort"},
        {"ticks": 4},
        {"assert_score": {"target": "#state", "objective": "slice.round", "equals": 0}},
        {"assert": "if entity @e[tag=t.p] unless entity @e[tag=slice.in_round]"},
        {"run": "kill @e[tag=t.p,limit=7]"},
        {"run": "execute as @e[tag=t.p] run function slice:queue/join"},
        {"run": "function slice:round/start"},
        {"assert": 'unless data storage slice:round current.map{id:"maze_rooms"}'},
        {"assert_score": {"target": "#n", "objective": "slice.round", "equals": 3}},
        {"ticks": 4},
        {"run": "function slice:round/abort"},
        {"ticks": 4},
        {"assert_score": {"target": "#state", "objective": "slice.round", "equals": 0}},
        {"run": "kill @e[tag=t.p,limit=1]"},
        {"run": "execute as @e[tag=t.p] run function slice:queue/join"},
        {"run": "execute store success score #ok t.s run function slice:round/start"},
        {"assert_score": {"target": "#ok", "objective": "t.s", "equals": 0}},
        {"assert": 'if data storage slice:round {last_error:"no minigame/map fits the participant count"}'},
        {"assert_score": {"target": "#state", "objective": "slice.round", "equals": 0}},
    ],
    "teardown": CLEAN})

w("e_preset_timer.test.json", {
    "description": "preset pvp_quick overrides settings (kit axe) and rules (60 s); when the round timer runs out every "
                   "survivor wins (linear 10 + 5 x 3, +2 participation), then shared_court is restored",
    "setup": stands(3),
    "steps": [
        {"run": 'function slice:round/start_with {game:"pvp_arena",map:"shared_court",preset:"pvp_quick"}'},
        {"ticks": 4},
        {"assert_score": {"target": "#state", "objective": "slice.round", "equals": 2}},
        {"assert_data": {"source": "storage slice:round", "path": "current.settings.kit", "equals": '"axe"'}},
        {"assert_data": {"source": "storage slice:round", "path": "current.rules.time_limit_seconds", "equals": "60"}},
        {"assert_output": {"command": "scoreboard players get #global slice.rtimer", "matches": "has 1[0-9]{3} "}},
        {"run": "scoreboard players set #global slice.rtimer 2"},
        {"ticks": 3},
        {"assert_output": {"command": "execute if entity @e[tag=t.p,scores={slice.coins=27}]", "contains": "Count: 3"}},
        {"ticks": 4},
        {"assert_score": {"target": "#state", "objective": "slice.round", "equals": 0}},
    ],
    "teardown": CLEAN})

w("f_gallery.test.json", {
    "description": "gallery/build places every pool map side by side in the arena dimension with 3 labels each",
    "steps": [
        {"run": "function slice:gallery/build"},
        {"ticks": 21},
        {"assert":"in slice:arena if block 0 64 4096 minecraft:smooth_stone"},
        {"assert_output": {"command": "execute if entity @e[type=minecraft:text_display,tag=slice.gallery]", "contains": "Count: 9"}},
    ]})
print("wrote tests")
