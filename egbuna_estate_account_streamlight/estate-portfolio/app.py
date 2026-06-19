"""
Estate Portfolio Management System - Streamlit Application
Single-file MVP for managing Nigerian stock portfolio
"""

import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import re
import time
import subprocess

# ============================================================================
# DATABASE CONNECTION
# ============================================================================

@st.cache_resource(ttl=600)  # Bug Fix: Reconnect every 10 min to prevent stale connections
def get_db_connection():
    """Create PostgreSQL connection (cached, with auto-expiry to prevent stale connections)"""
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "openagile_postgres"),
            database=os.getenv("DB_NAME", "estate_portfolio"),
            user=os.getenv("DB_USER", "openagile"),
            password=os.getenv("DB_PASSWORD", "")
        )
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        st.stop()

def query_db(sql, params=None):
    """Execute SELECT query and return DataFrame"""
    try:
        conn = get_db_connection()
        df = pd.read_sql_query(sql, conn, params=params)
        return df
    except psycopg2.OperationalError:
        # Connection went stale — clear cache and retry once
        st.cache_resource.clear()
        try:
            conn = get_db_connection()
            return pd.read_sql_query(sql, conn, params=params)
        except Exception as e:
            st.error(f"Query failed after reconnect: {e}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Query failed: {e}")
        return pd.DataFrame()

