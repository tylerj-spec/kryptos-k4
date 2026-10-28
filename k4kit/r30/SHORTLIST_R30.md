# R30 human-review shortlist (REVIEW ONLY unless marked CANDIDATE)

Each row is the raw 97-letter output of the English search for one key setting, exactly as decrypted (it re-encrypts to K4 with its own alphabets, checked independently).
- **Forced mask:** the letters the clue equations force for that key (`.` means the optimiser chose the letter). Only forced letters are evidence.
- **W:** the word score. Readable planted English scores about −69 to −95. The best wrong keys reach about −115.
- **Word split:** the scorer's own segmentation, given as an interpretation aid only.

**Why every row shows EASTNORTHEAST and BERLINCLOCK.**
- Each row starts from the original K4 ciphertext and re-encrypts back to it exactly.
- These families assume two *unknown* scrambled alphabets, besides the key. The 24 known letters are the only firm information about those alphabets, so they are used to fill them in, and every row shows the clues by construction.
- Without the clues even the true key fails: 0/8 planted messages recovered (ledger L109).
- **The real checks are elsewhere.**
  - The exact clue test rejects about 2,099 of every 2,100 keys before any filling happens (Carter book: 1,131,312 → 585).
  - A right key would make the other 73 letters readable, and the same on every re-run. Wrong keys leave most of them to the optimiser, which is why the rest differs from run to run.
- With fixed standard alphabets (nothing fitted), the clues must appear on their own. For the Carter book they never do: best 9/24 over 13.6 million decryptions, about what luck gives (L109).

| Family | Settings | Best W | Bar | Candidates |
|---|---|---|---|---|
| E4 Carter & Mace 1923 vol. I as running key, all 585 passes (English, 64 restarts) | 585 | -140.51 | -114.90 | 0 |
| E6 Carter passes + 39 Gromark primers, German word model | 624 | -121.44 | -117.07 | 0 |
| E6 Carter passes + 39 Gromark primers, Dutch word model | 624 | -121.32 | -112.05 | 0 |
| E6 Carter passes + 39 Gromark primers, mixed English/German/Dutch model | 624 | -103.30 | -99.89 | 0 |
| E1 chain addition, 6/7-digit primers (English) | 4246 | -136.40 | -114.90 | 0 |
| E2 one-cycle K3-style routes + Gromark (English) | 6607 | -142.19 | -114.90 | 0 |
| E5 one mis-carved clue letter + Gromark (English) | 3178 | -140.94 | -114.90 | 0 |
| E3a 5-digit Gromark, 39 primers (punctuation model; exploratory, gate failed) | 39 | -131.99 | -114.90 | 0 |
| E3b two-cycle K3-style routes + Gromark (punctuation model; exploratory) | 39 | -138.50 | -114.90 | 0 |
| Reference: 5-digit Gromark, 39 primers (English, re-run) | 39 | -140.88 | -114.90 | 0 |
| Reference: two-cycle routes (English, re-run) | 39 | -148.34 | -114.90 | 0 |

## E4 Carter & Mace 1923 vol. I as running key, all 585 passes (English, 64 restarts)

- **Searched:** 585 settings at 64 restarts.
- **Best W** -140.51, median -160.71, bar -114.90; above the bar: 0.
- **Candidates:** 0.

**BOOK|carter_v1_doran|fwd|KRY|232399**: W -140.51 (below the bar, so not replicated); forced beyond clues 4; REVIEW ONLY

```
raw   UPIRSZBEAISUSIUPCLADAEASTNORTHEASTWINDAUOFBYMBREDINEYGAPMENILQUBERLINCLOCKFANREEDTYPESWADOCUTKBAT
mask  .....................EASTNORTHEAST.I..............N............BERLINCLOCK...................K..T
```
Word split (interpretation): `UP I RSZ BE A IS US I UP CLAD A EAST NORTHEAST WIND A U OF BY M BRED IN EY GAP MEN IL QU BERLIN CLOCK FAN REED TYPES WA DO CUT KB AT`

**BOOK|carter_v1_doran|rev|AZ|126618**: W -140.85 (below the bar, so not replicated); forced beyond clues 4; REVIEW ONLY

```
raw   VEJUSTZUMIHEFEEISLOWBEASTNORTHEASTMMISDRYRGEWHMXIIUNOWNGIDRAHVIBERLINCLOCKTMMASSUNOISIFAUMMAISBUD
mask  .....................EASTNORTHEAST..........................H..BERLINCLOCK...AS......I...........
```
Word split (interpretation): `VE JUST ZUM I HE FEE IS LOW BEAST NORTHEAST MM IS DRY RGEW~ HM XII UN OWN GIDR~ AH VI BERLIN CLOCK TM MASS UNO IS IF A UM MAIS BUD`

**BOOK|carter_v1_doran|rev|AZ|187055**: W -141.18 (below the bar, so not replicated); forced beyond clues 6; REVIEW ONLY

```
raw   FOIMONSMITHEOTMLOWANPEASTNORTHEASTVINAGFIDNGASRIBYIUPWAYPARFELLBERLINCLOCKBEDAERZAHEBUSHOMYESITAX
mask  ........I....T.......EASTNORTHEAST.I..............I............BERLINCLOCK.E.A...................
```
Word split (interpretation): `FO IM ONS MIT HE O TM LOW ANP EAST NORTHEAST V IN AG FIDN~ GA SRI BY I UP WAY PAR FELL BERLIN CLOCK BE DA ERZA HE BUSH OM YES I TAX`

**BOOK|carter_v1_doran|rev|KRY|164568**: W -141.35 (below the bar, so not replicated); forced beyond clues 8; REVIEW ONLY

