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


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)



def read_firebird_database():
    """Create Inventory Value Summary from Fishbowl"""
    stock = []
    con = fdb.connect(
        host=os.environ.get('HOST'),
        database=os.environ.get('DATABASE'),
        user=os.environ.get('USER'),
        password=os.environ.get("PASSWORD"),
        charset='WIN1252'
    )

    select = """
    SELECT locationGroup.name AS "Group",
        COALESCE(partcost.avgcost, 0) AS averageunitcost,
        COALESCE(part.stdcost, 0) AS standardunitcost,
        locationgroup.name AS locationgroup,
        part.num AS partnumber,
        part.description AS partdescription,
        location.name AS location, asaccount.name AS inventoryaccount,
        uom.code AS uomcode, sum(tag.qty) AS qty, company.name AS company
    FROM part
        INNER JOIN partcost ON part.id = partcost.partid
        INNER JOIN tag ON part.id = tag.partid
        INNER JOIN location ON tag.locationid = location.id
        INNER JOIN locationgroup ON location.locationgroupid = locationgroup.id
        LEFT JOIN asaccount ON part.inventoryaccountid = asaccount.id
        LEFT JOIN uom ON uom.id = part.uomid
        JOIN company ON company.id = 1
    WHERE locationgroup.id IN (1)
    GROUP BY averageunitcost, standardunitcost, locationgroup, partnumber,
        partdescription, location, inventoryaccount, uomcode, company
    """

    select = """
    SELECT name, description FROM taxrate WHERE name = '98520'
    """
    cur = con.cursor()
    cur.execute(select)
    for (name, description) in cur:
        print(name, description)

    """
    for (group, avgcost, stdcost, locationgroup, partnum, partdescription,
         location, invaccount, uom, qty, company) in cur:
        if location in exclude:
            continue
        if include and location not in include:
            continue
        stock.append([
            location,
            partnum,
            partdescription,
            str(Decimal(str(qty)).quantize(Decimal("1.00"))),
            uom,
            str(Decimal(str(avgcost)).quantize(Decimal("1.00"))),
        ])

    stock = sorted(stock, key=lambda k: (k[0], k[1]))
    return stock
    """

if __name__ == "__main__":
    load_dotenv(resource_path('.env'))  # use os.environ.get()
    read_firebird_database()
    # application = QApplication()
    # dialog = Dialog()
    # dialog.show()
    # sys.exit(application.exec_())
