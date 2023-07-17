import email
import logging
import os
import requests

from tqdm import tqdm


basedir = os.path.join(os.path.dirname(__file__), "..")


def filename_from_header(h):
    # Note cgi deprectation: https://peps.python.org/pep-0594/#cgi
    m = email.message.Message()
    m['content-type'] = h
    return m.get_param('filename')


def download(url):
    """ Download in chunks with status bar.  Adapted from https://gist.github.com/yanqd0/c13ed29e29432e3cf3e7c38467f42f51 """
    resp = requests.get(url, stream=True)
    logging.debug(resp.headers)

    os.makedirs("data", exist_ok=True)
    fname = os.path.join(basedir, "data", filename_from_header(resp.headers['Content-Disposition']))

    total = int(resp.headers.get('content-length', 0))
    with open(fname, 'wb') as file, tqdm(
            desc=fname,
            total=total,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data) 
            # "Content-Encoding = gzip" means file size inflated compared to "Content-Length"
            # bar.update(size)  # <-- this will track actual downloaded file size (but overflow the % status bar)
            bar.update(1024)  # <-- this will correctly track % complete (but undercount the downloaded file size)


if __name__ == '__main__':

    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    datasets = []

    # ########################################################
    # # Dataset: Nigeria Settlement Extents Version 01.02
    # # Explore at https://data.grid3.org/datasets/1cbdf89be31f4ebfac304c352c700ee9_0
    # # GeoJSON: 3.4 GB (976.0 MB gzip)
    # datasets += ["1cbdf89be31f4ebfac304c352c700ee9_0"]

    # ########################################################
    # # Dataset: Nigeria Settlement Points
    # # Explore at https://data.grid3.org/datasets/GRID3::nigeria-settlement-points
    # # GeoJSON: 157.8 MB (28.3 MB gzip)
    # datasets += ["73d8522d1c4d4c75be6c10fa790c685c_0"]

    ########################################################
    # Dataset: Nigeria - State Boundaries
    # Explore at https://data.grid3.org/datasets/GRID3::nigeria-state-boundaries/explore
    # GeoJSON: 2.3 MB (734.7 KB gzip)
    datasets += ["c41532b720504f4799fe20438b7e3b7f_0"]

    format = "geojson"
    for dataset in datasets:
        url = f"https://opendata.arcgis.com/api/v3/datasets/{dataset}/downloads/data?format={format}&spatialRefId=4326&where=1%3D1"
        download(url)