def execute_db(sql, params=None):
    """Execute INSERT/UPDATE/DELETE"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        cursor.close()
        return True
    except psycopg2.OperationalError:
        # Stale connection — clear cache and retry once
        st.cache_resource.clear()
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            st.error(f"Database operation failed after reconnect: {e}")
            return False
    except Exception as e:
        st.error(f"Database operation failed: {e}")
        return False

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Estate Portfolio Manager",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .gain { color: #10b981; font-weight: bold; }
    .loss { color: #ef4444; font-weight: bold; }
    .stDataFrame { font-size: 0.9rem; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

st.sidebar.title("📊 Estate Portfolio")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Dashboard", "🏢 Companies", "💼 Holdings", "💰 Transactions", 
     "📈 Price History", "💸 Dividends", "👥 Registrars", "💬 Communications", 
     "📊 Reports", "⚙️ Settings"]
)

st.sidebar.markdown("---")
st.sidebar.info(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# ============================================================================
# DASHBOARD PAGE
# ============================================================================

if page == "🏠 Dashboard":
    st.title("Estate Portfolio Dashboard")
    
    # Portfolio Summary Metrics
    summary_query = """
    SELECT 
        COUNT(DISTINCT h.company_id) as total_holdings,
        COALESCE(SUM(h.total_cost), 0) as total_invested,
        COALESCE(SUM(h.num_shares * COALESCE(c.current_price, 0)), 0) as current_value,
        COALESCE(SUM((h.num_shares * COALESCE(c.current_price, 0)) - h.total_cost), 0) as unrealized_gain_loss
    FROM holdings h
    JOIN companies c ON h.company_id = c.id
    WHERE h.deleted_at IS NULL AND c.deleted_at IS NULL
    """
    
    summary = query_db(summary_query)
    
    if not summary.empty and pd.to_numeric(summary.iloc[0]['total_holdings']) > 0:
        summary_row = summary.iloc[0]
        return_pct = (summary_row['unrealized_gain_loss'] / summary_row['total_invested'] * 100) if summary_row['total_invested'] > 0 else 0
        
        # Top metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Portfolio Value",
                value=f"₦{summary_row['current_value']:,.0f}",
                delta=f"{return_pct:.2f}%"
            )
        
        with col2:
            st.metric(
                label="Total Invested",
                value=f"₦{summary_row['total_invested']:,.0f}"
            )
        
        with col3:
            st.metric(
                label="Unrealized Gain/Loss",
                value=f"₦{summary_row['unrealized_gain_loss']:,.0f}",
                delta=f"{return_pct:.2f}%"
            )
        
        with col4:
            st.metric(
                label="Total Holdings",
                value=f"{int(summary_row['total_holdings'])}"
            )
        
        st.markdown("---")
        
        # Charts Row
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sector Allocation")
            
            sector_query = """
            SELECT 
                c.sector,
                SUM(h.num_shares * COALESCE(c.current_price, 0)) as sector_value
            FROM holdings h
            JOIN companies c ON h.company_id = c.id
            WHERE h.deleted_at IS NULL AND c.deleted_at IS NULL AND c.sector IS NOT NULL
            GROUP BY c.sector
            ORDER BY sector_value DESC
            """
            
            sector_data = query_db(sector_query)
            
            if not sector_data.empty:
                fig = px.pie(
                    sector_data, 
                    values='sector_value', 
                    names='sector',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(showlegend=True, height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No sector data available")
        
        with col2:
            st.subheader("Top 10 Holdings")
            
            top_holdings_query = """
            SELECT 
                c.ticker,
                c.name,
                (h.num_shares * COALESCE(c.current_price, 0)) as current_value,
                (((h.num_shares * COALESCE(c.current_price, 0)) - h.total_cost) / NULLIF(h.total_cost, 0) * 100) as return_pct
            FROM holdings h
            JOIN companies c ON h.company_id = c.id
            WHERE h.deleted_at IS NULL AND c.deleted_at IS NULL
            ORDER BY current_value DESC
            LIMIT 10
            """
            
            top_holdings = query_db(top_holdings_query)
            
            if not top_holdings.empty:
                fig = px.bar(
                    top_holdings,
                    x='current_value',
                    y='ticker',
                    orientation='h',
                    color='return_pct',
                    color_continuous_scale=['red', 'yellow', 'green'],
                    labels={'current_value': 'Value (₦)', 'return_pct': 'Return %'},
                    height=400
                )
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No holdings data available")
        
        st.markdown("---")
        
        # Recent Activity
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Recent Transactions")
            
            recent_trans_query = """
            SELECT 
                t.transaction_date,
                c.ticker,
                t.transaction_type,
                t.num_shares,
                t.price_per_share,
                t.net_amount
            FROM transactions t
            JOIN companies c ON t.company_id = c.id
            WHERE t.deleted_at IS NULL
            ORDER BY t.transaction_date DESC
            LIMIT 5
            """
            
            recent_trans = query_db(recent_trans_query)
            
            if not recent_trans.empty:
                display_trans = recent_trans.copy()
                display_trans['transaction_date'] = pd.to_datetime(display_trans['transaction_date']).dt.strftime('%Y-%m-%d')
                display_trans['net_amount'] = display_trans['net_amount'].apply(lambda x: f"₦{x:,.0f}" if pd.notna(x) else "N/A")
                display_trans['num_shares'] = display_trans['num_shares'].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
                st.dataframe(display_trans, use_container_width=True, hide_index=True)
            else:
                st.info("No recent transactions")
        
        with col2:
            st.subheader("Action Items")
            
            action_items_query = """
            SELECT 
                communication_date,
                entity_type,
                summary,
                follow_up_date,
                priority
            FROM communication_logs
            WHERE status != 'resolved' 
              AND deleted_at IS NULL
              AND follow_up_date >= CURRENT_DATE
            ORDER BY follow_up_date ASC, priority DESC
            LIMIT 5
            """
            
            action_items = query_db(action_items_query)
            
            if not action_items.empty:
                for idx, row in action_items.iterrows():
                    priority_emoji = "🔴" if row['priority'] == 'high' else "🟡" if row['priority'] == 'medium' else "🟢"
                    st.markdown(f"{priority_emoji} **{row['entity_type']}** - {row['summary'][:50]}...")
                    st.caption(f"Follow-up: {row['follow_up_date']}")
            else:
                st.success("✅ No pending action items!")
    else:
        st.info("👋 Welcome! Start by adding companies and holdings in the sidebar.")
        st.markdown("""
        ### Quick Start:
        1. **Add Companies** - Go to Companies page
        2. **Add Holdings** - Record your share ownership
        3. **Import from Obsidian** - Use Settings to import existing data
        4. **Enable Price Updates** - Weekly scraper will keep prices current
        """)

# ============================================================================
# COMPANIES PAGE
# ============================================================================

elif page == "🏢 Companies":
    st.title("Companies Master List")
    
    # Add new company form
    with st.expander("➕ Add New Company"):
        with st.form("add_company_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                ticker = st.text_input("Ticker Symbol*", max_chars=10)
                name = st.text_input("Company Name*")
                sector = st.selectbox("Sector", 
                    ["", "Banking", "Insurance", "Oil & Gas", "Consumer Goods", 
                     "Industrial", "ICT", "Healthcare", "Agriculture", "Other"])
            
            with col2:
                isin = st.text_input("ISIN", max_chars=12)
                status = st.selectbox("Status", ["listed", "merged", "defunct", "delisted"])
                
                # Get registrars for dropdown
                registrars = query_db("SELECT id, name FROM registrars WHERE deleted_at IS NULL ORDER BY name")
                registrar_options = {row['name']: row['id'] for _, row in registrars.iterrows()}
                registrar_name = st.selectbox("Registrar", [""] + list(registrar_options.keys()))
            
            notes = st.text_area("Notes")
            
            submitted = st.form_submit_button("Add Company")
            
            if submitted:
                if not ticker or not name:
                    st.error("Ticker and Name are required!")
                else:
                    registrar_id = registrar_options.get(registrar_name) if registrar_name else None
                    
                    success = execute_db("""
                        INSERT INTO companies (ticker, name, sector, isin, status, registrar_id, notes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (ticker.upper(), name, sector or None, isin or None, status, registrar_id, notes or None))
                    
                    if success:
                        st.success(f"✅ Added {ticker} - {name}")
                        time.sleep(1)
                        st.rerun()
    
    st.markdown("---")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_status = st.multiselect("Filter by Status", 
            ["listed", "merged", "defunct", "delisted"], default=["listed"])
    with col2:
        sectors = query_db("SELECT DISTINCT sector FROM companies WHERE sector IS NOT NULL ORDER BY sector")
        filter_sector = st.multiselect("Filter by Sector", sectors['sector'].tolist() if not sectors.empty else [])
    with col3:
        search_query = st.text_input("🔍 Search companies", "")
    
    # Build query with filters
    companies_query = """
    SELECT 
        c.id,
        c.ticker,
        c.name,
        c.sector,
        c.status,
        r.name as registrar,
        c.current_price,
        c.last_price_update,
        COALESCE(h.num_shares, 0) as shares_owned
    FROM companies c
    LEFT JOIN registrars r ON c.registrar_id = r.id AND r.deleted_at IS NULL
    LEFT JOIN holdings h ON c.id = h.company_id AND h.deleted_at IS NULL
    WHERE c.deleted_at IS NULL
    """
    
    params = []
    if filter_status:
        placeholders = ','.join(['%s'] * len(filter_status))
        companies_query += f" AND c.status IN ({placeholders})"
        params.extend(filter_status)
    
    if filter_sector:
        placeholders = ','.join(['%s'] * len(filter_sector))
        companies_query += f" AND c.sector IN ({placeholders})"
        params.extend(filter_sector)
    
    if search_query:
        companies_query += " AND (c.ticker ILIKE %s OR c.name ILIKE %s)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
    
    companies_query += " ORDER BY c.ticker"
    
    companies_df = query_db(companies_query, params if params else None)
    
    if not companies_df.empty:
        # Format display
        display_df = companies_df.copy()
        display_df['current_price'] = display_df['current_price'].apply(
            lambda x: f"₦{x:.2f}" if pd.notna(x) else "N/A"
        )
        display_df['last_price_update'] = pd.to_datetime(display_df['last_price_update']).dt.strftime('%Y-%m-%d')
        display_df['shares_owned'] = display_df['shares_owned'].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(
            display_df[['ticker', 'name', 'sector', 'status', 'registrar', 'current_price', 'shares_owned']],
            use_container_width=True,
            hide_index=True
        )
        
        st.caption(f"Showing {len(companies_df)} companies")
    else:
        st.info("No companies found matching filters")

