import re
import ssl
import urllib.request

import bs4
import numpy as np
import pandas as pd


def knot_to_ms(knot):
    ms = 0.514444 * knot
    return ms

def ms_to_knot(ms):
    kt = ms / 0.514444
    return kt

def nmi_to_km(nmi):
    km = nmi * 1.852
    return km

def km_to_nmi(km):
    nmi = km / 1.852
    return nmi

def bb_to_basin(bb):
    basin = {"AL":"ATL","EP":"EPAC","WP":"WPAC","IO":"IO","SH":"SHEM"}[bb]
    return basin

def b_to_bb(b):
    bb = {"L":"AL","E":"EP","W":"WP","A":"IO","B":"IO","S":"SH","P":"SH"}[b]
    return bb

def basin_to_bb(bb):
    basin = {"ATL":"AL","EPAC":"EP","WPAC":"WP","IO":"IO","SHEM":"SH"}[bb]
    return basin

def b_to_bb(b):
    bb = {"L":"AL","E":"EP","W":"WP","A":"IO","B":"IO","S":"SH","P":"SH"}[b]
    return bb

def b_to_basin(b):
    return bb_to_basin(b_to_bb(b))

def _rawtext_to_rows(text, sep=" "):
    """
    Convert raw text data into a list of rows.

    Parameters
    ----------
    text : str
        A string representing the raw text data.

    Returns
    -------
    List[List[str]]
        A list of rows representing the data.
    """
    text = text.split("\n")
    text.remove("")
    
    rows = []
    for entry in text:
        values = re.split(f"{sep}+", entry)
        rows.append(values)
    return rows

def bbnnyyyy_to_nnbname(bbnnyyyy):
    url_header = "https://www.nrlmry.navy.mil/tcdat"
    bb, year = bbnnyyyy[:2], bbnnyyyy[4:]
    basin = bb_to_basin(bb)

    url = f"{url_header}/tc{year[-2:]}/{basin}/"
    ssl._create_default_https_context = ssl._create_unverified_context
    response = urllib.request.urlopen(url)
    html = response.read().decode('utf-8')
    pattern = rf'href="({bbnnyyyy[2:4]}[A-Z].[A-Z]+)/">'
    nnbname = re.findall(pattern, html)[0]
    return nnbname

def get_jtwc_IDs(year, bb):
    """
    Get a list of JTWC TC directory names for the specified year and basin.

    Parameters
    ----------
    year : int
        The year to retrieve the TC directories.
    bb : str
        The basin to retrieve the TC directories.
        Valid values are "AL" (Atlantic), "EP" (Eastern Pacific), "WP" (Western Pacific),
        "IO" (Indian Ocean), and "SH" (Southern Hemisphere).

    Returns
    -------
    numpy.ndarray
        A 1-dimensional array of TC directory names.
    """
    year = str(year)
    bb = bb.upper()
    if bb not in ("AL","EP","WP","IO","SH"):
        raise ValueError('bb must be in ["AL","EP","WP","IO","SH"]')
    url_header = "https://www.nrlmry.navy.mil/tcdat"

    url = f"{url_header}/tc{year}/{bb}/"

    ssl._create_default_https_context = ssl._create_unverified_context
    response = urllib.request.urlopen(url)
    html = response.read().decode('utf-8')

    pattern = r'<a href="([A-Z][A-Z][0-4][0-9][1-2][0-9][0-9][0-9])/">.*\d{2}-[A-Za-z]{3}-\d{4} \d{2}:\d{2}'
    IDs = re.findall(pattern, html)
    return IDs

def get_lastmod(bbnnyyyy):
    bbnnyyyy = bbnnyyyy.upper()
    url_header = "https://www.nrlmry.navy.mil/tcdat"
    url = f"{url_header}/tc{bbnnyyyy[-4:]}/{bbnnyyyy[:2]}/{bbnnyyyy}/txt/"
    ssl._create_default_https_context = ssl._create_unverified_context
    response = urllib.request.urlopen(url)
    html = response.read().decode('utf-8')

    pattern = r'trackfile.txt</a>.*(\d{2}-[A-Za-z]{3}-\d{4} \d{2}:\d{2})'
    lastmod = re.findall(pattern, html)[0]
    return lastmod

