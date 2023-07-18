import argparse
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

    os.makedirs(os.path.join(basedir, "data"), exist_ok=True)
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

    parser = argparse.ArgumentParser(
        prog="download_GRID3_data",
        description="Downloads GeoJSON files from GRID3")
    
    parser.add_argument('--nowarn', 
                        action='store_true')
    
    args = parser.parse_args()

    datasets = []

    # ########################################################
    # # Dataset: Nigeria Settlement Extents Version 01.02
    # # Explore at https://data.grid3.org/datasets/1cbdf89be31f4ebfac304c352c700ee9_0
    # # GeoJSON: 3.4 GB (976.0 MB gzip)
    datasets += ["1cbdf89be31f4ebfac304c352c700ee9_0"]

    ########################################################
    # Dataset: Nigeria - State Boundaries
    # Explore at https://data.grid3.org/datasets/GRID3::nigeria-state-boundaries/explore
    # GeoJSON: 2.3 MB (734.7 KB gzip)
    datasets += ["c41532b720504f4799fe20438b7e3b7f_0"]

    logging.info("Datasets to download:\n\t%s", "\n\t".join(datasets))

    if not args.nowarn:
        while True:
            user_input = input("Are you sure you want to download several GBs worth of GeoJSON files? (y/n)")
            if user_input.lower() == "y":
                break
            elif user_input.lower() == "n":
                logging.info("Canceling large-file downloads...")
                import sys
                sys.exit()
            else:
                print("Type 'y' or 'n'")

    logging.info("Downloading...")

    format = "geojson"
    for dataset in datasets:
        url = f"https://opendata.arcgis.com/api/v3/datasets/{dataset}/downloads/data?format={format}&spatialRefId=4326&where=1%3D1"
        download(url)