# ============================================================================
# HOLDINGS PAGE
# ============================================================================

elif page == "💼 Holdings":
    st.title("Share Holdings")
    
    # Add new holding form
    with st.expander("➕ Add New Holding"):
        with st.form("add_holding_form"):
            # Get companies for dropdown
            companies = query_db("SELECT id, ticker, name FROM companies WHERE deleted_at IS NULL ORDER BY ticker")
            company_options = {f"{row['ticker']} - {row['name']}": row['id'] for _, row in companies.iterrows()}
            
            col1, col2 = st.columns(2)
            
            with col1:
                company_label = st.selectbox("Company*", [""] + list(company_options.keys()))
                num_shares = st.number_input("Number of Shares*", min_value=0.0, step=1.0, format="%.2f")
                purchase_date = st.date_input("Purchase Date*", value=datetime.now())
            
            with col2:
                purchase_price = st.number_input("Purchase Price per Share (₦)*", min_value=0.0, step=0.01, format="%.2f")
                certificate_num = st.text_input("Certificate Number")
                allocation_notes = st.text_area("Allocation Notes (e.g., 'For daughter's education')")
            
            submitted = st.form_submit_button("Add Holding")
            
            if submitted:
                if not company_label or num_shares <= 0 or purchase_price <= 0:
                    st.error("Please fill all required fields!")
                else:
                    company_id = company_options[company_label]
                    total_cost = num_shares * purchase_price
                    
                    # Insert holding
                    success1 = execute_db("""
                        INSERT INTO holdings (
                            company_id, num_shares, average_cost_basis, 
                            total_cost, certificate_number, allocation_notes
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """, (company_id, num_shares, purchase_price, total_cost, certificate_num or None, allocation_notes or None))
                    
                    # Also create buy transaction
                    success2 = execute_db("""
                        INSERT INTO transactions (
                            company_id, transaction_type, transaction_date,
                            num_shares, price_per_share, gross_amount, net_amount
                        ) VALUES (%s, 'buy', %s, %s, %s, %s, %s)
                    """, (company_id, purchase_date, num_shares, purchase_price, total_cost, total_cost))
                    
                    if success1 and success2:
                        st.success(f"✅ Added holding for {company_label}")
                        time.sleep(1)
                        st.rerun()
    
    st.markdown("---")
    
    # Holdings table with live calculations
    holdings_query = """
    SELECT 
        c.ticker,
        c.name,
        c.sector,
        h.num_shares,
        h.average_cost_basis,
        h.total_cost,
        c.current_price,
        (h.num_shares * COALESCE(c.current_price, 0)) as current_value,
        ((h.num_shares * COALESCE(c.current_price, 0)) - h.total_cost) as gain_loss,
        (((h.num_shares * COALESCE(c.current_price, 0)) - h.total_cost) / NULLIF(h.total_cost, 0) * 100) as return_pct,
        h.allocation_notes
    FROM holdings h
    JOIN companies c ON h.company_id = c.id
    WHERE h.deleted_at IS NULL AND c.deleted_at IS NULL
    ORDER BY current_value DESC
    """
    
    holdings_df = query_db(holdings_query)
    
    if not holdings_df.empty:
        # Format for display
        display_df = holdings_df.copy()
        display_df['num_shares'] = display_df['num_shares'].apply(lambda x: f"{x:,.2f}")
        display_df['average_cost_basis'] = display_df['average_cost_basis'].apply(lambda x: f"₦{x:.2f}")
        display_df['total_cost'] = display_df['total_cost'].apply(lambda x: f"₦{x:,.0f}")
        display_df['current_price'] = display_df['current_price'].apply(lambda x: f"₦{x:.2f}" if pd.notna(x) else "N/A")
        display_df['current_value'] = display_df['current_value'].apply(lambda x: f"₦{x:,.0f}")
        display_df['gain_loss'] = display_df['gain_loss'].apply(lambda x: f"₦{x:,.0f}")
        display_df['return_pct'] = display_df['return_pct'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
        
        st.dataframe(
            display_df[['ticker', 'name', 'num_shares', 'average_cost_basis', 'current_price', 
                       'current_value', 'gain_loss', 'return_pct']],
            use_container_width=True,
            hide_index=True
        )
        
        # Summary at bottom
        total_invested = holdings_df['total_cost'].sum()
        total_current = holdings_df['current_value'].sum()
        total_gain = total_current - total_invested
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Invested", f"₦{total_invested:,.0f}")
        col2.metric("Current Value", f"₦{total_current:,.0f}")
        col3.metric("Total Gain/Loss", f"₦{total_gain:,.0f}", f"{(total_gain/total_invested*100):.2f}%")
    else:
        st.info("No holdings yet. Add your first holding above!")

# ============================================================================
# TRANSACTIONS PAGE
# ============================================================================

elif page == "💰 Transactions":
    st.title("Transaction History")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        trans_type = st.multiselect("Transaction Type", 
            ["buy", "sell", "dividend", "stock_split", "bonus_issue", "rights_issue"])
    with col2:
        date_from = st.date_input("From Date", value=datetime.now() - timedelta(days=365))
    with col3:
        date_to = st.date_input("To Date", value=datetime.now())
    
    query = """
        SELECT 
            t.transaction_date,
            c.ticker,
            c.name,
            t.transaction_type,
            t.num_shares,
            t.price_per_share,
            t.net_amount,
            t.notes
        FROM transactions t
        JOIN companies c ON t.company_id = c.id
        WHERE t.deleted_at IS NULL
          AND t.transaction_date BETWEEN %s AND %s
    """
    params = [date_from, date_to]
    
    if trans_type:
        placeholders = ','.join(['%s'] * len(trans_type))
        query += f" AND t.transaction_type IN ({placeholders})"
        params.extend(trans_type)
    
    query += " ORDER BY t.transaction_date DESC LIMIT 100"
    
    transactions = query_db(query, params)
    
    if not transactions.empty:
        display_trans = transactions.copy()
        display_trans['transaction_date'] = pd.to_datetime(display_trans['transaction_date']).dt.strftime('%Y-%m-%d')
        display_trans['num_shares'] = display_trans['num_shares'].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "N/A")
        display_trans['price_per_share'] = display_trans['price_per_share'].apply(lambda x: f"₦{x:.2f}" if pd.notna(x) else "N/A")
        display_trans['net_amount'] = display_trans['net_amount'].apply(lambda x: f"₦{x:,.0f}" if pd.notna(x) else "N/A")
        
        st.dataframe(display_trans, use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(transactions)} transactions")
    else:
        st.info("No transactions found for selected filters")

