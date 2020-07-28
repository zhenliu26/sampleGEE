import ee
import folium
import io
import sys
import pandas as pd
from PyQt5 import QtWidgets, QtWebEngineWidgets
from PyQt5.QtWidgets import QMainWindow
from mainUI import Ui_MainWindow
from folium import plugins
# import mainUI
ee.Initialize()
# date property name in csv
dateName = "startDate"
# ID property name in csv
IDName = 'idNum'
# ID property name in GEE
IDGEE = 'idString'
# date property name in GEE
dateGEE = dateName
sourceName = 'source_test.csv'
#  the dataframe to store the sample data. (it will be updated everytime you click enter)
df = pd.read_csv(sourceName)
# sample point feature collection
sample = ee.FeatureCollection('users/BAI_debug/sampleMidWest')
classCode = ['NotAssessed','water','non-water']

# data processing (prepare the image to show)
S2 = ee.ImageCollection("COPERNICUS/S2")
studyArea = ee.Geometry.Polygon(
    [[[-94.37600552554129, 43.810559961893695],
      [-96.50735318179129, 43.810559961893695],
      [-97.78176724429129, 39.690080813204126],
      [-94.29910122866629, 39.698534386332796]]]);

S2_select = S2.filterDate(ee.Date('2019-03-11'), ee.Date('2019-05-06')).filterBounds(studyArea).filterMetadata(
    'CLOUDY_PIXEL_PERCENTAGE', 'less_than', 80).filterMetadata('SENSING_ORBIT_NUMBER', 'equals', 112)


def selectDate(x):
    x = ee.Image(x)
    x = x.set('startDate', ee.Date(x.get('system:time_start')).format('yyyy-MM-dd'))
    return x


histoSelect = S2_select.map(selectDate)

dates = histoSelect.aggregate_histogram('startDate').keys()


def mosaicImage(x):
    image = S2_select.filterDate(ee.Date(x).millis(), ee.Date(x).advance(1, 'day').millis()).mosaic()
    return image


imagelist = dates.map(mosaicImage)


def getSeasonalWater(start, end):
    startMonth = ee.Date(start).get('month');
    endMonth = ee.Date(end).get('month');
    monthList = ee.List.sequence(startMonth, endMonth, 1);
    jrc_monthly = ee.ImageCollection('JRC/GSW1_2/MonthlyRecurrence');
    recurrence = jrc_monthly.filter(ee.Filter.inList('month', monthList));

    def recurrenceMap(img):
        return img.select('monthly_recurrence').gte(30).unmask()

    seasonal = recurrence.map(recurrenceMap).max().rename('seasonalWater')
    return seasonal


seasonalWater = getSeasonalWater(dates.get(0), dates.get(-1)).rename('water')


def addWater(x):
    x = ee.Image(x).addBands(seasonalWater)
    index = x.get('system:index')
    x = x.set('startDate', dates.get(ee.Number.parse(index)))
    return x


finalResult = ee.ImageCollection(imagelist).map(addWater)




