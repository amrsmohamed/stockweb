import yfinance as yf
import streamlit as st
from datetime import date
from fbprophet import Prophet
from fbprophet.plot import plot_plotly
from plotly import graph_objs as go

@st.cache
def load_data(ticker, START, TODAY):
    stock = yf.Ticker(ticker)
    #data = yf.download(ticker, START, TODAY)
    data = stock.history(start=START, end=TODAY)
    try:
        shortName = stock.info['shortName']
    except:
        shortName = selected_stock
    data.reset_index(inplace=True)
    return data, shortName


def plot_raw_data(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name='stock_open'))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='stock_close'))
    fig.layout.update(title_text = "Time series data", xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)


def gostock(selected_stock):
    START = "2015-01-01"
    TODAY = date.today().strftime("%Y-%m-%d")
    #st.write("<style>red{color:red} orange{color:orange}....</style>")
    #data_load_state = st.write("Load data for <*font color=‘red’>" + selected_stock + "</*font> ...", unsafe_allow_html=True)
    data_load_state = st.write("Load data for " + selected_stock + " ...",
                               unsafe_allow_html=True)
    data, shortName = load_data(selected_stock, START, TODAY)
    if(len(data)<4):
        data_load_state = st.error("Loading data ... Error: stock or index not found")
        return
    else:
        data_load_state = st.success("Loading data for " + shortName + " ... done!")
    st.subheader('Raw data')
    st.write(data.tail())

    plot_raw_data(data)

    #forecasting
    df_train = data[['Date', 'Close']]
    df_train = df_train.rename (columns={"Date": "ds", "Close": "y"})
    st.subheader("Analyzing data for " + shortName + ", please wait....")
    m = Prophet()
    m.fit(df_train)
    future = m.make_future_dataframe(periods = period)
    forecast = m.predict(future)
    #forecast = forecast.rename (columns={"ds": "Date", "y" : "Price($)"})
    st.success('Forecast data for ' + shortName)
    st.write(forecast.tail())

    st.write('Forecast data, you can interact with the graph below using the slider to adjust the dates')
    fig1 = plot_plotly(m, forecast, xlabel='Date', ylabel='Price ($)')
    st.plotly_chart(fig1)

    st.success('Forecast components showing the seasonablity of the data')
    fig2 = m.plot_components(forecast)
    st.write(fig2)



st.title("Stock Prediction")
#stocks = ("AAPL", "GOOG", "MSFT", "TSLA")
st.subheader('Usage:- Please, type the name of the stock or the index in the textbox below, slide the scale to adjust the forcasting days, and then click on the Go button')
selected_stock = st.text_input("Write the name of the stock", "^IXIC")

n_days = st.slider("Days of prediction: ", 1, 365, 100)
period = n_days
if st.button("Go"):
    gostock(selected_stock)