# ============================================================================
# PRICE HISTORY PAGE
# ============================================================================

elif page == "📈 Price History":
    st.title("Price History")
    
    # Company selector
    companies = query_db("SELECT ticker, name FROM companies WHERE deleted_at IS NULL ORDER BY ticker")
    if not companies.empty:
        company_options = {f"{row['ticker']} - {row['name']}": row['ticker'] for _, row in companies.iterrows()}
        
        selected_company = st.selectbox("Select Company", list(company_options.keys()))
        
        if selected_company:
            ticker = company_options[selected_company]
            
            # Date range
            col1, col2 = st.columns(2)
            with col1:
                days_back = st.selectbox("Time Period", [30, 90, 180, 365], format_func=lambda x: f"Last {x} days")
            
            price_history = query_db("""
                SELECT 
                    price_date,
                    close_price
                FROM price_history ph
                JOIN companies c ON ph.company_id = c.id
                WHERE c.ticker = %s
                  AND ph.price_date >= CURRENT_DATE - (%s * INTERVAL '1 day')
                ORDER BY price_date DESC
            """, (ticker, days_back))
            
            if not price_history.empty:
                sorted_history = price_history.sort_values('price_date')
                
                fig = px.line(
                    sorted_history,
                    x='price_date',
                    y='close_price',
                    title=f"{selected_company} - Price History",
                    labels={'close_price': 'Price (₦)', 'price_date': 'Date'}
                )
                fig.update_traces(line_color='#667eea', line_width=2)
                fig.update_layout(hovermode='x unified', height=500)
                st.plotly_chart(fig, use_container_width=True)
                
                # Stats
                latest_price = sorted_history.iloc[-1]['close_price']
                oldest_price = sorted_history.iloc[0]['close_price']
                price_change = latest_price - oldest_price
                price_change_pct = (price_change / oldest_price * 100) if oldest_price > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Current Price", f"₦{latest_price:.2f}")
                col2.metric("Period Change", f"₦{price_change:.2f}", f"{price_change_pct:.2f}%")
                col3.metric("Data Points", len(sorted_history))
                
                st.markdown("---")
                
                # Data table
                st.subheader("Historical Data")
                display_history = price_history.copy()
                display_history['price_date'] = pd.to_datetime(display_history['price_date']).dt.strftime('%Y-%m-%d')
                display_history['close_price'] = display_history['close_price'].apply(lambda x: f"₦{x:.2f}")
                st.dataframe(display_history, use_container_width=True, hide_index=True)
            else:
                st.info("No price history available for this company")
    else:
        st.info("No companies available. Add companies first!")

