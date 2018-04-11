# Crime Predictor: Chicago

## Pre-requisites

* PyPy3 Interpreter: Installation steps can be found [here](https://pypy.org/download.html)
* Third party PyPy3 / Python modules
  * [panadas](https://pandas.pydata.org/pandas-docs/stable/install.html)


## STEP 1: Clone the repository

Please run the command ``git clone https://github.com/shanbhag10/Crime-Predictor-Chicago.git``

## STEP 2: Change the directory to scripts

Please run the command ``cd <PATH_OF_CLONE_FOLDER>/Crime-Predictor-Chicago/scripts``

## STEP 3: Pre process raw data [ONLY IF REQUIRED]

Please run the command ``python3 preProcessData.py ../config/<PRE_PROCESS_FILE>.config ../config/<MAIN_PROCESS_FILENAME>.config``

Example:

``python3 preProcessData.py ../config/preprocess_all.config ../config/main.config``

The structure of <PRE_PROCESS_FILE>.config is as follows

``<RAW_FILE_PATH>,<PROCESSED_FILE_PATH>,<ROW_FILTER_KEY>,<COL_NAME_HAVING_THE_FILTER_KEY>,<COL_NAME_FOR_LATITUDE>,<COL_NAME_FOR_LONGITUDE>``

For multiple files put each entry on a new line

**NOTE**: The ROW_FILTER_KEY and COL_NAME_HAVING_THE_FILTER_KEY can be empty if you don't want to filter rows

Example content:

../data/overlap/crime.csv,../data/input/homicide.csv,HOMICIDE,PRIMARY DESCRIPTION,LATITUDE,LONGITUDE<br>
../data/overlap/bars.csv,../data/input/bars.csv,,,LATITUDE,LONGITUDE<br>
../data/overlap/church.csv,../data/input/church.csv,,,"LAT","LONG"<br>
../data/overlap/library.csv,../data/input/library.csv,,,LAT,LONG<br>
../data/overlap/school.csv,../data/input/school.csv,,,Lat,Long<br>
../data/overlap/police.csv,../data/input/police.csv,,,LATITUDE,LONGITUDE<br>

## STEP 4: Create the <MAIN_PROCESS_FILENAME> [ONLY IF Pre prossing step is skipped]

Create a file <MAIN_PROCESS_FILENAME>.config in the config directory with the names of clean input files separated by ','

Example Content:

``../data/input/test_crime.csv,../data/input/test_bar.csv,../data/input/test_school.csv
``

Please make sure that the file above only have the latitude and longitude values for each record for the corresponding feature in a new line

Example input file content: ../data/input/test_crime.csv

41.86922,-87.66249<br>
41.86923,-87.66249<br>
41.86921,-87.66248<br>
41.86923,-87.66248<br>
41.86920,-87.66247

## STEP 5: Run the Main algorithm

Run the following command

``pypy3 colocationAlgo.py ../config/<MAIN_PROCESS_FILENAME>.config ../data/output/<OUTPUT_FILE_NAME>.txt``

Example:

``pypy3 colocationAlgo.py ../config/main.config ../data/output.txt``
