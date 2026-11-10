"""Single source of truth for the fish catalog: 122 fish, 6 rarities, 12 zones, 5 rod tiers, 10 mutations.

Both fish_catalog.md (fish_catalog_gen.py) and the 3D fish models (fish_models.py) are generated from this file,
so the documentation and the models can never drift apart. Lengths in cm, weights in kg, money in coins.
"""
import math

# ---------------------------------------------------------------- rarities

RARITIES = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythical"]
RARITY = {
    #               spawn weight, value mult, difficulty band, colour (UI), availability
    "Common":    dict(weight=100.0, mult=1,   diff=(5, 20),  ui="#9aa3ad", avail="Everywhere, all day. Most casts land one.",
                      visual="Natural, muted colours: silver, sand, olive, brown. Simple silhouettes.",
                      progression="Day 1 with the Starter Rod. Pays for bait, fuel and the first upgrades."),
    "Uncommon":  dict(weight=45.0,  mult=3,   diff=(18, 35), ui="#58b368", avail="Common in the right zone, a few per trip.",
                      visual="Stronger colours or one stand-out feature (stripe, spot, spines, odd shape).",
                      progression="Starter Rod catches the lighter ones; Coastline Rod catches all of them."),
    "Rare":      dict(weight=15.0,  mult=8,   diff=(33, 55), ui="#3d8bd9", avail="Needs the right zone; often time-of-day bound.",
                      visual="Bright patterns, special fins or unusual anatomy; many reef and deep-sea oddities.",
                      progression="Main target of the Reefrunner Rod and the first boat upgrade."),
    "Epic":      dict(weight=5.0,   mult=25,  diff=(52, 72), ui="#9b59d0", avail="Few per session, mostly zone-exclusive.",
                      visual="Big predators, deep-sea creatures and the first fantasy fish. Glow details allowed.",
                      progression="Mid/late game with the Stormcaller Rod; pays for the best boats."),
    "Legendary": dict(weight=1.2,   mult=80,  diff=(70, 88), ui="#f0a020", avail="A handful per play-through; often night or weather bound.",
                      visual="Iconic giants and quest fish. Strong silhouettes, recognisable from far away.",
                      progression="Endgame trophies. Leviathan Rod recommended, Stormcaller Rod possible."),
    "Mythical":  dict(weight=0.25,  mult=250, diff=(86, 98), ui="#e8457a", avail="Extremely rare, only in hidden zones and special conditions.",
                      visual="Fantasy creatures with glowing, crystal or golden parts. Unique silhouettes.",
                      progression="Collector goal after the main story. Even the Leviathan Rod needs skill here."),
}
BASE_COIN = 12   # value of an average Common fish with species factor 1.0

# ---------------------------------------------------------------- zones
# Positions are Blender world X/Y in metres (the FishingZone_* empties in the world FBX carry them into Unity).
# When zones overlap the one with the highest priority wins.

ZONES = {
    "HOME": dict(name="Home Lagoon", depth="Shallow (0-6 m)", priority=3,
                 anchors=[(-185, -120, 110)],
                 desc="Warm, sandy lagoon and beach around Home Island. Clear water, seagrass and the swim raft.",
                 env="Sand bottom, seagrass, gentle waves, lots of light. Calm at night.",
                 progression="Starting zone. Starter Rod is enough for everything except a few Rare fish."),
    "HARB": dict(name="Harbor Waters", depth="Shallow-Medium (2-12 m)", priority=4,
                 anchors=[(150, -119, 45), (123, 140, 50)],
                 desc="The working harbour of Fish Selling Island and the marina of Boat Dealer Island. Pilings, ropes and fish scraps.",
                 env="Muddy-sand bottom between dock pilings, scraps from the fish market attract scavengers.",
                 progression="Early game; good money for Common/Uncommon fish close to Ruben's shop."),
    "LIGHT": dict(name="Lighthouse Point", depth="Medium (6-30 m)", priority=5,
                  anchors=[(232, -182, 80)],
                  desc="Rough water under the cliffs of the lighthouse. At night the rotating beam sweeps the water.",
                  env="Rocky bottom, strong currents, cold water. Night: the beam attracts light-loving fish.",
                  progression="Early-mid game; night fishing here is part of quest Q5 (Lightfish)."),
    "KELP": dict(name="Kelp Rocks", depth="Shallow-Medium (3-18 m)", priority=3,
                 anchors=[(-190, 170, 110), (-30, 340, 80)],
                 desc="Kelp forests and boulders around the Rod Shop island and the coast of Teun's Rock.",
                 env="Dense kelp, rocks and crevices. Ambush hunters and camouflage specialists.",
                 progression="Early-mid game; Coastline Rod recommended for the bigger kelp fish."),
    "REEF": dict(name="Sunlit Reefs", depth="Shallow-Medium (2-20 m)", priority=4,
                 anchors=[(185, 200, 120), (10, -170, 30), (-210, 30, 30), (215, 25, 30), (95, 300, 30), (-120, 330, 30)],
                 desc="Tropical shallows around Boat Dealer Island and the rocky reefs (Sea_Reef_*) that break the surface.",
                 env="Warm, bright, colourful. Rocks covered in growth, many small territorial fish.",
                 progression="Mid game; the Reefrunner Rod is built for this zone."),
    "OPEN": dict(name="Open Ocean", depth="Medium (20-60 m)", priority=1,
                 anchors=[(0, 0, 330)],
                 desc="The blue water between the islands, including the fish schools at Sea_FishingSpot_1..8 and the centre beacon.",
                 env="Open water, fast pelagic hunters following bait schools. Birds show where fish are.",
                 progression="Whole game; the default zone wherever no other zone applies inside the islands' ring."),
    "DEEP": dict(name="The Drop (Deep Ocean)", depth="Deep (60-400 m)", priority=0,
                 anchors=[(0, 0, 9999)],
                 desc="The outer ring of the map, farther than ~330 m from the centre beacon, where the seabed falls away.",
                 env="Dark, cold, high pressure. Bioluminescent fish, giant predators. Heavy swell.",
                 progression="Late game; needs a bigger boat and the Stormcaller Rod."),
    "WRECK": dict(name="Shipwreck Graveyard", depth="Medium-Deep (15-40 m)", priority=8,
                  anchors=[(-360, 300, 60)],
                  desc="Hidden zone around the sunken ship in the north-west (EE_Shipwreck).",
                  env="Rotting timbers, cannons and a treasure chest. Ambush predators hide in the hull.",
                  progression="Hidden; reachable mid game but its Epic/Legendary fish need a strong rod."),
    "GROTTO": dict(name="Teun's Grotto", depth="Cave pool (special)", priority=10,
                   anchors=[(-30, 350, 6)],
                   desc="The glowing pool inside Teun's cave (Cave_Pool_FishingSpot). Unlocked by quest Q6.",
                   env="Still, glowing water lit by crystals. Very few fish, all of them special.",
                   progression="Story zone: Zilverkoning (Q7) lives here."),
    "ABYSS": dict(name="Serpent's Abyss", depth="Abyssal (400 m+)", priority=9,
                  anchors=[(380, 395, 70)],
                  desc="Hidden trench in the far north-east, where the sea serpent shows its back (EE_SeaSerpent).",
                  env="Pitch black water, strange currents. Only the bravest boats survive the swell.",
                  progression="Endgame. Leviathan Rod strongly recommended."),
    "TREASURE": dict(name="Treasure Shoal", depth="Shallow (1-8 m)", priority=9,
                     anchors=[(380, -385, 45)],
                     desc="Hidden sand shoal around the tiny islet with the red X (EE_TreasureIslet).",
                     env="Turquoise shallows, white sand, coins glinting on the bottom.",
                     progression="Hidden; easy fish plus one Mythical."),
    "DUCK": dict(name="Duck Drift", depth="Medium (10-30 m)", priority=9,
                 anchors=[(-390, -380, 45)],
                 desc="Hidden easter-egg zone around the giant rubber duck in the south-west (EE_RubberDuck).",
                 env="Calm, oddly cheerful water. Things float here that should not float.",
                 progression="Hidden; mostly open-ocean fish plus one very silly Mythical."),
}
ZONE_ORDER = ["HOME", "HARB", "LIGHT", "KELP", "REEF", "OPEN", "DEEP", "WRECK", "GROTTO", "ABYSS", "TREASURE", "DUCK"]

