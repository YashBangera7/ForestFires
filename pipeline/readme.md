# Pipeline

 - Standardize train, validation, test data for ALL models
- Allows for standardized evaluation and ensemble modeling
- Save time in preprocessing

## How to use the files
All files are Pandas dataframes in pickle format. 
Train and validation files are 80/20 split with the same positive %. 
Use the file with the latest date in the name if there are several.

Sample pickle loading code:

infile = open('directory/traindate.pickle','rb')

train = pickle.load(infile)

infile.close()