# ============================================================================
# DIVIDENDS PAGE
# ============================================================================

elif page == "💸 Dividends":
    st.title("Dividend Tracker")
    
    # Add dividend form
    with st.expander("➕ Record Dividend"):
        with st.form("add_dividend_form"):
            companies = query_db("SELECT id, ticker, name FROM companies WHERE deleted_at IS NULL ORDER BY ticker")
            company_options = {f"{row['ticker']} - {row['name']}": row['id'] for _, row in companies.iterrows()}
            
            col1, col2 = st.columns(2)
            
            with col1:
                company_label = st.selectbox("Company*", [""] + list(company_options.keys()))
                payment_date = st.date_input("Payment Date*", value=datetime.now())
                amount_per_share = st.number_input("Amount per Share (₦)*", min_value=0.0, step=0.01, format="%.4f")
            
            with col2:
                # Get shares held
                shares_held = st.number_input("Shares Held at Ex-Dividend Date", min_value=0.0, step=1.0)
                status = st.selectbox("Status", ["declared", "pending", "paid", "cancelled"])
                
            notes = st.text_area("Notes")
            
            submitted = st.form_submit_button("Record Dividend")
            
            if submitted and company_label and amount_per_share > 0:
                company_id = company_options[company_label]
                gross_amount = shares_held * amount_per_share if shares_held > 0 else 0
                tax_withheld = gross_amount * 0.10  # 10% WHT
                net_amount = gross_amount - tax_withheld
                
                success = execute_db("""
                    INSERT INTO dividends (
                        company_id, payment_date, amount_per_share, shares_held,
                        gross_amount, tax_withheld, net_amount, status, notes
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (company_id, payment_date, amount_per_share, shares_held or None,
                      gross_amount, tax_withheld, net_amount, status, notes or None))
                
                if success:
                    st.success(f"✅ Recorded dividend for {company_label}")
                    time.sleep(1)
                    st.rerun()
    
    st.markdown("---")
    
    # Dividend history
    dividends = query_db("""
        SELECT 
            d.payment_date,
            c.ticker,
            c.name,
            d.amount_per_share,
            d.shares_held,
            d.gross_amount,
            d.tax_withheld,
            d.net_amount,
            d.status
        FROM dividends d
        JOIN companies c ON d.company_id = c.id
        WHERE d.deleted_at IS NULL
        ORDER BY d.payment_date DESC
        LIMIT 50
    """)
    
    if not dividends.empty:
        display_div = dividends.copy()
        display_div['payment_date'] = pd.to_datetime(display_div['payment_date']).dt.strftime('%Y-%m-%d')
        display_div['amount_per_share'] = display_div['amount_per_share'].apply(lambda x: f"₦{x:.4f}")
        display_div['gross_amount'] = display_div['gross_amount'].apply(lambda x: f"₦{x:,.2f}" if pd.notna(x) else "N/A")
        display_div['net_amount'] = display_div['net_amount'].apply(lambda x: f"₦{x:,.2f}" if pd.notna(x) else "N/A")
        
        st.dataframe(display_div, use_container_width=True, hide_index=True)
    else:
        st.info("No dividends recorded yet")

# ============================================================================
# REGISTRARS PAGE
# ============================================================================

elif page == "👥 Registrars":
    st.title("Registrars CRM")
    
    # Add registrar
    with st.expander("➕ Add Registrar"):
        with st.form("add_registrar_form"):
            col1, col2 = st.columns(2)
            with col1:
                reg_name = st.text_input("Name*")
                reg_email = st.text_input("Email")
                reg_phone = st.text_input("Phone")
            with col2:
                reg_address = st.text_area("Address")
                reg_website = st.text_input("Website")
                reg_rating = st.slider("Response Rating", 1, 5, 3)
            
            submitted = st.form_submit_button("Add Registrar")
            if submitted and reg_name:
                execute_db("""
                    INSERT INTO registrars (name, email, phone, address, website, response_rating)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (reg_name, reg_email or None, reg_phone or None, reg_address or None, reg_website or None, reg_rating))
                st.success(f"✅ Added {reg_name}")
                time.sleep(1)
                st.rerun()
    
    st.markdown("---")
    
    registrars = query_db("""
        SELECT 
            r.name,
            r.email,
            r.phone,
            r.response_rating,
            COUNT(c.id) as num_companies
        FROM registrars r
        LEFT JOIN companies c ON r.id = c.registrar_id AND c.deleted_at IS NULL
        WHERE r.deleted_at IS NULL
        GROUP BY r.id, r.name, r.email, r.phone, r.response_rating
        ORDER BY r.name
    """)
    
    if not registrars.empty:
        st.dataframe(registrars, use_container_width=True, hide_index=True)
    else:
        st.info("No registrars added yet")

# ============================================================================
# COMMUNICATIONS PAGE
# ============================================================================