# ---------------------------------------------------------------- rods (gameplay only, models are made by the team)

RODS = [
    dict(tier=1, name="Starter Rod", power=25, luck=0, bonus=0, price="Free",
         zones=["HOME", "HARB"],
         unlock="Given by Mark at the start of quest Q1 (the 'bamboo rod' Teun sends you for).",
         role="Learn the minigame. Catches all Common fish and the lighter Uncommon fish."),
    dict(tier=2, name="Coastline Rod", power=42, luck=5, bonus=10, price="450",
         zones=["HOME", "HARB", "KELP", "LIGHT", "REEF"],
         unlock="Sold by Mark after quest Q2 (first sale to Ruben).",
         role="All Uncommon fish and the first Rare ones along the coasts."),
    dict(tier=3, name="Reefrunner Rod", power=60, luck=12, bonus=25, price="2,500",
         zones=["HOME", "HARB", "KELP", "LIGHT", "REEF", "OPEN", "WRECK", "TREASURE", "DUCK"],
         unlock="Sold by Mark after quest Q4 (you own a better boat) and 25 species in the journal.",
         role="Workhorse of the mid game: all Rare fish and the lighter Epic fish."),
    dict(tier=4, name="Stormcaller Rod", power=78, luck=20, bonus=45, price="7,500",
         zones=["all except ABYSS"],
         unlock="Sold by Mark after quest Q6 (Teun's sea chart) and 60 species in the journal.",
         role="All Epic fish, most Legendary fish. Needed for The Drop and Teun's Grotto."),
    dict(tier=5, name="Leviathan Rod", power=92, luck=30, bonus=70, price="25,000",
         zones=["all"],
         unlock="Sold by Mark after quest Q7 (Zilverkoning caught) and 3 Legendary fish in the journal.",
         role="Best rod. Every fish can be hooked, but Mythical fish (difficulty 86-98) still fight above its power."),
]

# ---------------------------------------------------------------- mutations (separate layer on top of rarity)

MUTATIONS = [
    dict(name="Albino", chance=250, mult=2.0, cond="Any zone, any time.",
         look="Body and fins pure white to pale pink, eyes red. Pattern faintly visible.",
         special="Size/weight unchanged. First mutation most players see.",
         model="Swap every body/fin material for M_Mut_Albino (white, slightly pink fins); eye material -> red."),
    dict(name="Shadow", chance=400, mult=2.5, cond="Night only.",
         look="Near-black body with deep purple fins; eyes glow faint violet.",
         special="Only rolls at night. Slightly faster fight (+5 difficulty).",
         model="Body/fins -> M_Mut_Shadow (black, purple fins), eyes -> emissive violet."),
    dict(name="Glowing", chance=350, mult=3.0, cond="Night, or any time in The Drop / Serpent's Abyss.",
         look="Pattern and fin edges glow cyan; the fish lights up the water around it.",
         special="Visible from the boat at night (small point light in Unity).",
         model="Pattern/accent materials -> emissive cyan M_Mut_Glow; add a small point light (range ~2x fish length)."),
    dict(name="Golden", chance=600, mult=5.0, cond="Any zone, any time.",
         look="Polished gold body, brighter gold fins, metallic shine.",
         special="Weight +10% (gold is heavy). Classic collector mutation.",
         model="All body/fin materials -> M_Mut_Golden (metallic 1.0, roughness 0.25)."),
    dict(name="Radioactive", chance=1500, mult=4.0, cond="After a storm, any zone.",
         look="Toxic green body with glowing yellow-green blotches.",
         special="Cannot be eaten in future cooking systems; worth more to collectors.",
         model="Body -> M_Mut_Radioactive (green), pattern faces -> emissive lime; optional faint green particles."),
    dict(name="Crystal", chance=1200, mult=6.0, cond="Any zone; 5x more likely in Teun's Grotto.",
         look="Translucent ice-blue body with faceted crystal shards growing from the back.",
         special="Weight +30%. Shards make it instantly recognisable.",
         model="Body -> transparent M_Mut_Crystal; add 3-6 crystal shard cones along the dorsal line (as in the preview)."),
    dict(name="Ancient", chance=2000, mult=8.0, cond="Shipwreck Graveyard and The Drop only.",
         look="Bronze/stone coloured body covered in bony plates, like a living fossil.",
         special="Size +25%, weight +40%. Heaviest possible version of any species.",
         model="Body -> M_Mut_Ancient (bronze stone); add bony plate boxes on the back; scale model by 1.25."),
    dict(name="Ghost", chance=3000, mult=7.0, cond="Night, Shipwreck Graveyard 4x more likely.",
         look="Pale, see-through body; only the skeleton line and eyes are solid.",
         special="Weight -50% (barely there).",
         model="Body/fins -> transparent M_Mut_Ghost (alpha ~0.35); keep eyes opaque."),
    dict(name="Rainbow", chance=5000, mult=12.0, cond="Any zone during or right after rain.",
         look="Every band of the fish a different colour of the rainbow, shimmering.",
         special="Cannot combine with other mutations (it replaces them).",
         model="Assign rainbow materials per pattern band/fin (red-orange-yellow-green-blue-violet)."),
    dict(name="Celestial", chance=20000, mult=25.0, cond="Clear night only; 3x more likely in Serpent's Abyss.",
         look="Deep night-blue body sprinkled with glowing stars; fins fade into a nebula purple.",
         special="Rarest mutation. Shows a star trail when reeled in.",
         model="Body -> M_Mut_Celestial (dark blue) + emissive star dots; fins -> purple gradient."),
]

# ---------------------------------------------------------------- fish

FISH = []


def fish(name, rarity, family, plan, size, weight, zones, desc, special, look, abundance=1.0, factor=None):
    FISH.append(dict(name=name, rarity=rarity, family=family, plan=plan, size=size, weight=weight, zones=zones,
                     desc=desc, special=special, look=look, abundance=abundance, factor=factor))


def L(tail, dorsal, colors, pattern="plain", extras=(), anal="std", pect="std", eye=1.0, **shape):
    """Model look: tail/dorsal/anal/pectoral types, (back, belly, fin, accent) colours, pattern, extras."""
    return dict(tail=tail, dorsal=dorsal, anal=anal, pect=pect, colors=colors, pattern=pattern,
                extras=list(extras), eye=eye, shape=shape)


# ---------- Common (36)
C = "Common"
fish("Sand Goby", C, "Goby", "fusiform", (4, 10), (0.005, 0.03), ["HOME", "HARB"],
     "Tiny bottom-dweller that hides in the sand of the Home lagoon.", "Often caught by accident; great bait fish.",
     L("rounded", "double", ("#c9b38a", "#efe3c8", "#b09a70", "#7a6648"), "spots", eye=1.5, hmax=0.11, a=0.5))
fish("Silver Sprat", C, "Herring", "slim", (8, 16), (0.01, 0.04), ["OPEN", "HOME", "HARB", "DUCK"],
     "Small silver schooling fish; the food of almost everything else.", "Comes in schools: catching one makes the next cast faster.",
     L("forked", "single", ("#7f9aab", "#eef2f4", "#a7b9c2", "#5d7686"), "gradient"), abundance=1.4)
fish("Atlantic Mackerel", C, "Mackerel", "fusiform", (25, 45), (0.3, 1.2), ["OPEN", "HARB", "LIGHT"],
     "Fast, striped open-water fish that bites on almost anything.", "Finlets between dorsal fin and tail.",
     L("forked", "double", ("#2f6b5e", "#e6ece6", "#41675a", "#16362f"), "wavy", ["finlets"]), abundance=1.2)
fish("Harbor Sardine", C, "Sardine", "slim", (12, 22), (0.05, 0.15), ["HARB", "OPEN"],
     "Oily little fish that gathers around the fish market's pilings.", "Row of dark spots along the flank.",
     L("forked", "single", ("#4d6f8f", "#e9edf1", "#8ea4b8", "#22344a"), "spot_row"), abundance=1.3)
fish("Common Bream", C, "Bream", "compressed", (25, 50), (0.4, 2.5), ["HOME", "HARB"],
     "Tall, bronze bottom-feeder that cruises the lagoon in slow groups.", "Very tall, flat body.",
     L("forked", "single", ("#9a8a5a", "#d8cfa8", "#6d6448", "#5b4f30"), "gradient", hmax=0.24))