```
raw   HERNODLUEVBCIOZSHEAHBEASTNORTHEASTBYAAETHMEZRAPAYARESOISHAARMWEBERLINCLOCKMEHADIONASHCFNMDAIORDXV
mask  ........E........E...EASTNORTHEAST....ET.....A.................BERLINCLOCK.E.A..O................
```
Word split (interpretation): `HER NODLUE~ VB CIO Z SHE AH BEAST NORTHEAST BY A AET HM EZRA PAY ARE SO IS HAAR M WE BERLIN CLOCK ME HAD I ON ASH CF NM DA I ORD XV`

**BOOK|carter_v1_doran|rev|AZ|162943**: W -141.40 (below the bar, so not replicated); forced beyond clues 4; REVIEW ONLY

```
raw   TIMEAIBYLLMYISIXIPGTOEASTNORTHEASTNDEVAAXIJMREWOEUPFEBOMXIXHADOBERLINCLOCKUPPIELEOHMWESEYEWASNDUA
mask  .............S.......EASTNORTHEAST.......I.....................BERLINCLOCK......E....E...........
```
Word split (interpretation): `TIME A I BY LL MY I SIX I PG TO EAST NORTHEAST N DE VA AX IJM~ RE WOE UP FEB OM XIX HAD OBERLIN CLOCK UPPIE LEO HM WES EYE WASN DU A`

## E6 Carter passes + 39 Gromark primers, German word model

- **Searched:** 624 settings at 64 restarts.
- **Best W** -121.44, median -133.15, bar -117.07; above the bar: 0.
- **Candidates:** 0.

**BOOK|carter_v1_doran|fwd|AZ|246833**: W -121.44 (replication W -121.44, 0 letters changed); forced beyond clues 7; REVIEW ONLY

```
raw   CRZNEINESIEKALKPKREISEASTNORTHEASTMITDAOFMCSOZUPAYNEONFDPJANAUMBERLINCLOCKHFMALDHUGEMALWIECAMPFIG
mask  ...........K.L.......EASTNORTHEAST.I.......S......N............BERLINCLOCK...AL..................
```
Word split (interpretation): `CR ZN EINE SIE KALK P KREIS EAST NORTHEAST MIT DA OF MC SO ZU PAYNE ON FDP JANA UM BERLIN CLOCK HF MAL D HUGE MAL WIE CAMP FIG`

**BOOK|carter_v1_doran|rev|AZ|154385**: W -122.47 (replication W -124.79, 47 letters changed); forced beyond clues 6; REVIEW ONLY

```
raw   AUSTNOXZUVOLLEFORMVIDEASTNORTHEASTPPKAVTINYKLINGTLIOFTZTWERWIRABERLINCLOCKOMMILMALINOHSODEUNDUNIS
mask  ...T.................EASTNORTHEAST.....T.N........I............BERLINCLOCK....L.................S
```
Word split (interpretation): `AUS T NOX ZU VOLLE FORM VID EAST NORTHEAST PP KAV TINY KLINGT LI OF TZT WER WIR A BERLIN CLOCK OM MIL MAL IN OH SO DE UND UNIS`

**BOOK|carter_v1_doran|rev|AZ|25621**: W -123.84 (replication W -123.50, 44 letters changed); forced beyond clues 8; REVIEW ONLY

```
raw   ALDEOWIENDEEDDYUABNAMEASTNORTHEASTINUNDAELTERESUSFLEXEHMCBWOIHMBERLINCLOCKSNGAROEKOLAMMAUCHYKVBCO
mask  ........N............EASTNORTHEAST.N.N....T...S................BERLINCLOCK.N.A..E................
```
Word split (interpretation): `AL DE O WIEN DE EDDY U AB NAM EAST NORTHEAST IN UND AELTERES US FLEX EH MCB WO IHM BERLIN CLOCK SN GAR OEKO LAMM AUCH Y KVB CO`

**BOOK|carter_v1_doran|rev|AZ|225846**: W -124.32 (replication W -126.11, 61 letters changed); forced beyond clues 5; REVIEW ONLY

```
raw   ESZUFRISSTDERGEOIMNUREASTNORTHEASTNESDOMITIANNFOXYDIRWAVAFHSEAMBERLINCLOCKEDMALIDEETVCLBTWDRKAMGV
mask  .....................EASTNORTHEAST.E..O........................BERLINCLOCK...AL..............A...
```
Word split (interpretation): `ES ZU FRISST DER GEO IM NUR EAST NORTHEAST NES DOMITIAN N FOXY DIR WAV AF HSE AM BERLIN C LOCKED MAL IDEE TV CL BTW DR KAM GV`

**G5|22856**: W -124.33 (replication W -125.52, 13 letters changed); forced beyond clues 9; REVIEW ONLY

```
raw   GSAALSHAUSKUUNSHEYFAZEASTNORTHEASTDIETRGEILATXWOHLTZAUCHMLBVYOUBERLINCLOCKDESTVRCRSPUELISTINNAFAX
mask  ..A..................EASTNORTHEAST.I.....IL.........A........O.BERLINCLOCK.E.........E.......A...
```
Word split (interpretation): `GSA ALS HAUS KU UNS HEY FAZ EAST NORTHEAST DIE TR GEIL AT X WOHL TZ AUCH ML BV YOU BERLIN CLOCK DES TVR CR SPUEL IST IN NA FAX`

## E6 Carter passes + 39 Gromark primers, Dutch word model

- **Searched:** 624 settings at 64 restarts.
- **Best W** -121.32, median -131.03, bar -112.05; above the bar: 0.
- **Candidates:** 0.

**BOOK|carter_v1_doran|rev|KRY|73183**: W -121.32 (replication W -124.39, 61 letters changed); forced beyond clues 2; REVIEW ONLY

```
raw   IMPULSHARDDOOVNOFZOADEASTNORTHEASTDEEPAFCAVAAMYBIJLABIJZUIDNAGABERLINCLOCKCAFJAISNYCREENHETMNHOSP
mask  .....................EASTNORTHEAST.E...........................BERLINCLOCK...........E...........
```
Word split (interpretation): `IMPULS HARD DOO VN OF ZO A DE AS T NORTHEAST DEEP AF CAVA A MY BIJ LA BIJ ZUID NA GA BERLIN CLOCK CAF JA IS NYC R EEN HET MN HOSP`