elif page == "💬 Communications":
    st.title("Communication Logs")
    
    # Add communication
    with st.expander("➕ Log Communication"):
        with st.form("add_comm_form"):
            col1, col2 = st.columns(2)
            with col1:
                entity_type = st.selectbox("Entity Type", ["registrar", "company", "sec", "ngx", "other"])
                comm_type = st.selectbox("Communication Type", ["email", "phone", "in_person", "letter"])
                comm_date = st.date_input("Date", value=datetime.now())
            with col2:
                contact_person = st.text_input("Contact Person")
                priority = st.selectbox("Priority", ["low", "medium", "high"])
                follow_up_date = st.date_input("Follow-up Date", value=datetime.now() + timedelta(days=7))
            
            summary = st.text_area("Summary*")
            next_action = st.text_area("Next Action")
            
            submitted = st.form_submit_button("Log Communication")
            if submitted and summary:
                execute_db("""
                    INSERT INTO communication_logs (
                        entity_type, communication_type, communication_date,
                        contact_person, summary, priority, follow_up_date, next_action, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'open')
                """, (entity_type, comm_type, comm_date, contact_person or None, summary, 
                      priority, follow_up_date, next_action or None))
                st.success("✅ Communication logged")
                time.sleep(1)
                st.rerun()
    
    st.markdown("---")
    
    # Filter
    status_filter = st.multiselect("Status", ["open", "pending", "resolved", "escalated"], default=["open", "pending"])
    
    query = """
        SELECT 
            communication_date,
            entity_type,
            communication_type,
            summary,
            status,
            priority,
            follow_up_date,
            contact_person
        FROM communication_logs
        WHERE deleted_at IS NULL
    """
    params = []
    if status_filter:
        placeholders = ','.join(['%s'] * len(status_filter))
        query += f" AND status IN ({placeholders})"
        params.extend(status_filter)
    
    query += " ORDER BY communication_date DESC LIMIT 50"
    
    comms = query_db(query, params if params else None)
    
    if not comms.empty:
        display_comms = comms.copy()
        display_comms['communication_date'] = pd.to_datetime(display_comms['communication_date']).dt.strftime('%Y-%m-%d')
        display_comms['follow_up_date'] = pd.to_datetime(display_comms['follow_up_date']).dt.strftime('%Y-%m-%d')
        st.dataframe(display_comms, use_container_width=True, hide_index=True)
    else:
        st.info("No communication logs yet")

# ============================================================================
# REPORTS PAGE
# ============================================================================