fish("Striped Mullet", C, "Mullet", "fusiform", (30, 60), (0.5, 3.0), ["HOME", "HARB"],
     "Grey mullet with dark lines; jumps out of the water when startled.", "Blunt head, two separate dorsal fins.",
     L("forked", "double", ("#6f7d86", "#e3e6e6", "#7d8a92", "#3f4a52"), "stripes_h", a=0.45))
fish("Sandy Flounder", C, "Flounder", "flatfish", (20, 45), (0.2, 1.5), ["HOME"],
     "Flat fish that lies on the sand with both eyes on its upper side.", "Camouflaged: harder to spot, easier to reel.",
     L("rounded", "long", ("#a8916a", "#f2ecdf", "#9a845e", "#6e5a3a"), "spots", anal="long"))
fish("Blue Tang", C, "Surgeonfish", "compressed", (15, 30), (0.2, 0.6), ["REEF", "TREASURE"],
     "Bright blue reef fish with a yellow tail.", "Sharp scalpel spine at the base of the tail.",
     L("truncate", "long", ("#2e5fb5", "#3a6ec4", "#1f3f80", "#f2c230"), "tail_accent", anal="long", hmax=0.22))
fish("Sergeant Major", C, "Damselfish", "compressed", (10, 20), (0.05, 0.2), ["REEF", "HARB", "TREASURE"],
     "Yellow-and-black banded little fish that defends its patch of reef.", "Five black vertical bands.",
     L("forked", "single", ("#d9cf5a", "#f1f0e0", "#bdb36a", "#262620"), "bands"))
fish("Rock Blenny", C, "Blenny", "blenny", (6, 15), (0.01, 0.06), ["KELP", "LIGHT"],
     "Big-eyed little rock-hopper with a fringed crest on its head.", "Can survive out of water for minutes.",
     L("rounded", "long", ("#6b5a45", "#b8a888", "#7a6650", "#3e3226"), "mottled", ["crest"], eye=1.6))
fish("Green Wrasse", C, "Wrasse", "fusiform", (15, 35), (0.1, 0.8), ["KELP", "REEF"],
     "Green, slightly speckled wrasse that pecks at the kelp.", "Changes from green to brown as it grows.",
     L("truncate", "long", ("#3f8a5a", "#cfe3b0", "#4f9a68", "#24583a"), "spots"))
fish("Pollock", C, "Cod", "fusiform", (40, 80), (0.8, 5.0), ["OPEN", "LIGHT", "DEEP", "WRECK"],
     "Olive cod relative that hunts along the lighthouse cliffs.", "Three dorsal fins, protruding lower jaw.",
     L("truncate", "triple", ("#4a5a3a", "#d9dccb", "#5a6a48", "#2e3a24"), "gradient", anal="double"))
fish("Whiting", C, "Cod", "slim", (25, 45), (0.2, 1.0), ["HOME", "OPEN"],
     "Pale sandy cod that feeds over sand at dusk.", "Most active in the evening.",
     L("truncate", "triple", ("#b3a68a", "#efece2", "#a8997a", "#7a6d52"), "gradient", anal="double"))
fish("Kelp Bass", C, "Sea bass", "fusiform", (25, 55), (0.4, 3.0), ["KELP"],
     "Chunky brown bass that ambushes from the kelp.", "Spiny first dorsal fin.",
     L("truncate", "spiny", ("#5a4a33", "#cbbf95", "#6b5a3e", "#2e2618"), "spots", hmax=0.15))
fish("Pinfish", C, "Porgy", "compressed", (12, 25), (0.05, 0.3), ["HOME", "HARB"],
     "Silvery panfish with thin yellow lines; steals bait constantly.", "Notorious bait thief.",
     L("forked", "spiny", ("#b8b8a0", "#eceadc", "#c9c08a", "#e0c860"), "stripes_h"), abundance=1.2)
fish("Bluestriped Grunt", C, "Grunt", "fusiform", (20, 40), (0.2, 1.0), ["REEF"],
     "Yellow reef fish with blue lines that grunts when caught.", "Makes a grunting sound (audio hook).",
     L("forked", "spiny", ("#d9b740", "#efe2a0", "#c9a838", "#3f6db0"), "stripes_h", hmax=0.15))
fish("Hardhead Catfish", C, "Sea catfish", "flat", (25, 50), (0.3, 2.5), ["HARB"],
     "Whiskered scavenger that lives under the harbour docks.", "Barbels; stiff spines on dorsal and pectoral fins.",
     L("forked", "spine", ("#6e6a62", "#d6d2c6", "#5e5a52", "#3a3832"), "gradient", ["barbels"]))
fish("Garfish", C, "Needlefish", "slim", (40, 80), (0.3, 1.2), ["HOME", "OPEN"],
     "Long, thin fish with a needle-like beak and green bones.", "Leaps over the surface; green bones.",
     L("forked", "rear", ("#3f6f74", "#dfe8e6", "#4f8085", "#24464a"), "gradient", ["beak"], anal="rear", hmax=0.06, wmax=0.05))
fish("Sand Eel", C, "Sandlance", "eel", (10, 25), (0.01, 0.05), ["HOME"],
     "Shiny little eel-like fish that dives head-first into sand.", "Burrows: only bites near sandy bottom.",
     L("forked", "long", ("#9fb0b8", "#eef2f2", "#b5c2c8", "#6f8088"), "gradient"), abundance=1.2)
fish("Cunner", C, "Wrasse", "fusiform", (15, 30), (0.1, 0.6), ["KELP"],
     "Reddish-brown mottled wrasse of the rocky coast.", "Very common under the Rod Shop dock.",
     L("rounded", "long", ("#8a5a40", "#d9b89a", "#7a4e38", "#4e3222"), "mottled", hmax=0.15))
fish("Atlantic Silverside", C, "Silverside", "slim", (8, 15), (0.01, 0.03), ["HOME", "HARB"],
     "Translucent green fish with a bright silver side stripe.", "Two small dorsal fins far back.",
     L("forked", "double", ("#8fb3a0", "#eef4ee", "#a8c6b6", "#e8eef0"), "stripes_h", eye=1.4))
fish("Atlantic Herring", C, "Herring", "fusiform", (20, 40), (0.1, 0.6), ["OPEN", "DUCK"],
     "Blue-backed herring that travels in huge schools.", "Great for selling in bulk.",
     L("forked", "single", ("#3e5f80", "#e9eef2", "#6d86a0", "#1f3248"), "gradient"), abundance=1.3)
fish("Bay Anchovy", C, "Anchovy", "slim", (5, 10), (0.003, 0.01), ["HARB", "HOME"],
     "Tiny, see-through fish with a huge mouth for its size.", "Smallest fish in the game.",
     L("forked", "single", ("#aebfc0", "#f0f4f4", "#c3d0d0", "#d8e2e2"), "gradient", eye=1.6))
fish("Sheepshead", C, "Porgy", "compressed", (30, 60), (1.0, 7.0), ["HARB"],
     "Convict-striped porgy with human-like teeth that crunches barnacles off pilings.", "Teeth; strong bite steals bait.",
     L("forked", "spiny", ("#c9c9c0", "#ecebe6", "#8a8a80", "#24241f"), "bands", ["teeth"], hmax=0.22))
fish("Shore Rockling", C, "Rockling", "eel", (15, 30), (0.05, 0.3), ["KELP", "LIGHT", "WRECK"],
     "Slender brown rockling with three whiskers on its snout.", "Three barbels; hides in rock pools.",
     L("rounded", "long", ("#6a4e36", "#c8ae8a", "#5e4430", "#3a2a1c"), "mottled", ["barbels"], hmax=0.07, wmax=0.06))
fish("Yellowtail Snapper", C, "Snapper", "fusiform", (25, 50), (0.3, 2.0), ["REEF", "OPEN"],
     "Blue-grey snapper with a yellow line and a bright yellow tail.", "Deeply forked yellow tail.",
     L("forked", "spiny", ("#9aa6bc", "#e6eaf0", "#e8c640", "#e8c640"), "stripe_tail"))
fish("Painted Comber", C, "Sea bass", "fusiform", (15, 30), (0.1, 0.4), ["KELP", "REEF"],
     "Small bass with dark bands and a blue belly patch.", "Defends a small territory.",
     L("truncate", "spiny", ("#b07a50", "#5a7ab0", "#a06a44", "#3e2a1c"), "bands"))
