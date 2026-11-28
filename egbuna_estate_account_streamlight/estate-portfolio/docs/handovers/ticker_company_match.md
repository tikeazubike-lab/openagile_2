# Ticker ↔ company match: research handover

| Field | Value |
|---|---|
| Date | 2026-11-28 |
| From | Claude Code (EPM v2 orchestrator), HO-160 / F-026c registrar research import |
| For | Product Owner (independent research) |
| Status | Open: answers feed spec F-026c §12 before the production write |

## 1. Background
EPM v2 (Estate Portfolio Manager) keeps a list of Nigerian listed companies, each with a ticker, a company name and a share registrar. A
researched file (`docs/registrars/registrars_contact_details_final.md`) is being imported. It links each company, **by ticker**, to its
registrar, and adds the registrars' contact details.

A read-only check of production on 2026-11-28 found three kinds of problem:
- many companies stored under the ticker instead of their real name;
- some names that differ from the research file;
- a few companies recorded twice under two tickers.

The import matches on the ticker only, so the ticker must be right before any name or registrar is written.

## 2. What to research
For each company below, confirm against NGX (ngxgroup.com), SEC Nigeria or the company's own investor-relations page:
1. **The current NGX ticker.** Is the ticker shown here the one the company trades under today?
2. **The current legal name**, for example after a rebrand or holding-company restructure.
3. **The share registrar in Nigeria**, which only needs checking where you have doubts. The research file's registrar is shown.
4. **Status**: listed and trading, suspended, delisted, or moved to NASD OTC.

## 3. Already settled by the Product Owner (2026-11-28): no research needed
| Topic | Decision |
|---|---|
| Seplat Energy Plc (SEPLAT) | Nigerian registrar = DataMax Registrars Limited. Computershare handles only the London listing. In EPM: DataMax only |
| "Co-registrar" | Not a concept on NGX or at SEC. Each company has one registrar |
| Okomu Oil Palm | Correct row = OKOMUOIL "Okomu Oil Palm Company PLC". OKOMOILP is a duplicate |
| Trans-Nationwide Express | Registrar CardinalStone. PO wrote ticker **TRANEX**; EPM and the research file use **TRANSEXPR**. **Please confirm which is right** |
| Wema Bank Plc | WEMABANK, Greenwich Registrars & Data Solutions. WEMA is a duplicate |
| Learn Africa Plc | LEARNAFRCA, First Registrars & Investor Services. LEARNAFR is a duplicate |
| Livestock Feeds Plc | LIVESTOCK, CardinalStone (Registrars). LIVESTOK is a duplicate |
| Transcorp Power Plc | TRANSPOWER, Africa Prudential. TRANSCORPPOWER is a duplicate |
| Meyer Plc (formerly DN Meyer Plc) | DNMEYER, Greenwich. MEYER is a duplicate. **Note: the research file lists it under "MEYER"** |
| Access Bank Plc | Delisted from NGX in March 2022, now NASD OTC SDACCESS. ACCESSCORP = Access Holdings Plc. The ACCESS row is obsolete |
| GTL Registrars | The former name of Greenwich Registrars & Data Solutions. Merged into Greenwich |
| Not duplicates (different companies) | TRANSCORP vs TRANSCORPPOWER, CAP vs UCAP, UCBAL/UCBOND/UCEURO, TAJSUKS1 vs TAJSUKS2 |

## 4. List A: name in EPM is just the ticker (90). Proposed name = research file name
Mark each row ✅ (ticker and name correct), or give the correct ticker/name.

