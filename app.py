import csv
from flask import Flask, render_template, request, redirect, url_for
import requests
from pager import Pager
import pandas as pd
import h5py

APPNAME = "BL Event Viewer"
STATIC_FOLDER = 'static'
L_TABLE_FILE    = 'static/lband2019/lband2019_events.h5'
S_TABLE_FILE = 'static/sband2019/sband2019_events.h5'

def read_table(url):
    """Return a list of dict"""
    with h5py.File(url) as h5:
        dd = dict([(col, h5[col][:]) for col in h5.keys()])
    df= pd.DataFrame.from_dict(dd)
    df['ID'] = df['ID'].astype(str)
    return df

app = Flask(__name__, static_folder=STATIC_FOLDER)
app.config.update(
    APPNAME=APPNAME,
    )

l_table = read_table(L_TABLE_FILE)
s_table = read_table(S_TABLE_FILE)
l_pager = Pager(len(l_table))
s_pager = Pager(len(s_table))

def get_db(band):
    band = band.upper().strip()
    hc = _load_hits(band)
    if band == 'L':
        l_table['HitCategory'] = hc
        return l_table, l_pager
    elif band == 'S':
        s_table['HitCategory'] = hc
        return s_table, s_pager

def _load_hits(band):
    """ Reload hit category -- only call from get_db """
    band = band.upper().strip()
    if band == 'L':
        h5 = h5py.File(L_TABLE_FILE)
    elif band == 'S':
        h5 = h5py.File(S_TABLE_FILE)
    hc = h5['HitCategory'][:]
    h5.close()
    return hc

def _update_hits(band, idx, val):
    """ Reload hit category -- only call from get_db """
    band = band.upper().strip()
    if band == 'L':
        h5 = h5py.File(L_TABLE_FILE)
    elif band == 'S':
        h5 = h5py.File(S_TABLE_FILE)
    h5['HitCategory'][idx] = val
    print "Updating db: %s" % val
    h5.close()

def sort_table(stbl, sortidx):
    if sortidx in ('freq', 'frequency', 'freqs'):
        stbl = stbl.sort_values('FreqMid')
    elif sortidx in ('src', 'source'):
        stbl = stbl.sort_values('Source')
    elif sortidx in ('driftrate', 'drate'):
        stbl = stbl.sort_values('DriftRateMax')
    elif sortidx in ('nevent', 'events', 'event'):
        stbl = stbl.sort_values('Nevent')
    return stbl


@app.route('/')
@app.route('/l')
def index():
    return redirect('/l/0')

@app.route('/s')
def indexS():
    return redirect('/s/0')

@app.route('/<string:band>/<int:ind>/')
def image_view(band='L', ind=None):
    table, pager = get_db(band)
    if ind >= pager.count:
        return render_template("404.html"), 404
    else:
        pager.current = ind
        return render_template(
            'imageview.html',
            index=ind,
            band=band,
            pager=pager,
            data=dict(table.iloc[ind])
            )

@app.route('/<string:band>/viewall/')
def view_all_all0(band):
    return redirect('/%s/viewall/freqs/all' %band ) 


@app.route('/<string:band>/viewall/<string:sortidx>')
def view_all_all(band='L', sortidx=None):
    return redirect('/%s/viewall/%s/all' % (band, sortidx))


@app.route('/<string:band>/viewall/<string:sortidx>/<string:srcid>/<int:fstart>/<int:fstop>')
@app.route('/<string:band>/viewall/<string:sortidx>/<string:srcid>/<float:fstart>/<float:fstop>')
def image_view_fstart_fstop(band='L', sortidx=None, srcid=None, fstart=None, fstop=None):
    table, pager = get_db(band)
    if srcid == 'candidates':
        stbl = table[table['HitCategory'].str.contains('follow up')] 
    elif srcid is not None and srcid != 'all':
        stbl = table[table['Source'].str.lower() == srcid.lower()]
    else:
        stbl = table
    if fstart is not None:
        stbl = stbl[stbl['FreqMid'] > fstart]
    if fstop is not None:
        stbl = stbl[stbl['FreqMid'] < fstop]
    stbl = sort_table(stbl, sortidx)
    return render_template(
        'imageview_all.html',
        srcid=srcid,
        band=band,
        data=zip(stbl.index, stbl['PngFile'])
        )

@app.route('/<string:band>/viewall/<string:sortidx>/<string:srcid>')
def image_view_all(band, sortidx=None, srcid=None):
    table, pager = get_db(band)
    if srcid == 'candidates':
        stbl = table[table['HitCategory'].str.contains('follow up')] 
    elif srcid is not None and srcid != 'all':
        stbl = table[table['Source'].str.lower() == srcid.lower()]
    else:
        stbl = table

    stbl = sort_table(stbl, sortidx)
    return render_template(
        'imageview_all.html',
        srcid=srcid,
        band=band,
        data=zip(stbl.index, stbl['PngFile'])
        )

@app.route('/goto', methods=['POST', 'GET'])    
def goto():
    return redirect('/' + request.form['index'])

@app.route('/<string:band>/hitsinoff/<int:ind>')
def dbupdate_hits_in_off(band, ind):
    _update_hits(band, ind, 'Hits in off')
    return "Nothing"

@app.route('/<string:band>/followup/<int:ind>')
def dbupdate_followup(band, ind):
    _update_hits(band, ind, 'Requires follow up')
    return "Nothing"

@app.route('/<string:band>/plottingissue/<int:ind>')
def dbupdate_plotting_issue(band, ind):
    _update_hits(band, ind, 'Plotting issue')
    return "Nothing"

@app.route('/<string:band>/interestingnotet/<int:ind>')
def dbupdate_interesting_not_et(band, ind):
    _update_hits(band, ind, 'Interesting but not ET')
    return "Nothing"

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0')
