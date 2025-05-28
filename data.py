import tempfile
import zipfile
from pathlib import Path
import wget

import polars as pl

URL_FILE = "https://github.com/thiagodiasbispo/FatorCapaciidade/raw/refs/heads/main/fc.zip"
FILE_NAME = "fc.csv"


def download_data():
    zip_file =  Path(tempfile.mktemp(suffix=".zip"))
    wget.download(URL_FILE, str(zip_file))
    csv_file = Path(tempfile.gettempdir()) / FILE_NAME
    zipfile.ZipFile(zip_file).extractall(tempfile.gettempdir())
    return csv_file


def ler_dados_fc():
    arquivo_csv = download_data()
    df = pl.read_csv(arquivo_csv).to_pandas()

    if "level_0" in df.columns:
        df = df.drop(columns=["level_0"])

    return df


def extrair_media_mensal_fc(df=None):
    df = df if df is not None else ler_dados_fc()
    fc_media_mensal = df.groupby(['id_estado', 'nom_tipousina', 'nom_localizacao', 'mes_num', 'mes', 'ano'])[
        "val_fatorcapacidade"].mean().reset_index()

    fc_media_mensal["val_fatorcapacidade"] = round(fc_media_mensal["val_fatorcapacidade"] * 100, 2)

    # Ordenando segundo ordem de localidade, tipo e meses no ano segundo sua ordem
    fc_media_mensal = fc_media_mensal.sort_values(['id_estado', 'nom_tipousina', 'nom_localizacao', 'ano', 'mes_num'])
    fc_media_mensal = fc_media_mensal.drop(columns=["mes_num"])

    fc_media_mensal = fc_media_mensal.rename(
        columns={'id_estado': "UF", 'nom_tipousina': "Tipo", 'nom_localizacao': "Localização", 'mes': "Mês",
                 'ano': "Ano",
                 "val_fatorcapacidade": "FC_Méd_Mensal"})

    return fc_media_mensal


def get_quadrimestre(mes_num):
    if 1 <= mes_num <= 4:
        return 1
    if 5 <= mes_num <= 8:
        return 2
    return 3


def extrair_media_quadrimestral_fc(df=None):
    dfs_quadrimestre = df if df is not None else ler_dados_fc()

    dfs_quadrimestre["Quadri"] = dfs_quadrimestre.mes_num.map(get_quadrimestre)

    # Como já extraímos o quadrimestre, as informações sobre mês não interessam mais
    dfs_quadrimestre = dfs_quadrimestre.drop(columns=["mes", "mes_num"])

    fc_media_quadri = dfs_quadrimestre.groupby(['id_estado', 'nom_tipousina', 'nom_localizacao', 'Quadri', 'ano'])[
        "val_fatorcapacidade"].mean().reset_index()

    fc_media_quadri["val_fatorcapacidade"] = round(fc_media_quadri["val_fatorcapacidade"] * 100, 2)

    fc_media_quadri = fc_media_quadri.sort_values(['id_estado', 'nom_tipousina', 'nom_localizacao', 'ano', 'Quadri'])

    fc_media_quadri = fc_media_quadri.rename(
        columns={'id_estado': "UF", 'nom_tipousina': "Tipo", 'nom_localizacao': "Localização",
                 "val_fatorcapacidade": "FC_Méd_Quadr", "ano": "Ano"})

    return fc_media_quadri
