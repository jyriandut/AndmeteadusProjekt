import streamlit as st
import pandas as pd
import plotly.express as px
from scipy import stats
import numpy as np

# Seadistame lehe laiemaks
st.set_page_config(page_title="Andmeteaduse Projekt", layout="wide")

# Andmete laadimine vahemällu


@st.cache_data
def load_data():
    df = pd.read_parquet("data/app_data.parquet")

    # Veendume, et vajalikud veerud on olemas
    if 'minimaalne kategooria andmete alusel' not in df.columns:
        df['minimaalne kategooria andmete alusel'] = 'Tundmatu'
    else:
        df['minimaalne kategooria andmete alusel'] = df['minimaalne kategooria andmete alusel'].fillna(
            'Tundmatu')

    return df


st.title("Sissejuhatus andmeteadusesse: Projekt")
st.markdown("Autorid: Jüri Andrejev, Georg Allikas, Viktor Lantov")
st.markdown("""
See töölaud pakub interaktiivset ülevaadet Eesti ettevõtete finantsandmetest aastatel 2019-2025. 
Siin saab uurida ettevõtete demograafiat ja finantsnäitajaid, testida püstitatud statistilisi hüpoteese ning 
vaadata masinõppemudelite ennustustulemusi ettevõtete kasumlikkuse ja aktiivsuse kohta.
""")
st.divider()

