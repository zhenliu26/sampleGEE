import ee
import folium
import pandas as pd


ee.Initialize()
# customize: the property you need, the feature collection of sample points, and save address
outProperty = ['idNum','ran','startDate']
sample = ee.FeatureCollection('users/BAI_debug/sampleMidWest')
saveAddress = "source_test.csv"


# get the property of each feature
def getProperty(source):
    source = ee.Feature(source)
    return source.toDictionary(outProperty)



# def Dataget(source):
#     source = ee.Feature(source)
#     return [source.get('idNum'),source.get('ran'),source.get('startDate'),'NotAssessed']

dataList = sample.toList(sample.size()).map(getProperty)
dataList = dataList.getInfo()
final_dataList = list()
for items in dataList:
    final_dataList.insert(-1,list(items.values()))
df = pd.DataFrame(dataList, columns=outProperty)
df['class'] = 'NotAssessed'
df.to_csv(saveAddress,index=False)
