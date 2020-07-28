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

> Tips: Don't forget to authorize the Google Earth Engine account by ee.Authenticate().

### Step 1: restore the feature collection to the local

Open the restoretool.py at first. Be sure that change the output properties, sample feature collection address, and save address is correct. Click "run" to save the featurecolelction file in Google earth engine to the local.

```python
outProperty = ['idNum','ran','startDate']
sample = ee.FeatureCollection('users/BAI_debug/sampleMidWest')
saveAddress = "data\source_test.csv"
```

### Step 2: Hand label

Change date name, ID name in both csv and GEE, and the source name
```python
# import mainUI
ee.Initialize()
# date property name in csv
dateName = "startDate"
# ID property name in csv
IDName = 'idNum'
# ID property name in GEE
IDGEE = 'idString'
# date property name in GEE
dateGEE = 'startDate'
sourceName = 'data/source_test.csv'
#  the dataframe to store the sample data. (it will be updated everytime you click enter)
df = pd.read_csv(sourceName)
sample = ee.FeatureCollection('users/BAI_debug/sampleMidWest')
classCode = ['NotAssessed','water','non-water']
```

Because the imagecollection can't be stored in Google Earth Engine Asset, so that the final result (which is the imagecollection in Google Earth Engine) should be calculated in the data preparation module.
```python
# data processing
finalResult = ee.ImageCollection(image)
```
[![INSERT YOUR GRAPHIC HERE](https://raw.githubusercontent.com/zhenliu26/Images/master/sampleUI.jpg)]()
