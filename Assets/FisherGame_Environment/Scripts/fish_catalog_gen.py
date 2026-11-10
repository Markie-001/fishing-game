"""Writes ../fish_catalog.md from fish_data.py (run: python3 fish_catalog_gen.py)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fish_data as D

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fish_catalog.md")
PREFERRED_BONUS = 1.5     # a fish spawns 1.5x more often in its preferred (first listed) zone
HOOK_MARGIN = 8           # a rod can hook fish up to (power + 8) difficulty, above its power the fight is harder

PLAN_TXT = {
    "fusiform": "torpedo-shaped (fusiform) body", "slim": "long, slim streamlined body", "compressed": "tall, laterally flattened body",
    "deep": "very deep, disc-like flattened body", "flat": "wide, flattened (depressed) body with a broad head",
    "eel": "long eel body with continuous fins", "round": "round, inflatable body", "box": "box-shaped armoured body",
    "shark": "shark body with pointed snout and gill slits", "flatfish": "oval flatfish body lying on its side, both eyes on top",
    "ray": "flat disc/wing body (ray)", "angler": "huge round head with a wide mouth, short tapering body",
    "diamond": "diamond-shaped, deep body", "blenny": "short elongated body with a blunt head",
    "pipefish": "stick-thin body with a tube snout", "lookdown": "very deep body with a vertical, steep forehead",
    "mahi": "long body with a tall, blunt forehead", "seahorse": "upright seahorse body with a curled tail and horse-like head",
    "seadragon": "straighter seahorse body with leafy flaps", "hatchet": "tiny axe-blade-shaped body",
    "gulper": "thin whip body with an enormous mouth", "sturgeon": "long armoured body with a shovel snout",
    "chimaera": "big-headed tapering body ending in a whip", "oarfish": "very long silver ribbon body",
    "mola": "giant round disc body that ends abruptly (no real tail)", "serpent": "undulating serpent body",
    "coin": "perfectly round, flat coin-shaped body",
}
TAIL_TXT = {
    "forked": "forked tail", "forked_low": "forked tail with a longer lower lobe", "rounded": "rounded fan tail",
    "truncate": "straight-edged tail", "lunate": "crescent (lunate) tail", "lunate_big": "large crescent tail",
    "heterocercal": "shark tail with a long upper lobe", "thresher": "extremely long upper tail lobe", "fan": "small fan tail",
    "whip": "long whip tail", "whip_short": "short whip tail", "whip_glow": "whip tail with a glowing tip", "eel": "pointed eel tail",
    "none": "no tail fin", "paddle": "small paddle tail", "clavus": "scalloped 'clavus' band instead of a tail",
    "diphycercal": "three-lobed (diphycercal) tail", "fin_tip": "tail ending in a finned tip",
}
DORSAL_TXT = {
    "single": "one dorsal fin", "double": "two dorsal fins", "triple": "three dorsal fins", "spiny": "spiny dorsal fin",
    "spiny_black": "black venomous dorsal fin", "long": "long continuous dorsal fin", "long_low": "long low dorsal fin",
    "long_tall": "dorsal fin along the whole back", "small": "small dorsal fin", "small_rear": "small dorsal fins near the tail",
    "sail": "huge sail dorsal fin", "sail_small": "raised sail-like dorsal fin", "filament": "dorsal fin with trailing filament",
    "filament_short": "dorsal fin with a short filament", "spine": "single stiff dorsal spine", "trigger": "locking trigger spine",
    "shark": "triangular shark dorsal fin", "shark_low": "low shark dorsal fins", "shark_tall": "very tall sickle shark dorsal",
    "sickle": "sickle-shaped dorsal fin", "sickle_tall": "tall sickle dorsal fin", "rear": "dorsal fin set far back",
    "double_far": "two widely separated dorsal fins", "single_front": "dorsal fin set forward", "hump": "fleshy dorsal hump",
    "lobe": "pointed dorsal lobe", "lion": "mane of long venomous spines", "crest": "red crest running from head to tail",
    "mola": "tall rigid dorsal blade", "crown": "crown of tall fin rays", "mane": "spiked mane", "crystal": "dorsal of crystal shards",
    "none": "no dorsal fin",
}
PATTERN_TXT = {
    "plain": "plain colouring", "gradient": "dark back fading to a light belly", "spots": "spotted", "mottled": "mottled camouflage",
    "stripes_h": "horizontal stripes", "bands": "vertical bands", "bars": "dark vertical bars", "wavy": "wavy tiger stripes on the back",
    "spot_row": "row of spots along the flank", "tail_accent": "contrasting tail", "stripe_tail": "side stripe running into a coloured tail",
    "head_band": "coloured band/crown on the head", "scales": "large visible scales", "diag": "diagonal stripes",
    "swirl": "swirling patterns", "photophores": "glowing photophore dots", "glass": "transparent body",
    "fin_tips": "black-tipped fins", "big_spots": "big polka dots", "glow_fins": "glowing fins", "manta": "white belly with dark back and white shoulder patches",
    "belly_plates": "plated belly", "stars": "glowing star specks", "coin": "embossed coin rim", "stripe_yellow": "yellow side stripe",
}
EXTRA_TXT = {
    "barb": "tail barb", "barbels": "whisker barbels", "chin_barbel": "single chin barbel", "chin_barbels": "two chin barbels",
    "barnacles": "barnacle crust", "beak": "needle-like beak", "beak_parrot": "parrot beak", "big_mouth": "enormous mouth",
    "bill": "long bill/sword", "cephalic": "horn-like head fins", "crest": "fringed head crest", "crown": "golden crown rays",
    "crystals": "crystal shards", "duck_bill": "duck bill", "eyes_up": "upward-facing eyes", "eyespot": "dark eye-spot",
    "fangs": "oversized fangs", "finlets": "finlets before the tail", "gills": "gill slits", "hammer": "hammer-shaped head",
    "horns": "horns on head and tail", "horns_back": "swept-back horns", "hump": "bulging forehead hump", "leaves": "leaf-like flaps",
    "lure": "glowing lure on a stalk", "lure2": "second lure", "lure_small": "tiny lure", "nostrils": "flared nostrils",
    "photophores": "glowing light organs", "scutes": "rows of bony plates", "scutes_side": "bony scutes along the side",
    "skeleton": "visible glowing skeleton", "snout_eagle": "duck-like snout", "spikes": "body spikes", "tabs": "fleshy skin flaps",
    "tail_spot": "black eye-spot on the tail", "teeth": "visible teeth", "tentacles": "tentacle-like chin barbels",
    "tubercles": "bony bumps",
}


def zone_weights(zone, rod=None):
    """Spawn weight of every fish in a zone (optionally with a rod's rarity bonus)."""
    out = []
    for f in D.FISH:
        if zone not in f["zones"]:
            continue
        w = f["spawn_weight"] * (PREFERRED_BONUS if f["zones"][0] == zone else 1.0)
        if rod and D.RARITIES.index(f["rarity"]) >= 2:
            w *= 1 + rod["bonus"] / 100
        out.append((f, w))
    return out


def pct(x):
    return ("%.2f%%" % (x * 100)) if x < 0.1 else ("%.1f%%" % (x * 100))


def kg(w):
    return ("%.3f" % w).rstrip("0").rstrip(".") if w < 1 else ("%.1f" % w if w < 100 else "%d" % round(w))


def fname(f):
    return "Fish_%03d_%s" % (f["id"], "".join(ch if ch.isalnum() else "_" for ch in f["name"]).strip("_"))


def model_text(f):
    lk = f["look"]
    back, belly, fin, accent = lk["colors"]
    bits = [PLAN_TXT[f["plan"]], TAIL_TXT[lk["tail"]], DORSAL_TXT[lk["dorsal"]]]
    if lk["pect"] not in ("std", "none"):
        bits.append({"wing": "large wing-like pectoral fins", "wing_huge": "huge gliding wing fins", "fan": "fan-like pectoral fins",
                     "legs": "leg-like pectoral fins", "big": "big pectoral fins", "lobe": "fleshy lobed (limb-like) fins",
                     "sickle": "long sickle pectoral fins", "small": "small pectoral fins"}[lk["pect"]])
    extras = ", ".join(EXTRA_TXT[e] for e in lk["extras"])
    txt = "%s; %s. Colours: back `%s`, belly `%s`, fins `%s`, accent `%s` (%s)." % (
        bits[0][0].upper() + bits[0][1:], ", ".join(bits[1:]), back, belly, fin, accent, PATTERN_TXT[lk["pattern"]])
    if extras:
        txt += " Signature details: %s." % extras
    if lk["eye"] >= 1.4:
        txt += " Oversized eyes."
    return txt


def build():
    D.validate()
    F = D.FISH
    out = []
    w = out.append
    counts = {r: sum(f["rarity"] == r for f in F) for r in D.RARITIES}

    # ------------------------------------------------------------ 1
    w("# Fisher Game – Fish Catalog\n")
    w("> Generated from `Scripts/fish_data.py` by `Scripts/fish_catalog_gen.py`. Edit the data file and re-run the generator;"
      " do not edit this file by hand. 3D models: `Blender/Models/Fish.blend`, one FBX per fish in `Export/Fish/`.\n")
    w("## Contents\n")
    for i, t in enumerate(["Project overview", "Fish rarity system", "Fishing zones", "Fishing rod progression", "Complete fish catalog",
                           "Fish spawning distribution", "Fish economy and selling values", "Model creation guidelines",
                           "Technical implementation notes"], 1):
        w("%d. [%s](#%d-%s)" % (i, t, i, t.lower().replace(" ", "-")))
    w("")
    w("## 1. Project overview\n")
    w("Fisher Game is a low-poly 3D fishing game set in a small archipelago. This document defines **everything about the fish**: "
      "the 122 species, their rarity, where they live, what they are worth, how big they get, the mutation layer and the "
      "five fishing rod tiers. It is meant to be complete enough to implement fishing without inventing missing data.\n")
    w("| Item | Count |\n|---|---|")
    w("| Fish species | **%d** |" % len(F))
    w("| Rarities | **%d** (%s) |" % (len(D.RARITIES), ", ".join("%s %d" % (r, counts[r]) for r in D.RARITIES)))
    w("| Fishing zones | **%d** (8 regular, 4 hidden/special) |" % len(D.ZONES))
    w("| Fishing rod tiers | **%d** (gameplay stats only, models are made by the team) |" % len(D.RODS))
    w("| Mutations | **%d** (separate layer on top of rarity) |" % len(D.MUTATIONS))
    w("")
    w("**The world.** The game has the four main islands plus Teun's quest island (see `QUESTLINE.md`):\n")
    w("| Island | Role | Fishing zones around it |\n|---|---|---|")
    w("| Home Island | Player's home | Home Lagoon |")
    w("| Fish Selling Island | Ruben buys fish in the lighthouse | Harbor Waters (harbour), Lighthouse Point (cliffs) |")
    w("| Boat Dealer Island | Emre sells boats | Harbor Waters (marina), Sunlit Reefs |")
    w("| Fishing Rod Shop Island | Mark sells rods and the rod upgrades below | Kelp Rocks |")
    w("| Teun's Rock (Cave Island) | Quest hub | Kelp Rocks (coast), Teun's Grotto (cave pool) |")
    w("| Open sea | – | Open Ocean (centre), The Drop (outer ring), 4 hidden zones at the map corners |")
    w("")
    w("**Restrictions respected.** The existing wave code (`WaterManagement`, `WaterManager`, `Floater`) is untouched and no new water "
      "system is introduced. No boat models or boat systems are created (boats are made by another developer). No fishing-rod "
      "models are created; rods are documented as gameplay data only.\n")

    # ------------------------------------------------------------ 2
    w("## 2. Fish rarity system\n")
    w("Every fish has exactly one rarity. Rarity sets the base spawn weight, the value multiplier and the difficulty band "
      "(how hard the fish fights, compared with the rod's *fishing power*).\n")
    w("| Rarity | Fish | Spawn weight | Value multiplier | Value range | Difficulty | UI colour | Availability |")
    w("|---|---|---|---|---|---|---|---|")
    for r in D.RARITIES:
        R = D.RARITY[r]
        vals = [f["value"] for f in F if f["rarity"] == r]
        w("| **%s** | %d | %g | ×%d | %d–%d | %d–%d | `%s` | %s |" % (r, counts[r], R["weight"], R["mult"], min(vals), max(vals),
                                                               R["diff"][0], R["diff"][1], R["ui"], R["avail"]))
    w("")
    w("### Spawn chance guidelines\n")
    w("Each zone has a list of fish. A bite picks one fish from that list, weighted by its **spawn weight** "
      "(rarity weight × species abundance, ×%.1f in the fish's preferred zone, × the rod's rarity bonus for Rare and above). "
      "Because zones contain different mixes, the real chance differs per zone; section 6 lists all of them. "
      "Typical share of a bite in a mixed zone (Open Ocean):\n" % PREFERRED_BONUS)
    w("| Rarity | Starter Rod | Reefrunner Rod | Leviathan Rod |\n|---|---|---|---|")
    for r in D.RARITIES:
        row = []
        for rod in (D.RODS[0], D.RODS[2], D.RODS[4]):
            zw = zone_weights("OPEN", rod)
            tot = sum(x for _, x in zw)
            row.append(pct(sum(x for f, x in zw if f["rarity"] == r) / tot))
        w("| %s | %s |" % (r, " | ".join(row)))
    w("")
    w("### Visual characteristics and progression\n")
    w("| Rarity | Visual characteristics | Expected progression |\n|---|---|---|")
    for r in D.RARITIES:
        w("| **%s** | %s | %s |" % (r, D.RARITY[r]["visual"], D.RARITY[r]["progression"]))
    w("")
    w("### Mutations (separate layer)\n")
    w("Mutations are **not** a rarity. After a fish is chosen, a mutation is rolled independently, so a Common Sand Goby can be "
      "Celestial and a Mythical Quackfin can be Golden. A fish has at most one mutation. Mutations change the existing model "
      "through materials (and a few small geometry add-ons); there are no separate mutation species.\n")
    w("| Mutation | Chance | Value × | Condition | Appearance | Special |\n|---|---|---|---|---|---|")
    for m in D.MUTATIONS:
        w("| **%s** | 1 in %s | ×%g | %s | %s | %s |" % (m["name"], "{:,}".format(m["chance"]), m["mult"], m["cond"], m["look"], m["special"]))
    w("")
    w("**Roll order.** Mutations are checked from rarest (Celestial) to most common (Albino); the first success wins. "
      "Each chance is multiplied by `1 + luck/100` of the rod and only rolls when its condition is met. "
      "Rainbow replaces any other mutation. The Crystal Sovereign cannot become Crystal.\n")
    w("**Model modification per mutation:**\n")
    for m in D.MUTATIONS:
        w("- **%s**: %s" % (m["name"], m["model"]))
    w("")
    w("A preview of every mutation applied to the same fish is in `Fish.blend` (collection `Mutation_Preview`).\n")

    # ------------------------------------------------------------ 3
    w("## 3. Fishing zones\n")
    w("Zones are circles around anchor points in the world (Blender X/Y in metres). The empties `FishingZone_<CODE>_<n>` in the "
      "world file (`Export/FishingZones.fbx`) carry them into Unity with the right position and a radius in their name/custom data. "
      "When circles overlap, the zone with the highest priority wins; outside all circles within 330 m of the centre it is **Open Ocean**, "
      "beyond that **The Drop**.\n")
    w("| Code | Zone | Depth | Priority | Fish | Rarity mix (C/U/R/E/L/M) | Recommended rod |\n|---|---|---|---|---|---|---|")
    rec = {"HOME": 1, "HARB": 1, "LIGHT": 2, "KELP": 2, "REEF": 3, "OPEN": 3, "DEEP": 4, "WRECK": 3, "GROTTO": 4, "ABYSS": 5, "TREASURE": 3, "DUCK": 3}
    for z in D.ZONE_ORDER:
        Z = D.ZONES[z]
        fz = [f for f in F if z in f["zones"]]
        mix = "/".join(str(sum(f["rarity"] == r for f in fz)) for r in D.RARITIES)
        w("| `%s` | %s | %s | %d | %d | %s | %s |" % (z, Z["name"], Z["depth"], Z["priority"], len(fz), mix, D.RODS[rec[z] - 1]["name"]))
    w("")
    for z in D.ZONE_ORDER:
        Z = D.ZONES[z]
        zw = zone_weights(z)
        fz = [f for f, _ in zw]
        w("### %s (`%s`)\n" % (Z["name"], z))
        w("- **Description:** %s" % Z["desc"])
        w("- **Depth:** %s" % Z["depth"])
        w("- **Environment:** %s" % Z["env"])
        w("- **Location:** %s" % "; ".join("centre (%g, %g) radius %g m" % a if a[2] < 9000 else "everything farther than 330 m from the centre"
                                            for a in Z["anchors"]))
        w("- **Recommended progression:** %s" % Z["progression"])
        top = sorted(zw, key=lambda t: -t[1])[:5]
        w("- **Especially common:** %s" % ", ".join(f["name"] for f, _ in top))
        excl = [f for f in fz if f["zones"] == [z] and D.RARITIES.index(f["rarity"]) >= 2]
        w("- **Exclusive rare fish:** %s" % (", ".join("%s (%s)" % (f["name"], f["rarity"]) for f in excl) if excl else "none"))
        w("- **All fish (%d):** %s\n" % (len(fz), ", ".join("%s *(%s)*" % (f["name"], f["rarity"][0] if f["rarity"] != "Mythical" else "M")
                                                       for f in sorted(fz, key=lambda f: (D.RARITIES.index(f["rarity"]), f["name"])))))

    # ------------------------------------------------------------ 4
    w("## 4. Fishing rod progression\n")
    w("Rods are **gameplay data only** – the rod models are made by the team. Mark sells every rod on the Fishing Rod Shop Island.\n")
    w("| Tier | Rod | Fishing power | Luck | Rarity bonus | Price | Unlock requirement |\n|---|---|---|---|---|---|---|")
    for r in D.RODS:
        w("| %d | **%s** | %d | %d | +%d%% | %s | %s |" % (r["tier"], r["name"], r["power"], r["luck"], r["bonus"], r["price"], r["unlock"]))
    w("")
    w("| Rod | Suitable zones | Can hook (difficulty ≤ power + %d) | Progression role |\n|---|---|---|---|" % HOOK_MARGIN)
    for r in D.RODS:
        ok = [f for f in F if f["difficulty"] <= r["power"] + HOOK_MARGIN]
        by = ", ".join("%s %d/%d" % (rr, sum(f["rarity"] == rr for f in ok), counts[rr]) for rr in D.RARITIES if any(f["rarity"] == rr for f in ok))
        zs = ", ".join(D.ZONES[z]["name"] if z in D.ZONES else z for z in r["zones"])
        w("| %s | %s | %s | %s |" % (r["name"], zs, by, r["role"]))
    w("")
    w("**How the stats work**\n")
    w("- **Fishing power** vs. fish **difficulty**: a fish can be hooked when `difficulty ≤ power + %d`. If the difficulty is above the "
      "power, the reel minigame gets harder (faster fish, smaller catch zone) by `(difficulty − power) × 4%%`. Above `power + %d` the line "
      "always snaps." % (HOOK_MARGIN, HOOK_MARGIN))
    w("- **Rarity bonus** multiplies the spawn weight of Rare, Epic, Legendary and Mythical fish.")
    w("- **Luck** multiplies every mutation chance by `1 + luck/100` and adds `luck/2` % to the chance of the bigger half of a fish's size range.")
    w("- The Starter Rod (power 25) lands every Common fish and the lighter Uncommon fish. The Leviathan Rod (power 92) can hook "
      "everything, but Mythical fish (difficulty 86–98) still fight above its power, so the challenge remains.\n")

    # ------------------------------------------------------------ 5
    w("## 5. Complete fish catalog\n")
    w("Lengths in cm, weights in kg, values in coins at average weight without mutation. Spawn weight = relative chance before zone "
      "and rod modifiers. Model = file name in `Export/Fish/`.\n")
    w("| # | Fish | Rarity | Type | Size | Length (cm) | Weight (kg) | Value | Difficulty | Spawn wt | Preferred zone | Zones |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for f in F:
        w("| %d | %s | %s | %s | %s | %g–%g | %s–%s | %d | %d | %g | %s | %s |" % (
            f["id"], f["name"], f["rarity"], f["family"], f["size_cat"], f["size"][0], f["size"][1], kg(f["weight"][0]), kg(f["weight"][1]),
            f["value"], f["difficulty"], f["spawn_weight"], D.ZONES[f["zones"][0]]["name"], ", ".join(f["zones"])))
    w("")
    w("### Individual fish entries\n")
    for r in D.RARITIES:
        w("#### %s fish\n" % r)
        for f in [x for x in F if x["rarity"] == r]:
            w("##### #%03d %s\n" % (f["id"], f["name"]))
            w("- **Rarity:** %s · **Type:** %s · **Size category:** %s" % (f["rarity"], f["family"], f["size_cat"]))
            w("- **Description:** %s" % f["desc"])
            w("- **Preferred zone:** %s · **Spawns in:** %s" % (D.ZONES[f["zones"][0]]["name"], ", ".join(D.ZONES[z]["name"] for z in f["zones"])))
            w("- **Relative spawn chance:** weight %g (×%.1f in preferred zone)" % (f["spawn_weight"], PREFERRED_BONUS))
            w("- **Size:** %g–%g cm (avg %g cm) · **Weight:** %s–%s kg (avg %s kg)" % (
                f["size"][0], f["size"][1], f["size_avg"], kg(f["weight"][0]), kg(f["weight"][1]), kg(f["weight_avg"])))
            w("- **Selling value:** %d coins at average weight · **Difficulty:** %d" % (f["value"], f["difficulty"]))
            w("- **Special:** %s" % f["special"])
            w("- **Model:** %s Model file `%s.fbx`, average length %g cm.\n" % (model_text(f), fname(f), f["size_avg"]))

    # ------------------------------------------------------------ 6
    w("## 6. Fish spawning distribution\n")
    w("Chance that a bite in the zone is that fish, with the Starter Rod and with the Leviathan Rod (rarity bonus applied). "
      "Preferred-zone fish are marked ★.\n")
    for z in D.ZONE_ORDER:
        a = zone_weights(z)
        b = dict((f["id"], x) for f, x in zone_weights(z, D.RODS[4]))
        ta, tb = sum(x for _, x in a), sum(b.values())
        w("### %s\n" % D.ZONES[z]["name"])
        w("| Fish | Rarity | Starter Rod | Leviathan Rod |\n|---|---|---|---|")
        for f, x in sorted(a, key=lambda t: -t[1]):
            w("| %s%s | %s | %s | %s |" % (f["name"], " ★" if f["zones"][0] == z else "", f["rarity"], pct(x / ta), pct(b[f["id"]] / tb)))
        w("")

    # ------------------------------------------------------------ 7
    w("## 7. Fish economy and selling values\n")
    w("**Base value** of a species = `%d × rarity multiplier × species factor` (species factor 0.8–1.3; heavier species in a rarity are "
      "worth a bit more). Ruben (Fish Selling Island) pays:\n" % D.BASE_COIN)
    w("```\nprice = round(base_value × size_multiplier × mutation_multiplier)\n"
      "size_multiplier = clamp((weight / average_weight) ^ 0.6, 0.6, 1.8)\n```\n")
    w("| Rarity | Multiplier | Lowest base value | Highest base value | Avg. base value |\n|---|---|---|---|---|")
    for r in D.RARITIES:
        vals = [f["value"] for f in F if f["rarity"] == r]
        w("| %s | ×%d | %d | %d | %d |" % (r, D.RARITY[r]["mult"], min(vals), max(vals), round(sum(vals) / len(vals))))
    w("")
    w("### Size and weight\n")
    w("Every catch gets its own size and weight inside the species range:\n")
    w("```\nt      = (rand() + rand()) / 2            # bell curve, most fish are average\n"
      "t      = t ^ (1 - luck/200)                 # luck nudges toward bigger fish\n"
      "length = lerp(min_length, max_length, t)\n"
      "k      = (length^3 - min_length^3) / (max_length^3 - min_length^3)\n"
      "weight = lerp(min_weight, max_weight, k) × random(0.92, 1.08)   # clamp to the weight range\n```\n")
    w("Weight follows the cube of length, so a longer fish is (almost) always heavier. The model is scaled by "
      "`length / average_length`. Average values in the catalog use the same formula at `t = 0.5`.\n")
    w("### Mutations and value\n")
    w("Mutation multipliers stack with size, not with each other (one mutation per fish). Some mutations also change size or weight "
      "(Golden +10%% weight, Crystal +30%% weight, Ancient +25%% length/+40%% weight, Ghost −50%% weight), applied after the roll.\n")
    bf = next(f for f in F if f["name"] == "Atlantic Bluefin Tuna")
    L_, W_ = 260, 380.0
    sm = max(0.6, min(1.8, (W_ * 1.1 / bf["weight_avg"]) ** 0.6))
    w("**Example – Golden Atlantic Bluefin Tuna:** Legendary, base value %d. Caught at %d cm, %.0f kg → Golden adds 10%% weight → "
      "%.0f kg. Average weight is %.0f kg, size multiplier = %.2f. Price = %d × %.2f × 5 = **%s coins**.\n" % (
          bf["value"], L_, W_, W_ * 1.1, bf["weight_avg"], sm, bf["value"], sm, "{:,}".format(round(bf["value"] * sm * 5))))
    w("### Expected income per bite\n")
    w("Average coins per landed bite (no mutations, average size), counting only fish the rod can hook:\n")
    w("| Zone | %s |\n|---|%s" % (" | ".join(r["name"] for r in D.RODS), "---|" * len(D.RODS)))
    for z in D.ZONE_ORDER:
        row = []
        for rod in D.RODS:
            zw = [(f, x) for f, x in zone_weights(z, rod) if f["difficulty"] <= rod["power"] + HOOK_MARGIN]
            tot = sum(x for _, x in zw)
            row.append("%d" % round(sum(f["value"] * x for f, x in zw) / tot) if tot else "–")
        w("| %s | %s |" % (D.ZONES[z]["name"], " | ".join(row)))
    w("")
    w("**Upgrade pacing** – bites needed to afford the next rod while fishing the best zone of the current rod "
      "(average fish, no mutations, before spending on bait/fuel/boats):\n")
    w("| Current rod | Best zone | Coins per bite | Next rod | Price | Bites needed |\n|---|---|---|---|---|---|")
    for cur, nxt in zip(D.RODS, D.RODS[1:]):
        zones = D.ZONE_ORDER if cur["zones"][0].startswith("all") else cur["zones"]
        best, best_v = None, 0
        for z in zones:
            if z in ("ABYSS", "GROTTO"):          # story/endgame zones with very few bites
                continue
            zw = [(f, x) for f, x in zone_weights(z, cur) if f["difficulty"] <= cur["power"] + HOOK_MARGIN]
            tot = sum(x for _, x in zw)
            v = sum(f["value"] * x for f, x in zw) / tot if tot else 0
            if v > best_v:
                best, best_v = z, v
        price = int(nxt["price"].replace(",", ""))
        w("| %s | %s | %d | %s | %s | ~%d |" % (cur["name"], D.ZONES[best]["name"], round(best_v), nxt["name"], nxt["price"], round(price / best_v)))
    w("\nMutations, big individuals and Legendary catches shorten these numbers a lot, so the Leviathan Rod stays a long-term goal "
      "without feeling out of reach.\n")

    # ------------------------------------------------------------ 8
    w("## 8. Model creation guidelines\n")
    w("All 122 fish models exist and are generated by `Scripts/fish_models.py` from the same data as this document.\n")
    w("- **Style:** low poly, flat shaded, solid colours (no textures), matching the islands. Budget: ~80–700 vertices per fish "
      "(average ~200, all 122 together ~24,500 vertices).")
    w("- **Shapes:** 27 body plans (torpedo, deep, flat, eel, ray, shark, angler, seahorse, mola, ...), 18 tail types, 30+ dorsal "
      "fin types and 40 signature details (bills, lures, horns, barbels, photophores, crystals, ...). Colour is never the only difference.")
    w("- **Scale:** each model is built at the species' **average length** in metres. Scale at runtime by `length / average_length`.")
    w("- **Orientation:** the head points to Blender **-Y**, which is Unity's **+Z (forward)** with the project's FBX export settings; "
      "up is Blender +Z / Unity +Y. Origin = centre of the body.")
    w("- **Materials:** shared colour materials named `M_Fish_<hex>`, eyes `M_FishEye`/`M_FishPupil`, glow `M_FishGlow_<hex>`. "
      "Mutations replace the colour materials (see section 2) and never the eye materials.")
    w("- **Files:** `Blender/Models/Fish.blend` (collections per rarity, a normalised catalogue sheet and the mutation preview) and "
      "`Export/Fish/Fish_###_Name.fbx` (one per fish, at the origin).")
    w("- **Rods and boats:** not modelled here on purpose.\n")
    w("Each fish's individual model description is part of its catalog entry in section 5.\n")

    # ------------------------------------------------------------ 9
    w("## 9. Technical implementation notes\n")
    w("**Data.** Put each fish in a `FishSpecies` ScriptableObject (or one JSON/CSV generated from `fish_data.py`):\n")
    w("```csharp\npublic enum FishRarity { Common, Uncommon, Rare, Epic, Legendary, Mythical }\n"
      "[CreateAssetMenu] public class FishSpecies : ScriptableObject {\n"
      "    public int id; public string displayName; public FishRarity rarity; public string family;\n"
      "    public string[] zones;            // first = preferred zone\n"
      "    public float spawnWeight;         // see section 5\n"
      "    public Vector2 lengthCm, weightKg; public float avgLengthCm, avgWeightKg;\n"
      "    public int baseValue, difficulty;\n"
      "    public GameObject model;          // Export/Fish/Fish_###_Name.fbx\n}\n"
      "public class CaughtFish { public FishSpecies species; public float lengthCm, weightKg; public string mutation; public int price; }\n```\n")
    w("**Spawning a bite.**\n")
    w("```\nzone    = highest-priority FishingZone containing the bobber (else OPEN / DEEP by distance to centre)\n"
      "pool    = species with zone in species.zones\n"
      "weight  = spawnWeight × (1.5 if zones[0] == zone) × (1 + rod.bonus/100 if rarity >= Rare)\n"
      "species = weighted_random(pool)\n"
      "if species.difficulty > rod.power + 8: bite still happens, line snaps during the fight\n"
      "length, weight = size roll (section 7);  mutation = mutation roll (section 2)\n```\n")
    w("**World hooks already in the scene:** `FishingZone_*` empties (zones), `Sea_FishingSpot_1..8` + `Sea_FishSchool_*` (good bite spots "
      "inside Open Ocean), `Cave_Pool_FishingSpot` (Teun's Grotto), `Fish_Lighthouse_BeamRig` (beam for night fish at Lighthouse Point), "
      "`NPC_Ruben_Spot` (selling).\n")
    w("**Waves and boats.** Fishing reads the water height from the existing `WaterManagement.instance.GetWaveHeight(x, z)` "
      "(e.g. to keep the bobber on the surface, the same way `Floater` does). Nothing in the wave code or the boat code needs to change.\n")
    w("**Quests.** `QUESTLINE.md` uses these fish: Q1–Q2 any Common fish, Q5 **Lightfish** (Epic, Lighthouse Point, night), "
      "Q7 **Zilverkoning** (Legendary, Teun's Grotto). Rod unlocks in section 4 follow the quest steps.\n")
    w("**Validation (generator asserts):** exactly %d fish, unique names, 6 rarities (%s), every fish has a zone, a price and a size/weight "
      "range, every zone has fish, 5 rod tiers.\n" % (len(F), ", ".join("%d %s" % (counts[r], r) for r in D.RARITIES)))
    return "\n".join(out)


if __name__ == "__main__":
    text = build()
    with open(OUT, "w") as fh:
        fh.write(text)
    print("wrote", OUT, len(text.splitlines()), "lines")
