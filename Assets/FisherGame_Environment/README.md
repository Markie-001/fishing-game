# Fisher Game – Island Environment

Low-poly (maar niet té low-poly) 3D-wereld met vijf eilanden en vier NPC's voor de fisher game.
De questline en alle NPC-/questplekken staan in **[QUESTLINE.md](QUESTLINE.md)**.
Alleen de omgeving: geen gameplay, geen nieuw watersysteem.

## Mappen

| Map | Inhoud |
|---|---|
| `Blender/FisherGame_Islands.blend` | Het Blender-bestand. Scène **FisherWorld** bevat de wereld. |
| `Scripts/` | Python-scripts die de hele wereld opbouwen (zie hieronder). |
| `Export/` | Eén FBX per eiland, klaar voor Unity. |
| `Unity/LighthouseRotator.cs` | Draait de lichtbundel van de vuurtoren in Unity. |
| `Renders/` | Overzichtsrender van de wereld, `Fish_Catalog_Sheet.png` (alle 122 vissen) en `Fish_Mutations_Preview.png`. |
| `QUESTLINE.md` | NPC's, questline en afspraken voor latere prompts. |
| `fish_catalog.md` | **Viscatalogus**: 122 vissen, 6 rarities, 12 viszones, 5 hengels, 10 mutaties, economie (Engels). |
| `Blender/Models/Fish.blend` | Alle 122 vismodellen (los van het wereldbestand). |
| `Export/Fish/` | Eén FBX per vis (`Fish_###_Naam.fbx`), op ware gemiddelde grootte. |

## De vijf eilanden

| Eiland | Grootte | Karakter | Dock + fuel pump |
|---|---|---|---|
| **Home Island** (`10_Home_Island`) | middel (~85 m) | Tropisch: wit strand, palmen, duin-heuvel, rotsklif aan de achterkant. Strandhuisje op palen met veranda, hangmat, kampvuur, ligstoelen, surfplanken. | T-vormige privé-steiger met zijsteiger (leeg) voor de eigen boot, rode pomp. |
| **Fish Selling Island** (`20_FishMarket_Island`) | middel (~95 m) | Ruige kust met hoge kliffen, grasland en dennen. **Vuurtoren** (~28 m) met de **visverkoper op de begane grond** (toonbank, ijsvitrine met vis, weegschaal, prijsbord, wenteltrap). Wachterhuisje ernaast. | Brede werkhaven met losplatform, kraan, viskratten, netten, blauwe pomp. Ligplaatsen zijn leeg. |
| **Boat Dealer Island** (`30_BoatDealer_Island`) | groot (~150 m) | Modern: glazen showroom "ISLAND BOATS" met 3 boten op podia, plein met vlaggen, botenlift met boot. | Marina met 8 lege ligplaatsen en een overdekt tankstation met 2 gele pompen. |
| **Fishing Rod Shop Island** (`40_RodShop_Island`) | klein (~60 m) | Rotsig met dennenheuvel. Verweerde **"BAIT & TACKLE"**-winkel met binnenruimte: hengelrekken, kunstaasschappen, aasvriezer, toonbank, opgezette vis, vis-bord op het dak. | Zigzag-steiger met netten-schuurtje, kreeftenfuiken, vaten, rode pomp. |
| **Cave Island – Teun's Rots** (`50_Cave_Island`) | klein (~70 m) | Rotsig eilandje met een breed, gelaagd **rotsmassief** en een natuurlijke **rotsboog** in zee. In het massief zit een **grot** met mijnpoort: gloeiende poel, kristallen, oude kist, stenen tafel met zeekaart, fakkels. Kamp van Teun met tent, kampvuur en questbord. In de grot zit ook een easter egg. | Korte L-steiger, blauwe pomp. |

Elk eiland heeft één root-object (`<Eiland>_Island_Root`) met daaronder de collecties
`Terrain`, `Buildings`, `Dock`, `Props`, `Vegetation`, `Lights` en `NPCs`.
Objectnamen beginnen met het eiland (`Home_`, `Fish_`, `Dealer_`, `Rod_`, `Cave_`), NPC's met `NPC_`.
Bomen, rotsen, pompen, vaten enz. zijn **gedeelde assets** (`00_Assets_Library`, uitgesloten van de view layer):
één mesh, veel instanties.

