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

Now the code can be run writing the following code snippet in the terminal in the project:
```
python3 dictionarytagger.py
```
