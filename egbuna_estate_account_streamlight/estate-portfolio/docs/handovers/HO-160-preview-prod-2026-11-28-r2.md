# HO-160 — production preview #3 (read-only), 2026-11-28, script at 886eda2b026aae3b0c18d6797b6bae33ea0194b3

```
EVIDENCE transaction_read_only = on | db = estate_portfolio
== registrar research import: plan ==
  create registrar 'Apel Registrars And Corporate Services Limited' (slug apel)
  create registrar 'Cordros Registrars Limited' (slug cordros)
  create registrar 'Lighthouse Registrars Ltd' (slug lighthouse)
  create registrar 'PAC Registrars & Investor Services Limited' (slug pac)
  create registrar 'Lancelot Registrars And Investors Relations Limited' (slug lancelot)
  create registrar 'FSL Registrars Limited' (slug fsl)
  create registrar 'Paxhil Minerva Registrars Limited' (slug paxhil-minerva)
  registrar #8: rename 'Greenwich-Registrars-and-Data-Solutions' -> 'Greenwich Registrars & Data Solutions Limited'
  registrar #13: rename 'Veritas-Registrars-Limited' -> 'Veritas Registrars Limited'
  registrar #7: rename 'Atlas-Registrars-Limited' -> 'Atlas Registrars Limited'
  merge #9: re-point link #54 (company #55) -> #2
  company #55: registrar_id #9 -> #2
  registrar #9: soft-delete (merged into #2)
  merge #57: re-point link #324 (company #327) -> #2
  merge #57: re-point link #325 (company #328) -> #2
  registrar #57: soft-delete (merged into #2)
  merge #6: re-point link #35 (company #57) -> #50
  merge #6: re-point link #50 (company #6) -> #50
  company #57: registrar_id #6 -> #50
  company #6: registrar_id #6 -> #50
  registrar #6: soft-delete (merged into #50)
  merge #11: re-point link #18 (company #29) -> #52
  merge #11: re-point link #24 (company #37) -> #52
  merge #11: re-point link #40 (company #62) -> #52
  merge #11: re-point link #55 (company #22) -> #52
  company #29: registrar_id #11 -> #52
  company #37: registrar_id #11 -> #52
  company #62: registrar_id #11 -> #52
  company #22: registrar_id #11 -> #52
  registrar #11: soft-delete (merged into #52)
  field #8: registrar #3 -> #8
  registrar #3: soft-delete (merged into #8)
  merge #56: re-point link #316 (company #6) -> #8
  merge #56: re-point link #318 (company #326) -> #8
  registrar #56: soft-delete (merged into #8)
  registrar #8: merge values from #3 (response_rating)
  merge #12: re-point link #13 (company #23) -> #51
  company #23: registrar_id #12 -> #51
  registrar #12: soft-delete (merged into #51)
  merge #21: re-point link #21 (company #33) -> #55
  merge #21: re-point link #27 (company #44) -> #55
  merge #21: re-point link #45 (company #70) -> #55
  company #33: registrar_id #21 -> #55
  company #44: registrar_id #21 -> #55
  company #70: registrar_id #21 -> #55
  registrar #21: soft-delete (merged into #55)
  registrar #53: soft-delete (merged into #13)
  merge #17: re-point link #17 (company #28) -> #1
  merge #17: re-point link #25 (company #38) -> #1
  merge #17: re-point link #28 (company #47) -> #1
  merge #17: re-point link #59 (company #41) -> #1
  company #28: registrar_id #17 -> #1
  company #38: registrar_id #17 -> #1
  company #47: registrar_id #17 -> #1
  company #41: registrar_id #17 -> #1
  registrar #17: soft-delete (merged into #1)
  registrar #2: add address field '213 Herbert Macaulay Way, Adekunle, Yaba, Lagos' (label 'Head office', sort 10)
  registrar #2: add phone field '+23412809250' (label 'main line', sort 20)
  registrar #2: add phone field '+23412809253' (label 'main line', sort 30)
  registrar #2: add phone field '+23418920491' (label 'lines printed by client', sort 40)
  registrar #2: add phone field '+23418920492' (label 'lines printed by client', sort 50)
  registrar #2: add phone field '+234800006374734' (label 'registrar contact form on group domain, read 2026-11-27', sort 60)
  registrar #2: add email field 'info@meristemregistrars.com' (label 'Email', sort 70)
  registrar #2: add other field 'https://www.meristemregistrars.com' (label 'Website (not verified, copy manually)', sort 80)
  registrar #2: add website field 'https://contactform.meristemng.com/mrpsl' (label 'Online portal', sort 90)
  registrar #2: add email field 'registrar@meristem.com.ng' (label 'Entered manually', sort 100)
  registrar #2: add phone field '+234-1-345-6789' (label 'Entered manually', sort 110)
  registrar #2: fill NULL legacy columns address
  registrar #50: add address field '220B Ikorodu Road, Palmgrove, Lagos' (label 'Head office', sort 10)
  registrar #50: add phone field '+2342018889720' (label 'main line', sort 20)
  registrar #50: add phone field '+2348141618239' (label 'WhatsApp', sort 30)
  registrar #50: add phone field '+23470023747783' (label 'contact centre', sort 40)
  registrar #50: add email field 'cxc@africaprudential.com' (label 'customer experience', sort 50)
  registrar #50: add website field 'https://www.africaprudential.com' (label 'Website', sort 60)
  registrar #50: add website field 'https://www.africaprudential.com/self-service/Self-Service' (label 'Online portal', sort 70)
  registrar #50: add website field 'https://www.africaprudential.com/Contact-Us' (label 'Self Service, Claim Dividend, APEMS e-Ticketing, WhatsApp links', sort 80)
  registrar #50: add website field 'https://play.google.com/store/apps/details?id=com.africaprudential.invearn' (label 'InvEarn app', sort 90)
  registrar #50: add website field 'https://apps.apple.com/us/app/invearn-by-africa-prudential/id6474125659' (label 'Online portal', sort 100)
  registrar #50: add address field 'Infinity House (2nd Floor), 11 Kaura Namoda Street, off Faskari Crescent, Area 3, Garki, Abuja' (label 'Branch (please confirm)', sort 110)
  registrar #50: add address field 'UBA Plc Building, 2nd Floor, 16 Olu Obasanjo Road, GRA Phase 2, Port Harcourt' (label 'Branch (please confirm)', sort 120)
  registrar #50: fill NULL legacy columns address, email, phone, website
  registrar #52: add address field '2 Abebe Village Road, Iganmu, Lagos (P.M.B. 12692, Marina)' (label 'Head office', sort 10)
  registrar #52: add phone field '+2349154123719' (label 'customer line', sort 20)
  registrar #52: add phone field '+2349154123720' (label 'customer line', sort 30)
  registrar #52: add phone field '+2349154123721' (label 'customer line', sort 40)
  registrar #52: add phone field '+2349154123722' (label 'customer line', sort 50)
  registrar #52: add phone field '+23412799880' (label 'main line', sort 60)
  registrar #52: add phone field '+23417743309' (label 'may be older landlines)', sort 70)
  registrar #52: add phone field '+23412701078' (label 'may be older landlines)', sort 80)
  registrar #52: add phone field '+23412701079' (label 'may be older landlines)', sort 90)
  registrar #52: add email field 'info@firstregistrarsnigeria.com' (label 'general', sort 100)
  registrar #52: add website field 'https://firstregistrarsnigeria.com' (label 'Website', sort 110)
  registrar #52: add website field 'https://firstregistrarsnigeria.com/e-products/e-dividend' (label 'Online portal', sort 120)
  registrar #52: add address field 'First Bank of Nigeria Limited Building, Plot 451 Jos Street, opp. Sharon Ultimate Hotel, Area 3, Garki, Abuja' (label 'Liaison office (please confirm)', sort 130)
  registrar #52: add address field 'C/O FirstBank of Nigeria Limited, 2nd Floor, FBN Building, No 48 Alhaji Abdulazeez Arisekola Alao Way, opposite Challenge Car Park, Challenge, Ibadan, Oyo State' (label 'Liaison office (please confirm)', sort 140)
  registrar #52: add address field 'First Bank of Nigeria Limited Building (Main Branch), 2nd Floor, 22/24 Aba Road, Port Harcourt, Rivers State' (label 'Liaison office (please confirm)', sort 150)
  registrar #52: fill NULL legacy columns address, email, phone, website
  registrar #8: add address field '274 Murtala Muhammed Way, Alagomeji, Yaba, Lagos (P.M.B. 12717, Apapa)' (label 'Head office', sort 11)
  registrar #8: add phone field '+2342017006700' (label 'head office', sort 21)
  registrar #8: add phone field '+2342012275427' (label 'head office', sort 31)
  registrar #8: add phone field '+23470022554737' (label 'contact centre', sort 41)
  registrar #8: add phone field '+23412793160' (label 'main line (SEC register)', sort 51)
  registrar #8: add email field 'info@greenwichregistrars.com' (label 'general', sort 61)
  registrar #8: add website field 'https://greenwichregistrars.com' (label 'Website', sort 71)
  registrar #8: add other field 'https://ss.gtlregistrars.com' (label 'Online portal', sort 81)
  registrar #8: add website field 'https://play.google.com/store/apps/details?id=com.grdsease.grdsease' (label 'G-Ease app', sort 91)
  registrar #8: add other field 'http://ss.gtlregistrars.com/GTLROnline/Account/Login.aspx' (label "site's 'Shareholder portal' link; old domain, see website status", sort 101)
  registrar #8: add address field 'No 26 Aba Road, Port Harcourt, Rivers State' (label 'Branch (please confirm)', sort 111)
  registrar #8: add address field '1st Floor, 37 Niger / Murtala Mohammed Way, P.M.B 3007, Kano, Kano State' (label 'Branch (please confirm)', sort 121)
  registrar #8: add address field 'Bank of Industry Tower 11, 1st Floor, Plot 256, Zone A O, off Herbert Macaulay Way, Central Business District, Abuja' (label 'Branch (please confirm)', sort 131)
  registrar #8: fill NULL legacy columns address, email, phone, website
  registrar #51: add address field '9 Amodu Ojikutu Street, off Saka Tinubu, Victoria Island, Lagos' (label 'Head office', sort 10)
  registrar #51: add phone field '+2342012272570' (label 'contact centre', sort 20)
  registrar #51: add phone field '+2348052097331' (label 'main line on SEC register', sort 30)
  registrar #51: add email field 'customercare@coronationregistrars.com' (label 'customer care', sort 40)
  registrar #51: add website field 'https://coronationregistrars.com' (label 'Website', sort 50)
  registrar #51: add website field 'https://crlselfservice.coronation.ng' (label 'Online portal', sort 60)
  registrar #51: add website field 'https://shareholderlive.coronationregistrars.com/' (label 'ShareholderLive', sort 70)
  registrar #51: add website field 'https://shareholderlive.coronationregistrars.com/udivsearch/' (label 'unclaimed dividend search', sort 80)
  registrar #51: fill NULL legacy columns address, email, phone, website
  registrar #55: add address field '335/337 Herbert Macaulay Way, Yaba, Lagos' (label 'Head office (please confirm)', sort 10)
  registrar #55: add phone field '+2342017120090' (label 'Lagos office', sort 20)
  registrar #55: add phone field '+2342016308091' (label 'Lagos office', sort 30)
  registrar #55: add phone field '+2348073580521' (label 'forfeited/unclaimed dividend enquiries (FAQ)', sort 40)
  registrar #55: add email field 'registrars@cardinalstone.com' (label 'general; obfuscated on website, plain on SEC register', sort 50)
  registrar #55: add website field 'https://cardinalstoneregistrars.com' (label 'Website', sort 60)
  registrar #55: add website field 'https://shareholders.cardinalstone.com' (label 'Online portal', sort 70)
  registrar #55: add website field 'https://e-dividend.cardinalstone.com' (label 'Online portal', sort 80)
  registrar #55: add other field 'https://vrss.cardinalstone.com/emandate.html' (label 'e-dividend mandate', sort 90)
  registrar #55: add address field 'Plot 252 Herbert Macaulay Way, Central Business District, Abuja (FCMB Building per e-dividend form)' (label 'Branch (please confirm)', sort 100)
  registrar #55: add address field '85 Aba Road, by Garrison Junction, Port Harcourt, Rivers (FCMB Building per e-dividend form)' (label 'Branch (please confirm)', sort 110)
  registrar #55: fill NULL legacy columns address, email, phone, website
  registrar new[apel]: add address field '8 Alhaji Bashorun Street, off Norman Williams Crescent, South-West Ikoyi, Lagos' (label 'Head office (please confirm)', sort 10)
  registrar new[apel]: add phone field '+2347046277071' (label 'main line / WhatsApp', sort 20)
  registrar new[apel]: add phone field '+2347046126698' (label 'main line', sort 30)
  registrar new[apel]: add phone field '+2348128225828' (label 'main line', sort 40)
  registrar new[apel]: add email field 'registrars@apel.com.ng' (label 'registrars desk', sort 50)
  registrar new[apel]: add email field 'info@apel.com.ng' (label 'general', sort 60)
  registrar new[apel]: add email field 'customercare@apel.ng' (label "customer care; link target. Visible text reads 'customercare@apelng'", sort 70)
  registrar new[apel]: add email field 'registrars@apel.ng' (label 'general (own site)', sort 80)
  registrar new[apel]: add website field 'https://www.apel.com.ng' (label 'Website', sort 90)
  registrar new[apel]: add website field 'https://myapel.com' (label 'shareholder portal, named in FAQ', sort 100)
  registrar new[apel]: add website field 'https://registrars.apel.com.ng/' (label 'KYC Update, E-dividend Search', sort 110)
  registrar new[apel]: fill NULL legacy columns address, email, phone, website
  registrar new[cordros]: add address field '131 Ikorodu Road, Onipanu, Lagos' (label 'Head office (please confirm)', sort 10)
  registrar new[cordros]: add phone field '+2347002673767' (label 'contact centre', sort 20)
  registrar new[cordros]: add phone field '+2342012910538' (label 'WhatsApp', sort 30)
  registrar new[cordros]: add phone field '+23419049041' (label 'main phone on SEC register', sort 40)
  registrar new[cordros]: add email field 'contactcentre@cordros.com' (label 'contact centre', sort 50)
  registrar new[cordros]: add email field 'cordrosregistrars@cordros.com' (label 'registrar desk', sort 60)
  registrar new[cordros]: add email field 'registrars@cordros.com' (label 'registrar desk', sort 70)
  registrar new[cordros]: add website field 'https://cordros.com/registrars' (label 'Website', sort 80)
  registrar new[cordros]: add address field '21, 70, 110 Norman Williams Street, Ikoyi, Lagos' (label 'Branch (please confirm)', sort 90)
  registrar new[cordros]: add address field '2 Aba Close, off Ogbomosho Street, Area 8, Garki, Abuja' (label 'Branch (please confirm)', sort 100)
  registrar new[cordros]: add address field 'Globus Bank, Plot 467 Trans-Amadi Layout, Port Harcourt, Rivers' (label 'Shareholder service point (in partner bank) (please confirm)', sort 110)
  registrar new[cordros]: add address field 'Globus Bank, 11A Murtala Muhammad Way, Kano' (label 'Shareholder service point (in partner bank) (please confirm)', sort 120)
  registrar new[cordros]: fill NULL legacy columns address, email, phone, website
  registrar #61: add address field '2A Gbagada Expressway, Anthony, Lagos (Beko Ransome Kuti Gardens, opposite Dr Anthony)' (label 'Head office', sort 10)
  registrar #61: add phone field '+2348107005494' (label 'main line', sort 20)
  registrar #61: add email field 'info@carnationregistrars.com' (label 'general', sort 30)
  registrar #61: add other field 'https://carnationregistrars.com' (label 'Website (not verified, copy manually)', sort 40)
  registrar #61: fill NULL legacy columns address, email, phone
  registrar #54: add address field '2C Gbagada Expressway, by Beko Ransome Kuti Park, Gbagada, Lagos' (label 'Head office', sort 10)
  registrar #54: add phone field '+2347064000751' (label 'main line', sort 20)
  registrar #54: add email field 'datamax@datamaxregistrars.com' (label 'general; obfuscated on website, plain on SEC register', sort 30)
  registrar #54: add email field 'investorsenquiries@datamaxregistrars.com' (label 'investor enquiries (GTCO circular)', sort 40)
  registrar #54: add email field 'RMU@datamaxregistrars.com' (label 'register management unit (GTCO circular)', sort 50)
  registrar #54: add website field 'https://datamaxregistrars.com' (label 'Website', sort 60)
  registrar #54: add website field 'https://dataregview.datamaxregistrars.info' (label 'Online portal', sort 70)
  registrar #54: fill NULL legacy columns address, email, phone, website
  registrar #58: add address field '8th Floor, Knight Frank Building, 24 Campbell Street, Lagos Island, Lagos' (label 'Head office', sort 10)
  registrar #58: add phone field '+2347072427755' (label 'main line', sort 20)
  registrar #58: add phone field '+23412790797' (label 'main line', sort 30)
  registrar #58: add phone field '+23412635607' (label 'lines printed by client', sort 40)
  registrar #58: add phone field '+23417303445' (label 'lines printed by client', sort 50)
  registrar #58: add phone field '+23412805538' (label 'lines printed by client', sort 60)
  registrar #58: add email field 'info@paceregistrars.com' (label 'general', sort 70)
  registrar #58: add website field 'https://paceregistrars.com' (label 'Website', sort 80)
  registrar #58: add address field 'Any Sterling Bank or Alternative Bank branch (forms for Sterling HoldCo shareholders)' (label "Shareholder service point (client's bank) (please confirm)", sort 90)
  registrar #58: fill NULL legacy columns address, email, phone, website
  registrar #13: add address field 'Plot 89A Ajose Adeogun Street, Victoria Island, Lagos' (label 'Head office', sort 10)
  registrar #13: add phone field '+2342012784167' (label 'main line', sort 20)
  registrar #13: add phone field '+2342012784169' (label 'main line', sort 30)
  registrar #13: add phone field '+2342012784170' (label 'main line', sort 40)
  registrar #13: add phone field '+2347044997048' (label 'text messages only', sort 50)
  registrar #13: add phone field '+23412784158' (label 'department lines (FAQ)', sort 60)
  registrar #13: add phone field '+23412784172' (label 'department lines (FAQ)', sort 70)
  registrar #13: add phone field '+23412784156' (label 'department lines (FAQ)', sort 80)
  registrar #13: add phone field '+23412708930' (label 'line printed by client', sort 90)
  registrar #13: add email field 'enquiry@veritasregistrars.com' (label 'enquiries', sort 100)
  registrar #13: add email field 'customercare@veritasregistrars.com' (label 'customer care', sort 110)
  registrar #13: add email field 'probateadministration@veritasregistrars.com' (label 'probate / transmission', sort 120)
  registrar #13: add email field 'vrcustomerservice@veritasregistrars.com' (label 'change of name / customer service', sort 130)
  registrar #13: add website field 'https://veritasregistrars.com' (label 'Website', sort 140)
  registrar #13: add website field 'https://veritasregistrars.com/UnclaimedDividends.aspx' (label 'Online portal', sort 150)
  registrar #13: add website field 'https://www.veritasregistrars.com/' (label "online portal link 'Customer Services' / 'Unclaimed Dividends'", sort 160)
  registrar #13: add address field '40 Aba Road, CFC Bus Stop, Port Harcourt, Rivers State' (label 'Liaison office (please confirm)', sort 170)
  registrar #13: add address field '57 Gana Street, Maitama, Abuja, FCT' (label 'Liaison office (please confirm)', sort 180)
  registrar #13: add address field "Any Zenith Bank branch ('walk into any Zenith Bank branch', own contact page)" (label 'Shareholder service point (bank branches) (please confirm)', sort 190)
  registrar #13: add phone field ' +234 02 01 278 4167' (label 'Entered manually', sort 200)
  registrar #13: add address field 'Plot 89A, Ajose-Adeogun Street,\nVictoria Island Extension, Lagos.' (label 'Entered manually', sort 210)
  registrar #59: add address field '23 Olusoji Idowu Street, Ilupeju, Lagos (behind Mutual Benefit Insurance head office)' (label 'Head office', sort 10)
  registrar #59: add phone field '+234204538671' (label 'head office — unusual number length as printed (020-4538671-4); confirm before publishing', sort 20)
  registrar #59: add phone field '+2348054538356' (label 'main line on SEC register', sort 30)
  registrar #59: add email field 'info@crescentregistrars.com' (label 'general', sort 40)
  registrar #59: add website field 'https://crescentregistrars.com' (label 'Website', sort 50)
  registrar #59: add website field 'https://crescentregistrars.com/Login/Company' (label 'Online portal', sort 60)
  registrar #59: add address field 'Suite 26, Amssco Plaza, Niger River Road, Amssco Platinum City Estate, Galadimawa, Abuja' (label 'Branch (please confirm)', sort 70)
  registrar #59: fill NULL legacy columns address, email, phone, website
  registrar new[lighthouse]: add address field '2nd Floor, 39 Adeola Odeku Street, Victoria Island, Lagos' (label 'Head office', sort 10)
  registrar new[lighthouse]: add phone field '+2342012718910' (label 'group line', sort 20)
  registrar new[lighthouse]: add phone field '+2349090908084' (label 'group line', sort 30)
  registrar new[lighthouse]: add phone field '+2349090908085' (label 'group line', sort 40)
  registrar new[lighthouse]: add email field 'info.reg@lighthousecapital.ng' (label 'registrar desk', sort 50)
  registrar new[lighthouse]: add email field 'info@lighthousecapital.ng' (label 'group general', sort 60)
  registrar new[lighthouse]: add email field 'lighthouseRegistrars@lighthouse.com.ng' (label 'registrar (client notice; different domain lighthouse.com.ng)', sort 70)
  registrar new[lighthouse]: add website field 'https://lighthousecapital.ng' (label 'Website', sort 80)
  registrar new[lighthouse]: fill NULL legacy columns address, email, phone, website
  registrar new[pac]: add address field '122 Bode Thomas Street, Surulere, Lagos' (label 'Head office', sort 10)
  registrar new[pac]: add phone field '+2349168629450' (label 'main line (visible text)', sort 20)
  registrar new[pac]: add phone field '+2349086790272' (label "behind a click-to-call link — SEC register and the registrar's website differ by one digit; confirm ", sort 30)
  registrar new[pac]: add phone field '+2349080790272' (label "main line on SEC register — SEC register and the registrar's website differ by one digit; confirm be", sort 40)
  registrar new[pac]: add email field 'info@pacregistrars.com' (label 'general', sort 50)
  registrar new[pac]: add website field 'https://pacregistrars.com' (label 'Website', sort 60)
  registrar new[pac]: add other field 'https://shareholder.pacregistrarslimited.com/login.aspx' (label 'Online portal', sort 70)
  registrar new[pac]: add other field 'http://clients.pacregistrarslimited.com/login.aspx' (label 'Online portal', sort 80)
  registrar new[pac]: add other field 'http://brokers.pacregistrarslimited.com/login.aspx' (label 'Online portal', sort 90)
  registrar new[pac]: add website field 'https://docuhub3.nibss-plc.com.ng/edmms/self-service' (label 'NIBSS e-dividend mandate', sort 100)
  registrar new[pac]: fill NULL legacy columns address, email, phone, website
  registrar #7: add address field 'Bagco Building (4th Floor), 34 Eric Moore Road, Iganmu, Lagos (P.O. Box 3554)' (label 'Head office', sort 10)
  registrar #7: add phone field '+2348175425054' (label 'main line', sort 20)
  registrar #7: add phone field '+2348108724445' (label 'main line', sort 30)
  registrar #7: add email field 'registrars@atlasregistrars.com' (label 'registrars desk', sort 40)
  registrar #7: add website field 'https://atlasregistrars.com' (label 'Website', sort 50)
  registrar #7: add website field 'https://docuhub3.nibss-plc.com.ng/edmms/self-service' (label 'NIBSS e-dividend mandate, linked from site', sort 60)
  registrar #7: fill NULL legacy columns address, email, phone, website
  registrar #1: add address field '25 Ogunlana Drive, Surulere, Lagos' (label 'Head office (please confirm)', sort 10)
  registrar #1: add phone field '+2348033006038' (label 'main line', sort 20)
  registrar #1: add email field 'info@unityregistrarsng.com' (label 'general', sort 30)
  registrar #1: add other field 'https://unityregistrarsng.com' (label 'Website (not verified, copy manually)', sort 40)
  registrar #1: add email field 'info@unityregistrars.com' (label 'Entered manually', sort 50)
  registrar #1: add phone field '+234-1-234-5678' (label 'Entered manually', sort 60)
  registrar #1: fill NULL legacy columns address
  registrar new[lancelot]: add address field '245 Herbert Macaulay Way, Alagomeji, Yaba, Lagos' (label 'Head office', sort 10)
  registrar new[lancelot]: add phone field '+2349169660770' (label 'main line', sort 20)
  registrar new[lancelot]: add email field 'info@lancelotregistrars.com' (label 'general', sort 30)
  registrar new[lancelot]: add website field 'https://lancelotregistrars.com' (label 'Website', sort 40)
  registrar new[lancelot]: fill NULL legacy columns address, email, phone, website
  registrar new[fsl]: add address field 'Plot 688 Ahmodu Tijani Close, off Sanusi Fafunwa Street, Victoria Island, Lagos' (label 'Head office (please confirm)', sort 10)
  registrar new[fsl]: add phone field '+2348151590112' (label 'all offices', sort 20)
  registrar new[fsl]: add email field 'info@fsl.ng' (label 'group general', sort 30)
  registrar new[fsl]: add email field 'tellme@fsl.ng' (label 'group', sort 40)
  registrar new[fsl]: add website field 'https://fsl.ng' (label 'Website', sort 50)
  registrar new[fsl]: fill NULL legacy columns address, email, phone, website
  registrar new[paxhil-minerva]: add address field '10 Bankole Oki Road, Ikoyi, Lagos' (label 'Head office', sort 10)
  registrar new[paxhil-minerva]: add phone field '+2349078072602' (label 'main line', sort 20)
  registrar new[paxhil-minerva]: add email field 'info@paxhillminervaregistrars.com' (label 'general', sort 30)
  registrar new[paxhil-minerva]: add website field 'https://paxhillminervaregistrars.com' (label 'Website', sort 40)
  registrar new[paxhil-minerva]: fill NULL legacy columns address, email, phone, website
  company #16: soft-delete primary link #58 (registrar #11)
  company #16: soft-delete primary link #319 (registrar #57)
  company #16: create primary link -> #2
  company #16: registrar_id 11 -> #2
  company #34: soft-delete primary link #57 (registrar #11)
  company #34: soft-delete primary link #320 (registrar #57)
  company #34: create primary link -> #2
  company #34: registrar_id 11 -> #2
  company #92: create primary link -> #2
  company #92: registrar_id None -> #2
  company #94: soft-delete primary link #267 (registrar #50)
  company #94: create primary link -> #2
  company #94: registrar_id None -> #2
  company #102: soft-delete primary link #338 (registrar #61)
  company #102: create primary link -> #2
  company #102: registrar_id None -> #2
  company #107: create primary link -> #2
  company #107: registrar_id None -> #2
  company #108: create primary link -> #2
  company #108: registrar_id None -> #2
  company #110: soft-delete primary link #322 (registrar #57)
  company #110: create primary link -> #2
  company #110: registrar_id None -> #2
  company #111: soft-delete primary link #282 (registrar #51)
  company #111: create primary link -> #2
  company #111: registrar_id None -> #2
  company #121: soft-delete primary link #352 (registrar #61)
  company #121: create primary link -> #2
  company #121: registrar_id None -> #2
  company #146: create primary link -> #2
  company #146: registrar_id None -> #2
  company #63: soft-delete primary link #63 (registrar #4)
  company #63: soft-delete primary link #311 (registrar #55)
  company #63: create primary link -> #2
  company #63: registrar_id 4 -> #2
  company #188: create primary link -> #2
  company #188: registrar_id None -> #2
  company #45: soft-delete primary link #69 (registrar #6)
  company #45: soft-delete primary link #310 (registrar #55)
  company #45: create primary link -> #2
  company #45: registrar_id 6 -> #2
  company #50: soft-delete primary link #70 (registrar #21)
  company #50: create primary link -> #2
  company #50: registrar_id 21 -> #2
  company #162: soft-delete primary link #349 (registrar #61)
  company #162: create primary link -> #2
  company #162: registrar_id None -> #2
  company #176: create primary link -> #2
  company #176: registrar_id None -> #2
  company #83: registrar_id None -> #50
  company #84: registrar_id None -> #50
  company #87: create primary link -> #50
  company #87: registrar_id None -> #50
  company #116: create primary link -> #50
  company #116: registrar_id None -> #50
  company #119: registrar_id None -> #50
  company #122: create primary link -> #50
  company #122: registrar_id None -> #50
  company #132: create primary link -> #50
  company #132: registrar_id None -> #50
  company #179: create primary link -> #50
  company #179: registrar_id None -> #50
  company #181: registrar_id None -> #50
  company #180: registrar_id None -> #50
  company #18: soft-delete primary link #65 (registrar #6)
  company #18: soft-delete primary link #294 (registrar #52)
  company #18: create primary link -> #50
  company #18: registrar_id 6 -> #50
  company #183: registrar_id None -> #50
  company #184: create primary link -> #50
  company #184: registrar_id None -> #50
  company #196: create primary link -> #50
  company #196: registrar_id None -> #50
  company #76: create primary link -> #50
  company #76: registrar_id None -> #50
  company #74: create primary link -> #52
  company #74: registrar_id None -> #52
  company #81: soft-delete primary link #270 (registrar #50)
  company #81: create primary link -> #52
  company #81: registrar_id None -> #52
  company #85: soft-delete primary link #314 (registrar #56)
  company #85: create primary link -> #52
  company #85: registrar_id None -> #52
  company #88: soft-delete primary link #337 (registrar #61)
  company #88: create primary link -> #52
  company #88: registrar_id None -> #52
  company #66: soft-delete primary link #64 (registrar #11)
  company #66: soft-delete primary link #327 (registrar #58)
  company #66: create primary link -> #52
  company #66: registrar_id 11 -> #52
  company #126: create primary link -> #52
  company #126: registrar_id None -> #52
  company #128: create primary link -> #52
  company #128: registrar_id None -> #52
  company #40: soft-delete primary link #67 (registrar #11)
  company #40: registrar_id 11 -> #52
  company #155: registrar_id None -> #52
  company #158: registrar_id None -> #52
  company #160: registrar_id None -> #52
  company #170: registrar_id None -> #52
  company #189: create primary link -> #52
  company #189: registrar_id None -> #52
  company #82: create primary link -> #8
  company #82: registrar_id None -> #8
  company #89: create primary link -> #8
  company #89: registrar_id None -> #8
  company #101: soft-delete primary link #332 (registrar #60)
  company #101: create primary link -> #8
  company #101: registrar_id None -> #8
  company #3: soft-delete primary link #48 (registrar #4)
  company #3: soft-delete primary link #328 (registrar #58)
  company #3: create primary link -> #8
  company #3: registrar_id 4 -> #8
  company #125: create primary link -> #8
  company #125: registrar_id None -> #8
  company #124: soft-delete primary link #312 (registrar #56)
  company #124: create primary link -> #8
  company #124: registrar_id None -> #8
  company #141: soft-delete primary link #317 (registrar #56)
  company #141: create primary link -> #8
  company #141: registrar_id None -> #8
  company #27: soft-delete primary link #61 (registrar #15)
  company #27: soft-delete primary link #313 (registrar #56)
  company #27: create primary link -> #8
  company #27: registrar_id 15 -> #8
  company #182: create primary link -> #8
  company #182: registrar_id None -> #8
  company #68: soft-delete primary link #56 (registrar #13)
  company #68: soft-delete primary link #315 (registrar #56)
  company #68: create primary link -> #8
  company #68: registrar_id 13 -> #8
  company #190: create primary link -> #8
  company #190: registrar_id None -> #8
  company #199: create primary link -> #8
  company #199: registrar_id None -> #8
  company #51: soft-delete primary link #71 (registrar #20)
  company #51: create primary link -> #51
  company #51: registrar_id 20 -> #51
  company #77: soft-delete primary link #333 (registrar #60)
  company #77: create primary link -> #51
  company #77: registrar_id None -> #51
  company #78: create primary link -> #51
  company #78: registrar_id None -> #51
  company #80: registrar_id None -> #51
  company #86: create primary link -> #51
  company #86: registrar_id None -> #51
  company #150: create primary link -> #51
  company #150: registrar_id None -> #51
  company #91: create primary link -> #51
  company #91: registrar_id None -> #51
  company #21: soft-delete primary link #53 (registrar #12)
  company #21: registrar_id 12 -> #51
  company #143: registrar_id None -> #51
  company #153: create primary link -> #51
  company #153: registrar_id None -> #51
  company #137: create primary link -> #51
  company #137: registrar_id None -> #51
  company #42: soft-delete primary link #68 (registrar #21)
  company #42: registrar_id 21 -> #55
  company #114: soft-delete primary link #351 (registrar #61)
  company #114: create primary link -> #55
  company #114: registrar_id None -> #55
  company #131: create primary link -> #55
  company #131: registrar_id None -> #55
  company #142: create primary link -> #55
  company #142: registrar_id None -> #55
  company #145: soft-delete primary link #336 (registrar #60)
  company #145: create primary link -> #55
  company #145: registrar_id None -> #55
  company #152: create primary link -> #55
  company #152: registrar_id None -> #55
  company #157: create primary link -> #55
  company #157: registrar_id None -> #55
  company #1: soft-delete primary link #2 (registrar #11)
  company #1: create primary link -> #55
  company #1: registrar_id 11 -> #55
  company #178: soft-delete primary link #321 (registrar #57)
  company #178: create primary link -> #55
  company #178: registrar_id None -> #55
  company #11: soft-delete primary link #52 (registrar #11)
  company #11: create primary link -> #55
  company #11: registrar_id 11 -> #55
  company #163: soft-delete primary link #340 (registrar #61)
  company #163: create primary link -> #55
  company #163: registrar_id None -> #55
  company #120: create primary link -> new[apel]
  company #120: registrar_id None -> new[apel]
  company #127: soft-delete primary link #347 (registrar #61)
  company #127: create primary link -> new[apel]
  company #127: registrar_id None -> new[apel]
  company #130: soft-delete primary link #348 (registrar #61)
  company #130: create primary link -> new[apel]
  company #130: registrar_id None -> new[apel]
  company #136: create primary link -> new[apel]
  company #136: registrar_id None -> new[apel]
  company #147: soft-delete primary link #296 (registrar #52)
  company #147: create primary link -> new[apel]
  company #147: registrar_id None -> new[apel]
  company #7: soft-delete primary link #60 (registrar #13)
  company #7: soft-delete primary link #344 (registrar #61)
  company #7: create primary link -> new[apel]
  company #7: registrar_id 13 -> new[apel]
  company #161: create primary link -> new[apel]
  company #161: registrar_id None -> new[apel]
  company #168: create primary link -> new[apel]
  company #168: registrar_id None -> new[apel]
  company #177: create primary link -> new[apel]
  company #177: registrar_id None -> new[apel]
  company #103: create primary link -> new[apel]
  company #103: registrar_id None -> new[apel]
  company #95: soft-delete primary link #323 (registrar #57)
  company #95: create primary link -> new[cordros]
  company #95: registrar_id None -> new[cordros]
  company #99: create primary link -> new[cordros]
  company #99: registrar_id None -> new[cordros]
  company #100: soft-delete primary link #302 (registrar #53)
  company #100: create primary link -> new[cordros]
  company #100: registrar_id None -> new[cordros]
  company #138: create primary link -> new[cordros]
  company #138: registrar_id None -> new[cordros]
  company #90: create primary link -> new[cordros]
  company #90: registrar_id None -> new[cordros]
  company #144: create primary link -> #61
  company #144: registrar_id None -> #61
  company #187: create primary link -> #61
  company #187: registrar_id None -> #61
  company #156: create primary link -> #61
  company #156: registrar_id None -> #61
  company #134: soft-delete primary link #330 (registrar #59)
  company #134: create primary link -> #54
  company #134: registrar_id None -> #54
  company #129: create primary link -> #54
  company #129: registrar_id None -> #54
  company #149: create primary link -> #54
  company #149: registrar_id None -> #54
  company #165: registrar_id None -> #54
  company #201: registrar_id None -> #54
  company #113: create primary link -> #54
  company #113: registrar_id None -> #54
  company #75: create primary link -> #58
  company #75: registrar_id None -> #58
  company #166: create primary link -> #58
  company #166: registrar_id None -> #58
  company #172: create primary link -> #58
  company #172: registrar_id None -> #58
  company #123: create primary link -> #58
  company #123: registrar_id None -> #58
  company #97: soft-delete primary link #301 (registrar #53)
  company #97: create primary link -> #13
  company #97: registrar_id None -> #13
  company #115: create primary link -> #13
  company #115: registrar_id None -> #13
  company #135: create primary link -> #13
  company #135: registrar_id None -> #13
  company #200: soft-delete primary link #300 (registrar #53)
  company #200: create primary link -> #13
  company #200: registrar_id None -> #13
  company #173: soft-delete primary link #335 (registrar #60)
  company #173: create primary link -> #59
  company #173: registrar_id None -> #59
  company #93: soft-delete primary link #346 (registrar #61)
  company #93: create primary link -> new[lighthouse]
  company #93: registrar_id None -> new[lighthouse]
  company #109: create primary link -> new[pac]
  company #109: registrar_id None -> new[pac]
  company #154: create primary link -> new[pac]
  company #154: registrar_id None -> new[pac]
  company #117: create primary link -> #7
  company #117: registrar_id None -> #7
  company #118: create primary link -> new[lancelot]
  company #118: registrar_id None -> new[lancelot]

== counts ==
  registrars: created=7 merged=10 soft-deleted=10 renamed=3
  contact fields: added=184 moved=1
  legacy columns filled=69
  links: created=100 reactivated=0 soft-deleted=54 repointed=19
  requirements repointed=0
  companies.registrar_id changed=132
  held back (weak)=13
  unmatched=53
  without contact record=5

== report (informational, no changes) ==
  held back (weak): MULTITREX (Multi-Trex Integrated Foods Plc) for meristem — no link change, Product Owner decides [Low/SINGLE-SOURCE]
  held back (weak): SOVRENINS (SOVRENINS) for meristem — no link change, Product Owner decides [Low/STALE]
  held back (weak): CAP (CAP Plc) for africa-prudential — no link change, Product Owner decides [Low/STALE]
  held back (weak): SCOA (SCOA) for africa-prudential — no link change, Product Owner decides [Low/STALE]
  held back (weak): DAARCOMM (DAARCOMM) for first-registrars — no link change, Product Owner decides [Low/STALE]
  held back (weak): PRESTIGE (PRESTIGE) for first-registrars — no link change, Product Owner decides [Low/STALE]
  held back (weak): ALEX (ALEX) for greenwich — no link change, Product Owner decides [Low/STALE]
  held back (weak): WAPIC (WAPIC Insurance) for coronation — no link change, Product Owner decides [Low/STALE]
  held back (weak): RONCHESS (Ronchess Global Resources Plc) for coronation — no link change, Product Owner decides [Low/STALE]
  held back (weak): AFROMEDIA (Afromedia Plc) for crescent — no link change, Product Owner decides [Low/STALE]
  held back (weak): CUTIX (CUTIX PLC) for crescent — no link change, Product Owner decides [Low/STALE]
  held back (weak): NNFM (NNFM) for atlas — no link change, Product Owner decides [Low/STALE]
  held back (weak): VERITASKAP (VERITASKAP) for unity — no link change, Product Owner decides [Low/STALE]
  unmatched: (no ticker) (Food Concepts PLC) for meristem — no ticker in the file, no link written
  unmatched: (no ticker) (Free Range Farms Plc) for meristem — no ticker in the file, no link written
  unmatched: (no ticker) (GEO-Fluids PLC) for meristem — no ticker in the file, no link written
  unmatched: (no ticker) (Newrest Asl Nigeria Plc) for meristem — no ticker in the file, no link written
  unmatched: (no ticker) (Nigeria Mortgage Refinance Company Plc) for meristem — no ticker in the file, no link written
  unmatched: (no ticker) (Nipco PLC) for meristem — no ticker in the file, no link written
  unmatched: (no ticker) (Paintcom Investment Nigeria Plc) for meristem — no ticker in the file, no link written
  unmatched: THOMASWY (Thomas Wyatt Nigeria Plc) for meristem — ticker not in companies, no link written
  unmatched: ABBEYBANK (Abbey Bank Plc) for africa-prudential — ticker not in companies, no link written
  unmatched: MOFIREIF (MOFI Real Estate Investment Fund) for africa-prudential — ticker not in companies, no link written
  unmatched: (no ticker) (Afriland Properties Plc) for africa-prudential — no ticker in the file, no link written
  unmatched: (no ticker) (Central Securities Clearing System (CSCS) PLC) for africa-prudential — no ticker in the file, no link written
  unmatched: (no ticker) (Golden Capital PLC) for africa-prudential — no ticker in the file, no link written
  unmatched: (no ticker) (Lagos Building Investment Company PLC) for africa-prudential — no ticker in the file, no link written
  unmatched: BAPLC (Briclinks Africa Plc) for africa-prudential — ticker not in companies, no link written
  unmatched: CMFC (Critical Minerals Financing Corp Plc) for first-registrars — ticker not in companies, no link written
  unmatched: (no ticker) (Costain (West Africa) Plc) for first-registrars — no ticker in the file, no link written
  unmatched: (no ticker) (CR Services Plc) for first-registrars — no ticker in the file, no link written
  unmatched: (no ticker) (Dufil Prima Foods Plc) for first-registrars — no ticker in the file, no link written
  unmatched: (no ticker) (Famad Nigeria Plc) for first-registrars — no ticker in the file, no link written
  unmatched: (no ticker) (Friesland Campina Wamco Nigeria PLC) for first-registrars — no ticker in the file, no link written
  unmatched: (no ticker) (MRS Oil Nigeria PLC) for first-registrars — no ticker in the file, no link written
  unmatched: (no ticker) (The Infrastructure Bank PLC) for first-registrars — no ticker in the file, no link written
  unmatched: ENAMELWA (Nigerian Enamelware Plc) for greenwich — ticker not in companies, no link written
  unmatched: (no ticker) (11 PLC) for greenwich — no ticker in the file, no link written
  unmatched: (no ticker) (Great Nigeria Insurance PLC) for greenwich — no ticker in the file, no link written
  unmatched: (no ticker) (Impresit Bakolori PLC) for greenwich — no ticker in the file, no link written
  unmatched: (no ticker) (Industrial and General Insurance PLC) for greenwich — no ticker in the file, no link written
  unmatched: (no ticker) (IPWA PLC) for greenwich — no ticker in the file, no link written
  unmatched: (no ticker) (Okitipupa Oil Palm Plc) for greenwich — no ticker in the file, no link written
  unmatched: (no ticker) (UBN Property Company Plc) for greenwich — no ticker in the file, no link written
  unmatched: UHREIT (UH Real Estate Investment Trust) for greenwich — ticker not in companies, no link written
  unmatched: (no ticker) (Access Bank Plc) for coronation — no ticker in the file, no link written
  unmatched: (no ticker) (FirstTrust Mortgage Bank Plc) for coronation — no ticker in the file, no link written
  unmatched: (no ticker) (NASD Plc) for coronation — no ticker in the file, no link written
  unmatched: (no ticker) (Nitrox Industrial Gases Plc) for coronation — no ticker in the file, no link written
  unmatched: HBMNG (HBM Nigeria Plc) for cardinalstone — ticker not in companies, no link written
  unmatched: (no ticker) (Acorn Petroleum Plc) for cardinalstone — no ticker in the file, no link written
  unmatched: (no ticker) (AG Mortgage Bank Plc) for cardinalstone — no ticker in the file, no link written
  unmatched: (no ticker) (Infrastructure Credit Guarantee Company) for cardinalstone — no ticker in the file, no link written
  unmatched: (no ticker) (Purple Real Estate Income PLC) for cardinalstone — no ticker in the file, no link written
  unmatched: (no ticker) (Mass Telecoms Innovation Plc) for apel — no ticker in the file, no link written
  unmatched: PHARMDEKO (Pharma-Deko Plc) for apel — ticker not in companies, no link written
  unmatched: AVAIF (AVA Infrastructure Fund) for cordros — ticker not in companies, no link written
  unmatched: (no ticker) (Capital Hotels Plc) for cordros — no ticker in the file, no link written
  unmatched: AVACAP (Ava Capital Plc) for cordros — ticker not in companies, no link written
  unmatched: AFRINSURE (African Alliance Insurance Plc) for carnation — ticker not in companies, no link written
  unmatched: (no ticker) (Riggs Ventures West African PLC) for carnation — no ticker in the file, no link written
  unmatched: GOLDBREW (Golden Guinea Breweries Plc) for carnation — ticker not in companies, no link written
  unmatched: (no ticker) (Capital Bancorp PLC) for lighthouse — no ticker in the file, no link written
  unmatched: (no ticker) (Lighthouse Financial Services Plc) for lighthouse — no ticker in the file, no link written
  unmatched: (no ticker) (Fumman Agricultural Products Plc) for pac — no ticker in the file, no link written
  unmatched: UNITYBNK (Unity Bank Plc) for unity — ticker not in companies, no link written
  without contact record: (no ticker) (Vital Products Plc) for Centurion Registrars Limited (suspended; not on SEC register) — Reported suspended by the SEC (March 2025); not found among SEC-registered registrars on 2026-11-26., no company created
  without contact record: UNIONDICON (Union Dicon Salt Plc) for Centurion Registrars Limited (suspended; not on SEC register) — Reported suspended by the SEC (March 2025); not found among SEC-registered registrars on 2026-11-26., no company created
  without contact record: (no ticker) (Resourcery PLC) for ECO Securities (not on SEC register) — Not on the SEC register as a registrar., no company created
  without contact record: (no ticker) (International Packing Industries Nigeria Plc) for LENNAP Securities (not on SEC register) — Not on the SEC register as a registrar., no company created
  without contact record: EKOCORP (Ekocorp Plc) for UNVERIFIED - not found — Registrar not identified., no company created
```