fish("Lesser Weever", C, "Weever", "fusiform", (10, 15), (0.02, 0.05), ["HOME"],
     "Sand-coloured fish that buries itself, with a black venomous dorsal fin.", "Venomous: handle with care (short stun on catch).",
     L("truncate", "spiny_black", ("#c2ac80", "#efe4cc", "#b09a70", "#1a1a1a"), "spots", eye=1.3, a=0.6))
fish("Horse Mackerel", C, "Jack", "fusiform", (20, 40), (0.2, 0.8), ["OPEN", "HARB"],
     "Jack with a line of bony scutes along its side.", "Lateral line of scutes.",
     L("forked", "double", ("#5e7a8a", "#e4eaee", "#7f96a4", "#3a4e5a"), "stripes_h", ["scutes_side"]))
fish("Grey Triggerfish", C, "Triggerfish", "diamond", (25, 45), (0.5, 2.5), ["LIGHT", "REEF"],
     "Diamond-shaped grey fish that locks its first dorsal spine like a trigger.", "Trigger spine; tough skin.",
     L("lunate", "trigger", ("#7d8790", "#c8ced2", "#6d7780", "#4a525a"), "mottled", anal="tall"))
fish("Common Dab", C, "Flatfish", "flatfish", (15, 30), (0.1, 0.4), ["HOME", "HARB"],
     "Small, rough-skinned flatfish of sandy bays.", "Bites best on an incoming tide.",
     L("rounded", "long", ("#b09a74", "#f2ece0", "#a08a66", "#7a6646"), "spots", anal="long"), abundance=1.1)
fish("Gilthead Seabream", C, "Bream", "compressed", (25, 55), (0.4, 3.0), ["HARB", "HOME"],
     "Silver bream with a golden band between the eyes.", "Gold band on the forehead.",
     L("forked", "spiny", ("#a7b0b6", "#eef0f0", "#8a949a", "#e0b840"), "head_band", hmax=0.21))
fish("Red Mullet", C, "Goatfish", "fusiform", (15, 30), (0.1, 0.5), ["HOME", "REEF"],
     "Pink-red bottom feeder that searches the sand with two chin whiskers.", "Two chin barbels.",
     L("forked", "double", ("#d0605a", "#f2d4c8", "#d8786a", "#e8b040"), "stripes_h", ["chin_barbels"]))
fish("Spotted Catshark", C, "Catshark", "shark", (50, 80), (0.8, 2.0), ["LIGHT", "KELP"],
     "Small, sand-coloured shark covered in dark spots.", "Smallest shark; lays 'mermaid's purse' eggs.",
     L("heterocercal", "shark_low", ("#b49a70", "#eadfc8", "#a68c62", "#4a3a26"), "spots", ["gills"], anal="shark"))
fish("Sharpnose Puffer", C, "Puffer", "round", (8, 12), (0.02, 0.08), ["REEF", "HARB"],
     "Little spotted puffer that inflates into a ball when caught.", "Inflates on catch (animation hook).",
     L("rounded", "small", ("#c88a50", "#f4ead8", "#d8a060", "#3a6ab0"), "spots", eye=1.4))
fish("Seaweed Pipefish", C, "Pipefish", "pipefish", (15, 35), (0.005, 0.02), ["KELP", "HOME"],
     "Stick-thin relative of the seahorse that hides between seaweed.", "Males carry the eggs.",
     L("fan", "small", ("#7a8a40", "#c8c890", "#8a9a50", "#4a5a28"), "bands"))

# ---------- Uncommon (30)
U = "Uncommon"
fish("Atlantic Cod", U, "Cod", "fusiform", (50, 120), (2, 20), ["OPEN", "LIGHT", "DEEP"],
     "Big-headed, speckled cod: the classic North Atlantic catch.", "Chin barbel; three dorsal fins.",
     L("truncate", "triple", ("#7a7448", "#e6e2cc", "#6a6440", "#4a4428"), "spots", ["chin_barbel"], anal="double", hmax=0.14))
fish("European Seabass", U, "Sea bass", "fusiform", (35, 80), (0.6, 7), ["LIGHT", "HARB"],
     "Silver predator that hunts in the white water at the cliffs.", "Bites best in rough weather.",
     L("forked", "double", ("#7c8e9c", "#eef1f3", "#8a9aa6", "#3e4c58"), "gradient"))
fish("Red Snapper", U, "Snapper", "fusiform", (40, 90), (1.5, 12), ["REEF", "OPEN"],
     "Rose-red snapper prized by Ruben's customers.", "High selling demand at the fish market.",
     L("truncate", "spiny", ("#c84a40", "#f2c4b8", "#b83a30", "#8a2a22"), "gradient", hmax=0.16), factor=1.15)
fish("Lookdown", U, "Jack", "lookdown", (20, 40), (0.3, 2.0), ["HARB", "OPEN"],
     "Mirror-silver fish with an absurdly steep forehead and trailing fin filaments.", "Almost invisible from the side.",
     L("forked", "filament", ("#c8d2d8", "#f2f5f6", "#b8c2c8", "#909aa0"), "plain", anal="filament", eye=1.3))
fish("Porcupinefish", U, "Puffer", "round", (25, 50), (1, 3), ["REEF", "KELP"],
     "Spiny puffer with big friendly eyes; puffs up into a spiky ball.", "Covered in spines.",
     L("rounded", "small", ("#c8b080", "#f2ead8", "#b8a070", "#3a2e1e"), "spots", ["spikes"], eye=1.5))
fish("Green Moray", U, "Moray", "eel", (80, 180), (2, 15), ["KELP", "LIGHT", "WRECK"],
     "Thick green eel that lives in holes and shows its teeth.", "Bites back: line tension spikes.",
     L("eel", "long", ("#4a7a3a", "#6a9a4a", "#3e6a30", "#2a4a20"), "plain", ["teeth"], anal="long", pect="none", hmax=0.07, wmax=0.06))
fish("Bonito", U, "Tuna", "fusiform", (45, 80), (2, 8), ["OPEN", "DUCK"],
     "Small tuna with dark diagonal stripes on its back.", "Very fast first run.",
     L("lunate", "double", ("#2e4a6a", "#e8ecf0", "#3a5470", "#16283a"), "diag", ["finlets"]))
fish("Southern Stingray", U, "Stingray", "ray", (60, 150), (10, 80), ["HOME", "HARB"],
     "Diamond-shaped ray that glides over the sand of the lagoon.", "Tail barb; size = disc width.",
     L("whip", "none", ("#8a7a60", "#f0ece4", "#7a6a50", "#5a4a36"), "plain", ["barb"], anal="none", pect="none", round=0.7))
fish("Scorpionfish", U, "Scorpionfish", "fusiform", (20, 45), (0.3, 2), ["KELP", "LIGHT"],
     "Ugly, camouflaged ambush hunter with skin flaps and venomous spines.", "Venomous spines; perfect camouflage.",
     L("rounded", "spiny", ("#a0503a", "#d8a088", "#8a4030", "#5a2a1e"), "mottled", ["tabs"], hmax=0.15, wmax=0.12, a=0.4))
fish("Great Barracuda", U, "Barracuda", "slim", (60, 150), (3, 25), ["OPEN", "REEF"],
     "Long silver predator with an underbite full of fangs.", "Teeth: can cut weak lines.",
     L("forked", "double_far", ("#7e8c96", "#eef0f2", "#6e7c86", "#2e3a42"), "bars", ["teeth"], hmax=0.075, wmax=0.06, a=1.2))
fish("Parrotfish", U, "Parrotfish", "fusiform", (30, 70), (1, 7), ["REEF", "TREASURE"],
     "Turquoise-and-pink reef grazer with a parrot beak; makes sand from coral.", "Sleeps in a mucus bubble at night.",
     L("lunate", "long", ("#2ab0a0", "#f0a0b8", "#e080a0", "#f2d040"), "scales", ["beak_parrot"], hmax=0.16))
fish("Longhorn Cowfish", U, "Boxfish", "box", (15, 40), (0.2, 1.0), ["REEF"],
     "Yellow boxfish with two horns on its head and two at its tail end.", "Hard shell; slow swimmer.",
     L("fan", "small", ("#e0c040", "#f4e8a0", "#d0b030", "#4a6aa0"), "spots", ["horns"], anal="small"))
