# Give the executing player a named, unbreakable diamond sword (item components, not NBT).
# Usage: execute as <player> run function example:reward
scoreboard players add #global example.calls 1
give @s minecraft:diamond_sword[minecraft:custom_name={text:"Reward",color:"gold",italic:false},minecraft:unbreakable={},minecraft:custom_data={example:{reward:1b}}] 1
