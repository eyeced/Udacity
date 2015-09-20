#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json


def insert(file_name):
    from pymongo import MongoClient
    client = MongoClient('mongodb://localhost:27017/')
    print(client.database_names())
    db = client.city.cities
    with open(file_name, 'r') as f:
        data = json.loads(f.read())
        db.insert(data)
        print(db.find_one())

if __name__ == "__main__":
    insert('san_fran.osm.json')