| # | Ticker | Proposed name (research file) | Registrar (research file) | ✅ / correction |
|---|---|---|---|---|
| 1 | ABCTRANS | ABC Transport Plc | First Registrars | |
| 2 | ACADEMY | Academy Press Plc | Pace | |
| 3 | AFRIPRUD | Africa Prudential Plc | Africa Prudential | |
| 4 | AIICO | AIICO Insurance Plc | Coronation | |
| 5 | AIRTELAFRI | Airtel Africa Plc | Coronation | |
| 6 | ALEX | Aluminium Extrusion Industries Plc | Greenwich | |
| 7 | AUSTINLAZ | Austin Laz & Company Plc | First Registrars | |
| 8 | BETAGLAS | Beta Glass Plc | Greenwich | |
| 9 | BUACEMENT | BUA Cement Plc | Africa Prudential | |
| 10 | BUAFOODS | BUA Foods Plc | Africa Prudential | |
| 11 | CAVERTON | Caverton Offshore Support Group Plc | Coronation | |
| 12 | CHAMPION | Champion Breweries Plc | Africa Prudential | |
| 13 | CHELLARAM | Chellarams Plc | Greenwich | |
| 14 | CILEASING | C & I Leasing Plc | Cordros | |
| 15 | CNIF | Coronation Infrastructure Fund | Coronation | |
| 16 | CONHALLPLC | Consolidated Hallmark Holdings Plc | Meristem | |
| 17 | CORNERST | Cornerstone Insurance Plc | Lighthouse | |
| 18 | CUSTODIAN | Custodian Investment Plc | Meristem | |
| 19 | DAARCOMM | Daar Communications Plc | First Registrars | |
| 20 | DANGSUGAR | Dangote Sugar Refinery Plc | Veritas | |
| 21 | ELLAHLAKES | Ellah Lakes Plc | Cordros | |
| 22 | ETI | Ecobank Transnational Incorporated | Greenwich | |
| 23 | ETRANZACT | E-Tranzact International Plc | Meristem | |
| 24 | EUNISELL | Eunisell Interlinked Plc | Apel | |
| 25 | FIDSON | Fidson Healthcare Plc | Meristem | |
| 26 | FIRSTHOLDCO | First HoldCo Plc | Meristem | |
| 27 | FTGINSURE | Fortis Global Insurance Plc | PAC | |
| 28 | FTNCOCOA | FTN Cocoa Processors Plc | Meristem | |
| 29 | GEREGU | Geregu Power Plc | Meristem | |
| 30 | GTCO | Guaranty Trust Holding Company Plc | DataMax | |
| 31 | GUINEAINS | Guinea Insurance Plc | CardinalStone | |
| 32 | HMCALL | Haldane McCall Plc | Africa Prudential | |
| 33 | HONYFLOUR | Honeywell Flour Mill Plc | Atlas | |
| 34 | IMG | Industrial & Medical Gases Nigeria Plc | Lancelot | |
| 35 | INFINITY | Infinity Trust Mortgage Bank Plc | Africa Prudential | |
| 36 | INTBREW | International Breweries Plc | Apel | |
| 37 | INTENEGINS | International Energy Insurance Plc | Meristem | |
| 38 | JAIZBANK | Jaiz Bank Plc | Africa Prudential | |
| 39 | JAPAULGOLD | Japaul Gold & Ventures Plc | Pace | |
| 40 | JBERGER | Julius Berger Nigeria Plc | Greenwich | |
| 41 | JOHNHOLT | John Holt Plc | Greenwich | |
| 42 | LASACO | Lasaco Assurance Plc | Apel | |
| 43 | LEGENDINT | Legend Internet Plc | DataMax | |
| 44 | LINKASSURE | Linkage Assurance Plc | Apel | |
| 45 | LIVINGTRUST | LivingTrust Mortgage Bank Plc | Africa Prudential | |
| 46 | MANSARD | AXA Mansard Insurance Plc | DataMax | |
| 47 | MAYBAKER | May & Baker Nigeria Plc | Veritas | |
| 48 | MBENEFIT | Mutual Benefits Assurance Plc | Apel | |
| 49 | MCNICHOLS | McNichols Consolidated Plc | Coronation | |
| 50 | MECURE | Mecure Industries Plc | Cordros | |
| 51 | MORISON | Morison Industries Plc | CardinalStone | |
| 52 | MTNN | MTN Nigeria Communications Plc | Coronation | |
| 53 | MULTIVERSE | Multiverse Mining and Exploration Plc | Carnation | |
| 54 | NAHCO | Nigerian Aviation Handling Company Plc | CardinalStone | |
| 55 | NASCON | NASCON Allied Industries Plc | Meristem | |
| 56 | NGXGROUP | Nigerian Exchange Group Plc | DataMax | |
| 57 | NIDF | Chapel Hill Denham Nigeria Infrastructure Debt Fund | Coronation | |
| 58 | NNFM | Northern Nigeria Flour Mills Plc | Atlas | |
| 59 | NPFMCRFBK | NPF Microfinance Bank Plc | CardinalStone | |
| 60 | NREIT | Nigeria Real Estate Investment Trust Fund | Coronation | |
| 61 | NSLTECH | Secure Electronic Technology Plc | PAC | |
| 62 | OMATEK | Omatek Ventures Plc | Carnation | |
| 63 | PREMPAINTS | Premier Paints Plc | CardinalStone | |
| 64 | PRESTIGE | Prestige Assurance Plc | First Registrars | |
| 65 | PZ | PZ Cussons Nigeria Plc | First Registrars | |
| 66 | REDSTAREX | Red Star Express Plc | Apel | |
| 67 | REGALINS | Regency Alliance Insurance Plc | Meristem | |
| 68 | ROYALEX | Royal Exchange Plc | CardinalStone | |
| 69 | SEPLAT | Seplat Energy Plc | DataMax | |
| 70 | SFSREIT | SFS Real Estate Investment Trust | Pace | |
| 71 | SKYAVN | Skyway Aviation Handling Company Plc | Apel | |
| 72 | SOVRENINS | Sovereign Trust Insurance Plc | Meristem | |
| 73 | STANBIC | Stanbic IBTC Holdings Plc | First Registrars | |
| 74 | STERLINGNG | Sterling Financial Holdings Company Plc | Pace | |
| 75 | SUNUASSUR | Sunu Assurances Nigeria Plc | Crescent | |
| 76 | TANTALIZER | Tantalizers Plc | Meristem | |
| 77 | TIP | The Initiates Plc | Apel | |
| 78 | TOTAL | TotalEnergies Marketing Nigeria Plc | CardinalStone | |
| 79 | TRANSCOHOT | Transcorp Hotels Plc | Africa Prudential | |
| 80 | TRANSCORP | Transnational Corporation Plc | Africa Prudential | |
| 81 | TRIPPLEG | Tripple Gee and Company Plc | Greenwich | |
| 82 | UBA | United Bank for Africa Plc | Africa Prudential | |
| 83 | UCAP | United Capital Plc | Africa Prudential | |
| 84 | UNIVINSURE | Universal Insurance Plc | Carnation | |
| 85 | UPDCREIT | UPDC Real Estate Investment Trust | First Registrars | |
| 86 | UPL | University Press Plc | Greenwich | |
| 87 | VERITASKAP | Veritas Kapital Assurance Plc | Unity | |
| 88 | VFDGROUP | VFD Group Plc | Africa Prudential | |
| 89 | ZENITHBANK | Zenith Bank Plc | Veritas | |
| 90 | ZICHIS | Zichis Agro Allied Industries Plc | DataMax | |

