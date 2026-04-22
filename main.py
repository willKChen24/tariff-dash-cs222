import streamlit as st
import pandas as pd
import requests

#globals
country_codes = { #country codes (values) must be lowercase for API endpoint
    "US" : "usa",
    "China" : "chn",
    "European Union" : "deu",
    "Japan" : "jpn",
    "Canada" : "can"
}

#basic dashboard functions
def atr_and_top_3_tr(json_response):
    tariff_series = json_response['dataSets'][0]['series']
    tariff_rates = []

    for dim in json_response['structure']['dimensions']['series']:
        if dim['id'] == 'PRODUCTCODE': #isolate the product code
            product_categories = dim['values'] #this is a list of dicts with id and name
            #product_categories looks something like this:
          #{
              #"id": "84-85_MachElec",
              #"name": "Mach and Elec"
           #}
            break

    for key, entry in tariff_series.items():
        #IMPORTANT- key = FREQ : REPORTER : PARTNER : PRODUCTCODE : INDICATOR
        rate = entry["observations"]["0"][0]
        parts = key.split(':')
        category_idx = int(parts[3]) #gets PRODUCTCODE
        tariff_rates.append((rate, category_idx))

    #obtain the top 3 highest tariff rates
    tariff_rates_sorted = sorted(tariff_rates, reverse=True) #sort in descending order
    top_3_tr = tariff_rates_sorted[:3] #get the first 3 tariff rates
    atr = round((sum(t[0] for t in tariff_rates)/len(tariff_rates)), 2)
    #obtain the respective categories for the top 3 highest tariff rates
    top_3_tr_categories = []
    for rate, idx in top_3_tr:
        category_code = product_categories[idx]["id"]
        top_3_tr_categories.append({"Tariff Rate (%)" : round(rate, 2), "Category" : category_code})

    return atr, top_3_tr_categories

#UI contents

st.title("TariffDash- A Tariff Analysis Dashboard")
select_country = st.selectbox("Select a country's tariff to analyze", ["US", "China", "European Union", "Japan", "Canada"])
country_code = country_codes[select_country]
st.write(f"You selected {select_country} for analysis.")
select_year = st.selectbox("Select a year for tariff data", ["2016", "2017", "2018", "2019", "2020", "2021", "2022"])

response = requests.get(f"https://wits.worldbank.org/API/V1/SDMX/V21/datasource/tradestats-tariff/reporter/{country_code}/year/{select_year}/partner/WLD/product/all/indicator/AHS-SMPL-AVRG?format=JSON")
print(f"Status: {response.status_code}")
response_body = response.json()
print(response)

tariff_stats = atr_and_top_3_tr(response_body)
st.metric(label=f"Average Tariff Rate for {select_country}", value=f"{tariff_stats[0]}%")
top_3_tr_categories = tariff_stats[1]
top_3_tr_df = pd.DataFrame(top_3_tr_categories)
st.write("Top 3 Tariff Rates and Categories:")
st.dataframe(top_3_tr_df)

#chatbot logic
st.title("TariffBot- Statistical Prediction Chatbot")

#initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

#display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Say something")
if prompt:
    #display the user's message in the chat container
    st.chat_message("user").markdown(prompt)
    
    #add user's message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    #respond the user's message (WIP)
    bot_response = "Hello! How may I assist you today?"

    #display the bot response in the chat container
    with st.chat_message("assistant"):
        st.markdown(bot_response)
    st.session_state.messages.append({"role" : "assistant", "content" : bot_response})

