"""Rebuilds the whole Fisher Game environment in the scene 'FisherWorld'.

Run in Blender: Scripting tab -> open this file -> Run Script.
Only collections created by these scripts are cleared and rebuilt.
Pass ONLY = {"Home"} etc. to rebuild a single island.
"""
import bpy, os, sys, importlib

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else \
    os.path.join(os.path.expanduser("~"), "Documents/GitHub/blenderfiles/FisherGame_Environment/Scripts")
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import fg_lib, fg_assets, fg_world, fg_sea, island_home, island_fish, island_dealer, island_rod, island_cave
for m in (fg_lib, fg_assets, fg_world, fg_sea, island_home, island_fish, island_dealer, island_rod, island_cave):
    importlib.reload(m)

ONLY = globals().get("ONLY")
P, A = fg_world.build_base()
builders = {
    "Home": island_home.build,
    "Fish": island_fish.build,
    "Dealer": island_dealer.build,
    "Rod": island_rod.build,
    "Cave": island_cave.build,
}
for key, fn in builders.items():
    if ONLY and key not in ONLY:
        continue
    fn(P, A, fg_world.ISLANDS[key]["center"])
# open water details and easter eggs depend on the island terrains, so they always rebuild last
fg_sea.build_sea_details(P, A, fg_world.ISLANDS)
fg_sea.build_easter_eggs(P, A)
fg_sea.build_fishing_zones()
# fish gallery under the map (needs Blender/Models/Fish.blend from fish_build.build())
import fish_build
importlib.reload(fish_build)
if os.path.exists(fish_build.BLEND):
    fish_build.build_gallery()
print("Fisher Game environment built.")
