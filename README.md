# sampleGEE
## Preparation

There are several required libraries before the start:
- Google Earth Engine
- folium
- PyQt5
- pandas
> Those liberary can be installed by pip
```shell
$ pip install earthengine-api --upgrade
$ pip install folium
$ pip install PyQt5
$ pip install pandas
```
## WorkFlow

### Step 1: restore the feature collection to the local

Open the restoretool.py at first. Be sure that change the output properties, sample feature collection address, and save address is correct. Click "run" to save the featurecolelction file in Google earth engine to the local

```python
outProperty = ['idNum','ran','startDate']
sample = ee.FeatureCollection('users/BAI_debug/sampleMidWest')
saveAddress = "data\source_test.csv"
```
