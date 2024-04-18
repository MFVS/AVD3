import pandas as pd
import requests
from io import StringIO

stupen_vzdelani = {
    "J": "Střední nebo střední odborné vzdělání (bez maturity i výučního listu)",
    "C": "Praktická škola",
    "E": "Střední odborné vzdělání s výučním listem",
    "H": "Střední odborné vzdělání s výučním listem",
    "M": "Úplné střední odborné vzdělání s maturitou (bez vyučení)",
    "L": "Úplné střední odborné vzdělání s odborným výcvikem a maturitou",
    "K": "Úplné střední všeobecné vzdělání (poskytují gymnázia)",
    "N": "Vyšší odborné vzdělání",
    "P": "Vyšší odborné vzdělání v konzervatoři",
}

skupina_oboru = {
    "16": "Ekologie a ochrana životního prostředí",
    "18": "Informatické obory",
    "21": "Hornictví a hornická geologie, hutnictví a slévárenství",
    "23": "Strojírenství a strojírenská výroba",
    "26": "Elektrotechnika, telekomunikační a výpočetní technika",
    "28": "Technická chemie a chemie silikátů",
    "29": "Potravinářství a potravinářská chemie",
    "31": "Textilní výroba a oděvnictví",
    "32": "Kožedělná a obuvnická výroba a zpracování plastů",
    "33": "Zpracování dřeva a výroba hudebních nástrojů",
    "34": "Polygrafie, zpracování papíru, filmu a fotografie",
    "36": "Stavebnictví, geodézie a kartografie",
    "37": "Doprava a spoje",
    "39": "Speciální a interdisciplinární technické obory",
    "41": "Zemědělství a lesnictví",
    "43": "Veterinářství a veterinární prevence",
    "53": "Zdravotnictví",
    "61": "Filozofie, teologie",
    "63": "Ekonomika a administrativa",
    "64": "Podnikání v oborech, odvětví",
    "65": "Gastronomie, hotelnictví a turismus",
    "66": "Obchod",
    "68": "Právo, právní a veřejnosprávní činnost",
    "69": "Osobní a provozní služby",
    "72": "Publicistika, knihovnictví a informatika",
    "74": "Tělesná kultura, tělovýchova a sport",
    "75": "Pedagogika, učitelství a sociální péče",
    "78": "Obecně odborná příprava",
    "79": "Obecná příprava",
    "82": "Umění a užité umění",
    "91": "Teorie vojenského umění",
}


def transform_data():
    df = pd.read_csv("data/prf_uchazeci.csv")

    df["KOLO_PRIHLASKY"] = df["PR_NAZEV"].str[-1].astype(int)

    df["skupina_oboru"] = df["CIS_OBORU"].str.extract(r"(\d{2})")
    df["stupen_vzdelani"] = df["CIS_OBORU"].str.extract(r"([A-Za-z])")

    df["skupina_oboru"].replace(skupina_oboru, inplace=True)
    df["stupen_vzdelani"].replace(stupen_vzdelani, inplace=True)

    df["ROK_NAR"].replace(0, None, inplace=True)

    return df


if __name__ == "__main__":
    df = transform_data()
    df.to_csv("data/uchazeci_transformed.csv", index=False)

    print("DataFrame length: ", len(df))
    print(df.head())
