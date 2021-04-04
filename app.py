import altair as alt
import numpy as np
import pandas as pd
import requests
import streamlit as st
import urllib

import content

# Introduzione
st.title("Quando è il mio turno del vaccino Covid? :syringe:")
st.write("Campagna vaccinale 2021-2022 - V.1")
st.header("Per chi è questo sito?")
st.write("In questo sito diamo un'approssimazione sulla data in cui riceverai il tuo vaccino Covid.")

# Inserimento dati

st.header("Inserisci la tua età :man:")
age = st.number_input(
    label='',
    min_value=0,
    max_value=130,
    value=50,
    step=1,
    format='%d',
    key="age"
)


st.header("Seleziona la regione di residenza :map:")
region = st.selectbox(
    label='',
    options=content.regions,
    key="regions",
    help="La regione di residenza sarà utilizzata per tenere in conto la diversa velocità di vaccinazione tra regioni."
)

st.header("Sei incinta? :baby:")
pregnant = st.selectbox(
    '',
    ('No', 'Sì'),
    key='pregnant',
    help='Donne incinta vengono date priorità in questa campagna vaccinale.')

st.header("Sei una persona estremamente vulnerabile?")
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

st.header("Sei una persona con aumentato rischio clinico?")
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


url_latest_vaccines = "https://raw.githubusercontent.com/italia/covid19-opendata-vaccini/master/dati/somministrazioni-vaccini-summary-latest.csv"
df = get_latest_vaccines(url_latest_vaccines).set_index("nome_area")


st.markdown("---")

try:
    if not age:
        st.error("Per favore, specifica la tua età")
    if not region:
        st.error("Per favore, seleziona la regione di residenza")
    else:
        # Popolazione
        pop = pd.read_csv("data/popolazione_italia.csv")
        pop.drop(columns=["ITTER107", "TIPO_DATO15",
                          "Tipo di indicatore demografico", "SEXISTAT1", "STATCIV2", "Età", "Stato civile", "TIME",
                          "Flag Codes", "Flags", "Seleziona periodo", "Sesso"], inplace=True)
        pop = pop.loc[pop["Territorio"] == region]

        st.write(pop)

        # Vacccini
        data = df.loc[region]
        data.rename(columns={"data_somministrazione": "Data",
                             "totale": "Vaccinazioni"}, inplace=True)
        data.sort_values(by='Data', ascending=False, inplace=True)
        st.write(data.head(7))

        chart = (
            alt.Chart(data)
            .mark_area(opacity=0.3)
            .encode(
                x="Data:T",
                y="Vaccinazioni:Q",
            )
        )
        st.altair_chart(chart, use_container_width=True)

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
    '\n* Assunzione riguardo a totale popolazione che verrà vaccinata: https://www.nature.com/articles/s41591-020-1124-9')
