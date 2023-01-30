#!/usr/bin/env python
"""
ivs create inventory valueation summmary sheet
"""

import os
from decimal import Decimal
from datetime import datetime
from datetime import timedelta
from platform import system
import fdb
import itertools
import click
from dotenv import load_dotenv
from csv import DictReader


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)



def do_it_all(file_name):
    # data section
    state_data = {"AK": 876, "CA": 418, "WA": 415}

    # read csv file get locations 
    with open(os.environ.get('FILE'),'r') as f:
        dict_reader = DictReader(f)
        tax_table = list(dict_reader)

    # get SETs of unique zip codes and states
    csv_locations = set([location['ZipCode']  for location in tax_table])
    csv_states = set([location['State']  for location in tax_table])

    # convert states into list of state_id's
    state_ids = [state_data[state] for state in csv_states]

    # create database connection we will leave open till we are done with things
    con = fdb.connect(
      host=os.environ.get('DB_HOST'),
      database=os.environ.get('DB_DATABASE'),
      user=os.environ.get('DB_USER'),
      password=os.environ.get("DB_PASSWORD"),
      charset='WIN1252'
    )
    cur = con.cursor()

    # find recrods in database to update
    select = (
        """SELECT name, description, rate FROM taxrate WHERE activeflag = 1 AND VENDORID IN (""" +
        ("?," * len(state_ids))[:-1] +
        """);"""
    )
    _ = cur.execute(select, state_ids)
    locations = cur.fetchallmap()

    # get SETs of unique zip codes 
    sql_locations = set([location['NAME']  for location in locations])

    # find locations in both sql and csv for UPDATEing
    updates = []
    for location in sql_locations.intersection(csv_locations):
        item = [item for item in tax_table if item['ZipCode'] == str(location)][0]
        updates.append((round(float(item['EstimatedCombinedRate']),4), item['ZipCode']))

    _ = cur.executemany("UPDATE taxrate SET rate = ?, datelastmodified = current_timestamp WHERE activeflag = 1 AND name = ?;", updates)
    con.commit()

    # get max rexord
    _ = cur.execute("SELECT MAX(id) FROM taxrate;")
    num = cur.fetchone()[0]

    # find locations in csv and not in sql for INSERTING
    inserts = []
    for location in  csv_locations.difference(sql_locations):
        num = num+1
        item = [item for item in tax_table if item['ZipCode'] == str(location)][0]
        inserts.append((num, item['ZipCode'], item['TaxRegionName'], round(float(item['EstimatedCombinedRate']),4), state_data[item['State']]))

    sql = (
        """INSERT INTO taxrate (""" +
        """id, name, code, description, rate, unitcost, typeid, defaultflag, vendorid, datecreated, datelastmodified, """ +
        """taxaccountid, accountingid, accountinghash, activeflag, ordertypeid, typecode) """ +
        """VALUES (?, ?, '', ?, ?, 0.0, 10, 0, ?, current_timestamp, current_timestamp, NULL, '', '', 1, NULL, '');"""
    )
    _ = cur.executemany(sql, inserts)
    con.commit()

    cur.close()
    con.close()



if __name__ == "__main__":
    load_dotenv(resource_path('.env'))  # use os.environ.get()
    do_it_all(os.environ.get('FILE'))
    # application = QApplication()
    # dialog = Dialog()
    # dialog.show()
    # sys.exit(application.exec_())
