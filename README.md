# Sissejuhatus andmeteadusesse: Projekt

**Autorid:** Jüri Andrejev, Georg Allikas, Viktor Lantov 

See repositoorium sisaldab Tartu Ülikooli aine "Sissejuhatus andmeteadusesse" raames valminud rühmaprojekti. Projekti eesmärgiks on uurida ja analüüsida **Eesti Äriregistri avaandmeid** (aastatest 2019–2025), et leida seoseid ettevõtete finantsnäitajate vahel ning ennustada nende tulevast kasumlikkust ja elujõulisust.

## 📊 Projekti ülevaade
Projekt koosneb andmete allalaadimisest, puhastamisest, statistilisest analüüsist (hüpoteeside testimine) ning masinõppemudelite treenimisest. Tulemuste mugavaks ja interaktiivseks uurimiseks on loodud **Streamlit** veebirakendus (töölaud).

### Põhilised uurimisküsimused ja mudelid:
1. **Statistilised hüpoteesid:**
   * Kas väikeettevõtjatel on keskmiselt oluliselt suurem varade maht kui mikroettevõtjatel?
   * Kas Aktsiaseltside (AS) ja Osaühingute (OÜ) keskmine töötajate arv erineb statistiliselt olulisel määral?
2. **Ennustav modelleerimine (Aastapõhine *Walk-Forward* lähenemine):**
   * **Mudel 1:** Ettevõtte järgmise aasta kasumi/kahjumi ennustamine.
   * **Mudel 2:** Ettevõtte aktiivse staatuse ennustamine (kas ettevõte on järgmisel aastal aktiivne või kustutatud/pankrotis).

---

## 📂 Projekti struktuur

* **`0. Download data.ipynb`** – Äriregistri avaandmete (ettevõtete rekvisiidid ja majandusaasta aruanded) automaatne allalaadimine ja lahtipakkimine.
* **`1. Merge Data.ipynb`** – Erinevate andmestike ühendamine, andmete viimine laia formaati (*pivot*) ja metaandmete lisamine. Tulemus salvestatakse efektiivsesse `parquet` formaati.
* **`2.Exploratory_Data_Analysis.ipynb`** – Andmete uuriv analüüs (EDA), andmete puhastamine puuduvatest väärtustest ning püstitatud statistiliste hüpoteeside kontrollimine.
* **`3.Predictive_Modelling.ipynb`** – Masinõppemudelite treenimine, testimine ja tunnuste olulisuse (*Feature Importance*) analüüs.
* **`app.py`** – Interaktiivne Streamlit veebirakendus andmete visualiseerimiseks ja mudelite tulemuste esitlemiseks.

---

## 🚀 Kuidas projekti käivitada?

### 1. Nõuded
Projekti käivitamiseks on vajalik Python 3.8+ ja järgmised teegid:
```bash
pip install pandas numpy scipy scikit-learn plotly streamlit fastparquet requests
```

### 2. Andmete ettevalmistamine
Kuna avaandmete mahud on suured, ei ole algseid andmefaile repositooriumis. Andmestiku genereerimiseks käivita Jupyter märkmikud järgmises järjekorras:
1. Käivita `0. Download data.ipynb` (tõmbab andmed kausta `raw_data`).
2. Käivita `1. Merge Data.ipynb` (loob töödeldud faili `data/merged_reports.parquet`).

### 3. Streamlit rakenduse käivitamine
Pärast andmete edukat ühendamist (samm 2) saad avada interaktiivse töölaua. Jooksuta terminalis:
```bash
streamlit run app.py
```
Rakendus avaneb automaatselt sinu veebibrauseris aadressil `http://localhost:8501`.

Või vaata Streamlit'is:
`https://andmeteadusprojekt-123.streamlit.app/`

---

*Tartu Ülikool, Sissejuhatus andmeteadusesse*