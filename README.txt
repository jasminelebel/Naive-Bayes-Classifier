Instructions on how to run the program:

1. After running the “beautiful_soup.py” class, the user will be asked to enter 0 or 1, depending on whether or not it wants to use the smoothing filtering, respectively. Smoothing filtering will gradually remove words, using a smoothing factor of 1, then 1.2, 1.4, 1.6, 1.8, and 2.0.
2. The user will then be asked to enter 0 or 1 again, depending on whether or not it wants to use the infrequent word filtering. Infrequent word filtering gradually removes words with a frequency of 1, then a frequency of less than 10, and lastly a frequency of less then 20. It the goes on to remove the top 5% most frequent words, the 10% most frequent words, and then the 20% most frequent words.
3. Thirdly, the user will be asked to enter 0 or 1 a third time, to determine whether or not it wants to use the word length filtering. Word length filtering gradually removes all words with a length less than 2, a length less than 4, and the a length greater than 9.
4. Depending on the choices made, the program will run and output the different results in different files. For example, if infrequent and length filtering is chosen, the program will generate 18 files, as infrequent word filtering generates 6 files every time, and word length filtering generates 3.
5. The program will then output the correctness of precision percentage for each of the output files.
5. Lastly, using matplotlib, the program will generate a graph, plotting all outputted correction of precision percentages, where the x-axis shows the output file number (run number) and the y-axis shows the accuracy percentage (correction of precision).


List of libraries:

from enum import unique
from requests import get
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import csv
import re
import string
import math