fish("Lumpsucker", U, "Lumpfish", "round", (25, 50), (1, 5), ["KELP", "LIGHT"],
     "Lumpy, bluish fish that sticks to rocks with a suction disc.", "Rows of bony bumps.",
     L("rounded", "hump", ("#5a7a8a", "#a8c0c8", "#4a6a78", "#2e4652"), "plain", ["tubercles"], hmax=0.24, wmax=0.2))
fish("John Dory", U, "Dory", "deep", (30, 60), (0.5, 3), ["LIGHT", "OPEN", "DEEP"],
     "Paper-thin, olive fish with a dark 'thumbprint' spot and long dorsal spines.", "Dark eye-spot on each side.",
     L("rounded", "filament", ("#8a8a6a", "#d8d8c0", "#7a7a5a", "#1e1e18"), "plain", ["eyespot"], anal="std"))
fish("Turbot", U, "Flatfish", "flatfish", (40, 80), (2, 12), ["HOME", "HARB"],
     "Round, knobbly flatfish that is a chef's favourite.", "Bony bumps on the eyed side.",
     L("rounded", "long", ("#7a6a50", "#f0e8dc", "#6a5a42", "#4a3e2c"), "mottled", ["tubercles"], anal="long", hmax=0.38), factor=1.2)
fish("Coney Grouper", U, "Grouper", "fusiform", (20, 40), (0.3, 1.5), ["REEF", "KELP"],
     "Small red grouper speckled with electric-blue dots.", "Blue dots glow under the lighthouse beam.",
     L("rounded", "spiny", ("#b84a3a", "#e8a090", "#a83a2e", "#3aa0e0"), "spots", hmax=0.15, wmax=0.11))
fish("Blue Runner", U, "Jack", "fusiform", (30, 60), (0.5, 3), ["OPEN", "HARB"],
     "Blue-green jack that runs hard and pulls harder.", "Long, fast fights for its size.",
     L("forked", "double", ("#3a6a7a", "#e2e8e8", "#4a7a88", "#1e3e48"), "gradient", ["scutes_side"]))
fish("Sea Raven", U, "Sculpin", "flat", (30, 60), (1, 3), ["KELP"],
     "Big-headed sculpin covered in fleshy flaps; looks like a rock.", "Inflates its belly when lifted.",
     L("rounded", "spiny", ("#a04030", "#e8c070", "#8a3428", "#5a2018"), "mottled", ["tabs"], pect="big"))
fish("Atlantic Spadefish", U, "Spadefish", "deep", (30, 60), (1, 6), ["HARB", "REEF"],
     "Silver disc with black bands and pointed dorsal and anal lobes.", "Schools around the marina pilings.",
     L("truncate", "lobe", ("#c8ccd0", "#eef0f2", "#9aa0a6", "#262a2e"), "bands", anal="lobe"))
fish("Conger Eel", U, "Conger", "eel", (80, 200), (2, 25), ["WRECK", "HARB", "KELP", "DEEP"],
     "Big grey eel that lives inside wrecks and dock foundations.", "Pulls back into its hole: needs a steady reel.",
     L("eel", "long", ("#5a6068", "#c8ccd0", "#4a5058", "#2a2e34"), "gradient", anal="long", hmax=0.06, wmax=0.055))
fish("Snook", U, "Snook", "fusiform", (50, 100), (1.5, 10), ["HARB", "HOME"],
     "Silver ambusher with a black racing stripe and a jutting lower jaw.", "Hangs under dock lights at night.",
     L("forked", "double", ("#9aa8a0", "#eef0ec", "#c8c070", "#1e1e1e"), "stripes_h", a=1.0))
fish("Ladyfish", U, "Ladyfish", "slim", (40, 80), (0.5, 3), ["HOME", "OPEN"],
     "Slim, shining silver fish that leaps like crazy.", "Jumps often: slack-line risk.",
     L("forked", "single", ("#a8b8c4", "#f2f5f8", "#b8c4cc", "#7a8a96"), "gradient"))
fish("Picasso Triggerfish", U, "Triggerfish", "diamond", (20, 30), (0.3, 0.7), ["REEF", "TREASURE"],
     "Triggerfish painted with blue, yellow and black lines like modern art.", "Grunts and buzzes when caught.",
     L("truncate", "trigger", ("#d8cfb8", "#f2ede0", "#3a6ab0", "#e0b030"), "diag", anal="tall"), factor=1.2)
fish("Frogfish", U, "Frogfish", "round", (10, 30), (0.2, 1.2), ["REEF", "WRECK"],
     "Lumpy yellow fish that 'walks' on its fins and fishes with a tiny lure.", "Lure on its head; walks on pectoral fins.",
     L("rounded", "small", ("#e0a030", "#f2d080", "#d09028", "#8a4a18"), "mottled", ["lure_small"], pect="legs", eye=0.8))
fish("Spotted Seatrout", U, "Drum", "fusiform", (35, 70), (0.5, 5), ["HOME", "HARB"],
     "Silver-grey drum covered in black spots, loves seagrass.", "Most active at dawn.",
     L("truncate", "double", ("#7a8a8a", "#eef0ee", "#8a9a9a", "#1e2222"), "spots"))
fish("Red Drum", U, "Drum", "fusiform", (50, 110), (2, 20), ["HARB", "HOME"],
     "Copper-coloured drum with a single black eye-spot on its tail.", "Tail eye-spot fools predators.",
     L("truncate", "double", ("#c07a40", "#f0d8c0", "#b06a34", "#1a1a1a"), "gradient", ["tail_spot"], hmax=0.14))
fish("Tub Gurnard", U, "Gurnard", "fusiform", (25, 60), (0.5, 5), ["HOME", "LIGHT"],
     "Orange fish with a bony head and huge blue-rimmed 'wing' fins.", "Walks on the seabed with finger-like fin rays.",
     L("truncate", "double", ("#d86a3a", "#f2d0b8", "#3a8ad0", "#c84a2a"), "gradient", pect="wing", a=0.45))
fish("Hogfish", U, "Wrasse", "compressed", (30, 70), (1, 10), ["REEF"],
     "Salmon-pink wrasse with a pig-like snout and long dorsal spines.", "Roots in the sand with its snout.",
     L("lunate", "filament", ("#e09080", "#f6dcd0", "#d07868", "#5a2a24"), "head_band", hmax=0.2, a=0.9))
fish("Bluefish", U, "Bluefish", "fusiform", (40, 90), (1, 9), ["OPEN", "HARB"],
     "Aggressive blue-green predator with razor teeth.", "Teeth; feeding frenzies near the surface.",
     L("forked", "double", ("#3a6a80", "#e0e8ec", "#4a7a8e", "#1e3a48"), "gradient", ["teeth"]))
fish("Dover Sole", U, "Flatfish", "flatfish", (25, 50), (0.3, 2), ["HOME"],
     "Elegant, oval flatfish; one of the most valuable small fish.", "Valued highly by Ruben.",
     L("rounded", "long", ("#7a6448", "#f0e8dc", "#6a5640", "#3e3222"), "plain", anal="long", hmax=0.22), factor=1.3)

# ---------- Rare (24)
R = "Rare"
fish("Lionfish", R, "Scorpionfish", "fusiform", (20, 38), (0.4, 1.3), ["REEF", "TREASURE"],
     "Red-and-white striped fish with a mane of venomous fin spines.", "Venomous; huge fan-like fins.",
     L("rounded", "lion", ("#c8402e", "#f4e4dc", "#e8d8d0", "#f4f0ec"), "bands", ["tabs"], pect="fan", hmax=0.14))
fish("Mahi-mahi", R, "Dorado", "mahi", (60, 140), (4, 20), ["OPEN", "DUCK"],
     "Neon green-gold-blue fish with a tall blunt forehead and a dorsal fin along its whole back.", "Changes colour while fighting.",
     L("forked", "long_tall", ("#2a9a7a", "#f0d040", "#3a70c0", "#e8c030"), "gradient", eye=0.9))
fish("Queen Angelfish", R, "Angelfish", "deep", (25, 45), (0.5, 1.6), ["REEF", "TREASURE"],
     "Electric blue-and-yellow angelfish with a blue 'crown' and trailing fins.", "Crown spot on the forehead.",
     L("rounded", "filament", ("#3a7ac0", "#f0d040", "#f0c030", "#1a3a80"), "head_band", anal="filament"))
