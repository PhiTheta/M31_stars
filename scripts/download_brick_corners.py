"""
Obtain the corners of PHAT bricks from the webpage and write them in a csv
file. The corners are the min and max of ra and dec values of stars in
in the brick. The brick column provides the bricknumber followed by digits
to make each entry unique.
"""
import os
import requests
import numpy as np
import pandas as pd
from astropy.io import fits
from astropy.table import Table
from bs4 import BeautifulSoup as Soup


def get_link(url):
    """
    """
    r  = requests.get(url)
    s = Soup(r.content.decode().split('html')[1]).findAll('a')[0]['href']
    print('will download file from url {}'.format(s))
    return s

def get_names(link_url):

    names = link_url.split('phat/')[1].split('/')[0] 
    return link_url, names + '.fits'

def download_file(url, fname):
    """
    url : 
    fname : name of file to save to
    """
    r = requests.get(url, allow_redirects=True)
    print('obtain requests')
    with open(fname, 'wb') as fh:
        fh.write(r.content)
    return

def get_corners(fitsfile):
    ra = 'ra'
    dec = 'dec'
    fh = fits.open(fitsfile)
    df =  Table(fh[1].data).to_pandas()
    c0 = df[ra].idxmax()
    c1 = df[ra].idxmin()
    c2 = df[dec].idxmax()
    c3 = df[dec].idxmin()
    return df.loc[[c0, c1, c2, c3]][[ra, dec]]

def delete_file(fname):
    os.remove(fname)

    
if __name__ == '__main__':

    dfs = []
    with open('failures.csv', "w+") as fh:
        fh.write('Failures\n')
    for bricknumber in np.arange(1, 24)[::-1]:
        try:
            website = 'http://archive.stsci.edu/pub/hlsp/phat/brick{}/'.format(bricknumber)
            link = get_link(website)
            url, fname = get_names(link)
            print('will get file from url {0}, and save it as {1}'.format(url, fname))
            download_file(url, fname)
            x = get_corners(fname)
            x['brick'] = bricknumber * 10 + np.arange(len(x))
            dfs.append(x)
            pd.concat(dfs).to_csv('partial_corners.csv', index=False)
            os.remove(fname)
        except:
            with open('failures.csv', "a+") as fh:
                fh.write('{}\n'.format(bricknumber))

            
    df = pd.concat(dfs)
    df.to_csv('corners.csv', index=False)
    os.remove('partial_corners.csv')
