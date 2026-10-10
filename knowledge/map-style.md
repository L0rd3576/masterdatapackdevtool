# Map style notes (the user's approved aesthetic and constraints)

Read before authoring a map (skill `map-authoring`). Add one line per approved or corrected map, with the date.
Status: no map has been reviewed by the user yet. The lines below are Claude's own review of the slice maps
(2026-10-10, top-down renders read) and are defaults until the user confirms or corrects them.

## Defaults (unconfirmed)
- Small, readable arenas: 21-31 blocks across for 3-10 players. Spawns on a ring >= `spawns.min_spacing` (3) apart.
- Fully enclosed: walls at least 4 high around every walkable area, so nothing falls into the void (void_gaps = 0).
- One config palette per map (`config.json palettes`, by role: floor/floor_alt/wall/wall_top/obstacle/...).
  Examples: duel_pit `stone_arena` (smooth stone + polished andesite checker floor, stone-brick walls),
  maze_rooms `mossy_maze`. shared_court is a hand-made .nbt (sandstone-coloured walls in the render).
- Obstacles cover 5-10% of the floor, 1-3 high, never within 1 block of a spawn (`spawn_clearance`).
- Room mazes: 3x3 rooms with 3-wide corridors. Black (void) between rooms is fine when walls enclose every room.
- Observed weak spot: room_grid can put spawns against a wall corner (`S#` in maze_rooms.layers.txt). Acceptable
  for now. Raise the spawn margin if the user objects.

## User-approved
- (none yet)