fish("Lined Seahorse", R, "Seahorse", "seahorse", (8, 18), (0.01, 0.03), ["KELP", "HOME"],
     "Yellow seahorse that holds on to seagrass with its curled tail.", "Swims upright; very easy to lose.",
     L("none", "small", ("#d8b040", "#f0d880", "#e0c060", "#8a6a20"), "bands"))
fish("Flying Fish", R, "Flyingfish", "slim", (20, 40), (0.2, 0.6), ["OPEN", "DUCK"],
     "Blue fish with enormous wing-like pectoral fins that glides over the waves.", "Glides above the water when hooked.",
     L("forked_low", "single", ("#2a4a80", "#e8eef4", "#7aa0d0", "#1a2a50"), "gradient", pect="wing_huge"))
fish("Glass Squirrelfish", R, "Squirrelfish", "fusiform", (15, 30), (0.2, 0.6), ["REEF", "WRECK"],
     "Red night fish with huge eyes and a spiky dorsal fin.", "Only bites at night.",
     L("forked", "spiny", ("#d03a30", "#f2b8a8", "#e8d0c8", "#f4e0d8"), "stripes_h", eye=1.8, hmax=0.15))
fish("Atlantic Halibut", R, "Flatfish", "flatfish", (80, 200), (5, 120), ["OPEN", "DEEP", "LIGHT"],
     "Giant, dark flatfish that can outweigh the angler.", "Largest flatfish; fights from the bottom.",
     L("lunate", "long", ("#4a4438", "#f0ece4", "#3e3a30", "#2a2620"), "plain", anal="long", hmax=0.26))
fish("Yellowfin Tuna", R, "Tuna", "fusiform", (80, 180), (10, 90), ["OPEN", "DEEP"],
     "Muscular tuna with sickle-shaped yellow fins.", "Long yellow second dorsal and anal fins.",
     L("lunate", "sickle", ("#24385a", "#e8ecf0", "#e8c830", "#e8c830"), "stripe_yellow", ["finlets"], anal="sickle", hmax=0.15))
fish("Wahoo", R, "Mackerel", "slim", (100, 200), (10, 60), ["OPEN"],
     "Long, barred speed-demon of the open ocean.", "Fastest first run in the game.",
     L("lunate", "long_low", ("#2a4a70", "#e8ecf0", "#3a5a80", "#1a2a44"), "bars", ["finlets"], hmax=0.07, a=1.2))
fish("Atlantic Wolffish", R, "Wolffish", "eel", (60, 120), (3, 20), ["KELP", "WRECK", "LIGHT"],
     "Grey-blue fish with a massive head and crushing tusks.", "Tusks crush shellfish (and cheap hooks).",
     L("rounded", "long", ("#5a6a7a", "#b8c4cc", "#4a5a68", "#2a3440"), "bars", ["teeth"], anal="long", hmax=0.1, wmax=0.09, a=0.4))
fish("Spotted Eagle Ray", R, "Eagle ray", "ray", (150, 300), (20, 200), ["REEF", "OPEN"],
     "Dark ray covered in white spots, with a duck-like snout and pointed wings.", "Leaps out of the water; size = wingspan.",
     L("whip", "none", ("#2a3440", "#f0f2f4", "#222a34", "#f0f2f4"), "spots", ["snout_eagle"], anal="none", pect="none", round=0.2))
fish("Blacktip Reef Shark", R, "Requiem shark", "shark", (120, 180), (15, 40), ["REEF", "OPEN"],
     "Sleek reef shark with black tips on every fin.", "Black fin tips.",
     L("heterocercal", "shark", ("#8a8a80", "#f0f0ec", "#8a8a80", "#1a1a1a"), "fin_tips", ["gills"], anal="shark"))
fish("Black Grouper", R, "Grouper", "fusiform", (60, 130), (5, 40), ["REEF", "WRECK"],
     "Heavy, dark-blotched grouper that dives straight back into its cave.", "Rock-dive: reel fast or lose it.",
     L("truncate", "spiny", ("#4a4a40", "#9a9a88", "#3a3a32", "#26261e"), "mottled", hmax=0.17, wmax=0.13))
fish("Monkfish", R, "Anglerfish", "angler", (50, 120), (3, 30), ["DEEP", "WRECK", "LIGHT"],
     "Flat, wide-mouthed angler with a fleshy lure on its head.", "Enormous mouth; lure.",
     L("rounded", "small", ("#6a5a48", "#c8b8a0", "#5a4a3a", "#3a2e22"), "mottled", ["lure", "teeth", "tabs"], wmax=0.3, hmax=0.14))
fish("Tarpon", R, "Tarpon", "fusiform", (100, 220), (15, 100), ["HARB", "OPEN"],
     "The 'silver king' of the shallows, with huge mirror scales.", "Spectacular jumps; huge scales.",
     L("forked", "filament_short", ("#9ab0b8", "#f2f5f6", "#8aa0a8", "#e8eef0"), "scales", hmax=0.13, a=0.9))
fish("Greater Amberjack", R, "Jack", "fusiform", (80, 160), (10, 60), ["WRECK", "OPEN"],
     "Bronze jack with an amber stripe through the eye, hunting around wrecks.", "Pulls toward the wreck to snag the line.",
     L("forked", "double", ("#8a7a5a", "#eee8dc", "#9a8a68", "#c8a050"), "stripes_h"))
fish("Ribbon Eel", R, "Moray", "eel", (70, 130), (0.2, 0.6), ["REEF"],
     "Electric-blue eel with a yellow fin and flared nostrils.", "Very thin; flared nostrils.",
     L("eel", "long", ("#2a5ad0", "#3a6ae0", "#f0d020", "#f0d020"), "plain", ["nostrils"], anal="long", pect="none", hmax=0.035, wmax=0.03))
fish("Stargazer", R, "Stargazer", "flat", (20, 45), (0.5, 3), ["HOME", "HARB"],
     "Buries itself in sand with only its upward-looking eyes and mouth showing.", "Mild electric shock on catch.",
     L("rounded", "small", ("#8a7a68", "#e8e0d0", "#7a6a58", "#f2f0e8"), "spots", ["eyes_up"], hmax=0.12, wmax=0.15, a=0.3))
fish("Leafy Seadragon", R, "Seadragon", "seadragon", (25, 35), (0.05, 0.15), ["KELP"],
     "Golden seahorse relative covered in leaf-like flaps.", "Looks exactly like drifting kelp.",
     L("none", "small", ("#c8a040", "#e8d080", "#7a9a40", "#5a7a30"), "bands", ["leaves"]))
fish("Clown Triggerfish", R, "Triggerfish", "diamond", (30, 50), (1, 3), ["REEF", "TREASURE"],
     "Black triggerfish with big white belly spots and a yellow saddle.", "Big white polka dots.",
     L("truncate", "trigger", ("#1e1e22", "#f0f0f0", "#2a2a30", "#f0c020"), "big_spots", anal="tall"))
fish("Electric Ray", R, "Torpedo ray", "ray", (40, 100), (5, 30), ["HOME", "HARB"],
     "Round, thick ray that can deliver a strong electric shock.", "Shock: brief screen flash and line slack on catch.",
     L("paddle", "small_rear", ("#7a5a40", "#f0e8dc", "#6a4a34", "#3e2a1c"), "spots", anal="none", pect="none", round=1.0))
fish("Mandarin Dragonet", R, "Dragonet", "blenny", (5, 7), (0.005, 0.02), ["REEF", "TREASURE"],
     "Tiny psychedelic fish with swirling orange-blue patterns.", "Smallest Rare; very picky biter.",
     L("rounded", "sail_small", ("#e07020", "#3a6ad0", "#2aa0b0", "#3a6ad0"), "swirl", eye=1.4))
fish("Viperfish", R, "Dragonfish", "slim", (20, 35), (0.05, 0.2), ["DEEP", "ABYSS"],
     "Deep-sea fish with fangs too big to fit in its mouth.", "Glowing photophores; fangs.",
     L("forked", "single_front", ("#2a2a3a", "#3a3a50", "#1e1e2a", "#40e0f0"), "photophores", ["fangs"], eye=1.3))
