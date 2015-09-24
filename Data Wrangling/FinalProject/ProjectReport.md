OpenStreetMap Project Data Wrangling with MongoDB
=================================================
_Abhinav Solan_
---------------

Map Area: [San Francisco, United States](http://www.openstreetmap.org/export#map=15/37.7650/-122.4435)

## 1. Problems Encountered in the Map
* Format of Phone numbers is not consistent overall the data, some are like +1 xxx xxxxxxx while some are (xxx) xxx xxxx
* In some cases phone and webstie are added as contact:phone or contact:website in the tags, adding them as values in phone and website directly.
* Some postal codes are not correct, in some of the entries people have added complete address in the postcode field which is not correct.

### Varied formats of Phone Numbers
Looking over the formats of provided phone numbers showed a varied formats given, e.g +1 123 456 7890 or +1 (123) 456 7890 or +1.123.456.7890 etc. some other formats were also in the document. To solve this I took last 10 valid numbers provided in the string, so now +1 (123) 456 7890 changes to 1234567890 only.

### Phone and Website lying under some other tag
In most of the cases phone and website were represented like this in the osm-
```xml
<tag k="phone" v="(415) 648-4104" />
<tag k="website" v="http://www.thegrowlersarms.com/" />
```
but in some cases it was like
```xml
<tag k="contact:phone" v="(415) 648-4104" />
<tag k="contact:website" v="http://www.thegrowlersarms.com/" />
```
And osm to json parsing was including them as contact:phone or contact:website only. To fix this I removed *contact:* from the key and replaced it with the ending string, so that we have uniform phone and website for the nodes and could be used in queries as well.

### Complete address showing up in postal code
In osm at some places people have added the complete address in the postcode, so while parsing it to json I am skipping these types of postcodes.
```xml
<tag k="addr:postcode" v="34 Church St, San Juan Bautista, CA 95045" />
```
Also there is one other format in postal code, which I am taking in consideration, but this would be split into postal code and postal area code.
```xml
<tag k="addr:postcode" v="95045-1234" />
```

## 2. Data Overview
This section contains the basic statistics about the dataset and MongoDB queries used to accumulate them.

### File Sizes

* san_fran.osm ........... 74 mb
* san_fran.osm.json .... 83 mb

### Data Analysis
#### # Number of documents
```sh
> db.find().count()
393461
```

#### # Number of nodes
```sh
> db.find({"type":"node"}).count()
358259
```

#### # Number of ways
```sh
> db.find({"type":"way"}).count()
35201
```

#### # Number of distinct users
```sh
> len(db.distinct('created.user'))
396
```

#### # Top Contributor
```sh
> db.aggregate([{'$group': {'_id': '$created.user', 'count': {'$sum': 1}}},
>               {'$sort': {'count': -1}}, {'$limit': 1}])
{'_id': 'ediyes', 'count': 185571}
```

#### # Number of contributors contributing more than 100 times
```sh
> db.aggregate([{'$group': {'_id': '$created.user', 'count': {'$sum': 1}}},
>               {'$match': {'count': {'$gte': 100}}},
>               {'$group': {'_id': 'null', 'count': {'$sum': 1}}}])
{'count': 36, '_id': 'null'}
```

## 3. Additional ideas

#### Suggestions for Data improvement

Data represented in the file, does not looks complete anyway, it would need to fetch data from multiple sources, listed are the few ideas I can think which might help.
* More users need to contribute to the data, to make it more interesting and increase user contribution, in the openstreetapp we can include some features like adding a review of a place, this could give motivation to that owner of the business to go and add some related data for the map.
* Also we can make the app more interesting and add few cool features like expressing emotions about how people feel while they are stuck in traffic, a social connect while stuck in a traffic jam could direct some more traffic to the app.
* We can go to the postal codes database and from the latitude longitude of and from the geospatial queries in MongoDB we can atleast add correct postal code for the given location.
* We can also make use of Google API or geocoder.ca APIs for fetching data for the map, but this would have limitation as the API calls are free for a certain limit only after that those would need subscription.

Parse the requested xml in the tree
```python
import xml.etree.ElementTree as ET
import urllib.request

tree = ET.fromstring(urllib.request.urlopen('http://geocoder.ca/37.7793173,-122.4508425?geoit=xml').read())
```
Resulting xml is

```xml
 <?xml version="1.0" encoding="UTF-8" ?>
<result>
    <geodata>
       <latt>37.779099</latt>
       <longt>-122.451448</longt>
       <city>San Francisco</city>
       <prov>CA</prov>
       <postal>94118</postal>
       <stnumber>2600</stnumber>
       <staddress>TURK BLVD</staddress>
       <inlatt>37.779317</inlatt>
       <inlongt>-122.450842</inlongt>
       <distance>0.059</distance><NearRoad>TURK BLVD</NearRoad>
       <NearRoadDistance>0.046</NearRoadDistance>
       <betweenRoad1>Roselyn</betweenRoad1>
       <betweenRoad2>Kittredge</betweenRoad2>
       <neighborhood>Anza Vista</neighborhood>
       <confidence></confidence>
       <intersection>
           <street1>Turk St</street1>
           <street2>Kittredge Ter</street2>
           <lattx>37.778165</lattx>
           <longtx>-122.450655</longtx>
           <city>Western Addition</city>
           <prov>CA</prov>
           <distance>0.129</distance>
       </intersection>
       <major_intersection>
           <street1>Turk Blvd</street1>
           <street2>Roselyn Ter</street2>
           <lattx>37.7782770000</lattx>
           <longtx>-122.4497670000</longtx>
           <city>San Francisco</city>
           <prov>CA</prov>
           <distance>0.149</distance>
       </major_intersection>
       <usa>
           <latt>37.7790988000</latt>
           <longt>-122.4514481000</longt>
           <uscity>San Francisco</uscity>
           <state>CA</state>
           <zip>94118</zip>
           <usstnumber>2600</usstnumber>
           <usstaddress>TURK BLVD</usstaddress>
           <inlatt>37.779317</inlatt>
           <inlongt>-122.450842</inlongt>
           <distance>0.059</distance>
       </usa>
    </geodata>
</result>
```

fetch the address tags in geodata
```python
geodata = tree.getchildren()[0]
```
set the address fields in the json
```python
node['address']['city'] = geodata[2]
node['address']['postcode'] = geodata[4]

```
Similarly add fields from the xml tags in the json, similar thing can be done using Google APIs as well.


### Additional Data exploration using MongoDB queries

#### # Top listed amenities
```sh
> db.aggregate([{'$match': {'amenity': {'$exists': 1}}},
>               {'$group': {'_id': '$amenity', 'count': {'$sum': 1}}},
>               {'$sort': {'count': -1}},
>               {'$limit': 10}])
{'_id': 'restaurant', 'count': 307}
{'_id': 'parking', 'count': 124}
{'_id': 'bicycle_parking', 'count': 119}
{'_id': 'post_box', 'count': 108}
{'_id': 'cafe', 'count': 104}
{'_id': 'bench', 'count': 94}
{'_id': 'place_of_worship', 'count': 84}
{'_id': 'school', 'count': 73}
{'_id': 'car_sharing', 'count': 65}
{'_id': 'bar', 'count': 51}
```

#### # Religion Numbers
```sh
> db.aggregate([{'$match': {'amenity': {'$exists': 1}, 'amenity': 'place_of_worship'}},
>               {'$group': {'_id': '$religion', 'count': {'$sum': 1}}},
>               {'$sort': {'count': -1}},
>               {'$limit': 10}])
{'_id': 'christian', 'count': 76}
{'_id': 'buddhist', 'count': 3}
{'_id': 'bahai', 'count': 1}
```

#### # Popular Cuisines
```sh
> db.aggregate([{'$match': {'amenity': {'$exists': 1}, 'amenity': 'restaurant'}},
>               {'$match': {'cuisine': {'$exists': 1}}},
>               {'$group': {'_id': '$cuisine', 'count': {'$sum': 1}}},
>               {'$sort': {'count': -1}},
>               {'$limit': 10}])
{'_id': 'mexican', 'count': 24}
{'_id': 'american', 'count': 17}
{'_id': 'japanese', 'count': 15}
{'_id': 'thai', 'count': 14}
{'_id': 'pizza', 'count': 14}
{'_id': 'chinese', 'count': 10}
{'_id': 'sushi', 'count': 9}
{'_id': 'burger', 'count': 8}
{'_id': 'indian', 'count': 7}
{'_id': 'vietnamese', 'count': 6}

```
#### # Postal Code with max number of restaurants
```sh
> db.aggregate([{'$match': {'amenity': {'$exists': 1}, 'amenity': 'restaurant'}},
>               {'$match': {'address.postcode': {'$exists': 1}}},
>               {'$group': {'_id': '$address.postcode', 'count': {'$sum': 1}}},
>               {'$sort': {'count': -1}},
>               {'$limit': 10}])
{'_id': '94122', 'count': 49}
{'_id': '94114', 'count': 32}
{'_id': '94110', 'count': 23}
{'_id': '94103', 'count': 18}
{'_id': '94117', 'count': 14}
{'_id': '94102', 'count': 10}
{'_id': '94115', 'count': 3}
```