def _get_jtwc_bt_text_from_navy(bbnnyyyy):
    """
    Parameters
    ----------
    bbnnyyyy : str
        ID for a TC consisting of [bb:basin][nn:number][yyyy:year]
        e.g., WP052023
    """
    bbnnyyyy = bbnnyyyy.upper()
    if not isinstance(bbnnyyyy,str) or len(bbnnyyyy) != 8:
        raise ValueError("`bbnnyyyy` must be str and length of 8")
    
    url_header = "https://www.nrlmry.navy.mil/tcdat"
    url = f"{url_header}/tc{bbnnyyyy[-4:]}/{bbnnyyyy[:2]}/{bbnnyyyy}/txt/trackfile.txt"

    ssl._create_default_https_context = ssl._create_unverified_context
    response = urllib.request.urlopen(url)
    text = response.read().decode('utf-8')
    return text

def download_jtwc_bt_from_navy(bbnnyyyy, opath=None, asxarray=True):
    """
    Download the Joint Typhoon Warning Center (JTWC) Best Track (BT) data from the Navy database for a given year and save it as a text file.

    Parameters
    ----------
    bbnnyyyy : str
        A string representing the year in the format "bbnnyyyy" (e.g., "bbnnyyyy" = "wp012022").
    opath : str, optional
        A string representing the output file path. If not provided, the file will be saved as "bbnnyyyy.txt" in the current directory.
    asxarray : bool, optional
        If True, return as xarray.Dataset
    
    Returns
    -------
    List[List[str]]
        A list of rows representing the BT data.
    """
    text = _get_jtwc_bt_text_from_navy(bbnnyyyy)
    if opath is None:
        opath = bbnnyyyy + ".txt"
    with open(opath, 'w') as file:
        file.write(text)
    if asxarray:
        rows = _rawtext_to_rows(text)
        ds = _read_jtwc_bt_from_rows(rows)
        return ds

def open_jtwc_bt_file(path_to_txt):
    """
    Open and read the JTWC BT data from a text file.

    Parameters
    ----------
    path_to_txt : str
        A string representing the path to the text file containing the BT data.

    Returns
    -------
    xr.Dataset
        A processed dataset containing the BT data.
    """
    rows = np.loadtxt(path_to_txt, dtype=str)
    return _read_jtwc_bt_from_rows(rows)

def _read_jtwc_bt_from_rows(rows):
    """
    Read and process the JTWC BT data from a list of rows.

    Parameters
    ----------
    rows : np.ndarray
        A NumPy array representing the BT data.

    Returns
    -------
    xr.Dataset
        A processed dataset containing the BT data.
    """
    df = pd.DataFrame(rows, columns=["nnb","name","yymmdd","HHMM","latNS","lonEW","basin","vmax_kt","pres"], dtype=str)
    df = df.where(df["yymmdd"]!="00").dropna()
    df["time"] = pd.to_datetime(df["yymmdd"], format="%y%m%d") + pd.to_timedelta(df["HHMM"].str[:2].astype(int), unit="h") + pd.to_timedelta(df["HHMM"].str[2:].astype(int), unit="min")
    df["lon"] = df["lonEW"].str[:-1].astype(float) * df["lonEW"].str[-1].replace({"E":"1","W":"-1"}).astype(float)
    df["lat"] = df["latNS"].str[:-1].astype(float) * df["latNS"].str[-1].replace({"N":"1","S":"-1"}).astype(float)
    df[["vmax_kt","pres"]] = df[["vmax_kt","pres"]].astype(float)

    ds = df[["time","lon","lat","vmax_kt","pres"]].to_xarray().swap_dims({"index": "time"}).drop("index").sortby("time")

    ds["pres"] = ds["pres"].where(ds["pres"]>0)
    ds["vmax_kt"] = ds["vmax_kt"].where(ds["vmax_kt"]>0)
    ds["vmax"] = knot_to_ms(ds["vmax_kt"])
    ds["nnb"] = df["nnb"].iloc[0]
    ds["name"] = df["name"].iloc[-1]
    ds["year"] = ds["time"][0].dt.year.item()
    basin = {"L":"AL", "E":"EP", "W":"WP", "A":"IO", "B":"IO", "S":"SH", "P":"SH"}[ds.nnb.item()[-1]]
    ds["bbnnyyyy"] = basin+ds.nnb.item()[:2]+str(ds.year.item())

    ds["lon"].attrs.update({"name":"lon","long_name":"Longitude","units":"degrees_east"})
    ds["lat"].attrs.update({"name":"lat","long_name":"Latitude","units":"degrees_north"})
    ds["vmax"].attrs.update({"name":"vmax","long_name":"1-min maximum sustained wind","units":"ms-1"})
    ds["vmax_kt"].attrs.update({"name":"vmax_kt","long_name":"1-min maximum sustained wind","units":"kt"})
    ds["pres"].attrs.update({"name":"pres","long_name":"Pressure","units":"hPa"})
    ds["nnb"].attrs.update({"name":"nnb","long_name":"Number and basin","units":""})
    ds["name"].attrs.update({"name":"name","long_name":"TC name","units":""})
    ds["year"].attrs.update({"name":"year","long_name":"Year","units":""})
    ds["bbnnyyyy"].attrs.update({"name":"bbnnyyyy","long_name":"bbnnyyyy","units":""})
    return ds

