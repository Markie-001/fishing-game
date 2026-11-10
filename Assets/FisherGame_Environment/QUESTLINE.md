# Fisher Game – Questline & NPC's

Ontwerpdocument voor latere prompts. Hier staat **wat er in de wereld staat** (namen van objecten, plekken)
en **hoe de questline loopt**. De quests zijn nog **niet** gebouwd: dit is het plan, de 3D-wereld is klaar.

> Tip voor een volgende prompt: "Lees `FisherGame_Environment/QUESTLINE.md` en bouw quest Q1 in Unity."

---

## 1. De wereld in het kort

Blender z 0 = zeeniveau = Unity y 0. Docks liggen op +1,8 m. De golven komen uit de bestaande Unity-code
(`WaterManagement`, `WaterManager`, `Floater`) en worden **niet** aangepast.

| Eiland | Collectie / FBX | Root-object | Wat is er |
|---|---|---|---|
| Home Island | `10_Home_Island` / `Island_Home.fbx` | `Home_Island_Root` | Strandhuis van de speler, steiger, **flessenpost** (`Home_MessageBottle`) |
| Fish Selling Island | `20_FishMarket_Island` / `Island_FishMarket.fbx` | `Fish_Island_Root` | Vuurtoren met viswinkel (Ruben), werkhaven |
| Boat Dealer Island | `30_BoatDealer_Island` / `Island_BoatDealer.fbx` | `Dealer_Island_Root` | Showroom "ISLAND BOATS" (Emre), marina met lege ligplaatsen |
| Fishing Rod Shop Island | `40_RodShop_Island` / `Island_RodShop.fbx` | `Rod_Island_Root` | "BAIT & TACKLE"-winkel (Mark) |
| **Cave Island – Teun's Rots** | `50_Cave_Island` / `Island_Cave.fbx` | `Cave_Island_Root` | Rotsmassief met grot, rotsboog in zee, kamp van Teun, questbord |
| Open zee | `60_Sea_Details` / `Sea_Details.fbx` | `Sea_Details_Root` | Boeien, baken in het midden, riffen, kelp, visscholen, meeuwen |

Elk eiland heeft een dock met fuel pump (`*_FuelPump`).

### Belangrijke markers (lege objecten, voor triggers en scripts)

| Object | Eiland | Gebruik |
|---|---|---|
| `NPC_Emre_Spot` | Boat Dealer | Interactiepunt Emre (achter de balie) |
| `NPC_Mark_Spot` | Rod Shop | Interactiepunt Mark (achter de toonbank) |
| `NPC_Ruben_Spot` | Fish Selling | Interactiepunt Ruben (achter de toonbank in de vuurtoren) |
| `NPC_Teun_Spot` | Cave | Interactiepunt Teun (bij het kampvuur) |
| `Player_Spawn` | Home | Startpunt van de speler (naast het strandhuis), `Player_Model` = speler-model |
| `Home_MessageBottle` | Home | Start van de questline (mesh, op het strand bij de steiger) |
| `Cave_Entrance_Trigger` | Cave | Ingang van de grot (mijnpoort) |
| `Cave_Chest_Spot` | Cave | Oude kist in de grot |
| `Cave_SeaChart_Spot` | Cave | Stenen tafel met zeekaart |
| `Cave_Pool_FishingSpot` | Cave | Gloeiende poel achter in de grot (legendarische vis) |
| `Cave_QuestBoard` | Cave | Prikbord "QUESTS" bij het kamp |
| `Fish_Lighthouse_BeamRig` | Fish Selling | Draaiende lichtbundel (`Unity/LighthouseRotator.cs`) |
| `Sea_FishingSpot_1..8` | Open zee | Visplekken met een visschool eronder (cirkel, ~6 m) |
| `Sea_Beacon_Center` | Open zee | Baken midden in de wereld: handig als ontmoetingspunt in quests |
| `Sea_NavBuoy_<Eiland>_*` | Open zee | Vaargeul naar elk eiland: goed voor een "vaar naar..."-pijl |

---

## 2. De NPC's

