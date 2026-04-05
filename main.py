import streamlit as st
import pandas as pd
import requests

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

st.title("TariffDash- A Tariff Analysis Dashboard")
select_country = st.selectbox("Select a country's tariff to analyze", ["USA", "Japan", "Mexico"])
st.write(f"You selected {select_country} for analysis.")
select_year = st.selectbox("Select a year for tariff data", ["2020", "2021", "2022"])

if select_country == "USA":
    #change this URL to the actual API endpoint for USA tariff data
    response = requests.get("https://wits.worldbank.org/API/V1/SDMX/V21/datasource/tradestats-tariff/reporter/usa/year/2022/partner/WLD/product/all/indicator/AHS-SMPL-AVRG?format=JSON")
    response_body = response.json()
    st.write("USA Tariff Data:")

    tariff_stats = atr_and_top_3_tr(response_body)
    st.metric(label=f"Average Tariff Rate for {select_country}", value=f"{tariff_stats[0]}%")
    top_3_tr_categories = tariff_stats[1]
    top_3_tr_df = pd.DataFrame(top_3_tr_categories)
    st.write("Top 3 Tariff Rates and Categories:")
    st.dataframe(top_3_tr_df)

# if __name__ == "__main__":