def get_jtwc_bt_from_navy(bbnnyyyy):
    """
    Parameters
    ----------
    bbnnyyyy : str
        ID for a TC consisting of [bb:basin][nn:number][yyyy:year]
        e.g., WP052023
    """
    text = _get_jtwc_bt_text_from_navy(bbnnyyyy)
    rows = _rawtext_to_rows(text)
    ds = _read_jtwc_bt_from_rows(rows)
    return ds

def get_NESDIS_SAR_ATCF_urls(bbnnyyyy):
    """
    Retrieve SAR ATCF URLs from the NESDIS website.

    Parameters
    ----------
    bbnnyyyy : str
        The year and storm code in the format 'BBNNYYYY'.

    Returns
    -------
    List[str]
        A list of SAR ATCF URLs.

    Raises
    ------
    urllib.error.URLError
        If there is an error in the URL request.
    """
    bbnnyyyy = bbnnyyyy.upper()
    year = bbnnyyyy[-4:]

    sar_header = "https://www.star.nesdis.noaa.gov/socd/mecb/sar"
    url = f"{sar_header}/sarwinds_tropical.php"
    ssl._create_default_https_context = ssl._create_unverified_context
    response = urllib.request.urlopen(url)
    html = response.read().decode('utf-8')

    pattern = r'(?<=storm=)(\w+)_([A-Za-z\-]+)'
    name_mapping = dict(re.findall(pattern, html))

    if bbnnyyyy not in name_mapping.keys():
        return []
    name = name_mapping[bbnnyyyy]
    url = f"{sar_header}/sarwinds_tropical.php?year={year}&storm={bbnnyyyy}_{name}"

    ssl._create_default_https_context = ssl._create_unverified_context
    response = urllib.request.urlopen(url)
    html = response.read().decode('utf-8')

    pattern = r'AKDEMO_products/[^"]+\.xfer'
    sar_atcf_url_matches = re.findall(pattern, html)
    sar_atcf_urls = sorted(list(set(sar_atcf_url_matches)))
    sar_atcf_urls = list(map(lambda x: sar_header+"/"+x, sar_atcf_urls))
    return sar_atcf_urls