De modellen zijn low poly en staan in **A-pose** (armen schuin omlaag). Dat is handig om ze later te riggen,
bijvoorbeeld met Mixamo. Ze zitten nu als statisch mesh in de FBX van hun eiland (`NPC_<Naam>`).

| NPC | Rol | Waar | Uiterlijk | Karakter |
|---|---|---|---|---|
| **Emre** | Boat dealer, verkoopt boten | Boat Dealer Island, showroom, achter de balie | Wit shirt, navy blazer, zonnebril, zwart haar | Gladde verkoper, enthousiast, altijd een "deal" |
| **Mark** | Verkoopt hengels, aas en lijnen | Fishing Rod Shop Island, in de winkel | Groene pet, rossige baard, olijfgroen vest, rode mouwen, laarzen | Nuchter, praktisch, kent elke vissoort |
| **Ruben** | Koopt de gevangen vis | Fish Selling Island, in de vuurtoren | Blauwe muts, geel oliepak, wit schort, witte laarzen | Vrolijk, roddelt graag over wat de vissers zien |
| **Teun** | Questgever | Cave Island, bij zijn kampvuur voor de grot | Kapiteinspet, lange witte baard, bruine jas, lantaarn | Oude kapitein, mysterieus, vertelt over de Zilverkoning |

### Voorbeeldzinnen (voor dialogen)

- **Teun**: "Zo, dus mijn fles is aangespoeld. Dan ben jij de nieuwe visser waar de zee om vroeg."
- **Mark**: "Teun stuurt je? Dan krijg je deze bamboe hengel van mij. Breek hem niet."
- **Ruben**: "Verse makreel! Daar geef ik je een eerlijke prijs voor. Nou ja, bijna eerlijk."
- **Emre**: "Die oude roeiboot van jou? Kom op. Voor een klein bedrag vaar je in stijl!"

---

## 3. Questline: "De Zilverkoning van Teun's Rots"

**Verhaal:** Teun is een oude kapitein die in de grot op het rotseiland woont. In de gloeiende poel
achter in zijn grot leeft volgens de legende **de Zilverkoning**, een vis die nog nooit iemand heeft gevangen.
Teun is te oud om hem zelf te vangen en zoekt een opvolger. Hij gooit een fles met een briefje in zee...

Bedragen en beloningen zijn **voorstellen**. Pas ze aan als de economie bestaat.

| ID | Titel | Gever | Vereist | Doel (stappen) | Plekken / objecten | Beloning (voorstel) | Ontgrendelt |
|---|---|---|---|---|---|---|---|
| **Q0** | Flessenpost | – (start) | Nieuw spel | 1. Raap de fles op het strand op. 2. Lees het briefje: *"Zoek de oude kapitein bij de grote rots in het noorden."* 3. Vaar naar Cave Island en praat met Teun. | `Home_MessageBottle` → `NPC_Teun_Spot` | – | Q1 |
| **Q1** | Een echte hengel | Teun | Q0 | 1. Vaar naar de hengelwinkel. 2. Praat met Mark: hij geeft je de **Bamboe hengel** omdat Teun je stuurt. 3. Vang 3 vissen (mag overal). | `NPC_Mark_Spot` | Bamboe hengel (gratis) | Q2 |
| **Q2** | Eerste verkoop | Teun | Q1 | 1. Verkoop minstens 3 vissen bij Ruben in de vuurtoren. 2. Ruben vertelt dat vissers 's nachts een zilveren glinstering zien. 3. Vertel het aan Teun. | `NPC_Ruben_Spot` → `NPC_Teun_Spot` | Geld voor de vis + 50 bonus | Q3 |
| **Q3** | Volgtanken! | Teun | Q2 | 1. Tank bij een fuel pump. 2. Leg aan bij alle 5 de docks (eilandtocht). | Alle `*_FuelPump`, alle `*_Dock` | 100 | Q4 |
| **Q4** | Een betere boot | Emre | Q3 | 1. Spaar geld. 2. Koop bij Emre een boot uit de showroom. Emre: *"Met die oude schuit kom je nooit door de nachtelijke golven bij de rots."* | `NPC_Emre_Spot`, showroom | Nieuwe boot (gekocht) | Q5 |
| **Q5** | Licht in de nacht | Ruben | Q4 | 1. Wacht tot het nacht is. 2. Vis in de lichtbundel van de vuurtoren en vang een **Lichtvis**. 3. Breng hem naar Teun. | Water rond Fish Selling Island, `Fish_Lighthouse_BeamRig` | 150 + Lichtvis-trofee | Q6 |
| **Q6** | De oude zeekaart | Teun | Q5 | 1. Ga de grot in. 2. Open de kist: daarin zit de sleutel van Teun's poel. 3. Bestudeer de zeekaart op de stenen tafel. 4. Haal bij Mark de **Kristallijn**, de enige lijn die sterk genoeg is. | `Cave_Entrance_Trigger`, `Cave_Chest_Spot`, `Cave_SeaChart_Spot`, `NPC_Mark_Spot` | Kristallijn (kopen) | Q7 |
| **Q7** | De Zilverkoning | Teun | Q6 | 1. Vis bij de gloeiende poel in de grot. 2. Vang de **Zilverkoning** (moeilijkste vangst). 3. Laat hem aan Teun zien. | `Cave_Pool_FishingSpot` → `NPC_Teun_Spot` | Teun's kapiteinspet + titel "Kapitein" + 1000 | Einde hoofdverhaal |

