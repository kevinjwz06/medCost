import streamlit as st
import csv
import pandas as pd

st.header("Welcome to MedCost", divider="green")
st.subheader("This website brings you the most up-to-date, and simplified medical costs associated with your visits.", divider = "green")


cityOptions = ["-- No City Selected --", "Baltimore", "Chicago", "Boston"]

baltimoreHospitals = ["-- No Hospital Selected --", "JHH", "Mercy", "MedStar", "UMMC"]
chicagoHospitals = ["-- No Hospital Selected --", "Rush", "Northwestern"]
bostonHospitals = ["-- No Hospital Selected --", "Massachusetts General Hospital", "Beth Israel Deaconess"]
allHospitals = baltimoreHospitals + chicagoHospitals + bostonHospitals

#Phase 1: Collect Info
def identifyCostInformation():
    selectedCity = st.selectbox("Choose a city", cityOptions)
    cityHospitals = []
    selectedHospital = ""
    
    if selectedCity == "Baltimore":
        cityHospitals = baltimoreHospitals
    elif selectedCity == "Chicago":
        cityHospitals = chicagoHospitals
    elif selectedCity == "Boston":
        cityHospitals = bostonHospitals

    if selectedCity != "-- No City Selected --":
        selectedHospital = st.selectbox(f"Select a Hospital from {selectedCity}:", cityHospitals)
    
        if selectedHospital != "-- No Hospital Selected --":
            userProcedure = st.text_input("Please input details of your procedure/service/test (key words):")
            
            return [selectedCity, selectedHospital, userProcedure]

def compareCostsInformation():
    numCities = st.number_input("How many cities would you like to compare?", min_value=1, max_value=3, step=1)

    columns = st.columns(numCities)

    # Render inputs and store in session state
    for i in range(int(numCities)):
        with columns[i]:
            st.markdown(f"### City {i+1}")

            city_key = f"city_{i}"
            hospital_key = f"hospital_{i}"
            procedure_key = f"procedure_{i}"

            selectedCity = st.selectbox(f"City #{i+1}", cityOptions, key=city_key)

            if selectedCity != "-- No City Selected --":
                if selectedCity == "Baltimore":
                    cityHospitals = baltimoreHospitals
                elif selectedCity == "Chicago":
                    cityHospitals = chicagoHospitals
                elif selectedCity == "Boston":
                    cityHospitals = bostonHospitals
                else:
                    cityHospitals = []

                selectedHospital = st.selectbox(f"Hospital in {selectedCity}", cityHospitals, key=hospital_key)

                if selectedHospital != "-- No Hospital Selected --":
                    st.text_input(f"Procedure at {selectedHospital}", key=procedure_key)

    # Gather results from session_state
    results = [
        [
            st.session_state.get(f"city_{i}"),
            st.session_state.get(f"hospital_{i}"),
            st.session_state.get(f"procedure_{i}", "").strip()
        ]
        for i in range(int(numCities))
    ]

    # Return results only if all fields are filled
    if all(all(cell != "" and cell != "-- No City Selected --" and cell != "-- No Hospital Selected --" for cell in row) for row in results):
        return results

#Phase 2: Searching
def priceSearch(inputInformation):
    city, hospital, parameters = inputInformation
    fileName = "MedCosts/" + hospital + ".csv"
    try:
        price = pd.read_csv(fileName, encoding="utf-8")
    except UnicodeDecodeError:
        price=pd.read_csv(fileName, encoding="ISO-8859-1")
    
    price["__search_text__"] = price.astype(str).agg(" ".join, axis=1).str.lower()

    keyWords = parameters.lower().split()
    prefixes = [kw[:3] for kw in keyWords if len(kw) >= 3]

    filtered_df = price.copy()

    for prefix in prefixes:
        regex = fr"\b{prefix}\w*"
        filtered_df = filtered_df[filtered_df["__search_text__"].str.contains(regex, regex=True)]

    # Drop duplicates and remove helper column
    filtered_df = filtered_df.drop_duplicates().drop(columns="__search_text__")

    if "__search_text__" in filtered_df.columns:
        filtered_df = filtered_df.drop(columns="__search_text__")

    return filtered_df

#Phase 3: Data Sorting
#def dataSorting():





#Select the Function + City/Cities + Hospital + Procedure Key Words
st.subheader("Information")
function = st.selectbox("Choose a function:", ["-- No Option Selected --", "Identify a Cost", "Compare Costs"])

if function == "Identify a Cost":
    #Phase 1: Collect Info
    information = []
    information = identifyCostInformation() #eg. ["Baltimore", "JHH", "angiogram"]

    matchedRows = []
    #Phase 2: Search
    if information:
        matchedRows = priceSearch(information)

    columns_to_keep = [matchedRows.columns[0]] + [col for col in matchedRows.columns if "standard_charge" in col.lower()]
    matchedRows = matchedRows[columns_to_keep]  
    matchedRows = matchedRows.drop_duplicates(subset=["hospital_name"])  

    st.dataframe(matchedRows, height=300)

elif function == "Compare Costs":
    #Phase 1: Collect Info
    information = []
    information = compareCostsInformation() #eg. [['Baltimore', 'Mercy', 'asfd'], ['Baltimore', 'JHH',  'asfda']]

    #Phase 2: Search
    if information:
        numItems = len(information)
        for i, inputSet in enumerate(information):
            try:
                result_df = priceSearch(inputSet)

                if result_df.empty:
                    st.warning(f"No results found for Hospital {i+1}: {inputSet}")
                else:
                    st.markdown(f"### Results for Hospital {i+1}: {inputSet[0]} — {inputSet[1]}")
                    columns_to_keep = [result_df.columns[0]] + [col for col in result_df.columns if "standard_charge" in col.lower()]
                    result_df = result_df[columns_to_keep]
                    result_df = result_df.drop_duplicates(subset=["hospital_name"])  
                    st.dataframe(result_df, height=300, use_container_width=True)

            except Exception as e:
                st.error(f"Error processing City {i+1}: {inputSet}")
                st.exception(e)