**BOOK|carter_v1_doran|rev|KRY|196114**: W -121.88 (replication W -126.81, 57 letters changed); forced beyond clues 6; REVIEW ONLY

```
raw   YCBSKAPOCHNSCBDIKENAFEASTNORTHEASTSCMETKIDHELDWKFUCKBYSACAFIKENBERLINCLOCKTOASIANKATEPRAATMAGVIND
mask  ...S.............E...EASTNORTHEAST...E.......................E.BERLINCLOCK.O....N................
```
Word split (interpretation): `Y CBS KAP OCH NS CBD IK EN A FEAST NORTHEAST SC MET KID HELD WK FUCK BY SAC AF IK EN BERLIN CLOCK TO ASIAN KATE PRAAT MAG VIND`

**BOOK|carter_v1_doran|rev|KRY|52903**: W -122.08 (replication W -125.59, 22 letters changed); forced beyond clues 8; REVIEW ONLY

```
raw   SOLCNEOFDRGAJEYORKMEEEASTNORTHEASTROKKMWUNOCHLYNDPHIJKWAMNARTVXBERLINCLOCKOPPELTBEDANIETOMWEZACHT
mask  ...........A.........EASTNORTHEAST.O.....N...........K.........BERLINCLOCK....L......I.......A..T
```
Word split (interpretation): `SO LC NE OF DR GA JE YORK MEE EAST NORTHEAST ROK KM WU NOCH LYN DP HIJ KWAM NA RTV X BERLIN CLOCK OP PELT BE DA NIET OM WE ZACHT`

**BOOK|carter_v1_doran|rev|AZ|162943**: W -122.17 (replication W -121.10, 61 letters changed); forced beyond clues 4; REVIEW ONLY

```
raw   GAFOMPLNUWAYASPHALTHHEASTNORTHEASTOPIMAMRICAREYVIELJECVRMLOONPZBERLINCLOCKALSIOPEDERDEZOTOMMYNLEM
mask  .............S.......EASTNORTHEAST.......I.....................BERLINCLOCK......E....E...........
```
Word split (interpretation): `GAF OM PL NU WAY ASPHALT HH EAST NORTHEAST OP IM AMRI CAREY VIEL JE CVRM LOON PZ BERLIN CLOCK ALS I OP E DER DE ZO TOMMY NL EM`

**BOOK|carter_v1_doran|fwd|AZ|246926**: W -122.22 (replication W -123.77, 31 letters changed); forced beyond clues 6; REVIEW ONLY

```
raw   LOCOUEENZULOPOEDKPNOFEASTNORTHEASTERVANXYOUOECKANIKNUUSTAPJEFEWBERLINCLOCKMIJNLTHDATIPTVALNUINZAL
mask  .....................EASTNORTHEAST....N..O...................E.BERLINCLOCK.I..L.................L
```
Word split (interpretation): `LOCO U EEN ZUL OP OED KPN OF EAST NORTHEAST ER VAN X YOU OE C KAN IK NU U STAPJE FEW BERLIN CLOCK MIJN L TH DAT IPTV AL NU IN ZAL`

## E6 Carter passes + 39 Gromark primers, mixed English/German/Dutch model

- **Searched:** 624 settings at 64 restarts.
- **Best W** -103.30, median -115.57, bar -99.89; above the bar: 0.
- **Candidates:** 0.

**BOOK|carter_v1_doran|rev|AZ|115847**: W -103.30 (replication W -113.07, 57 letters changed); forced beyond clues 6; REVIEW ONLY

```
raw   HEDUAOFHIJOPDANNYPHSVEASTNORTHEASTJUNGETETETEOFHYIMDEBTTASBYMAGBERLINCLOCKMEGAWAGTEFARGLAAENDEMZU
mask  ........I............EASTNORTHEAST....ET...T...................BERLINCLOCK.E.A...................
```
Word split (interpretation): `HE DU A OF HIJ OP DANNY P HSV EAST NORTHEAST JUNGE TE TE TE OF HY IM DEBT TAS BY MAG BERLIN CLOCK MEGA WAGTE FAR GLA A EN DEM ZU`

**BOOK|carter_v1_doran|rev|AZ|100568**: W -105.00 (replication W -105.09, 16 letters changed); forced beyond clues 6; REVIEW ONLY

```
raw   CRYZALSIEBIJALWSICINBEASTNORTHEASTENIGFDJNAVYPROFOMAHAARGOTENOUBERLINCLOCKETOFZAGEXAISTIEYESWEDEA
mask  ........E....L.......EASTNORTHEAST.N.....N...........A.......O.BERLINCLOCK.......................
```
Word split (interpretation): `CRY ZAL SIE BIJ ALWS~ IC IN BEAST NORTHEAST ENIG FDJ NAVY PROF OM A HAAR GO TE NOU BERLIN CLOCK ET OF ZAG EX A IST I EYES WE DE A`

**BOOK|carter_v1_doran|fwd|AZ|171060**: W -105.52 (replication W -109.60, 57 letters changed); forced beyond clues 8; REVIEW ONLY

```
raw   MOORDVOORLETDSUFFISOPEASTNORTHEASTALSIFMEWIDIPAYDIITASDEESZOIGOBERLINCLOCKWITHMAINUGIEVAJEFAAWIRA
mask  .............S...I...EASTNORTHEAST...I............I.A..........BERLINCLOCK.I....I....E...........
```
Word split (interpretation): `MOORD VOOR LET D SUFF IS OP EAST NORTHEAST ALS IF ME WID~ I PAY DI IT AS DE ES ZO I GO BERLIN CLOCK WITH MAI NU GIEV~ A JE FAA WIR A`

**BOOK|carter_v1_doran|rev|KRY|48714**: W -106.24 (replication W -105.85, 24 letters changed); forced beyond clues 5; REVIEW ONLY

