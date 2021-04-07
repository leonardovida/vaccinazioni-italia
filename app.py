import altair as alt
import numpy as np
import pandas as pd
import requests
import streamlit as st
import urllib

import content
import compute

# Introduzione
st.title("Quando verrò vaccinato? :syringe:")
st.write("Campagna vaccinale 2021-2022 - V.1")
st.header("Per chi è questo sito?")
st.write("In questo sito diamo un'approssimazione sulla data in cui riceverai il tuo vaccino Covid.")

# Inserimento dati

st.header("Inserisci la tua età :man: :girl: - :older_man: :older_woman:")
age = st.number_input(
    label='Età attuale.',
    min_value=0,
    max_value=130,
    value=50,
    step=1,
    format='%d',
    key="age"
)


st.header("Seleziona la regione di residenza :it:")
region = st.selectbox(
    label='Seleziona la regione di residenza e non di nascita.',
    options=content.regions,
    key="regions",
    help="La regione di residenza sarà utilizzata per tenere in conto la diversa velocità di vaccinazione tra regioni."
)

st.header("Inserisci il tuo CAP di residenza :house:")
cap = st.number_input(
    label='Inserisci il tuo CAP.',
    min_value=0,
    max_value=99999,
    step=1,
    value=20100,
    format='%d',
    key="cap",
    help="Il cap viene utilizzato per fornirti il punto vaccinale più vicino."
)

st.header("Sei incinta? :baby:")
pregnant = st.selectbox(
    'Sì, solo se attualmente incinta.',
    ('No', 'Sì'),
    key='pregnant',
    help='Donne incinta vengono date priorità in questa campagna vaccinale.')

st.header("Sei una persona estremamente vulnerabile? :hospital:")
category_1 = st.selectbox(
    '',
    ('No', 'Sì'),
    key='category_1',
    help='Persone estremamente vulnerabili hanno aumentata priorità in questa campagna vaccinale.')
expander_categoria_1 = st.beta_expander(
    "Clicca qui per vedere le patologie considerate come estremamente vulnerabili")
expander_categoria_1.markdown("All'interno della Categoria 1, rientrano i soggetti affetti dalle seguenti patologie:\n\
        \n* Malattie respiratorie\n* Malattie cardiocircolatorie\n* Condizioni neurologiche e disabilità\n* Diabete oppure altre endocrinopatie severe \
        \n* Fibrosi cistica\n* Insufficienza renale oppure patologia renale\n* Malattie autoimmuni – immunodeficienze primitive \
        \n* Malattia epatica\n* Malattie cerebrovascolari\n * Patologia oncologica ed emoglobinopatie\n * Sindrome di Down \
        \n* Trapianto di organo solido\n * Grave obesità")

st.header("Sei una persona con aumentato rischio clinico? :medical_symbol:")
category_2 = st.selectbox(
    '',
    ('No', 'Sì'),
    key='category_2',
    help='Persone con aumentato rischio clinico hanno aumentata priorità in questa campagna vaccinale.')
expander_categoria_2 = st.beta_expander(
    "Clicca qui per vedere le patologie considerate per l'aumentato rischio clinico")
expander_categoria_2.markdown("All'interno della Categoria 2, rientrano i soggetti affetti dalle seguenti patologie:\n \
    \n* Malattie respiratorie\n * Malattie cardiocircolatorie\n* Condizioni neurologiche e disabilità\n* Diabete oppure altre endocrinopatie \
    \n* HIV\n* Insufficienza renale oppure patologia renale\n* Ipertensione arteriosa\n* Malattie autoimmuni oppure immunodeficienze primitive \
    \n* Malattia epatica\n* Malattie cerebrovascolari\n* Patologia oncologica")

st.header("Dati inseriti")
st.write(f"Età: **{age}**")
st.write(f"Regione di residenza: **{region}**")
st.write(f"CAP di residenza: **{cap}**")
st.write(f'Incinta: **{pregnant}**')
st.write(f'Estremamente vulerabile: **{category_1}**')
st.write(f'Aumentato rischio clinico: **{category_2}**')

