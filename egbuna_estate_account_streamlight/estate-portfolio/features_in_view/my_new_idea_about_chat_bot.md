A feature i am looking to build:
Dashboard:
 - The notification bell will have more activities associated with it
   1. Ability to pull information as instant notification of the watchlist table. So that there will be a live API that will be integrated to to the watchlist to give the up to date information of the shares I am tracking
   2. It will also be able to give live news of events in the Nigeria financial space, and not limited to stocks[We will seek reliable free API with good rate limit that will be used to source news]
   3. Also as part of the instand notification, I will also want a consolidation of social media news[My prefered sources are twitter, reddit and new substack that writes about financial News]
  - The Watchlist Table and page will a dashboard for tracking the stocks I am watching. 
   - It will have these features:
    - The result of the pull and cached new or improved stocks from the Nigeria market that are worth considering to be purchased
    - Two cards [My current stocks that I am tracking to either add to remove or sell to buy other improved stocks that I have or the ones that I am tracking]
  - I want to be able to get live fetch of stocks, presented as news or tiny snippets that can then be checked in the dashboard for availability and when clicked I will be taken to a table that would take me through the process of purchasing stocks. It will guide me through its workflow in the steps that will be automated, e.g fetching registrar's contact details, integrated calendar that I can create appointment date. All details will be collated into an inbox that I can easily click, open and have the valuable informations in one place to be able to proceed with getting the right registrars and armed with the right informations to transact with them. 
  - I want to totally remove all inline and editing toggle features. Everything will be done in the Admin Features [Admin Section of the App]. This is to make it easy to filter out the Areas the Admin and read only users can see.
  
Companies
  - List the companies currently trading in the nigeria stock exchange [source: https://ngxgroup.com/exchange/trade/equities/listed-companies/]
  - Filter By Market Type | Filter By Sector
    - Market Type 
	  - All Market [Displays all the companies without filter]
	  - Premium Board [Filter by premium Board]
	  - Main Board [Filter by main board]
	  - Asem [Filter by Asem]
	  - Growth Board [Filter By growth board]
    - Sector
	-All Sector                                                         
	-AGRICULTURE                                                         
	-CONGLOMERATES                                                       
	-CONSTRUCTION/REAL ESTATE                                           
	-CONSUMER -GOODS                                                             
	-FINANCIAL -SERVICES                                                            
	-HEALTHCARE                                                          
	-INDUSTRIAL GOODS
	-NATURAL RESOURCES 
	-OIL AND GAS 
	-SERVICES
 Company Profile[ Page will not be visiblein the menu                                                                                                                                                                     
   - When any of the listed companies is clicked:
     - Open a new page and the page will contain
	- The current value of the share as of the closing of the previous market day
        - The Overview of the Company
-- Trading Information -- [Card]
Company Name
Ticker Symbol
Sector
Sub Sector
Market Classification
Market Cap (Mil.)
Shares Outstanding (Mil.): 
Official Open: 	
Official Close: 

[Menu] Profile 
Nature of Business: 	Primary Mortgage Bank (PMB)
Company Address: 	23 KARIMU KOTUN STREET VICTORIA ISLAND LAGOS
Telephone: 	019035700
Fax: 	
Email: 	enquiries@abbeymortgagebankplc.com
Auditor: 	
Registrar: 	
Company Secretary: 	
Date Listed: 	
Date of Incorporation: 	
Website: 	
Board Of Directors: 
More Info about company[route to NGX profile about the company]: 	


  

User Management:
  - The User Managemenent feature needs to be built too -
    - Add read only users[family members, stock brokers, registrar staffs, estimators] that would require access to evaluate the EPM's value and also know how to add their inputs in adding value to the web app
	 Features Include:
	  - Admin Users: Full CRUD access and access to all pages
	  - Read Only View to the Following:
	   - Dashboard [ Actions Items will not have any data on it or admin related information. Will oly have the static text "Portfolio up to date" and Checkmark icon on top]
	   - Holdings page
	   - Companies
	   - Dividends
	   - Price History
	   - Transaction [Will be reviewed when the page and table has been built]
	   - Registrars
	   - Nav History, Rebalancing and Admin Section  [They don't need to be visible or available to Read only users].
  - Add New User
  - Update Users
  - Delete Users
  - Add Roles
   - Define what Roles can do
   - Define what they can have access to
  - Update Roles
   - Update what roles can do
  - Delete Roles
   - Remove the assigned duties of roles
  - Create association of roles for users
  - Remove association
  -workflow for creating user and role
   create user -> create role [User doesn't need to receive emails to acknowledge creation of new user account]     

=============================== New ==================================== [You have not copied this to Claude] ==================

AI Chat Bot
==============

- Adding chat bot to EPM feature
--------------------------------------
I want to add an AI chat bot feature to my  EPM. The workflow or interaction will go as suggested below:

`
User:
How has my portfolio performed this month?

AI:
Your portfolio is up 4.2%.

Top performer:
MTN +8.4%

Worst performer:
UBA -3.1%

Dividend expected:
NGN 15,400

[chart]

or

User:
Why did my portfolio drop yesterday?

AI:
ZENITHBANK fell 4.2%.

This accounted for 68% of yesterday's decline.

[chart]

visually
---------

React Chat UI
+
LLM
+
Recharts

-------------

Architecture:

User
 ↓
Chat Interface
 ↓
FastAPI
 ↓
Portfolio Analytics Engine
 ↓
PostgreSQL
 ↓
LLM Explanation
 ↓
Chart Components

-------

Tech Stack

Frontend
────────
React 18
shadcn/ui
Tailwind
Recharts

Backend
────────
FastAPI

Analytics
────────
Python pandas
NumPy

Database
────────
PostgreSQL

AI
────────
LLM endpoint

Reuse existing resources and integrate with project.

The Bot 

===== In summary ========

The AI should be able to answer:

Which stock contributed most to my gains this year?

Show MTN performance against NGXASI.

Which holdings have not paid dividends in 3 years?

How much dividend income am I expected to receive?

What percentage of my portfolio is banking stocks?

Which registrar manages most of my holdings?

What documents are still missing for dormant claims?

And return:

Text explanation
+
Metrics
+
Embedded Recharts visualization                                                               