```
raw   BNUNDIEIVIAIOFMOGWAIMEASTNORTHEASTIKWIJLOSSENOFBEWKOHFAMETAIETSBERLINCLOCKBIERJESOFAWARYIFKIPKLOM
mask  .....................EASTNORTHEAST...I.L..S....................BERLINCLOCK.I.................K...
```
Word split (interpretation): `B NUN DIE I VIA I OF MOGWAI M EAST NORTHEAST IK WIJ LOSSEN OF BE WK OH FA MET A IETS BERLIN CLOCK BIER JE SOFA WARY IF KIP KLOM`

**BOOK|carter_v1_doran|fwd|AZ|231873**: W -106.82 (replication W -109.35, 9 letters changed); forced beyond clues 6; REVIEW ONLY

```
raw   PTNONLYZUWGJGVPWHORDWEASTNORTHEASTIMENIMBAATBMUIIHRENWAARDIGDATBERLINCLOCKICHHUNHADJBIGHABEERAVON
mask  .................O...EASTNORTHEAST...NI....T...................BERLINCLOCK...........I.......A...
```
Word split (interpretation): `PTN ONLY ZU WG JG VP WHO RDW EAST NORTHEAST IM EN IM BAAT BMU I IHREN WAARDIG DAT BERLIN CLOCK ICH HUN HADJ BIG HABE ER A VON`

## E1 chain addition, 6/7-digit primers (English)

- **Searched:** 4246 settings at 16 restarts.
- **Best W** -136.40, median -167.17, bar -114.90; above the bar: 0.
- **Candidates:** 0.

**E1|b6|537979**: W -136.40 (replication W -141.97, 58 letters changed); forced beyond clues 12; REVIEW ONLY

```
raw   HOISLKQUGRSRUMADIEDUREASTNORTHEASTISATNEWSEXWASZUMIGAONITMYNINEBERLINCLOCKAMCHLENGHTSNAVYBEPGHILB
mask  ...S.............E...EASTNORTHEAST....N......AS...I.A........N.BERLINCLOCK....L.N....NA..........
```
Word split (interpretation): `HOI SLK QU GRS RUM A DIE DUR EAST NORTHEAST IS AT NEW SEX WAS ZUM I GA ON IT MY NINE BERLIN CLOCK AM CH LENGHTS~ NAVY BE PG HIL B`

**E1|b7|2544997**: W -137.10 (replication W -136.64, 62 letters changed); forced beyond clues 7; REVIEW ONLY

```
raw   EGOFCMSDIGPAYSONOWLAYEASTNORTHEASTIBCNMRTACTBEAMSNOVOMSRUNSBEUPBERLINCLOCKREEDUPALGRAHILYLMYIITPP
mask  ........I..A.S.......EASTNORTHEAST...N.....T......O............BERLINCLOCK.E.....................
```
Word split (interpretation): `EG OF CMS DIG PAY SO NOW LAY EAST NORTHEAST I BCN MR TACT BEAMS NO VOM S RUNS BE UP BERLIN CLOCK REED UP AL GRA HILYL~ MY I IT PP`

**E1|b7|1522276**: W -138.69 (replication W -139.99, 51 letters changed); forced beyond clues 9; REVIEW ONLY

```
raw   NWAXORBYISWAOGGXVAIWEEASTNORTHEASTBWINGRAPTCLOUDALOEAVEYRLASQHEBERLINCLOCKHENDFNPOTNYOUEYEDIDUMFF
mask  ..A.....I..A.........EASTNORTHEAST...N....T.......O.A..........BERLINCLOCK.E.........O...........
```
Word split (interpretation): `N WAX OR BY IS WA OGG XV A I WE EAST NORTHEAST BWING RAPT CLOUD ALOE A VEYR~ LAS Q HE BERLIN CLOCK HEND FN POTN~ YOU EYE DID UM FF`

**E1|b7|8564775**: W -140.32 (replication W -154.77, 57 letters changed); forced beyond clues 10; REVIEW ONLY

```
raw   OFFPGWAXDARKUSEFEEAHWEASTNORTHEASTEBINGUPHITRPUTYSPYPARTISOWIOFBERLINCLOCKGCFAFTBYDUXXVIMEHIMSAYS
mask  ...........K.S...E...EASTNORTHEAST...N.....T...T.....A.......O.BERLINCLOCK...A..................S
```
Word split (interpretation): `OFF PG WAX DARK USE FEE AH WE AS T NORTHEAST EBING~ UP HIT R PUT Y SPY PART IS OWI OF BERLIN CLOCK G CF AFT BY DU XXVI ME HIM SAYS`

**E1|b7|8327963**: W -140.70 (replication W -147.04, 50 letters changed); forced beyond clues 7; REVIEW ONLY

```
raw   PEAKFORHOWIMPCONABBEAEASTNORTHEASTXXTPGTOOSHYSEESEXDIOAMIVANDEDBERLINCLOCKSPUSJARDWWWQFFPALNDAYHA
mask  ..A.....O............EASTNORTHEAST.....T.OS..................E.BERLINCLOCK...................A...
```
Word split (interpretation): `PEAK FOR HOW IM PC ON ABBE A EAST NORTHEAST XX TPG TOO SHY SEE SEX DIO AM I VAN DE D BERLIN CLOCKS PUS JARD~ WWW Q FF PALN~ DAY HA`

## E2 one-cycle K3-style routes + Gromark (English)

- **Searched:** 6607 settings at 16 restarts.
- **Best W** -142.19, median -176.91, bar -114.90; above the bar: 0.
- **Candidates:** 0.

**R27|R24x7/CCW/inv|T_then_S|13987**: W -142.19 (replication W -141.06, 49 letters changed); forced beyond clues 14; REVIEW ONLY

