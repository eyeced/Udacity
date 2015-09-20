OpenStreetMap Project Data Wrangling with MongoDB
=================================================
_Abhinav Solan_
---------------

Map Area: [San Francisco Bay Area, United States](https://s3.amazonaws.com/metro-extracts.mapzen.com/san-francisco-bay_california.osm.bz2)

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

* san-francisco-bay_california.osm ........... 1946 mb
* san-francisco-bay_cali_reduced.osm ......... 396 mb
* san-francisco-bay_cali_reduced.osm.json .... 446 mb

### Data Analysis
#### # Number of documents
```sh
> db.find().count()
2085162
```

#### # Number of nodes
```sh
> db.find({"type":"node"}).count()
1901446
```

#### # Number of ways
```sh
> db.find({"type":"way"}).count()
183622
```

#### # Number of distinct users
```sh
> len(db.distinct('created.user'))
2858
```

#### # Top Contributor
```sh
> db.aggregate([{'$group': {'_id': '$created.user', 'count': {'$sum': 1}}},
>               {'$sort': {'count': -1}}, {'$limit': 1}])
{'count': 367906, '_id': 'nmixter'}
```

#### # Number of contributors contributing more than 100 times
```sh
> db.aggregate([{'$group': {'_id': '$created.user', 'count': {'$sum': 1}}},
>               {'$match': {'count': {'$gte': 100}}},
>               {'$group': {'_id': 'null', 'count': {'$sum': 1}}}])
{'count': 416, '_id': 'null'}
```


### Additional Data exploration using MongoDB queries

#### # Top listed amenities
```sh
> db.aggregate([{'$match': {'amenity': {'$exists': 1}}},
>               {'$group': {'_id': '$amenity', 'count': {'$sum': 1}}},
>               {'$sort': {'count': -1}},
>               {'$limit': 10}])
{'count': 2286, '_id': 'parking'}
{'count': 943, '_id': 'restaurant'}
{'count': 861, '_id': 'school'}
{'count': 620, '_id': 'place_of_worship'}
{'count': 310, '_id': 'cafe'}
{'count': 306, '_id': 'fast_food'}
{'count': 293, '_id': 'bench'}
{'count': 288, '_id': 'toilets'}
{'count': 229, '_id': 'bicycle_parking'}
{'count': 217, '_id': 'fuel'}
```

#### # Second biggest religion

Jewish comes up as second biggest religion with 10 churches in the data and buddhist with 9 place of worships
```sh
> db.aggregate([{'$match': {'amenity': {'$exists': 1}, 'amenity': 'place_of_worship'}},
>               {'$group': {'_id': '$religion', 'count': {'$sum': 1}}},
>               {'$sort': {'count': -1}},
>               {'$limit': 10}])
{'count': 559, '_id': 'christian'}
{'count': 32, '_id': None}
{'count': 10, '_id': 'jewish'}
{'count': 9, '_id': 'buddhist'}
{'count': 4, '_id': 'muslim'}
{'count': 2, '_id': 'scientologist'}
{'count': 1, '_id': 'sikh'}
{'count': 1, '_id': 'eckankar'}
{'count': 1, '_id': 'spiritualist'}
{'count': 1, '_id': 'yogic'}
```

#### # Popular Cuisines
```sh
> db.aggregate([{'$match': {'amenity': {'$exists': 1}, 'amenity': 'restaurant'}},
>               {'$match': {'cuisine': {'$exists': 1}}},
>               {'$group': {'_id': '$cuisine', 'count': {'$sum': 1}}},
>               {'$sort': {'count': -1}},
>               {'$limit': 10}])
{'count': 80, '_id': 'mexican'}
{'count': 72, '_id': 'pizza'}
{'count': 51, '_id': 'chinese'}
{'count': 41, '_id': 'italian'}
{'count': 37, '_id': 'american'}
{'count': 35, '_id': 'japanese'}
{'count': 30, '_id': 'thai'}
{'count': 28, '_id': 'indian'}
{'count': 27, '_id': 'burger'}
{'count': 25, '_id': 'sandwich'}
```
#### # Postal Code with max number of restaurants
```sh
> db.aggregate([{'$match': {'amenity': {'$exists': 1}, 'amenity': 'restaurant'}},
>               {'$match': {'address.postcode': {'$exists': 1}}},
>               {'$group': {'_id': '$address.postcode', 'count': {'$sum': 1}}},
>               {'$sort': {'count': -1}},
>               {'$limit': 10}])
{'count': 12, '_id': '94063'}
{'count': 9, '_id': '94103'}
{'count': 9, '_id': '94110'}
{'count': 8, '_id': '94114'}
{'count': 7, '_id': '94122'}
{'count': 6, '_id': '94109'}
{'count': 6, '_id': '94133'}
{'count': 5, '_id': '94587'}
{'count': 5, '_id': '94115'}
{'count': 5, '_id': '94612'}
```