class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.currentClass = 0

        # sort out the date items
        df['datepd'] = pd.to_datetime(df[dateName])
        self.comboBox.addItems(df.sort_values(by='datepd',ascending=True)[dateName].unique())
        del df['datepd']
        # get current img for the date
        self.currentImg = finalResult.filter(ee.Filter.eq(dateGEE, str(self.comboBox.currentText()))).first()
        self.comboBox_2.addItems(df[df[dateName] == str(self.comboBox.currentText())][IDName].apply(str).tolist())
        self.comboBox_3.addItems(classCode)
        # the class of the first feature
        classIndex = classCode.index(df[(df[dateName] == str(self.comboBox.currentText()))&(df[IDName] == int(self.comboBox_2.currentText()))]['class'].tolist()[0])
        # show the class of the first feature
        self.comboBox_3.setCurrentIndex(classIndex)
        self.currentClass = self.comboBox_3.currentIndex()

        point_current = ee.Feature(sample
                           .filter(ee.Filter.eq(IDGEE, str(self.comboBox_2.currentText())))
                           .first())
        loadMap(self.currentImg, point_current)


        self.comboBox.currentIndexChanged.connect(self.dateChange)
        self.comboBox_2.currentIndexChanged.connect(self.ftChange)
        self.pushButton_3.clicked.connect(self.enterClick)
        self.pushButton_2.clicked.connect(self.nextClick)
        self.pushButton.clicked.connect(self.previousClick)

    def dateChange(self):
        self.comboBox_2.clear()  # delete all items from comboBox
        self.currentImg = finalResult.filter(ee.Filter.eq(dateGEE, str(self.comboBox.currentText()))).first()
        self.comboBox_2.addItems(df[df[dateName] == str(self.comboBox.currentText())][IDName].apply(str).tolist())


    def ftChange(self):
        if(self.comboBox_2.currentIndex()>-1):
            classIndex = classCode.index(
                df[(df[dateName] == str(self.comboBox.currentText())) & (df[IDName] == int(self.comboBox_2.currentText()))][
                    'class'].tolist()[0])
            self.comboBox_3.setCurrentIndex(classIndex)
            self.currentClass = self.comboBox_3.currentIndex()
            point = ee.Feature(sample
                               .filter(ee.Filter.eq(IDGEE, str(self.comboBox_2.currentText())))
                               .first())
            loadMap(self.currentImg,point)

    def nextClick(self):
        ftNum = self.comboBox_2.count()
        indexCurrent = self.comboBox_2.currentIndex()
        self.comboBox_2.setCurrentIndex((indexCurrent+1)%ftNum)
    def previousClick(self):
        ftNum = self.comboBox_2.count()
        indexCurrent = self.comboBox_2.currentIndex()
        self.comboBox_2.setCurrentIndex((indexCurrent+ftNum-1)%ftNum)

    def enterClick(self):
        classIndex = self.comboBox_3.currentIndex()
        df.loc[(df[dateName] == str(self.comboBox.currentText())) & (df[IDName] == int(self.comboBox_2.currentText())),'class'] = classCode[classIndex]
        df.to_csv(sourceName,index=False)

#  add ee layer to the map
def add_ee_layer(self, eeImageObject, visParams, name):
  tiles = ee.data.getTileUrl(eeImageObject.getMapId(visParams), 8014, 4817, 37)
  tiles = tiles[:-12] + "{z}/{x}/{y}"
  folium.raster_layers.TileLayer(
    tiles = tiles,
    attr = "Map Data © Google Earth Engine",
    name = name,
    overlay = True,
    control = True
  ).add_to(self)
folium.Map.add_ee_layer = add_ee_layer


# load ee map and point
def loadMap(img1, point):
    pointcor = point.geometry().coordinates().getInfo()
    m = folium.Map(
        location=[pointcor[1], pointcor[0]], tiles="OpenStreetMap", zoom_start=14
    )
    m.add_ee_layer(img1, {'bands': ['B12', 'B8', 'B5'], 'min': 100, 'max': 3500}, 'S2 Greenish')
    m.add_ee_layer(img1, {'bands': ['B8', 'B11', 'B4'], 'min': 100, 'max': 3500}, 'S2 Purplish')
    m.add_ee_layer(img1.normalizedDifference(['B3', 'B12']), {'min': -0.5, 'max': 0.5}, 'MNDWI')
    m.add_ee_layer(point, {}, 'p1')
    m.add_child(folium.LayerControl())
    data = io.BytesIO()
    m.save(data, close_file=False)
    w.setHtml(data.getvalue().decode())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = QtWebEngineWidgets.QWebEngineView()

    w.resize(640, 480)
    w.show()



# date_num = dates.length().getInfo()
    ui = MainWindow()
    ui.show()


    sys.exit(app.exec_())