```
raw   EHROTIYSIRRUMGODYETISEASTNORTHEASTARMYWRYQFLYZUSITBYINHMEITKOILBERLINCLOCKPARTPGLEGVSREIORHADINSQ
mask  E...TI...........ET..EASTNORTHEASTA..............T......E.....LBERLINCLOCK...T...E....E...H....S.
```
Word split (interpretation): `EH ROTI Y SIR RUM GOD YET IS EAST NORTHEAST ARMY WRY Q FLY ZU SIT BY IN H ME IT KOIL~ BERLIN CLOCK PART PG LEG VS REI OR HAD IN SQ`

**R27|R24x7/CCW/inv|S_then_T|03833**: W -143.30 (replication W -140.07, 51 letters changed); forced beyond clues 9; REVIEW ONLY

```
raw   AMIDTYWHTMLAEXPAANOTEEASTNORTHEASTGLOWAYDENBDOHERFISLBEDNEEAIISBERLINCLOCKDOTURCEEDDYIONFATONALBY
mask  ....T............N...EASTNORTHEAST.................S....N......BERLINCLOCK....RCEE...I...........
```
Word split (interpretation): `AMID TY W HTML A EXP A A NOTE EAST NORTHEAST GLO WAY DEN BDO HER FISL~ BED NEE A I IS BERLIN CLOCK DO TURCE~ EDDY I ON FAT ON AL BY`

**R27|R23x8/CCW/fwd|T_then_S|49239**: W -143.52 (replication W -142.11, 50 letters changed); forced beyond clues 15; REVIEW ONLY

```
raw   FLYWILDWETYPEACTUSEHOEASTNORTHEASTVIAITOREPEWCODYITDONBOXSJOWNDBERLINCLOCKSUSETIPCIISRESGJHLULIXX
mask  ....I....T.....T..EH.EASTNORTHEAST.I.....E.E.........N.........BERLINCLOCKS......C.I.RES.........
```
Word split (interpretation): `FLY WILD WE TYPE ACT USE HOE AS T NORTHEAST VIA I TORE PEW CODY IT DON BOX SJOWN~ D BERLIN CLOCKS USE TIP CI IS RE SG JH LUL I XX`

**R27|R24x9/CW/inv|S_then_T|21086**: W -144.02 (replication W -152.03, 53 letters changed); forced beyond clues 7; REVIEW ONLY

```
raw   GUMNDSGELMHEWDORIESNAEASTNORTHEASTCOXAGRUPRIDLUISQVASTIEREIHTERBERLINCLOCKWEPTAYMADAYOOPOHISFATMA
mask  ...............R.E...EASTNORTHEASTCO......R..............E.....BERLINCLOCK.E.....................
```
Word split (interpretation): `GUM NDS GEL M HE W DO RIESN~ A EAST NORTHEAST COXA GRUP RID LUIS Q VAST I ER EIHTER~ BERLIN CLOCK WEPT AY MA DAY O OP OH IS FATMA`

**R27|R24x7/CW/inv|T_then_S|85762**: W -146.24 (replication W -167.14, 51 letters changed); forced beyond clues 9; REVIEW ONLY

```
raw   LEFEBGOAPSTAALLPPAHPLEASTNORTHEASTEMFFMYDARKKIDAHSIORABLFFEXSUNBERLINCLOCKOLWERBYSOOINPMMETVIZTUT
mask  L..E.....S...L.......EASTNORTHEAST..................R..........BERLINCLOCK...E...........ET.....T
```
Word split (interpretation): `LE FEB GO APST~ A ALL PP A HP LEAST NORTHEAST EM FF MY DARK KID AHS I OR ABL FF EX SUN BERLIN CLOCK OLWER~ BY SOO IN PM MET VIZ TUT`

## E5 one mis-carved clue letter + Gromark (English)

- **Searched:** 3178 settings at 16 restarts.
- **Best W** -140.94, median -173.90, bar -114.90; above the bar: 0.
- **Candidates:** 0.

**E5|pos22|26767**: W -140.94 (replication W -170.35, 63 letters changed); forced beyond clues 7; REVIEW ONLY

```
raw   FEVREQUDATAVEJOYANDFRMASTNORTHEASTORNEWSTEXTSBYPEWSJAKOLAWXVTWOBERLINCLOCKOFBYLGZVSUPGAGTOYATHSAC
mask  .................N....ASTNORTHEAST.....S...T........AK.........BERLINCLOCK....L.......A..........
```
Word split (interpretation): `FEVRE~ QU DAT AVE JOY AND FR MAST NORTHEAST OR NEWS TEXTS BY PEW SJAKO~ LAW XV TWO BERLIN CLOCK OF BY LG Z VS UP GAG TOY AT H SAC`

**E5|pos34|22930**: W -143.72 (replication W -152.44, 51 letters changed); forced beyond clues 14; REVIEW ONLY

```
raw   HEASIXXHIOFUNSPASQFOGEASTNORTHEASADPGVOWDOUBTMRTIMEAOFUPBAPMBMEBERLINCLOCKINPMTPISOHOFKEYKBOWBOTH
mask  ..AS....I....S.A.....EASTNORTHEAS.....O..O.....T..E.........B..BERLINCLOCK.N..T.I.....K..........
```
Word split (interpretation): `HE A SIXX HI OF UNS PAS Q FOG EAST NOR THE AS A DPG VOW DOUBT MR TIME A OF UP BAP MB ME BERLIN CLOCK IN PM TPIS~ OH OF KEY K BOW BOTH`

**E5|pos33|86419**: W -143.98 (replication W -149.55, 61 letters changed); forced beyond clues 10; REVIEW ONLY

```
raw   OANTLIIAHMYRITZDUECABEASTNORTHEALTAIKNGSLAMMEDAMOEVENDTOMXXVWEOBERLINCLOCKBPOXVIFLAXTHATRENTPPAET
mask  ...T.........T...E...EASTNORTHEALT.I.N.S.....................E.BERLINCLOCK............A.........T
```
Word split (interpretation): `O AN TL II AH MY RITZ DUE CAB EAST NOR THE AL TAIKNG~ SLAMMED A MOEV~ END TOM XXV WE OBERLIN CLOCK BPO XVI FLAX THAT RENT PP AET`

