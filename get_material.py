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

    urls["hokkaido_tohoku"] = "http://www.s-recipe.com/local/hokkaido_tohoku.html"
    urls["kanto"]="http://www.s-recipe.com/local/kanto.html"
    urls["tyubu"]="http://www.s-recipe.com/local/tyubu.html"
    urls["kinki"]="http://www.s-recipe.com/local/kinki.html"
    urls["tyugoku"]="http://www.s-recipe.com/local/tyugoku.html"
    urls["shikoku"]="http://www.s-recipe.com/local/shikoku.html"
    urls["kyusyu_okinawa"]="http://www.s-recipe.com/local/kyusyu_okinawa.html"
    
    for key,url in urls.iteritems():
        # set up url
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        soup = BeautifulSoup(response.read())
        
        # list of kens in area with its dishes
        kens = dict()
        
        # retrival
        for ken in  soup.findAll('div',attrs={"class":"list"}):
            
            ken_name =  ken.text.encode("utf-8").strip().split("\n")
            links = ken.findAll("a",text=True)
        
            # dishes for each ken
            dishes = dict()
            for link in links:
                text= link.next.text

                if link["href"].find("http://www.s-recipe.com/local/") == -1:
                    href="http://www.s-recipe.com/local/"+link["href"]
                else:
                    href = link["href"]
            
                dish = {text:href}
                dishes.update(dish)
            kens.update({ken_name[0]:dishes})

        areas.update({key:kens})
    return areas


"""get a recipe from a link, return a dict with  dish's element and a list of element amount, unit as key,val """
def get_recipe(url, dish):
    #print "**********"
    #print dish
    
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    response1=response.read()
    
    soup = BeautifulSoup(response1,"html.parser")
    recipe =""
    for p in soup.findAll('p',text=False):  
        if p.text.find("人")!=-1 and p.text.find("材料")!=-1:
            recipe = p.text
    
    temps=recipe.split("\n")        
    elements =dict()
    amount=0
    people=0
    
    for temp in temps:
        
        # calculate number of people (done)
        if temp.find("材料")!=-1:
            people=float(re.search("[0-9]",zenhan.z2h(temp,2)).group())
            
        # get each element for one man (done)
        elif temp!="":
            
            element=temp.replace("●","").replace("○","").replace("〇","").replace("◎","").lstrip(" ")
            if temp.find("…")!=-1:
                element= element.split("…")
            else:
                element= element.split(None,1)
            
            if people!=0:
               
                # convert all string to hankaku
                if len(element) >= 2: 
                    han_element = zenhan.z2h(element[1],2)
                else: 
                    break
                # march unit                
                unit=re.search("[^0-9\/～ ]+",han_element).group(0)  
                string_amount=re.search("[0-9\/ ]+",han_element.replace(unit,""))  
                if string_amount!=None:
                    amount= float(sum(Fraction(s) for s in string_amount.group(0).split()))/people
                else:
                    amount =0    
            else:
                print "people=0"

            elements.update({element[0]:[amount,zenhan.h2z(unit,4)]})

    return elements

"""get all dishes in Japan, return a dict  with dish and list of its area, prefecture, link, recipe as key,val"""
def getAllDishes():

    areas = extract_link()
    
    dishes_dict=dict()
    for area, kens in areas.iteritems():
        for ken,dishes in kens.iteritems():
            for dish,link in dishes.iteritems():
                
                recipe=get_recipe(link,dish)
                if len(recipe)>0:
                    ken=ken.lstrip("【").rstrip("】")
                    dishes_dict.update({dish:[area,ken,link,recipe]})

    return dishes_dict

"""save to CSV format file"""
def save2CSV(dishes_dict):
    w =csv.writer(codecs.open("elements.csv","w",encoding="utf-8"))
    elements_all=getAreaElementsMeanAmount(None,dishes_dict)
    #print len(elements_all)
    for key,value in elements_all.iteritems():
        w.writerow([key.decode("utf-8")])

