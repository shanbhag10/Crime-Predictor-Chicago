# Crime Predictor: Chicago

## STEP 1: Clone the repository

Please run the command ``git clone https://github.com/shanbhag10/Crime-Predictor-Chicago.git``

## STEP 2: Change the directory to scripts

Please run the command ``cd <PATH_OF_CLONE_FOLDER>/Crime-Predictor-Chicago/scripts``

## STEP 3: Pre process raw data [ONLY IF REQUIRED]

Please run the command ``python3 preProcessData.py ../config/preprocess_all.config ../config/<MAIN_PROCESS_FILENAME>.config``

Example:

``python3 preProcessData.py ../config/preprocess_all.config ../config/main.config``

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
