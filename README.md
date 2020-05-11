# Dictionary tagger for COVID-19
This is a dictionary tagger which uses pattern based search for matching words in articles and exports them in pub-annotations format.

## Authors:
**Annie Tallind**, Lund University, Faculty of Engineering   
**Kaggle ID**: atllnd   
**Github ID**: annietllnd   
**Sofi Flink**, Lund University, Faculty of Engineering   
**Kaggle ID:** sofiflinck   
**Github ID:** obakanue

# Credit:
Dictionaries where generated using golden- and silver-standard
implemented by Aitslab.

# Set up environment:
*This implementation is built on LinuxOS and as such filepaths are system specific. If using Windows OS make sure to check the paths are written properly before running the code.*   
In order to run this program 'pandas' have to be installed, which is a Python Data Analysis Library. 
## Installing pandas with pip on Ubuntu:
1. Open terminal.
2. Enter following code snippets:
```
sudo apt-get install python3-pip
sudo pip3 install pandas
```

## Installing pandas with apt-get on Ubuntu:
1. Open terminal.
2. Enter following code snippet:
```
sudo apt-get install python3-pandas
```

## Modifications to the code: 
*In order to run the code properly, some of the paths need to be manually edited to find the sources of the data*. In `main.py` check the following:
### Subset 100
- `json_articles_dir_path`: The folder in which the article files are stored
- `metadata_file_path`: The path with the .csv file that is the metadata
- `vocabularies_dir_path`: The folder in which the dictionaries are stored
- `output_dir_path` and `tagger_output_dir_path`: A target folder to which the output files are written
- `true_output_dir_path`: The folder in which the gold standard output files are stored

### Subset 10 gold standard test
Same as above, but for the smaller subset. 

## Running the program:

Now the code can be run writing the following code snippet in the terminal in the project:
```
python3 -m bin.main
```
Python does not save the paths and as such won't find the imports, the IDE will work this out for you when you assign
working directory as edan70.