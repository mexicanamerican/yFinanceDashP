from functions import *
from contact import contact_form
from streamlit_javascript import st_javascript
from zoneinfo import ZoneInfo

@st.dialog("Contact Me")
def show_contact_form():
    contact_form()

st.set_page_config(
    page_title="Commodities", # The page title, shown in the browser tab.
    page_icon=":material/oil_barrel:",
    layout="wide", # How the page content should be laid out.
    initial_sidebar_state="auto", # How the sidebar should start out.
    menu_items={ # Configure the menu that appears on the top-right side of this app.
        "Get help": "https://github.com/LMAPcoder" # The URL this menu item should point to.
    }
)

# ----LOGO----
st.html("""
  <style>
    [alt=Logo] {
      height: 3rem;
      width: auto;
      padding-left: 1rem;
    }
  </style>
""")

# ----TIME ZONE----
if 'timezone' not in st.session_state:
    timezone = st_javascript("""await (async () => {
                    const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                    return userTimezone
                    })().then(returnValue => returnValue)""")
    if isinstance(timezone, int):
        st.stop()
    st.session_state['timezone'] = ZoneInfo(timezone)

# ----SESSION STATE -----
all_my_widget_keys_to_keep = {
    'current_time_commodity_page': datetime.datetime.now(st.session_state['timezone']).replace(microsecond=0, tzinfo=None),
    'tickers': "MSFT",
    'dark_mode': False,
    'toggle_theme': False,
    'financial_period': "Annual"
}

for key in all_my_widget_keys_to_keep:
    if key not in st.session_state:
        st.session_state[key] = all_my_widget_keys_to_keep[key]

for key in all_my_widget_keys_to_keep:
    st.session_state[key] = st.session_state[key]

# ---- SIDEBAR ----
with st.sidebar:
    commodities = {
        'West Texas Intermediate': 'CL=F',
        'Brent': 'BZ=F',
        'Natural Gas': 'NG=F',
        'Copper': 'HG=F',
        'Gold': 'GC=F',
        'Silver': 'SI=F',
        'Soybean': 'ZS=F',
        'Wheat': 'KE=F',
        'Corn': 'ZC=F',
        'Cotton': 'CT=F',
        'Sugar': 'SB=F',
        'Coffee': 'KC=F'
    }

    option = st.selectbox(
        label="Commodity",
        options=list(commodities.keys()),
        index=0,
        placeholder="Select commodity...",
    )

    COMMODITY = commodities[option]

    st.write(COMMODITY)

    periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]

    PERIOD = st.selectbox(
        label="Period",
        options=periods,
        index=3,
        placeholder="Select period...",
    )

    intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

    if PERIOD in intervals:
        idx = intervals.index(PERIOD)
        intervals = intervals[:idx]

    INTERVAL = st.selectbox(
        label="Interval",
        options=intervals,
        index=len(intervals) - 4,
        placeholder="Select interval...",
    )

    TOGGLE_VOL = st.toggle(
        label="Volume",
        value=True
    )

    indicator_list = ['SMA_20', 'SMA_50', 'SMA_200', 'SMA_X', 'EMA_20', 'EMA_50', 'EMA_200', 'EMA_X', 'ATR', 'MACD', 'RSI']

    INDICATORS = st.multiselect(
        label="Technical indicators:",
        options=indicator_list
    )

    if 'SMA_X' in INDICATORS or 'EMA_X' in INDICATORS:
        TIME_SPAN = st.slider(
            label="Select time span:",
            min_value=10,  # The minimum permitted value.
            max_value=200,  # The maximum permitted value.
            value=30  # The value of the slider when it first renders.
        )
        INDICATORS = [indicator.replace("X", str(TIME_SPAN)) if '_X' in indicator else indicator for indicator in INDICATORS]

    st.write("")
    button = st.button("Refresh data")

    if button:
        st.session_state['current_time_commodity_page'] = datetime.datetime.now(st.session_state['timezone']).replace(microsecond=0, tzinfo=None)
        fetch_table.clear()
        fetch_info.clear()
        fetch_history.clear()
        # st.cache_data.clear()

    st.write("Last update:", st.session_state['current_time_commodity_page'])

    st.sidebar.markdown("Made with ❤️ by Leonardo")
    button = st.button("✉️ Contact Me", key="contact")

    if button:
        show_contact_form()

    # ----CREDIT----
    st.write("")
    st.write("")
    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.markdown("<p style='text-align: right;'>Powered by:</p>", unsafe_allow_html=True)
    with col2:
        st.image("imgs/logo_yahoo_lightpurple.svg", width=100)