try:
    with st.spinner('Laen andmeid...'):
        df = load_data()

    # Külgriba navigeerimiseks
    st.sidebar.header("Navigatsioon")
    page = st.sidebar.radio("Vali leht:", [
                            "1. Andmete uurimine (EDA)", "2. Hüpoteeside testimine", "3. Ennustav modelleerimine"])

    # -------------------------------------------------------------------------
    # LEHT 1: EDA
    # -------------------------------------------------------------------------
    if page == "1. Andmete uurimine (EDA)":
        st.header("1. Andmete uurimine (EDA)")
        st.markdown(
            "Uurime Äriregistri avaandmeid, mis sisaldavad ettevõtete põhiandmeid ja majandusaasta aruandeid aastatel 2019-2025.")

        # Aasta filter
        years = sorted(
            df['aruandeaasta'].dropna().unique().astype(int).tolist())
        selected_year = st.selectbox("Vali aruandeaasta analüüsiks:", [
                                     "Kõik aastad"] + years)

        if selected_year != "Kõik aastad":
            df_plot = df[df['aruandeaasta'] == selected_year]
        else:
            df_plot = df

        col1, col2 = st.columns(2)

        with col1:
            # Plot 1: Suuruskategooriad
            cat_counts = df_plot['minimaalne kategooria andmete alusel'].value_counts(
            ).reset_index()
            cat_counts.columns = ['Kategooria', 'Arv']
            fig_cat = px.bar(cat_counts, y='Kategooria', x='Arv', orientation='h',
                             title=f"Ettevõtete jaotus suurusakategooriate kaupa ({selected_year})",
                             color_discrete_sequence=['#4c72b0'])
            fig_cat.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_cat, width="stretch")

        with col2:
            # Plot 2: Õiguslik vorm (Top 10)
            vorm_counts = df_plot['õiguslik vorm'].value_counts().nlargest(
                10).reset_index()
            vorm_counts.columns = ['Õiguslik vorm', 'Arv']
            fig_vorm = px.bar(vorm_counts, y='Õiguslik vorm', x='Arv', orientation='h',
                              title=f"Top 10 õiguslikku vormi ({selected_year})",
                              color_discrete_sequence=['#4c72b0'])
            fig_vorm.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_vorm, width="stretch")

        # Plot 3: Staatus
        st.markdown("###")
        status_counts = df_plot['staatus'].value_counts().reset_index()
        status_counts.columns = ['Staatus', 'Arv']
        fig_status = px.bar(status_counts, x='Staatus', y='Arv',
                            title=f"Ettevõtete staatus ({selected_year})",
                            color_discrete_sequence=['#4c72b0'])
        st.plotly_chart(fig_status, width="stretch")

        st.markdown("---")
        st.subheader("Finantsnäitajad ja töötajate arv")

        # Finantsnäitajate valik
        metrics_map = {
            "Töötajate arv": "AverageNumberOfEmployeesInFullTimeEquivalentUnits",
            "Käibevara": "CurrentAssets",
            "Lühiajalised kohustised": "CurrentLiabilities",
            "Jaotamata kasum/kahjum": "RetainedEarningsLoss",
            "Müügitulu": "Revenue",
            "Raha ja pangakontod": "CashAndCashEquivalents",
            "Aruandeaasta kasum/kahjum": "TotalAnnualPeriodProfitLoss"
        }

        selected_metric_name = st.selectbox(
            "Vali finantsnäitaja, mida uurida:", list(metrics_map.keys()))
        selected_metric_col = metrics_map[selected_metric_name]

        if selected_metric_col in df_plot.columns:
            # Arvutame keskmised suuruskategooria järgi
            avg_by_cat = df_plot.groupby('minimaalne kategooria andmete alusel')[
                selected_metric_col].mean().reset_index()
            avg_by_cat = avg_by_cat.dropna()

            fig_metric1 = px.bar(avg_by_cat, x='minimaalne kategooria andmete alusel', y=selected_metric_col,
                                 title=f"Keskmine {selected_metric_name.lower()} suurusakategooriate kaupa ({selected_year})",
                                 labels={selected_metric_col: f"Keskmine {selected_metric_name.lower()}",
                                         'minimaalne kategooria andmete alusel': 'Kategooria'},
                                 color_discrete_sequence=['#2ca02c'])
            fig_metric1.update_layout(
                xaxis={'categoryorder': 'total descending'})

            # Arvutame keskmised õigusliku vormi järgi (valime 10 kõige levinumat vormi)
            top_vormid = df_plot['õiguslik vorm'].value_counts().nlargest(
                10).index
            df_top_vormid = df_plot[df_plot['õiguslik vorm'].isin(top_vormid)]
            avg_by_vorm = df_top_vormid.groupby('õiguslik vorm')[
                selected_metric_col].mean().reset_index()
            avg_by_vorm = avg_by_vorm.dropna()

            fig_metric2 = px.bar(avg_by_vorm, x='õiguslik vorm', y=selected_metric_col,
                                 title=f"Keskmine {selected_metric_name.lower()} levinumate õiguslike vormide kaupa ({selected_year})",
                                 labels={
                                     selected_metric_col: f"Keskmine {selected_metric_name.lower()}", 'õiguslik vorm': 'Õiguslik vorm'},
                                 color_discrete_sequence=['#ff7f0e'])
            fig_metric2.update_layout(
                xaxis={'categoryorder': 'total descending'})

            col3, col4 = st.columns(2)
            with col3:
                st.plotly_chart(fig_metric1, width="stretch")
            with col4:
                st.plotly_chart(
                    fig_metric2, width="stretch")
        else:
            st.warning(
                f"Valitud tunnust ({selected_metric_name}) ei leitud andmestikust.")

    # -------------------------------------------------------------------------
    # LEHT 2: Hüpoteesid
    # -------------------------------------------------------------------------
    elif page == "2. Hüpoteeside testimine":
        st.header("2. Hüpoteeside testimine")

        years = sorted(
            df['aruandeaasta'].dropna().unique().astype(int).tolist())
        selected_year = st.selectbox("Vali aruandeaasta hüpoteeside testimiseks:", [
                                     "Kõik aastad"] + years)

        if selected_year != "Kõik aastad":
            df_hyp = df[df['aruandeaasta'] == selected_year]
        else:
            df_hyp = df

        st.markdown("---")
        st.subheader("Hüpotees 1")
        st.markdown("""
        **Väikeettevõtjad on keskmiselt suurema varade (Assets) mahuga kui Mikroettevõtjad.**
        * H0: Keskmiste varade mahus ei ole erinevust.
        * H1: Väikeettevõtjatel on suurem keskmine varade maht.
        """)

        micro_assets = df_hyp[df_hyp['minimaalne kategooria andmete alusel']
                              == 'Mikroettevõtja']['Assets'].dropna()
        small_assets = df_hyp[df_hyp['minimaalne kategooria andmete alusel']
                              == 'Väikeettevõtja']['Assets'].dropna()

        if len(micro_assets) > 0 and len(small_assets) > 0:
            micro_mean = micro_assets.mean()
            small_mean = small_assets.mean()

            # T-test (equal_var=False tähistab Welch's t-testi)
            t_stat, p_val = stats.ttest_ind(
                small_assets, micro_assets, equal_var=False, alternative='greater')

            col1, col2, col3 = st.columns(3)
            col1.metric("Mikroettevõtja keskmine vara",
                        f"{micro_mean:,.2f} €".replace(",", " "))
            col2.metric("Väikeettevõtja keskmine vara",
                        f"{small_mean:,.2f} €".replace(",", " "))
            col3.metric("T-statistik", f"{t_stat:.2f}")

            st.info(f"**p-väärtus:** {p_val:.5e}")
            if p_val < 0.05:
                st.success(
                    "Tulemus on statistiliselt oluline: lükkame H0 ümber, väikeettevõtjatel on oluliselt suuremad varad.")
            else:
                st.warning(
                    "Tulemus EI OLE statistiliselt oluline: me ei saa H0 ümber lükata.")
        else:
            st.warning("Valitud aasta kohta pole piisavalt andmeid testiks.")

        st.markdown("---")
        st.subheader("Hüpotees 2")
        st.markdown("""
        **Osaühingute (OÜ) ja Aktsiaseltside (AS) keskmine töötajate arv erineb statistiliselt olulisel määral.**
        * H0: Keskmine töötajate arv on sama.
        * H1: Keskmine töötajate arv on erinev.
        """)

        # Töötajate arvu veerg (sõltub täpsest nimest andmestikus)
        emp_col = 'AverageNumberOfEmployeesInFullTimeEquivalentUnits'
        if emp_col in df_hyp.columns:
            ou_emp = df_hyp[df_hyp['õiguslik vorm'] == 'OÜ'][emp_col].dropna()
            as_emp = df_hyp[df_hyp['õiguslik vorm'] == 'AS'][emp_col].dropna()

            if len(ou_emp) > 0 and len(as_emp) > 0:
                ou_mean = ou_emp.mean()
                as_mean = as_emp.mean()

                t_stat2, p_val2 = stats.ttest_ind(
                    as_emp, ou_emp, equal_var=False)

                col1, col2, col3 = st.columns(3)
                col1.metric("OÜ keskmine töötajate arv", f"{ou_mean:.2f}")
                col2.metric("AS keskmine töötajate arv", f"{as_mean:.2f}")
                col3.metric("T-statistik", f"{t_stat2:.2f}")

                st.info(f"**p-väärtus:** {p_val2:.5e}")
                if p_val2 < 0.05:
                    st.success(
                        "Tulemus on statistiliselt oluline: Aktsiaseltsidel on keskmiselt oluliselt rohkem töötajaid kui Osaühingutel.")
                else:
                    st.warning(
                        "Tulemus EI OLE statistiliselt oluline: me ei saa H0 ümber lükata.")
            else:
                st.warning(
                    "Valitud aasta kohta pole piisavalt andmeid testiks.")
        else:
            st.error("Töötajate arvu veergu ei leitud andmestikust.")

    # -------------------------------------------------------------------------
    # LEHT 3: Masinõpe / Predictive Modelling
    # -------------------------------------------------------------------------
    elif page == "3. Ennustav modelleerimine":
        st.header("3. Ennustav modelleerimine (Predictive Modelling)")
        st.markdown("""
        Loome kaks ennustavat mudelit:
        1. **Kasumi/kahjumi ennustamine:** Kas ettevõte jääb järgmisel aastal kasumisse või kahjumisse.
        2. **Staatus:** Kas ettevõtte staatus muutub "Kustutatud" või "Pankrotis" staatusesse.
        """)

        # Hardcoded results based on user's input
        model_results = {
            "2019 -> 2020 (Sihtmärk 2021)": {
                "m1_act": 49.4, "m1_pred": 55.8, "m1_err": 6.5, "m1_acc": 0.7681, "m1_prec": 0.7344, "m1_rec": 0.8307, "m1_f1": 0.7796,
                "m2_act": 90.2, "m2_pred": 68.5, "m2_err": 21.7, "m2_acc": 0.7106, "m2_prec": 0.9471, "m2_rec": 0.7194, "m2_f1": 0.8177
            },
            "2020 -> 2021 (Sihtmärk 2022)": {
                "m1_act": 48.3, "m1_pred": 62.3, "m1_err": 14.1, "m1_acc": 0.7582, "m1_prec": 0.6931, "m1_rec": 0.8954, "m1_f1": 0.7814,
                "m2_act": 92.8, "m2_pred": 71.6, "m2_err": 21.3, "m2_acc": 0.7294, "m2_prec": 0.9594, "m2_rec": 0.7398, "m2_f1": 0.8354
            },
            "2021 -> 2022 (Sihtmärk 2023)": {
                "m1_act": 48.4, "m1_pred": 60.6, "m1_err": 12.1, "m1_acc": 0.7466, "m1_prec": 0.6908, "m1_rec": 0.8634, "m1_f1": 0.7675,
                "m2_act": 96.0, "m2_pred": 72.2, "m2_err": 23.9, "m2_acc": 0.7298, "m2_prec": 0.9781, "m2_rec": 0.7350, "m2_f1": 0.8393
            },
            "2022 -> 2023 (Sihtmärk 2024)": {
                "m1_act": 48.1, "m1_pred": 59.9, "m1_err": 11.9, "m1_acc": 0.7441, "m1_prec": 0.6874, "m1_rec": 0.8573, "m1_f1": 0.7630,
                "m2_act": 97.7, "m2_pred": 76.8, "m2_err": 20.9, "m2_acc": 0.7717, "m2_prec": 0.9874, "m2_rec": 0.7761, "m2_f1": 0.8691
            },
            "2023 -> 2024 (Sihtmärk 2025)": {
                "m1_act": 52.8, "m1_pred": 61.9, "m1_err": 9.1, "m1_acc": 0.7388, "m1_prec": 0.7153, "m1_rec": 0.8388, "m1_f1": 0.7722,
                "m2_act": 93.3, "m2_pred": 76.9, "m2_err": 16.4, "m2_acc": 0.7848, "m2_prec": 0.9669, "m2_rec": 0.7967, "m2_f1": 0.8736
            }
        }

        selected_period = st.selectbox(
            "Vali mudeli treenimise ja testimise periood (Walk-Forward):", list(model_results.keys()))
        res = model_results[selected_period]

        st.divider()
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Mudel 1: Kasumi ennustamine")
            st.metric("Viga (protsendipunktides)", f"{res['m1_err']} pp")

            # Võrdlusgraafik
            fig_m1 = px.bar(
                x=['Tegelik kasumis %', 'Ennustatud kasumis %'],
                y=[res['m1_act'], res['m1_pred']],
                color=['Tegelik', 'Ennustatud'],
                title="Tegelik vs Ennustatud",
                text=[f"{res['m1_act']}%", f"{res['m1_pred']}%"]
            )
            fig_m1.update_traces(textposition='auto')
            fig_m1.update_layout(yaxis_title="Protsent (%)", xaxis_title="")
            st.plotly_chart(fig_m1, width="stretch")

            st.markdown(
                f"**Mõõdikud:** Accuracy: {res['m1_acc']} | Precision: {res['m1_prec']} | Recall: {res['m1_rec']} | F1: {res['m1_f1']}")

        with col2:
            st.subheader("Mudel 2: Staatuse ennustamine")
            st.metric("Viga (protsendipunktides)", f"{res['m2_err']} pp")

            # Võrdlusgraafik
            fig_m2 = px.bar(
                x=['Tegelik aktiivne %', 'Ennustatud aktiivne %'],
                y=[res['m2_act'], res['m2_pred']],
                color=['Tegelik', 'Ennustatud'],
                title="Tegelik vs Ennustatud",
                text=[f"{res['m2_act']}%", f"{res['m2_pred']}%"]
            )
            fig_m2.update_traces(textposition='auto')
            fig_m2.update_layout(yaxis_title="Protsent (%)", xaxis_title="")
            st.plotly_chart(fig_m2, width="stretch")

            st.markdown(
                f"**Mõõdikud:** Accuracy: {res['m2_acc']} | Precision: {res['m2_prec']} | Recall: {res['m2_rec']} | F1: {res['m2_f1']}")

        st.divider()
        st.subheader("Tunnuste olulisus (Feature Importance)")
        st.markdown("Graafikud näitavad, millised finantsnäitajad mõjutavad mudeleid kogu andmestiku (2019-2025) lõikes kõige enam. Kuvatud on koondtulemus.")

        # Hardcoded feature importance based on user images
        fi_m1 = pd.DataFrame({
            'Tunnus': ['TotalAnnualPeriodProfitLoss', 'Revenue', 'Equity', 'IssuedCapital', 'RetainedEarningsLoss', 'Assets', 'CurrentAssets', 'CurrentLiabilities', 'LaborExpense', 'Töötajate_arv'],
            'Tähtsus': [0.345, 0.302, 0.130, 0.084, 0.060, 0.030, 0.021, 0.015, 0.008, 0.003]
        })

        fi_m2 = pd.DataFrame({
            'Tunnus': ['TotalAnnualPeriodProfitLoss', 'RetainedEarningsLoss', 'Assets', 'Equity', 'Revenue', 'CurrentLiabilities', 'CurrentAssets', 'IssuedCapital', 'LaborExpense', 'Töötajate_arv'],
            'Tähtsus': [0.150, 0.143, 0.143, 0.125, 0.103, 0.086, 0.083, 0.075, 0.070, 0.021]
        })

        col_fi1, col_fi2 = st.columns(2)
        with col_fi1:
            fig_fi1 = px.bar(fi_m1, x='Tunnus', y='Tähtsus',
                             title="Mudel 1: Kasumi ennustamine")
            st.plotly_chart(fig_fi1, width="stretch")

        with col_fi2:
            fig_fi2 = px.bar(fi_m2, x='Tunnus', y='Tähtsus',
                             title="Mudel 2: Aktiivse staatuse ennustamine")
            st.plotly_chart(fig_fi2, width="stretch")

except FileNotFoundError:
    st.error("Andmefaili 'data/app_data.parquet' ei leitud.")
except Exception as e:
    st.error(f"Tekkis viga: {e}")