**E5|pos34|70623**: W -144.18 (replication W -155.00, 46 letters changed); forced beyond clues 7; REVIEW ONLY

```
raw   SONTOSJYBYOFBRINEWNODEASTNORTHEASRIMANAGEWHSADVYPDIEABEILCKHOWOBERLINCLOCKTALKYMUGPUSENWOOTHMDUTY
mask  ...T.................EASTNORTHEAS....N.....S......I.A..........BERLINCLOCK...K.......E...........
```
Word split (interpretation): `SON TO SJY~ BY OF BRI NEW NOD EAST NOR THE A SRI MANAGE WH SAD VY P DIE A BE ILCK~ HOW OBERLIN CLOCK TALK Y MUG PUS EN WOOT HM DUTY`

**E5|pos34|08035**: W -144.39 (replication W -155.59, 53 letters changed); forced beyond clues 9; REVIEW ONLY

```
raw   JETKEGVEXAPUNYCORDSDUEASTNORTHEASSWHYNOLYATKRIGELOTLKIEAFERRYEXBERLINCLOCKYEAOGGAYZATNTONMMORSEON
mask  .....................EASTNORTHEASS...NOL..T.........K........E.BERLINCLOCK.E.........N...........
```
Word split (interpretation): `JE T KEG VEX A PUNY CORDS DU EAST NOR THE ASS WHY NOLY~ AT KR IGE LOT LKIE~ A FERRY EX BERLIN CLOCK YEA OG GAY ZAT N TO NM MORSE ON`

## E3a 5-digit Gromark, 39 primers (punctuation model; exploratory, gate failed)

- **Searched:** 39 settings at 64 restarts.
- **Best W** -131.99, median -148.04, bar -114.90; above the bar: 0.
- **Candidates:** 0.

**G5|30640**: W -131.99 (below the bar, so not replicated); forced beyond clues 9; REVIEW ONLY

```
raw   AKUNDAHTIEEDAMUCHECLLEASTNORTHEASTYOUROAUOFXDUPAYFFTMBORNPAGISTBERLINCLOCKDIRTAWEUSIFQNOIVFORATAS
mask  ........I........E...EASTNORTHEAST.O..O..O.....................BERLINCLOCK.I....E............A..S
```
Word split (interpretation): `AK UND AH TIE E DA MUCH ECLL~ EAST NORTHEAST YOUR OA U OF X DU PAY FF TM BORN PAG IST BERLIN CLOCK DIRT A WE US IF Q NO IV FOR AT AS`

**G5|88254**: W -136.59 (below the bar, so not replicated); forced beyond clues 8; REVIEW ONLY

```
raw   XAACMEQKUIBCKNEWAVEZLEASTNORTHEASTHINTBYXIWCKWHOMQTOACTSXQIKNOKBERLINCLOCKOENUPEGGFREESOILLIXASOD
mask  ..A..................EASTNORTHEAST.I.....I..........A........O.BERLINCLOCK.E.........E.......A...
```
Word split (interpretation): `X A ACME~ Q KU IBC KNEW AVEZ LEAST NORTHEAST HINT BY X IWCK~ WHOM Q TO ACTS X Q IK NOK BERLIN CLOCK O EN UP EGG FREE SO ILL IX A SO D`

**G5|20173**: W -136.61 (below the bar, so not replicated); forced beyond clues 4; REVIEW ONLY

```
raw   WARPTWOASSTMBPARTQMALEASTNORTHEASTUPREPBUQFEDXXDUGQNAGBXVGILTITBERLINCLOCKIPADDIEXPASSRESPAKCXJAY
mask  .....................EASTNORTHEAST...E..............A........I.BERLINCLOCK......E................
```
Word split (interpretation): `WARP TWO AS ST MB PART QM A LEAST NORTHEAST UP REP BU Q FED XX DU GQ NA GB XV GILT IT BERLIN CLOCK IPAD DIE X PASSRES~ PAKC~ X JAY`

**G5|36650**: W -139.00 (below the bar, so not replicated); forced beyond clues 10; REVIEW ONLY

```
raw   CAPTYPATESBIATRAWAFFAEASTNORTHEASTSIIAQTOOFLGABYORXXNOTODINMEAIBERLINCLOCKXXOZHIPOHBEDCHURCHXKEAM
mask  ...T....E....T.A.....EASTNORTHEAST.I...T.O.L.A.................BERLINCLOCK...................K...
```
Word split (interpretation): `CAP TYP AT ES BI AT RAW A FF A EAST NORTHEAST SII AQ TO OF LG A BY OR XX NOT ODIN ME A I BERLIN CLOCK XX OZ HIP OH BED CHURCH X KE AM`

**G5|62389**: W -141.58 (below the bar, so not replicated); forced beyond clues 6; REVIEW ONLY

```
raw   KHOWIFXXUPHAISOXAXKUAEASTNORTHEASTQMONKSABDISRDJAWSLOAMTOYRONHEBERLINCLOCKXSIRVOMYOGOSONLEGISKATM
mask  ...........A.S.......EASTNORTHEAST...N.S.............A.........BERLINCLOCK...................K...
```
Word split (interpretation): `K HOW IF XX UP HAI SOX AX KU A EAST NORTHEAST Q MONKS ABDIS RD JAWS LOAM TOYR~ ON HE BERLIN CLOCK X SIR VOM YO GO SON LEG IS KAT M`

## E3b two-cycle K3-style routes + Gromark (punctuation model; exploratory)

- **Searched:** 39 settings at 64 restarts.
- **Best W** -138.50, median -154.67, bar -114.90; above the bar: 0.
- **Candidates:** 0.