fish("Silver Hatchetfish", R, "Hatchetfish", "hatchet", (3, 8), (0.005, 0.02), ["DEEP", "ABYSS"],
     "Tiny, mirror-silver deep-sea fish shaped like an axe blade, with glowing belly lights.", "Belly photophores.",
     L("forked", "small", ("#b8c4d0", "#e8eef4", "#a0acb8", "#60f0ff"), "photophores", eye=1.8))

# ---------- Epic (16)
E = "Epic"
fish("Lightfish", E, "Lanternfish (lighthouse form)", "fusiform", (30, 55), (0.5, 2.5), ["LIGHT"],
     "Teun's 'Lichtvis': a pale fish whose fins glow like the lighthouse lamp. Quest fish (Q5).", "Night only, inside the lighthouse beam.",
     L("forked", "sail_small", ("#f0ece0", "#fffaf0", "#ffe080", "#ffd040"), "glow_fins", ["photophores"], eye=1.3))
fish("Great Hammerhead", E, "Hammerhead shark", "shark", (250, 450), (100, 450), ["OPEN", "DEEP"],
     "Huge shark with a hammer-shaped head and a sickle dorsal fin.", "Hammer head; very tall dorsal.",
     L("heterocercal", "shark_tall", ("#8a8a84", "#eeeeea", "#7a7a74", "#5a5a54"), "gradient", ["hammer", "gills"], anal="shark"))
fish("Swordfish", E, "Billfish", "fusiform", (150, 350), (50, 400), ["OPEN", "DEEP"],
     "Dark gladiator of the deep with a long flat sword.", "Sword; dives deep at night.",
     L("lunate", "sickle_tall", ("#3a3a48", "#d8d8e0", "#2e2e3a", "#5a5a6a"), "gradient", ["bill"], anal="sickle", hmax=0.12, a=1.1))
fish("Sailfish", E, "Billfish", "slim", (150, 300), (25, 90), ["OPEN"],
     "Blue fish with a spear and a huge spotted sail it raises when excited.", "Raises its sail on the hook.",
     L("lunate", "sail", ("#2a4a90", "#e8ecf4", "#3a5ab0", "#7aa0e0"), "bars", ["bill"], anal="sickle"))
fish("Goliath Grouper", E, "Grouper", "fusiform", (150, 250), (100, 360), ["WRECK"],
     "Gigantic, mottled grouper that guards the shipwreck.", "Can swallow smaller hooked fish.",
     L("rounded", "spiny", ("#6a6450", "#b8b098", "#5a5442", "#3a3628"), "mottled", hmax=0.18, wmax=0.15, a=0.5))
fish("Opah", E, "Moonfish", "deep", (80, 180), (20, 80), ["DEEP", "OPEN"],
     "Round, red-finned moonfish dotted with silver; warm-blooded.", "Warm-blooded: bites in cold water too.",
     L("lunate", "sickle_tall", ("#c86a6a", "#e8c8c8", "#e02a2a", "#f0f0f0"), "spots", anal="sickle", pect="sickle", hmax=0.3, wmax=0.1))
fish("Gulper Eel", E, "Gulper", "gulper", (50, 100), (0.5, 2), ["DEEP", "ABYSS"],
     "Black deep-sea eel that is mostly mouth, with a glowing tail tip.", "Giant hinged mouth; glowing tail tip.",
     L("whip_glow", "none", ("#1a1a22", "#2a2a34", "#121218", "#ff4060"), "plain", ["big_mouth"], anal="none", pect="none"))
fish("Atlantic Sturgeon", E, "Sturgeon", "sturgeon", (100, 250), (20, 150), ["HARB", "DEEP"],
     "Prehistoric armoured fish with rows of bony plates and a shovel snout.", "Bony scutes; barbels; living fossil.",
     L("heterocercal", "rear", ("#5a5a50", "#d8d0c0", "#4a4a42", "#c8c0b0"), "gradient", ["scutes", "barbels"], anal="rear"))
fish("Thresher Shark", E, "Thresher shark", "shark", (300, 550), (150, 350), ["OPEN", "DEEP"],
     "Shark whose upper tail fin is as long as its body.", "Whips prey with its tail.",
     L("thresher", "shark", ("#5a6a80", "#eef0f2", "#4a5a70", "#3a4a60"), "gradient", ["gills"], anal="shark", eye=1.4))
fish("Fangtooth", E, "Fangtooth", "angler", (10, 17), (0.05, 0.12), ["DEEP", "ABYSS"],
     "Small black deep-sea fish with the largest teeth for its size of any fish.", "Lives in the darkest water.",
     L("forked", "small", ("#2a1e1e", "#3a2a2a", "#1e1414", "#e8e0d0"), "plain", ["fangs"], hmax=0.2, wmax=0.16))
fish("Ghost Shark", E, "Chimaera", "chimaera", (60, 150), (2, 10), ["DEEP", "WRECK"],
     "Pale, big-eyed cartilaginous fish with wing-like fins and a whip tail.", "Venomous dorsal spine; huge reflective eyes.",
     L("whip", "spine", ("#c8c8d0", "#f0f0f4", "#b0b0bc", "#8a8a9a"), "plain", pect="wing", anal="none", eye=2.0))
fish("Wreck Angler", E, "Anglerfish", "angler", (60, 110), (8, 30), ["WRECK"],
     "Anglerfish crusted with barnacles whose lure glows like a ship's lantern.", "Lantern lure; only lives in the wreck.",
     L("rounded", "small", ("#4a4a40", "#8a8a78", "#3a3a32", "#ffb040"), "mottled", ["lure", "teeth", "barnacles"], wmax=0.28, hmax=0.2))
fish("Grotto Glassfish", E, "Glassfish", "fusiform", (20, 40), (0.2, 0.8), ["GROTTO"],
     "Transparent fish from Teun's pool; you can see its glowing skeleton.", "See-through body; only in the grotto.",
     L("forked", "single", ("#b8f0f0", "#e0ffff", "#a0e8e8", "#40f0e0"), "glass", ["skeleton"], eye=1.3))
fish("Giant Trevally", E, "Jack", "fusiform", (80, 170), (20, 80), ["REEF", "OPEN"],
     "Steep-headed, brutally strong silver jack: the reef's bully.", "Strongest pull per kg in the game.",
     L("forked", "sickle", ("#6a7680", "#e8ecee", "#3a4048", "#2a3038"), "gradient", ["scutes_side"], anal="sickle", hmax=0.18, a=0.4))
fish("Humphead Wrasse", E, "Wrasse", "fusiform", (100, 200), (40, 190), ["REEF"],
     "Huge green-blue wrasse with a bulging forehead and thick lips.", "Hump grows with size.",
     L("rounded", "long", ("#3a8a8a", "#a8d8c8", "#2a7a7a", "#6ac0b0"), "swirl", ["hump"], hmax=0.17, wmax=0.12))
fish("Velvet Lanternshark", E, "Lanternshark", "shark", (20, 50), (0.3, 1.2), ["DEEP", "ABYSS"],
     "Tiny dark shark whose belly glows to hide its shadow.", "Glowing belly; schools in the dark.",
     L("heterocercal", "shark_low", ("#2a2a34", "#4a5070", "#1e1e28", "#40d0ff"), "photophores", ["gills"], anal="none", eye=1.6))

# ---------- Legendary (10)
LG = "Legendary"
fish("Atlantic Bluefin Tuna", LG, "Tuna", "fusiform", (180, 300), (150, 500), ["OPEN", "DEEP"],
     "The king of tuna: a torpedo of muscle that can cross oceans.", "Fights for minutes; yellow finlets.",
     L("lunate_big", "double", ("#1e2e50", "#e8ecf0", "#2e3e60", "#e8c830"), "gradient", ["finlets"], anal="std", hmax=0.15))
fish("Blue Marlin", LG, "Billfish", "slim", (250, 450), (100, 700), ["DEEP", "OPEN"],
     "Cobalt-blue giant with a spear, a tall dorsal and pale stripes.", "Tail-walks across the water.",
     L("lunate_big", "sickle_tall", ("#1e3a80", "#e8ecf4", "#2a4a9a", "#8ab0e8"), "bars", ["bill"], anal="sickle", hmax=0.1))