elif page == "📊 Reports":
    st.title("Portfolio Reports")
    
    report_type = st.selectbox("Select Report", 
        ["Weekly Valuation", "Performance Analysis", "Dividend Summary", "Tax Summary"])
    
    if report_type == "Weekly Valuation":
        st.subheader("Weekly Portfolio Valuation")
        
        # Current summary
        summary = query_db("""
            SELECT 
                COALESCE(SUM(h.total_cost), 0) as total_invested,
                COALESCE(SUM(h.num_shares * COALESCE(c.current_price, 0)), 0) as current_value,
                COALESCE(SUM((h.num_shares * COALESCE(c.current_price, 0)) - h.total_cost), 0) as unrealized_gain_loss
            FROM holdings h
            JOIN companies c ON h.company_id = c.id
            WHERE h.deleted_at IS NULL
        """)
        
        if not summary.empty:
            row = summary.iloc[0]
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Invested", f"₦{row['total_invested'] or 0:,.0f}")
            col2.metric("Current Value", f"₦{row['current_value'] or 0:,.0f}")
            col3.metric("Total Gain/Loss", f"₦{row['unrealized_gain_loss'] or 0:,.0f}")
        
        st.markdown("---")
        
        # Holdings breakdown
        holdings = query_db("""
            SELECT 
                c.ticker, c.name, c.sector,
                h.num_shares,
                c.current_price,
                (h.num_shares * COALESCE(c.current_price, 0)) as current_value,
                h.total_cost,
                ((h.num_shares * COALESCE(c.current_price, 0)) - h.total_cost) as gain_loss
            FROM holdings h
            JOIN companies c ON h.company_id = c.id
            WHERE h.deleted_at IS NULL
            ORDER BY current_value DESC
        """)
        
        if not holdings.empty:
            st.dataframe(holdings, use_container_width=True, hide_index=True)
            
            csv = holdings.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"portfolio_valuation_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    elif report_type == "Performance Analysis":
        st.subheader("Portfolio Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🚀 Top 5 Performers")
            top = query_db("""
                SELECT 
                    c.ticker, c.name,
                    h.average_cost_basis as avg_cost,
                    c.current_price,
                    (((c.current_price - h.average_cost_basis) / NULLIF(h.average_cost_basis, 0)) * 100) as return_pct
                FROM holdings h
                JOIN companies c ON h.company_id = c.id
                WHERE h.deleted_at IS NULL AND c.current_price IS NOT NULL
                ORDER BY return_pct DESC LIMIT 5
            """)
            
            if not top.empty:
                for _, row in top.iterrows():
                    st.markdown(f"**{row['ticker']}** - {row['name']}")
                    st.markdown(f"<span class='gain'>+{row['return_pct']:.2f}%</span>", unsafe_allow_html=True)
                    st.caption(f"₦{row['avg_cost']:.2f} → ₦{row['current_price']:.2f}")
                    st.markdown("---")
        
        with col2:
            st.markdown("### 📉 Bottom 5 Performers")
            bottom = query_db("""
                SELECT 
                    c.ticker, c.name,
                    h.average_cost_basis as avg_cost,
                    c.current_price,
                    (((c.current_price - h.average_cost_basis) / NULLIF(h.average_cost_basis, 0)) * 100) as return_pct
                FROM holdings h
                JOIN companies c ON h.company_id = c.id
                WHERE h.deleted_at IS NULL AND c.current_price IS NOT NULL
                ORDER BY return_pct ASC LIMIT 5
            """)
            
            if not bottom.empty:
                for _, row in bottom.iterrows():
                    st.markdown(f"**{row['ticker']}** - {row['name']}")
                    st.markdown(f"<span class='loss'>{row['return_pct']:.2f}%</span>", unsafe_allow_html=True)
                    st.caption(f"₦{row['avg_cost']:.2f} → ₦{row['current_price']:.2f}")
                    st.markdown("---")
    
    elif report_type == "Dividend Summary":
        st.subheader("Dividend Income Summary")
        
        years = query_db("SELECT DISTINCT EXTRACT(YEAR FROM payment_date) as year FROM dividends ORDER BY year DESC")
        selected_year = st.selectbox("Year", years['year'].tolist() if not years.empty else [datetime.now().year])
        
        div_summary = query_db("""
            SELECT 
                c.ticker, c.name,
                COUNT(*) as num_payments,
                SUM(d.gross_amount) as total_gross,
                SUM(d.tax_withheld) as total_tax,
                SUM(d.net_amount) as total_net
            FROM dividends d
            JOIN companies c ON d.company_id = c.id
            WHERE EXTRACT(YEAR FROM d.payment_date) = %s
              AND d.status = 'paid' AND d.deleted_at IS NULL
            GROUP BY c.ticker, c.name
            ORDER BY total_net DESC
        """, (int(selected_year),))
        
        if not div_summary.empty:
            totals = div_summary[['total_gross', 'total_tax', 'total_net']].sum()
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Gross", f"₦{totals['total_gross']:,.2f}")
            col2.metric("Total Tax", f"₦{totals['total_tax']:,.2f}")
            col3.metric("Total Net", f"₦{totals['total_net']:,.2f}")
            
            st.dataframe(div_summary, use_container_width=True, hide_index=True)
        else:
            st.info(f"No dividend payments for {selected_year}")
    
    elif report_type == "Tax Summary":
        st.subheader("Tax Summary Report")
        
        tax_year = st.selectbox("Tax Year", range(datetime.now().year, datetime.now().year - 5, -1))
        
        # Dividends
        div_tax = query_db("""
            SELECT 
                SUM(gross_amount) as total_dividend_gross,
                SUM(tax_withheld) as total_wht,
                SUM(net_amount) as total_dividend_net
            FROM dividends
            WHERE EXTRACT(YEAR FROM payment_date) = %s
              AND status = 'paid' AND deleted_at IS NULL
        """, (tax_year,))
        
        if not div_tax.empty and div_tax.iloc[0]['total_dividend_gross']:
            st.markdown("#### Dividend Income")
            col1, col2, col3 = st.columns(3)
            col1.metric("Gross", f"₦{div_tax.iloc[0]['total_dividend_gross']:,.2f}")
            col2.metric("WHT (10%)", f"₦{div_tax.iloc[0]['total_wht']:,.2f}")
            col3.metric("Net", f"₦{div_tax.iloc[0]['total_dividend_net']:,.2f}")
        
        st.markdown("---")
        
        # Capital gains
        cap_gains = query_db("""
            SELECT 
                c.ticker, t.transaction_date, t.num_shares,
                t.price_per_share as sale_price,
                h.average_cost_basis,
                (t.price_per_share - h.average_cost_basis) * t.num_shares as capital_gain
            FROM transactions t
            JOIN companies c ON t.company_id = c.id
            LEFT JOIN holdings h ON t.company_id = h.company_id AND h.deleted_at IS NULL
            WHERE t.transaction_type = 'sell'
              AND EXTRACT(YEAR FROM t.transaction_date) = %s
              AND t.deleted_at IS NULL
        """, (tax_year,))
        
        if not cap_gains.empty:
            st.markdown("#### Realized Capital Gains")
            st.dataframe(cap_gains, use_container_width=True, hide_index=True)
            st.metric("Total Capital Gains", f"₦{cap_gains['capital_gain'].sum():,.2f}")
        else:
            st.info("No realized capital gains this year")

# ============================================================================
# SETTINGS PAGE
# ============================================================================