**R27|R25x8/CW/inv|S_then_T|53961**: W -138.50 (below the bar, so not replicated); forced beyond clues 14; REVIEW ONLY

```
raw   ILLITVEQUMAPORSJAMOFHEASTNORTHEASTLRIWHOANUTSXXNOORBADGOPGVOLHEBERLINCLOCKBARCALUSIQIFTHAPUTXSURG
mask  ....T.E..............EASTNORTHEASTLR....A..T...N.......O....L..BERLINCLOCK..RCA..S.........T.....
```
Word split (interpretation): `ILL IT VE QU MAP OR SJAM~ OF HE AS T NORTHEAST LR I WHO A NUTS XX NO OR BAD GO PG VOL HE BERLIN CLOCK BARCA LUS IQ IF TH A PUT X SURG`

**R27|R24x9/CW/fwd|S_then_T|12048**: W -138.70 (below the bar, so not replicated); forced beyond clues 12; REVIEW ONLY

```
raw   SATRDNMEGARBIXHMTOAREEASTNORTHEASTPERRYPALSYAPRTUSTOHVASLIIOFSGBERLINCLOCKUFFAQXODDQAUIMAYTZIUSTM
mask  ..TR.N.E........TO..EEASTNORTHEAST................T............BERLINCLOCK......O.....I...T....T.
```
Word split (interpretation): `SAT RDN ME GAR BIX HM TO ARE EAST NORTHEAST PERRY PALSY APRT~ US TO H VASLII~ OF SG BERLIN CLOCK UFFA Q X ODD QA U I MAY TZ I US TM`

**R27|R25x8/CW/inv|T_then_S|65810**: W -144.13 (below the bar, so not replicated); forced beyond clues 12; REVIEW ONLY

```
raw   USFOHILAWISWIGDADQASKEASTNORTHEASTASPTYINPUTPOPXIFFBAKXXMYIOREIBERLINCLOCKOFGIANIVTMIUPCMBTWOTYNE
mask  .S.OH..........A....KEASTNORTHEAST.S.T..N..T..................IBERLINCLOCK....A...........T......
```
Word split (interpretation): `US FOH I LAW IS WIG DA DQ ASK EAST NORTHEAST AS P TY IN PUT POP XI FF BAK XX MY I OR EI BERLIN CLOCK OF GIAN I VTM I UP CM B TWO TYNE`

**R27|R24x9/CW/fwd|T_then_S|76560**: W -145.61 (below the bar, so not replicated); forced beyond clues 10; REVIEW ONLY

```
raw   OSXMYQXBYQDATEKLUEONSEASTNORTHEASTAKDISZSOJOYHAVEAUPGUTPPDRCOEXBERLINCLOCKAAAHFFORCHROUSACJAXXHIS
mask  ...............L.E..SEASTNORTHEAST.K..........A.E..........C...BERLINCLOCK.A....O.C..............
```
Word split (interpretation): `OSX MY Q X BY Q DATE KLUE~ ONS EAST NORTHEAST A KD IS Z SO JOY HAVE A UP GUT PP DR CO EX BERLIN CLOCK AAAH F FOR CHROUS~ AC JA XX HIS`

**R27|R24x9/CW/fwd|S_then_T|76400**: W -145.62 (below the bar, so not replicated); forced beyond clues 9; REVIEW ONLY

```
raw   AHKUUSTOXCHPMOFQXUPMYEASTNORTHEASTEDWAYONXCFHOAIANQASSHYNODETRDBERLINCLOCKAXZHEGINPUBDEUCLTAFIRTM
mask  .....STO.............EASTNORTHEAST...A........A......S.........BERLINCLOCK..........B.....T....T.
```
Word split (interpretation): `A HKU US TO X CHP M OF Q X UP MY EAST NORTHEAST ED WAY ON X CF HOAI AN Q AS SHY NO DE T RD BERLIN CLOCK AX ZHEG IN PUB DE UCLT~ AFIR~ TM`

## Reference: 5-digit Gromark, 39 primers (English, re-run)

- **Searched:** 39 settings at 64 restarts.
- **Best W** -140.88, median -158.27, bar -114.90; above the bar: 0.
- **Candidates:** 0.

**G5|30640**: W -140.88 (below the bar, so not replicated); forced beyond clues 9; REVIEW ONLY

```
raw   AKUNDAHTIEEDAMUCHECLLEASTNORTHEASTYOUROAUOFPDUWAYFFTMBORNWAXISTBERLINCLOCKDIRTAGEUSIFZNOIVFORATAS
mask  ........I........E...EASTNORTHEAST.O..O..O.....................BERLINCLOCK.I....E............A..S
```
Word split (interpretation): `AK UND AH TIE E DA MUCH ECLL~ EAST NORTHEAST YOUR OA U OF P DU WAY FF TM BORN WAX IST BERLIN CLOCK DIR TAGE US IF Z NO IV FOR AT AS`

**G5|62389**: W -144.14 (below the bar, so not replicated); forced beyond clues 6; REVIEW ONLY

```
raw   XXOPIIABYWHATSQVAVIFAEASTNORTHEASTHMONKSABDISRDGAPSLOAMHOURONHMBERLINCLOCKVSORZUMUNEOSONLEFISKETM
mask  ...........A.S.......EASTNORTHEAST...N.S.............A.........BERLINCLOCK...................K...
```
Word split (interpretation): `XX OP II A BY WHAT SQ VAV IF A EAST NORTHEAST H MONKS ABDIS RD GAPS LOAM HOUR ON HM BERLIN CLOCK VS OR ZUM U NEOS ON LE FISKE TM`

**G5|88254**: W -147.76 (below the bar, so not replicated); forced beyond clues 8; REVIEW ONLY