## NPC's

| NPC | Rol | Waar |
|---|---|---|
| **Emre** (`NPC_Emre`) | Boat dealer | Showroom, achter de balie |
| **Mark** (`NPC_Mark`) | Hengelverkoper | Bait & Tackle-winkel, achter de toonbank |
| **Ruben** (`NPC_Ruben`) | Koopt je vis | Vuurtoren, achter de toonbank |
| **Teun** (`NPC_Teun`) | Questgever | Cave Island, bij het kampvuur |

Low-poly modellen in A-pose (klaar om later te riggen), met een leeg `NPC_<Naam>_Spot` als interactiepunt.
**De speler** (`Player_Model`) staat op Home Island naast de trap van het strandhuis, met `Player_Spawn` als startpunt.

Meer markers (grot, kist, poel, flessenpost, visplekken) staan in [QUESTLINE.md](QUESTLINE.md).

## Op en in het water (`60_Sea_Details` / `Sea_Details.fbx`)

- **Vaargeul-boeien**: rood/groen poortje (2 paar) op de aanvaarroute naar elk eiland, met lichtje (`Sea_NavBuoy_*`).
- **Meerboeien** bij Home en de marina, **fuikboeitjes** met vlaggetjes bij Rod, Fish en Cave, een **netboeienlijn** bij Fish Island.
- **Zwemvlot** voor het strand van Home (`Sea_SwimRaft_Home`).
- **Baken** midden in de zee (`Sea_Beacon_Center`), geel/zwart met licht: oriëntatiepunt.
- **Riffen**: 6 rotsgroepen die uit het water steken tussen de eilanden (`Sea_Reef_*`).
- **Onder water**: kelp rond elk eiland, 8 visscholen (`Sea_FishSchool_*`) met een marker `Sea_FishingSpot_*` (voor later vissen).
- **Meeuwen**: zittend op baken, riffen en boeien, en vliegend boven elk eiland. Verder drijvende vaten en een kist.

Alles staat stil. Wil je dat een boei op de golven dobbert: Rigidbody + jullie `Floater`-script erop.

## Easter eggs (`70_EasterEggs` / `EasterEggs.fbx`)

