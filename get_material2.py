# -*- coding: utf-8 -*-

import codecs
import cPickle as pickle
import csv
import operator
import urllib2
from bs4 import BeautifulSoup
import re 
import mechanize
import html5lib
import sys
from fractions import Fraction
#import kconv
import zenhan
import math
import MeCab
import difflib


"""get all links content recipe"""
def extract_link():
    urls = dict()
    areas = dict()



def makeInsertRecipe(dishes):
    f=open("recipe1.sql","w")
    for dish in dishes:
        for ingredient in ingredients:
            f.write("INSERT INTO tbl_recipe VALUES(%s,%s,NOW(),NOW())"%(recipe,instruction))
    f.close()    


def makeInsertIngredient(dishes):
    f=open("ingredient1.sql","w")
    


"""read from CSV format file"""
def readCSV(filename):
    all_elements = {}
    for key in csv.reader(open(filename,"r")):
        all_elements.update({key[0]:0})#print key[0]
    #print len(all_elements)
    return all_elements


def main():
    reload(sys)
    sys.setdefaultencoding( "utf-8")






if __name__=="__main__":
    main()
