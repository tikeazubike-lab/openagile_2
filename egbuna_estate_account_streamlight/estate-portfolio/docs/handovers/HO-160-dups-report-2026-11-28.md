# HO-160 — read-only report: duplicate company rows and their references (2026-11-28)

Product Owner source for the correct tickers/registrars: chat of 2026-11-28 (Okomu, Trans-Nationwide, Wema, Learn Africa, Livestock Feeds, Transcorp Power, Meyer, Access Bank delisted -> NASD SDACCESS; Seplat Nigeria = DataMax, Computershare = LSE only).

```
EVIDENCE transaction_read_only = on | db = estate_portfolio

== company rows and what refers to them ==
  id 315 ACCESS "Access Holdings Plc" registrar=None  | price_history=4, price_audits=4, company_registrars=1
  id 51 ACCESSCORP "Access Bank PLC" registrar=20 United-Securities-Limited | holdings=1, transactions=1, price_history=2, price_audits=1, company_registrars=1
  id 12 DNMEYER "DN Meyer PLC" registrar=15 GTL-Registrars-Limited | holdings=1, transactions=1, company_registrars=1
  id 349 LEARNAFR "Learn Africa Plc" registrar=None  | price_history=4, price_audits=4
  id 128 LEARNAFRCA "LEARNAFRCA" registrar=None  | price_audits=1
  id 131 LIVESTOCK "LIVESTOCK" registrar=None  | price_history=33, price_audits=50
  id 319 LIVESTOK "Livestock Feeds Plc" registrar=None  | price_history=3, price_audits=3, company_registrars=1
  id 141 MEYER "MEYER" registrar=None  | price_history=36, price_audits=53, company_registrars=1
  id 318 OKOMOILP "Okomu Oil Palm Plc" registrar=None  | price_history=1, price_audits=1, company_registrars=1
  id 1 OKOMUOIL "Okomu Oil Palm Company PLC" registrar=11 First-Registrars-and-Investor-Services | holdings=1, transactions=1, price_history=2, price_audits=8, company_registrars=1
  id 165 SEPLAT "SEPLAT" registrar=None  | price_history=36, price_audits=53, company_registrars=2
  id 352 TRANSCORPPOWER "Transcorp Power Plc" registrar=None  | price_history=1, price_audits=1
  id 348 TRANSEX "Trans-Nationwide Express Plc" registrar=None  | price_history=4, price_audits=4
  id 11 TRANSEXPR "Transnationwide Express PLC" registrar=11 First-Registrars-and-Investor-Services | holdings=1, transactions=1, price_history=34, price_audits=49, company_registrars=1
  id 181 TRANSPOWER "TRANSPOWER" registrar=None  | company_registrars=1
  id 330 WEMA "Wema Bank Plc" registrar=None  | price_history=1, price_audits=1, company_registrars=1
  id 199 WEMABANK "WEMABANK" registrar=None  | price_history=35, price_audits=53
  not in companies: TRANEX, SDACCESS

== registrars not in the §3 resolution table ==
  #4 Other-Commercial-Registrars: 7 active companies
  #5 Uncertain-Requires-Confirmation: 3 active companies
  #10 Acquirer-Buyout-Scheme-Administrators: 2 active companies
  #14 Sterling-Registrars-Limited: 1 active companies
  #15 GTL-Registrars-Limited: 2 active companies
  #16 Oando-PLC-Registrar: 1 active companies
  #18 AMCON-NDIC-Administrator: 8 active companies
  #19 Registrar-General-Historical-Records: 11 active companies
  #20 United-Securities-Limited: 4 active companies
  #22 xyz test registrar: 0 active companies
  #23 Test Registrars: 0 active companies
  #60 United Securities Limited: 0 active companies
  #62 Computershare UK: 0 active companies

== companies on registrar #15 ==
  DNMEYER "DN Meyer PLC"
  NESTLE "Nestle Nigeria PLC"
```