# Calcoli


@st.cache
def get_latest_vaccines(url):
    res = requests.get(url, allow_redirects=True)
    with open('data/regioni_latest.csv', 'wb') as file:
        file.write(res.content)
    df = pd.read_csv("data/regioni_latest.csv")
    return df


# Retrieve latest data on vaccines to create region-specific trend
url_latest_vaccines = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-summary-latest.csv"
df = get_latest_vaccines(url_latest_vaccines).set_index("nome_area")


st.markdown("---")

try:
    if not age:
        st.error("Per favore, specifica la tua età")
    if not region:
        st.error("Per favore, seleziona la regione di residenza")
    else:
        # Total population per region
        total_pop = pd.read_csv(
            "data/pop_italy.csv")
        # Clean and convert ETA1 to int
        total_pop['ETA1'] = pd.to_numeric(total_pop['ETA1'].map(
            lambda x: x.lstrip('Y_GE')).copy())
        # Select only over 18
        total_pop = total_pop[total_pop["ETA1"] >= 18]
        total_pop_over_18_no_age = total_pop.drop(columns=[
            "ETA1"])
        total_pop_over_18_no_age = total_pop_over_18_no_age.groupby(
            ["Territorio"]).sum()
        # st.write(total_pop_over_18_no_age) # per regione

        # Population region over 18
        region_pop = total_pop.loc[total_pop["Territorio"] == region]

        # Regional share of vaccinations on country total
        regional_share_vax = sum(region_pop["Value"]) / sum(
            total_pop_over_18_no_age["Value"])
        regional_max_vax_rate = 500000 * regional_share_vax

        # Calculate trend vaccinations per region
        vaccinations = df.loc[region]
        vaccinations.rename(columns={"data_somministrazione": "Data",
                                     "totale": "Vaccinazioni"}, inplace=True)
        vaccinations.sort_values(by='Data', ascending=False, inplace=True)
        clean_vaccinations = compute.clean_dataset(vaccinations)
        clean_vaccinations = compute.split_dataset(clean_vaccinations)
        # Define the model name
        forecast = compute.arima_forecast(clean_vaccinations)
        st.write(forecast)

    #     pyplot.legend()
    # pyplot.title("Graph of full standard week having your date")
    # pyplot.xlabel("(Weekdays)")
    # pyplot.ylabel("(Units consumed)")
    # st.pyplot()

        # Compute past trend of vaccinations and extrapolate to the future
        # Max:
        # - 500.000 / region adjusted for population
        # - population of region
        # pred = compute.predict_trend_arima(vaccinations)
        # pred = compute.predict_trend_lstm()
        # st.write(pred)

        # Compute number of vaccinations for age interval
        # and category

        # Subtract vaccinations to population outstanding
        # Calculate how many people are remaining before user
        st.write('Share region on total vaccinations', regional_share_vax)
        st.write('Max regional daily vaccinations: ', regional_max_vax_rate)
        # st.write(region_pop) # popolazione per regione per anni

        # chart = (
        #     alt.Chart(data_trend)
        #     .mark_area(opacity=0.3)
        #     .encode(
        #         x="Data:T",
        #         y="Vaccinazioni:Q",
        #     )
        # )
        # st.altair_chart(chart, use_container_width=True)

except urllib.error.URLError as e:
    st.error(
        """
        **This demo requires internet access.**

        Connection error: %s
    """
        % e.reason
    )

st.markdown("---")


expander_assunzioni = st.beta_expander("Assunzioni utilizzate nel calcolo")
expander_assunzioni.write(
    '\n* Assunzione riguardo a totale popolazione che verrà vaccinata: https://www.nature.com/articles/s41591-020-1124- \
     \n* Il numero massimo di vaccinazioni giornaliere in Italia (500.000) è stato scelto seguendo il piano nazionale di Marzo 2021 (pag. 20): http://www.governo.it/sites/governo.it/files/210313_Piano_Vaccinale_marzo_2021_1.pdf')