elif page == "⚙️ Settings":
    st.title("Settings & Data Management")
    
    tab1, tab2, tab3 = st.tabs(["📥 Import Data", "🔄 Price Scraper", "🗄️ Database"])
    
    with tab1:
        st.subheader("Import from Obsidian")
        
        st.markdown("""
        The mounted Obsidian vault (`NigerianStocks/`) is automatically available to the import script.
        Click the button below to sync all companies, holdings, and dividends from your vault.
        
        **Vault path inside container**: `/app/NigerianStocks`
        
        Alternatively, upload individual markdown files:
        ```markdown
        # Company Name
        - Ticker: GTCO
        - Sector: Banking
        - Shares: 5000
        - Purchase Date: 2020-03-15
        - Purchase Price: 25.50
        ```
        """)
        
        # Primary: Import from mounted Obsidian vault
        vault_path = "/app/NigerianStocks"
        if os.path.exists(vault_path) and os.listdir(vault_path):
            st.info(f"📁 Vault mounted — found files in `{vault_path}`")
            if st.button("🚀 Import from Obsidian Vault"):
                with st.spinner("Importing from NigerianStocks vault..."):
                    try:
                        result = subprocess.run(
                            ["python3", "scripts/import_obsidian.py", vault_path],
                            capture_output=True,
                            text=True,
                            timeout=120
                        )
                        if result.returncode == 0:
                            st.success("✅ Import complete!")
                            with st.expander("📋 View Import Log"):
                                st.text(result.stdout)
                        else:
                            st.error("❌ Import failed")
                            with st.expander("🔍 Error Details"):
                                st.code(result.stderr)
                    except subprocess.TimeoutExpired:
                        st.error("❌ Import timed out after 2 minutes")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ NigerianStocks vault not found or empty at `/app/NigerianStocks`")
        
        st.markdown("---")
        st.subheader("Upload Individual Files")
        uploaded_files = st.file_uploader("Upload Markdown Files", accept_multiple_files=True, type=['md'])
        
        if uploaded_files and st.button("🚀 Import Uploaded Files"):
            with st.spinner("Importing..."):
                import tempfile, pathlib
                with tempfile.TemporaryDirectory() as tmpdir:
                    for f in uploaded_files:
                        pathlib.Path(tmpdir, f.name).write_bytes(f.read())
                    result = subprocess.run(
                        ["python3", "scripts/import_obsidian.py", tmpdir],
                        capture_output=True, text=True, timeout=60
                    )
                    if result.returncode == 0:
                        st.success(f"✅ Imported {len(uploaded_files)} files")
                        with st.expander("📋 View Import Log"):
                            st.text(result.stdout)
                    else:
                        st.error("❌ Import failed")
                        with st.expander("🔍 Error Details"):
                            st.code(result.stderr)
    
    with tab2:
        st.subheader("Price Scraper")
        
        # Status banner — honest about current state
        st.warning("""
        ⚠️ **EODHD Scraper currently returns HTTP 402** for Nigerian Exchange (XNSA) tickers.
        The EODHD free tier does not include the XNSA exchange. A paid plan ($19.99/mo) is required.

        **Workaround in progress**: Manual price entry UI will be added in Phase 2.
        """)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("**EODHD Scraper** *(requires paid plan for NGX data)*")
            if st.button("✨ Run EODHD Scraper", help="Will fail with 402 until paid plan is activated"):
                with st.spinner("Fetching prices from EODHD.com..."):
                    try:
                        result = subprocess.run(
                            ["python3", "scripts/eodhd_scraper.py"],
                            capture_output=True,
                            text=True,
                            timeout=300
                        )
                        
                        if result.returncode == 0:
                            output_lines = result.stdout.split('\n')
                            summary_line = [line for line in output_lines if 'Summary:' in line]
                            
                            if summary_line:
                                st.success(f"✅ {summary_line[0].split('INFO - ')[-1]}")
                            else:
                                st.success("✅ EODHD Scraper completed successfully!")
                            
                            with st.expander("📋 View Details"):
                                recent_updates = [line for line in output_lines if '✅' in line][-10:]
                                for line in recent_updates:
                                    if 'INFO - ✅' in line:
                                        st.text(line.split('INFO - ')[-1])
                        else:
                            st.error(f"❌ Scraper failed with error code {result.returncode}")
                            with st.expander("🔍 Error Details"):
                                st.code(result.stderr[-2000:])  # Show last 2000 chars only
                                
                    except subprocess.TimeoutExpired:
                        st.error("❌ Scraper timed out after 5 minutes")
                    except Exception as e:
                        st.error(f"❌ Error running scraper: {str(e)}")
        
        with col2:
            st.markdown("**Deprecated Scrapers**")
            st.error("🚧 NGX Scraper — disabled (anti-bot)")
            st.error("🚧 RapidAPI Scraper — disabled (no NGX support)")
        
        st.markdown("---")
        
        logs = query_db("""
            SELECT 
                DATE(created_at) as date,
                source,
                COUNT(*) as prices_updated,
                MAX(created_at) as last_update
            FROM price_history
            GROUP BY DATE(created_at), source
            ORDER BY date DESC
            LIMIT 10
        """)
        
        if not logs.empty:
            st.dataframe(logs, use_container_width=True, hide_index=True)
    
    with tab3:
        st.subheader("Database Operations")
        
        if st.button("📊 Database Stats"):
            stats = query_db("""
                SELECT 'Companies' as table_name, COUNT(*) as records FROM companies WHERE deleted_at IS NULL
                UNION ALL SELECT 'Holdings', COUNT(*) FROM holdings WHERE deleted_at IS NULL
                UNION ALL SELECT 'Transactions', COUNT(*) FROM transactions WHERE deleted_at IS NULL
                UNION ALL SELECT 'Dividends', COUNT(*) FROM dividends WHERE deleted_at IS NULL
                UNION ALL SELECT 'Price History', COUNT(*) FROM price_history
            """)
            st.dataframe(stats, use_container_width=True, hide_index=True)

# ============================================================================
# FOOTER
# ============================================================================

st.sidebar.markdown("---")
st.sidebar.caption("Estate Portfolio Manager v1.0")
st.sidebar.caption("Built with Streamlit 🎈")