### Na het hoofdverhaal (ideeën)

- **Dagelijkse quests** op het questbord (`Cave_QuestBoard`): "Vang 5 makrelen voor Ruben", "Breng Mark 10 aas".
- Ruben betaalt dubbel voor vis die 's nachts gevangen is.
- Emre krijgt nieuwe boten als de speler "Kapitein" is.

### Quest-status (voorstel voor de variabelen)

```
questStage: 0..8       // 0 = Q0 bezig, 8 = alles klaar
hasBambooRod, hasCrystalLine, hasChestKey: bool
fishSoldToRuben: int
docksVisited: set<string>  // "Home", "Fish", "Dealer", "Rod", "Cave"
caughtLightFish, caughtSilverKing: bool
```

---

## 4. Easter eggs (spoilers)

Ideaal voor achievements of een geheime quest. Wereldcoördinaten in Blender (x, y).

| Object | Waar | Wat |
|---|---|---|
| `EE_Shipwreck` + `EE_Shipwreck_TreasureChest` | Noordwest (-360, 300) | Gezonken schip met de mast boven water; op de bodem ligt een schatkist met goud |
| `EE_TreasureIslet` | Zuidoost (380, -385) | Mini-zandbankje met één palm, een rode **X** en een schep |
| `EE_RubberDuck` | Zuidwest (-390, -380) | Reusachtige badeend die rondjes drijft |
| `EE_SeaSerpent` | Noordoost (380, 395) | Zeeslang: drie bulten, kop met hoorns en een staartvin boven water |
| `EE_Cave_TeunWasHere` | In de grot van Teun, achterwand | Ingekerfd: "TEUN WAS HERE" |
| `EE_GoldenFish` | Achter de vuurtoren, op de klif | Klein gouden visbeeldje op een steen |

Idee: wie alle 6 vindt, krijgt van Teun een gouden hengel.

## 5. Afspraken voor latere prompts

- **3D-wereld**: alles komt uit `Scripts/build_all.py`. Pas eilanden aan in `Scripts/island_*.py`
  en NPC-uiterlijk in `NPC_STYLES` in `Scripts/fg_assets.py`. Daarna opnieuw draaien en de FBX'en exporteren.
- **Water/golven**: niet aankomen, die doet de bestaande Unity-code.
- **Naamgeving**: objecten beginnen met hun eiland (`Home_`, `Fish_`, `Dealer_`, `Rod_`, `Cave_`), NPC's met `NPC_`.
- **Wat nog niet bestaat**: vangen, inventaris, geld, winkels, dialogen, quest-systeem, dag/nacht-cyclus,
  rigging/animaties van de NPC's. Die bouwen we later, in Unity.