def download_SAR_ATCF_from_NESDIS(bbnnyyyy, odir="./"):
    """
    Downloads SAR ATCF data from NESDIS.

    Parameters
    ----------
    bbnnyyyy : str
        BBNNYYYY format string representing the desired data.
    odir : str, optional
        Output directory to save the downloaded data. Defaults to current directory.

    Returns
    -------
    ds : xarray.Dataset
        Xarray Dataset containing the downloaded SAR ATCF data.
    """
    sar_atcf_urls = get_NESDIS_SAR_ATCF_urls(bbnnyyyy)
    times, vmaxs_kt, rmws_nmi = [], [], []
    for sar_atcf_url in sar_atcf_urls:
        ssl._create_default_https_context = ssl._create_unverified_context
        table = pd.read_csv(sar_atcf_url, header=None)
        times.append(table.loc[0][2])
        vmaxs_kt.append(table.loc[0][11])
        rmws_nmi.append(table.loc[0][27])
    
    df = pd.DataFrame(np.array([times, vmaxs_kt, rmws_nmi]).T, columns=["time", "vmax_kt", "rmw_nmi"])
    df["time"] = pd.to_datetime(df["time"], format="%Y%m%d%H%M")
    df["vmax"] = np.round(knot_to_ms(df["vmax_kt"]),1)
    df["rmw"] = np.round(nmi_to_km(df["rmw_nmi"]),1)

    oname = bbnnyyyy + "_NESDIS_SAR.csv"
    df.to_csv(odir+"/"+oname, index_label="index")
    ds = df.to_xarray()
    return ds

def get_jma_bt_from_DigitalTyphoon(year, nn):
    """
    Parameters
    ----------
    year : int or str
        Year.
    nn : int or str
        Number of Typhoon.
    """
    url_header = "http://agora.ex.nii.ac.jp/digital-typhoon/summary/wnp/l"
    yyyynn = str(year)+str(nn).zfill(2)
    url = f"{url_header}/{yyyynn}.html.en"

    ssl._create_default_https_context = ssl._create_unverified_context
    try:
        response = urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise FileNotFoundError(f"Typhoon No.{nn} ({year}) is not found at {url}")
    text = response.read().decode('utf-8')
    soup = bs4.BeautifulSoup(text, 'html.parser')

    tyname_line = soup.find("div", attrs={"class":"TYNAME"}).text
    name = re.findall(r'Typhoon \d{6} \((.*?)\)', tyname_line)[0]
    latest_update_line = soup.find("td", attrs={"class", "INFOUPDATED"}).text
    latest_update = pd.to_datetime(re.findall(r'\d{4}-\d{2}-\d{2}', latest_update_line)[0])

    # Read Track
    pickup_lines = (soup.find_all("tr", attrs={"class", "ROW1", "ROW0"}))
    columns = ["time", "lat", "lon", "pres", "vmax_kt", "grade"]
    df = pd.DataFrame(np.full([len(pickup_lines), len(columns)], np.nan), columns=columns, index=None)
    for i, info in enumerate(pickup_lines):
        dfi = info.get_text().split()
        time = pd.Timestamp(int(dfi[0]), int(dfi[1]), int(dfi[2]), int(dfi[3]))
        lat, lon, pres, vmax_knot, grade = float(dfi[4]), float(dfi[5]), int(dfi[6]), int(dfi[7]), int(dfi[8])
        df.iloc[i,:] = time, lat, lon, pres, vmax_knot, grade
    df["vmax"] = np.round(knot_to_ms(df["vmax_kt"]),1)
    ds = df.to_xarray().swap_dims({"index": "time"})
    ds[["vmax_kt", "pres"]] = ds[["vmax_kt", "pres"]].astype(int)

    ds["name"] = name
    ds.attrs.update({
        "latest_update": latest_update.strftime("%Y-%m-%d %H:%M:%S")
    })
    return ds

def get_JMA_number_name_mapping(year):
    url = f"http://agora.ex.nii.ac.jp/digital-typhoon/year/wnp/{year}.html.en"
    ssl._create_default_https_context = ssl._create_unverified_context
    response = urllib.request.urlopen(url)
    text = response.read().decode('utf-8')
    soup = bs4.BeautifulSoup(text, 'html.parser')
    table = soup.find("table", attrs={"class":"TABLELIST"})
    rows = table.find_all("tr")[1:]
    
    mapping = {}
    for row in rows:
        columns = row.find_all("td")
        nn = columns[1].text[-2:]
        name = columns[2].text
        mapping[name] = nn
    return mapping