fish("Great White Shark", LG, "Mackerel shark", "shark", (350, 600), (600, 1800), ["DEEP", "OPEN", "LIGHT"],
     "The apex predator: grey back, white belly, black eyes.", "Circles the boat before biting.",
     L("lunate", "shark_tall", ("#6a7078", "#f2f2f2", "#5a6068", "#1a1a1a"), "gradient", ["gills", "teeth"], anal="shark", hmax=0.13))
fish("Giant Oarfish", LG, "Oarfish", "oarfish", (300, 800), (50, 270), ["DEEP", "ABYSS"],
     "Silver ribbon several metres long with a red crest; the origin of sea-serpent tales.", "Only surfaces before storms.",
     L("none", "crest", ("#c8d0d8", "#f0f4f8", "#e02a2a", "#e02a2a"), "spots", anal="none", pect="small"))
fish("Ocean Sunfish", LG, "Mola", "mola", (180, 330), (250, 1500), ["OPEN", "DUCK"],
     "Enormous, flat, round fish that seems to be all head; basks at the surface.", "Heaviest bony fish; lazy fighter.",
     L("clavus", "mola", ("#9aa0a8", "#d8dce0", "#8a9098", "#6a7078"), "mottled", anal="mola", pect="small", eye=0.8), factor=1.15)
fish("Manta Ray", LG, "Manta", "ray", (300, 700), (300, 1500), ["OPEN", "REEF"],
     "Gentle giant ray with head fins like horns; glides in loops.", "Somersaults when feeding; size = wingspan.",
     L("whip_short", "none", ("#1e2228", "#f2f2f2", "#1a1e22", "#f2f2f2"), "manta", ["cephalic"], anal="none", pect="none", round=0.0))
fish("Coelacanth", LG, "Lobe-finned fish", "fusiform", (150, 200), (60, 100), ["DEEP"],
     "Living fossil with leg-like lobed fins and white-flecked blue scales.", "Night only; thought extinct.",
     L("diphycercal", "double", ("#2a3a6a", "#4a5a8a", "#22305a", "#e8eef4"), "spots", pect="lobe", anal="lobe", hmax=0.16))
fish("Phantom Barracuda", LG, "Barracuda (ghost form)", "slim", (150, 250), (25, 60), ["WRECK"],
     "Pale, half-transparent barracuda that haunts the shipwreck.", "Only at night; partly see-through.",
     L("forked", "double_far", ("#c8e0e8", "#eef8fa", "#a8d0d8", "#80f0ff"), "glass", ["teeth", "skeleton"], hmax=0.075, wmax=0.06, a=1.2))
fish("Zilverkoning", LG, "Silver king (legend)", "fusiform", (120, 180), (30, 70), ["GROTTO"],
     "Teun's legend: a gleaming silver king-fish with a crown of fin rays. Final quest fish (Q7).", "Only in the grotto pool after Q6; one per day.",
     L("lunate_big", "crown", ("#d8e0e8", "#ffffff", "#e8eef4", "#f0c840"), "scales", ["crown"], anal="sickle", pect="sickle", hmax=0.16), factor=1.25)
fish("Megamouth Shark", LG, "Megamouth", "shark", (400, 550), (700, 1200), ["DEEP"],
     "Rare, soft-bodied shark with a gigantic glowing-lipped mouth.", "Rises from the deep only at night.",
     L("heterocercal", "shark_low", ("#3a3a40", "#c8c8c8", "#2e2e34", "#f0f0f0"), "gradient", ["big_mouth", "gills"], anal="shark", a=0.35))

# ---------- Mythical (6)
M = "Mythical"
fish("Serpent's Hatchling", M, "Sea serpent", "serpent", (300, 500), (80, 200), ["ABYSS"],
     "A young sea serpent from the Abyss: spiked mane, horns and a fin-tipped tail.", "Its mother is watching (EE_SeaSerpent).",
     L("fin_tip", "mane", ("#2a6a50", "#e0d080", "#e07030", "#e07030"), "belly_plates", ["horns_back"], anal="none", pect="small"))
fish("Celestial Moonray", M, "Ray (celestial)", "ray", (200, 400), (100, 400), ["ABYSS", "OPEN"],
     "Night-blue ray sprinkled with glowing stars; appears on clear nights.", "Clear nights only; leaves a star trail.",
     L("whip", "none", ("#141c48", "#2a2a60", "#3a2a80", "#ffffff"), "stars", ["cephalic"], anal="none", pect="none", round=0.15))
fish("Kraken Angler", M, "Anglerfish (abyssal)", "angler", (150, 250), (150, 400), ["ABYSS"],
     "Colossal anglerfish whose chin tentacles curl like a kraken's arms.", "Two glowing lures; pulls the boat.",
     L("rounded", "small", ("#2a1e30", "#4a3450", "#1e1424", "#40ffd0"), "photophores", ["lure", "lure2", "teeth", "tentacles"], wmax=0.3, hmax=0.22))
fish("Crystal Sovereign", M, "Crystal fish", "deep", (60, 90), (8, 20), ["GROTTO"],
     "A fish grown out of the grotto's crystals; light shines through it.", "Always counts as Crystal-tinted; cannot get the Crystal mutation.",
     L("lunate", "crystal", ("#80e0f0", "#d0f8ff", "#40c8e0", "#a0ffff"), "glass", ["crystals"], anal="sickle"))
fish("Doubloon Fish", M, "Treasure fish", "coin", (20, 30), (2, 4), ["TREASURE"],
     "A round golden fish stamped like an old coin. Pirates swore it was cursed.", "Heaviest fish for its size (gold).",
     L("fan", "small", ("#e0b030", "#f0d060", "#c89820", "#8a6a10"), "coin", anal="small", eye=1.2))
fish("Quackfin", M, "Duckfish (???)", "round", (30, 45), (1, 2), ["DUCK"],
     "A bright yellow fish with a duck bill. Nobody knows. Don't ask.", "Quacks on the hook (audio hook). Floats.",
     L("fan", "small", ("#f2d020", "#f8e870", "#f0a020", "#f08020"), "plain", ["duck_bill"], pect="small", eye=1.3))


# ---------------------------------------------------------------- derived values

def avg_weight(f):
    (lmin, lmax), (wmin, wmax) = f["size"], f["weight"]
    lavg = (lmin + lmax) / 2
    t = (lavg ** 3 - lmin ** 3) / (lmax ** 3 - lmin ** 3)
    return wmin + (wmax - wmin) * t


def size_category(cm_max):
    for limit, cat in ((15, "Tiny"), (40, "Small"), (100, "Medium"), (250, "Large"), (500, "Huge")):
        if cm_max <= limit:
            return cat
    return "Colossal"


def finalize():
    """Number the fish, derive averages, value, difficulty and spawn weight."""
    for i, f in enumerate(FISH):
        f["id"] = i + 1
        f["size_avg"] = round((f["size"][0] + f["size"][1]) / 2, 1)
        f["weight_avg"] = avg_weight(f)
        f["size_cat"] = size_category(f["size"][1])
    for r in RARITIES:
        group = sorted([f for f in FISH if f["rarity"] == r], key=lambda f: f["weight_avg"])
        lo, hi = RARITY[r]["diff"]
        for k, f in enumerate(group):
            rank = k / max(1, len(group) - 1)
            factor = f["factor"] if f["factor"] is not None else 0.8 + 0.4 * rank
            f["factor"] = factor
            f["value"] = int(round(BASE_COIN * RARITY[r]["mult"] * factor))
            f["difficulty"] = int(round(lo + (hi - lo) * rank))
            f["spawn_weight"] = round(RARITY[r]["weight"] * f["abundance"], 2)
    return FISH


def validate():
    names = [f["name"] for f in FISH]
    assert len(FISH) == 122, len(FISH)
    assert len(set(names)) == 122, "duplicate fish names"
    counts = {r: sum(f["rarity"] == r for f in FISH) for r in RARITIES}
    assert counts == {"Common": 36, "Uncommon": 30, "Rare": 24, "Epic": 16, "Legendary": 10, "Mythical": 6}, counts
    for f in FISH:
        assert f["zones"] and all(z in ZONES for z in f["zones"]), f["name"]
        assert f["size"][0] < f["size"][1] and f["weight"][0] < f["weight"][1], f["name"]
    for z in ZONES:
        assert any(z in f["zones"] for f in FISH), z
    assert len(RODS) == 5 and len(RARITIES) == 6
    return counts


finalize()