"""read from CSV format file"""
def readCSV(filename):
    all_elements = {}
    for key in csv.reader(open(filename,"r")):
        all_elements.update({key[0]:0})#print key[0]
    #print len(all_elements)
    return all_elements

"""save to binary file"""
def write2Pickle(dishes_dict):
    f=open("dishes","w")
    newData = pickle.dumps(dishes_dict,1)
    f.write(newData)
    f.close()

"""read from binary file"""
def readPickle():
    f=open("dishes","r")
    data = pickle.load(f)
    f.close()
    return data

 
def printText(dishes_dict):
    for key,value in dishes_dict.iteritems():
        print "*******************"
        print key
        print value[0]# area
        print value[1]# ken
        print value[2]# link
    
        for ke,val in  value[3].iteritems():
            if len(val)==2:
                print ke+"  "+str(val[1])+"  "+str(val[0])
            else:
                print ke+"  "+str(val[1])

def renameAllElements(dishes_dict):
    m= MeCab.Tagger("-Oyomi")
    all_elements=dict()
    dishes_dict1=dict()
    for key,value in dishes_dict.items():
        elements_dict=dict()
        for key1,val in  value[3].items():
            katakana_key=m.parse(str(key1)).replace("\n","")
            if all_elements.has_key(katakana_key) and difflib.SequenceMatacher(all_elements[katakana_key],str(key1))>0.1:
                elements_dict.update({all_elements[katakana_key]:val})
            else:
                all_elements.update({katakana_key:str(key1)})
                elements_dict.update({str(key1):val})

        dishes_dict1.update({str(key):[str(value[0]),str(value[1]),str(value[2]),elements_dict]})

    return dishes_dict1

"""get all dishes in a area, return a dict with area and dict of dish""" 
def getAreaDishes(area,dishes_dict):
    area_dishes=dict()
    for key,val in dishes_dict.iteritems():
        if val[0]==area:        
            area_dishes.update({key:val})

    return area_dishes

def getAreaElementsMeanAmount(area,dishes_dict):
    area_elements=dict()
    area_elements1=dict()
        
    m= MeCab.Tagger("-Oyomi")
    if area!=None:
        area_dishes=getAreaDishes(area,dishes_dict)
    else:
        area_dishes=dishes_dict

    for key,val in area_dishes.iteritems():
        #print key
        for key1,val1 in val[3].iteritems():
            katakana_key=m.parse(key1).replace("\n","")
            if area_elements.has_key(key1):
                area_elements[key1][0]+=1
                area_elements[key1][1]+=val1[0]
            else:
                area_elements[key1]=[1,1]

    for element,val in area_elements.iteritems():
        if val[0]!=-1:
            
            area_elements1.update({element:val[1]/val[0]})
    
    return area_elements1

            
"""get all element from a specified area, return a dict with element,its frequency as key, val"""
def getAreaElements(area,dishes_dict):
    area_elements=dict()
    area_elements1=dict()
    
    m= MeCab.Tagger("-Oyomi")
    if area!=None:
        area_dishes=getAreaDishes(area,dishes_dict)
    else:
        area_dishes=dishes_dict

    for key,val in area_dishes.iteritems():
        #print key
        for key1,val1 in val[3].iteritems():
            katakana_key=m.parse(key1).replace("\n","")
            area_elements[key1]=area_elements.setdefault(key1,0)+1      

    return area_elements

        
"""calculate tf for each element in a area, return a dict with element, its tf as key, val"""            
def tf(area,dishes_dict):
    area_elements=getAreaElements(area,dishes_dict)
    #print area_elements
    key = max(area_elements.iteritems(),key=operator.itemgetter(1))[0]
    val = area_elements[key]
    
    for key1,val1 in  area_elements.iteritems():    
        area_elements[key1]=float(val1)/val
    
    # dict of elements and its tf value in a specified area.    
    return area_elements    