Er zijn er 6 verstopt. Waar ze liggen staat (met spoilers) in [QUESTLINE.md](QUESTLINE.md#4-easter-eggs-spoilers).

## Vissen

Alles over de vissen komt uit één databestand: `Scripts/fish_data.py`. Daaruit worden gemaakt:

- `fish_catalog.md` met `python3 Scripts/fish_catalog_gen.py` (controleert ook: precies 122 vissen, unieke namen, elke vis een zone en prijs).
- `Blender/Models/Fish.blend`, de FBX'en in `Export/Fish/` en de twee renders met `fish_build.build()` in Blender (Scripting-tab: `import sys; sys.path.insert(0, '<pad>/Scripts'); import fish_build; fish_build.build()`).

De modellen zijn low poly en flat shaded, in de stijl van de eilanden, met 27 lichaamsbouwen en veel verschillende vinnen, staarten en details (zwaarden, lampjes, hoorns, voeldraden, kristallen...). In `Fish.blend` staan ze per rarity, plus een genormaliseerd overzicht (`Catalog_Sheet`) en `Mutation_Preview` (dezelfde vis met alle 10 mutaties via materiaalwissel).

**Visgalerij onder de map** (`85_Fish_Gallery`, `Export/FishGallery.fbx`): alle 122 vissen (2× vergroot, kleine visjes minstens 40 cm) op een vloer 60 m onder het midden van de zee (x 0, y 0, z −60), in rijen van 12 per rarity, van opzij te zien, met ruimte tussen de namen. Instellingen bovenaan `Scripts/fish_build.py` (`GALLERY_SCALE`, `LABEL_SIZE`, `LABEL_GAP`). De naambordjes zijn tekst-curves en zitten alleen in Blender, niet in de FBX. Handig om alle modellen in de wereld te bekijken; spelers kunnen er niet komen.

**Viszones** staan als cirkels in de wereld (`80_FishingZones`, `Export/FishingZones.fbx`): `FishingZone_<CODE>_<n>_r<straal>` met custom properties `zone`, `radius`, `priority`. Hengels en boten zijn alleen beschreven, niet gemodelleerd.

## Zeebodem (`02_Seabed` / `Seabed.fbx`)

Een low-poly zandbodem onder de hele zee: rond −13 m tussen de eilanden, aflopend naar ~−20 m aan de rand (The Drop). Zo kijk je nergens meer door het water de leegte (of de visgalerij) in. Neem `Seabed.fbx` mee in Unity, ook op (0, 0, 0).

## Water en de bestaande wave-code

De zee komt uit jullie eigen Unity-scripts (`WaterManagement`, `WaterManager`, `Floater`). Daar is niets aan veranderd.

- Zeeniveau = Blender z 0 = Unity y 0 (de hoogte van het water-object).
- `GetWaveHeight` blijft binnen ±`amplitude` (standaard 1 m). **Docks liggen op +1,8 m**,
  stranden lopen geleidelijk onder water. Zet `amplitude` niet hoger dan ~1,5, anders slaan de golven over de steigers.
- `Sea_Placeholder_NotForExport` is alleen een plat vlak om in Blender te kunnen kijken. Het zit niet in de FBX'en.
- Tip: `WaterManager` past elk punt van het water-mesh elk frame aan. Gebruik voor deze wereld (~900 × 900 m)
  een water-grid met cellen van ongeveer 3–4 m, niet de standaard Unity-plane opgeschaald.

## In Unity zetten

1. Sleep alle FBX'en uit `Export/` in `Assets/` (5 eilanden + `Seabed` + `Sea_Details` + `EasterEggs` + `FishingZones` + optioneel `FishGallery`). De vissen uit `Export/Fish/` zijn losse prefabs (niet op (0,0,0) in de wereld zetten, maar spawnen).
2. Zet ze allemaal op positie (0, 0, 0). Ze vallen dan vanzelf op de goede plek.
3. Wil je de lampen mee: zet bij het model **Import Lights** aan en stel de intensiteit in Unity bij
   (Blender gebruikt watt, Unity niet). Anders gewoon zelf lichten plaatsen.
4. Vuurtoren: zet `LighthouseRotator` op `Fish_Lighthouse_BeamRig`. Geef `M_LighthouseBeam` in Unity
   een transparant/additive materiaal; dat effect neemt FBX niet mee.
5. Glas (`M_Glass`) en `M_FresnelLens` ook transparant zetten in Unity.
6. Colliders: Mesh Collider op de `*_Terrain`, `*_Dock` en gebouwen.

## Vertex-budget

Alles samen: **~69.400 vertices** (wereld ~44.900, alle 122 vissen ~24.500), de helft van de eerste versie. Bijstellen kan centraal in `Scripts/fg_lib.py`:

- `TERRAIN_CELL_SCALE` (nu 1.6): hoger = grover terrein.
- `SCATTER_DENSITY` (nu 0.4): aantal bomen, struiken en rotsen.

Vissen: `self.N, self.R` (ringen × hoeken van het lijf) in `Scripts/fish_models.py`.

## Opnieuw opbouwen in Blender

Open `Blender/FisherGame_Islands.blend` → Scripting → open `Scripts/build_all.py` → Run Script.
Alles wordt opnieuw gegenereerd. Wil je één eiland, zet bovenaan `ONLY = {"Home"}`
(of `"Fish"`, `"Dealer"`, `"Rod"`, `"Cave"`).

Eilandvorm, positie en richting aanpassen: zie `shape()` en de constanten bovenaan elk `island_*.py`.
Posities van de eilanden staan in `Scripts/fg_world.py` (`ISLANDS`).