# ---- MAINPAGE ----

st.title("Commodity Market")

#----FIRST SECTION----




URL = "https://finance.yahoo.com/markets/commodities/"

df = fetch_table(URL)

COMMODITIES = ["GC=F", "SI=F", "HG=F", "NG=F", "BZ=F", "KC=F", "KE=F", "ZS=F"]

st.subheader("Top Commodities")
if isinstance(df, Exception):
    st.error(df)
    fetch_table.clear(URL)
else:
    with st.container(border=True):
        i = 0
        for _ in range(2):
            cols = st.columns(4, gap="small")
            for col in cols:
                with col:
                    row = df[df['Symbol'] == COMMODITIES[i]].iloc[0]
                    name = row['Name']
                    symbol = row['Symbol']
                    price, change, change_pt = row['Price'].split()
                    st.metric(
                        label=f'{name}',
                        value=f'{price}',
                        delta=f'{change} {change_pt}'
                    )
                i += 1

#----SECOND SECTION----

TITLE = f'Commodity: {option}'

st.header(TITLE)

# info = fetch_info(COMMODITY)

hist = fetch_history(COMMODITY, period=PERIOD, interval=INTERVAL)
if isinstance(hist, Exception):
    st.error(hist)
    fetch_history.clear(COMMODITY, period=PERIOD, interval=INTERVAL)
    st.stop()

df = hist.copy()

if not TOGGLE_VOL:
    df = df.drop(columns=['Volume'], axis=1)
else:
    df['ΔVolume%'] = df['Volume'].pct_change(periods=1) * 100
    df['ΔVolume%'] = df['ΔVolume%'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else None)

for INDICATOR in INDICATORS:
    if "SMA" in INDICATOR:
        window = int(INDICATOR.split("_")[1])
        df[INDICATOR] = df['Close'].rolling(window=window, min_periods=1).mean()
    if "EMA" in INDICATOR:
        window = int(INDICATOR.split("_")[1])
        df[INDICATOR] = df['Close'].ewm(span=window, adjust=False, min_periods=1).mean()

if "ATR" in INDICATORS:

    Prev_Close = df['Close'].shift(1)
    High_Low = df['High'] - df['Low']
    High_PrevClose = abs(df['High'] - Prev_Close)
    Low_PrevClose = abs(df['Low'] - Prev_Close)

    df['TR'] = pd.concat([High_Low, High_PrevClose, Low_PrevClose], axis=1).max(axis=1)

    df['ATR'] = df['TR'].rolling(window=14, min_periods=1).mean()

    df = df.drop(columns=['TR'], axis=1)

if "MACD" in INDICATORS:

    ema_short = df['Close'].ewm(span=12, adjust=False, min_periods=1).mean()
    ema_long = df['Close'].ewm(span=26, adjust=False, min_periods=1).mean()
    df['MACD'] = ema_short - ema_long
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False, min_periods=1).mean()
    df['MACD_Hist'] = df['MACD'] - df['Signal']

if "RSI" in INDICATORS:

    # delta = df['Close'].diff()
    delta = df['Close'].pct_change(periods=1) * 100

    # Separate gains and losses
    gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()

    # Calculate the relative strength (RS)
    rs = gain / loss

    df['RSI'] = 100 - (100 / (1 + rs))

fig = plot_candles_stick_bar(df, "Candlestick Chart")

st.plotly_chart(fig, use_container_width=True)

with st.expander("Show data"):
    st.dataframe(
        data=df.reset_index(),
        hide_index=True
    )