"""calculate idf for all element in Japan, return a dict with dict of element and its idf as key, val"""
def idf(dishes_dict):

    # areas_element is a dict with area and fic of all of its elements as key, val
    areas_element=dict()
    areas=["hokkaido_tohoku","kanto","tyubu","kinki","tyugoku","shikoku","kyusyu_okinawa"]
   
    for area in areas:
        area_elements=getAreaElements(area,dishes_dict)
        areas_element.update({area:area_elements})
        
    
    all_elements=getAreaElements(None,dishes_dict)        

    element_idf=all_elements
    for key,val in all_elements.iteritems():
        element_idf[key]=float(0)

    for element,val in  all_elements.iteritems():
        for area,element_dict in areas_element.iteritems():
            #print area
            if element_dict.has_key(element):# this area has that element

                element_idf[element]+=1
    n=len(areas)
    
    for key,val in element_idf.iteritems():
        
        element_idf[key]=math.log(float(n)/val,2)
        
    return element_idf


def tfidf(area, dishes_dict):
    elements_tf=tf(area,dishes_dict)
    elements_idf=idf(dishes_dict)
    elements_area_mean=getAreaElementsMeanAmount(area,dishes_dict)
    elements_all_mean=getAreaElementsMeanAmount(None,dishes_dict)
    elements_tfidf=dict()
    for element,val in elements_tf.iteritems():
        tfidf_value=val*elements_idf[element]
        if elements_all_mean[element]!=0:

            tfidf_value=elements_area_mean[element]/elements_all_mean[element]  
        elements_tfidf.update({element:tfidf_value})

    return elements_tfidf


"""get data from web and write to binary file"""
def getData():
    dishes_dict=getAllDishes()
    dishes_dict1=renameAllElements(dishes_dict)
    write2Pickle(dishes_dict1)

def printTFIDF(areas,dishes_dict):
    for area in areas:
        print area
        elements_tfidf=tfidf(area,dishes_dict)
        res = list(sorted(elements_tfidf, key=elements_tfidf.__getitem__, reverse=True))

        f=open("tfidf-"+area+".txt","w")
        for a in res:
            f.write("%s\t%6f\n"%(a,elements_tfidf[a]))
        f.close()

def printIDF(dishes_dict):
    elements_idf=idf(dishes_dict)
    res = list(sorted(elements_idf, key=elements_idf.__getitem__, reverse=True))
    f=open("idf.txt","w")
    for a in res: 
        f.write("%s\t%6f\n"%(a,elements_idf[a]))
    f.close()
    
def printTF(areas,dishes_dict):
    for area in areas:
        #print area
        elements_tf=tf(area,dishes_dict)
        res = list(sorted(elements_tf, key=elements_tf.__getitem__, reverse=True))
        
        f=open("tf-"+area+".txt","w")
        for a in res: 
            #print "%s%6f\n"%(a,elements_tf[a])
            f.write("%s\t%6f\n"%(a,elements_tf[a]))
        f.close()
        

def select_available(inputed_materials,dishes_dict):#input_materials is the dict of available materials and its amount. 
    #recipes dict in the area and its lacking material count
    recipes_index=dict()
    for recipe,val in dishes_dict.iteritems():
        count = 0
        for material in inputed_materials.iteritems():
            if !val[3].has_key(material):
                count+=1
        recipes_index.update({recipe:count})
    
    #sort recipe by count value
        

    
def main():
    reload(sys)
    sys.setdefaultencoding( "utf-8")
    #getData()
    dishes_dict=readPickle()
    #printText(dishes_dict)
    #printAllElements(dishes_dict)
    areas=["hokkaido_tohoku","kanto","tyubu","kinki","tyugoku","shikoku","kyusyu_okinawa"]
    printIDF(dishes_dict)
    printTF(areas,dishes_dict)
    printTFIDF(areas,dishes_dict)
    save2CSV(dishes_dict)
    readCSV("elements.csv")
if __name__== '__main__':
    main()
