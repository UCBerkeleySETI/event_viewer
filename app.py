import csv
from flask import Flask, render_template, request, redirect, url_for
import requests
from pager import Pager
import pandas as pd

import sys
try:
    import argparse
    p = argparse.ArgumentParser(description='BL Event Viewer')
    p.add_argument('band', type=str, help="Choose band to view (L or S)")
    p.add_argument("--port", type=int, default=5000, help="TCP port to run server on")
    args = p.parse_args()
    assert args.band in ('L', 'S')
except:
    print("Usage: ./app.py band (L or S)")

if args.band == 'L':
    APPNAME = "BL Event Viewer - L-band"
    STATIC_FOLDER = 'lband2019'
    TABLE_FILE    = 'lband2019/lband2019_events.csv'
elif args.band == 'S':
    APPNAME = "BL Event Viewer - S-band"
    STATIC_FOLDER = 'sband2019'
    TABLE_FILE = 'sband2019/sband2019_events.csv'


def read_table(url):
    """Return a list of dict"""
    # r = requests.get(url)
    #with open(url) as f:
    #    return [row for row in csv.DictReader(f.readlines())]
    df= pd.read_csv(TABLE_FILE)
    df['ID'] = df['ID'].astype(str)
    return df

app = Flask(__name__, static_folder=STATIC_FOLDER)
app.config.update(
    APPNAME=APPNAME,
    )

table = read_table(TABLE_FILE)
pager = Pager(len(table))

@app.route('/')
def index():
    return redirect('/0')


@app.route('/<int:ind>/')
def image_view(ind=None):
    if ind >= pager.count:
        return render_template("404.html"), 404
    else:
        pager.current = ind
        return render_template(
            'imageview.html',
            index=ind,
            pager=pager,
            data=dict(table.iloc[ind])
            )

@app.route('/viewall/')
def view_all_all0():
    return redirect('/viewall/freqs/all') 


@app.route('/viewall/<string:sortidx>')
def view_all_all(sortidx=None):
    return redirect('/viewall/%s/all' % sortidx)


@app.route('/viewall/<string:sortidx>/<string:srcid>/<int:fstart>/<int:fstop>')
@app.route('/viewall/<string:sortidx>/<string:srcid>/<float:fstart>/<float:fstop>')
def image_view_fstart_fstop(sortidx=None, srcid=None, fstart=None, fstop=None):
    if srcid is not None and srcid != 'all':
        stbl = table[table['Source'].str.lower() == srcid.lower()]
    else:
        stbl = table
    if fstart is not None:
        stbl = stbl[stbl['FreqMid'] > fstart]
    if fstop is not None:
        stbl = stbl[stbl['FreqMid'] < fstop]

    if sortidx in ('freq', 'frequency', 'freqs'):
        stbl = stbl.sort_values('FreqMid')
    elif sortidx in ('src', 'source'):
        stbl = stbl.sort_values('Source')
    elif sortidx in ('driftrate', 'drate'):
        stbl = stbl.sort_values('DriftRateMax')
    elif sortidx in ('nevent', 'events', 'event'):
        stbl = stbl.sort_values('Nevent')

    return render_template(
        'imageview_all.html',
        srcid=srcid,
        data=zip(stbl.index, stbl['PngFile'])
        )

@app.route('/viewall/<string:sortidx>/<string:srcid>')
def image_view_all(sortidx=None, srcid=None):
    if srcid is not None and srcid != 'all':
        stbl = table[table['Source'].str.lower() == srcid.lower()]
    else:
        stbl = table
    if sortidx in ('freq', 'frequency', 'freqs'):
        stbl = stbl.sort_values(['FreqMid', 'Source'])
    elif sortidx in ('src', 'source'):
        stbl = stbl.sort_values('Source')
    elif sortidx in ('driftrate', 'drate'):
        stbl = stbl.sort_values(['DriftRateMax', 'Source'])
    elif sortidx in ('nevent', 'events', 'event'):
        stbl = stbl.sort_values(['Nevent', 'Source'])

    return render_template(
        'imageview_all.html',
        srcid=srcid,
        data=zip(stbl.index, stbl['PngFile'])
        )

@app.route('/goto', methods=['POST', 'GET'])    
def goto():
    return redirect('/' + request.form['index'])

@app.route('/hitsinoff/<int:ind>')
def dbupdate_hits_in_off(ind):
    table.loc[ind, 'HitCategory'] = 'Hits in off'
    table.to_csv(TABLE_FILE)
    return "Nothing"

@app.route('/followup/<int:ind>')
def dbupdate_followup(ind):
    table.loc[ind, 'HitCategory'] = 'Requires follow up'
    table.to_csv(TABLE_FILE)
    return "Nothing"

@app.route('/plottingissue/<int:ind>')
def dbupdate_plotting_issue(ind):
    table.loc[ind, 'HitCategory'] = 'Plotting issue'
    table.to_csv(TABLE_FILE)
    return "Nothing"

@app.route('/interestingnotet/<int:ind>')
def dbupdate_interesting_not_et(ind):
    table.loc[ind, 'HitCategory'] = 'Interesting but not ET'
    table.to_csv(TABLE_FILE)
    return "Nothing"




if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=args.port)