## 5. List B: EPM has a different full name (7)
| # | Ticker | Name in EPM | Name in research file | Registrar (research file) | ✅ / correction |
|---|---|---|---|---|---|
| 1 | BERGER | Berger Paint Nigeria PLC | Berger Paints Nigeria Plc | Meristem | |
| 2 | CAP | CAP Plc | Chemical and Allied Products Plc | Africa Prudential | |
| 3 | NEIMETH | Neimeth International Pharmaceutical PLC | Neimeth International Pharmaceuticals Plc | Meristem | |
| 4 | TRANSEXPR | Transnationwide Express PLC | Trans-Nationwide Express Plc | CardinalStone | |
| 5 | UNILEVER | Lever Brothers Nigeria PLC | Unilever Nigeria Plc | Greenwich | |
| 6 | VITAFOAM | Vita Foam Nigeria PLC | Vitafoam Nigeria Plc | Meristem | |
| 7 | WAPIC | WAPIC Insurance | Coronation Insurance Plc | Coronation | |

## 6. Proposed renames already approved in principle (please confirm)
| Ticker | Name now | Proposed name |
|---|---|---|
| WEMABANK | WEMABANK | Wema Bank Plc |
| LEARNAFRCA | LEARNAFRCA | Learn Africa Plc |
| LIVESTOCK | LIVESTOCK | Livestock Feeds Plc |
| TRANSPOWER | TRANSPOWER | Transcorp Power Plc |
| DNMEYER | DN Meyer PLC | Meyer Plc |
| ACCESSCORP | Access Bank PLC | Access Holdings Plc |

## 7. Points that need special attention
- **TRANEX vs TRANSEXPR** (§3). The current ticker of Trans-Nationwide Express Plc decides which EPM row is kept.
- **WAPIC → Coronation Insurance Plc.** Has the NGX ticker changed too? If so, give the new one.
- **Low-confidence mappings held back from the import** (13). Their registrar links wait for a one-by-one decision. Confirming the registrar here would release them:

  | Ticker | Research file maps it to |
  |---|---|
  | MULTITREX | Meristem |
  | SOVRENINS | Meristem |
  | CAP | Africa Prudential |
  | SCOA | Africa Prudential |
  | DAARCOMM | First Registrars |
  | PRESTIGE | First Registrars |
  | ALEX | Greenwich |
  | WAPIC | Coronation |
  | RONCHESS | Coronation |
  | AFROMEDIA | Crescent |
  | CUTIX | Crescent |
  | NNFM | Atlas |
  | VERITASKAP | Unity |

- **Delisted or suspended companies:** please mark any company in Lists A and B that is no longer trading on NGX, as for Access Bank.

## 8. How to return the answers
Paste the filled tables back into the Claude Code session, or use one line per change:
`#<list><row> <TICKER>: ticker=<correct> name=<correct> registrar=<correct> status=<trading|suspended|delisted>`.
Example: `A52 MTNN: ✅` or `B7 WAPIC: ticker=CORONATION name=Coronation Insurance Plc`.
Rows left blank are taken as ✅, so they'll be renamed as proposed.