```
raw   LMABFTINJOBBENTDOQUAYEASTNORTHEASTSIWTCHDIDBUDZONSTQABPERSTIXOEBERLINCLOCKLEDJGRVENULESSODEJEAWAY
mask  ..A..................EASTNORTHEAST.I.....I..........A........O.BERLINCLOCK.E.........E.......A...
```
Word split (interpretation): `LMAB~ FT IN JOB BENT DO QUAY EAST NORTHEAST SIWTCH~ DID BUD ZON ST Q ABP ERST IX OE BERLIN CLOCK LED J GR VENULES SO DE JE AWAY`

**G5|22856**: W -148.54 (below the bar, so not replicated); forced beyond clues 9; REVIEW ONLY

```
raw   GLADVAHUMBUOTNANAUPIDEASTNORTHEASTIISTYBUILDXXVOHOTGAOFFVOBYJOTBERLINCLOCKPEMEGRAIHDREWABOYYEASPP
mask  ..A..................EASTNORTHEAST.I.....IL.........A........O.BERLINCLOCK.E.........E.......A...
```
Word split (interpretation): `GLAD VA HUM BUOT~ NANA~ UP IDEAS T NORTHEAST I IST Y BUILD XXV O HOT GA OFF VO BY JOT BERLIN CLOCK PE ME GRA IH DREW A BOY YEAS PP`

**G5|70460**: W -148.84 (below the bar, so not replicated); forced beyond clues 7; REVIEW ONLY

```
raw   SPYHUSJFATSKEVOLVEDWEEASTNORTHEASTTOYMOMIOICRYCMXIVDRFORUPATOPABERLINCLOCKWARGMESICASWEOKHIOXALDS
mask  ...........K.....E...EASTNORTHEAST.O..O..O.....................BERLINCLOCK...................A..S
```
Word split (interpretation): `SPY HUSJ~ FAT SK EVOLVED WE EAST NORTHEAST TOY MO MIO I CRY CM XIV DR FOR UP AT OP A BERLIN CLOCK WAR G ME SIC AS WE OK HI OX ALDS~`

## Reference: two-cycle routes (English, re-run)

- **Searched:** 39 settings at 64 restarts.
- **Best W** -148.34, median -165.53, bar -114.90; above the bar: 0.
- **Candidates:** 0.

**R27|R25x8/CW/inv|S_then_T|53961**: W -148.34 (below the bar, so not replicated); forced beyond clues 14; REVIEW ONLY

```
raw   XVHITJEWHUTDODAMLBOFBEASTNORTHEASTLRIPBOANUTSKYNOXRNAGGODOJELHEBERLINCLOCKIARCAMUSIWILTHADUTASURF
mask  ....T.E..............EASTNORTHEASTLR....A..T...N.......O....L..BERLINCLOCK..RCA..S.........T.....
```
Word split (interpretation): `XV HITJE W HUT DO DA MLB OF BEAST NORTHEAST L RIP BOA NUT SKY NOX RNAG~ GODO~ JE L HE BERLIN CLOCK I ARC AM US I WILT HAD UTA SURF`

**R27|R24x9/CW/fwd|S_then_T|12048**: W -149.26 (below the bar, so not replicated); forced beyond clues 12; REVIEW ONLY

```
raw   IITRUNAEHTHYLLDATOAREEASTNORTHEASTDUGKUJAFORINKLYATMGIGYEORMBIFBERLINCLOCKOVOTRPOAAJZZIFTUTIVYITY
mask  ..TR.N.E........TO..EEASTNORTHEAST................T............BERLINCLOCK......O.....I...T....T.
```
Word split (interpretation): `I IT RUN AEH THY LL DA TO ARE EAST NORTHEAST DUG KU JA FOR INKL YA TM GIG YE OR MB IF BERLIN CLOCK OVO TRPO~ A AJZZ~ IF TUT IVY IT Y`

**R27|R24x9/CW/fwd|S_then_T|34068**: W -151.70 (below the bar, so not replicated); forced beyond clues 13; REVIEW ONLY

```
raw   DSERAGRATFNIPPMYMENLYEASTNORTHEASTREWARIFINAFORABHEIUGHQUYERDIGBERLINCLOCKOMBYTHEPCETHAAITBLTEABU
mask  ..ER......N......E...EASTNORTHEAST...A............E............BERLINCLOCK..B..HE.CE........TE...
```
Word split (interpretation): `D SERA GRATF~ NI PP MY MEN LY EAST NORTHEAST RE WAR IF IN A FOR AB HE I UGH QU YER DIG BERLIN CLOCK OM BY THE PC ETH A A IT BL TE ABU`

**R27|R24x9/CW/fwd|T_then_S|63085**: W -154.91 (below the bar, so not replicated); forced beyond clues 13; REVIEW ONLY

```
raw   OPWHOOKKOFRWITHLMEIJMEASTNORTHEASTORGWODSOPITIAKITSAYSUTBINCSEEBERLINCLOCKIANDZNOBUYAHXXIVFNKEYTM
mask  .....O.........L.E...EASTNORTHEAST...........IA...S..S.....C..EBERLINCLOCK.A....O............E.T.
```
Word split (interpretation): `OP WHO OKK OF R WITH L ME IJM~ EAST NORTHEAST ORG WO D SO PITI A KIT SAYS UT BIN C SEE BERLIN CLOCK I AND Z NO BUY AH XXIV FN KEY TM`

**R27|R24x9/CW/fwd|S_then_T|66831**: W -154.97 (below the bar, so not replicated); forced beyond clues 13; REVIEW ONLY

```
raw   HEIVALYLIXOEILYOEELLOEASTNORTHEASTGOTTWOOFTOERDHIMGODNEISKMCHAPBERLINCLOCKUPWOXVLBUGIWAREXDAYSATM
mask  .....L.L..O....OEE..OEASTNORTHEAST...................N.....CH..BERLINCLOCK......L............S.T.
```
Word split (interpretation): `HE IV ALYL~ IX OEI LY OE ELLO EAST NORTHEAST GOT TWO OF TO ER D HIM GOD NE IS KM CHAP BERLIN CLOCK UP WO XV L BUG I WAR EX DAYS AT M`

