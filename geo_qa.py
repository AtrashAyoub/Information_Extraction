
BASE_URL="https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"
import rdflib
import requests
import lxml.html
import re
import os
from argparse import ArgumentParser
wiki_prefix = "http://en.wikipedia.org"
WIKI_HTTPS_PREFIX = "https://en.wikipedia.org/wiki/"
WIKI_HTTP_PREFIX = "http://en.wikipedia.org/wiki/"
global f
f = open('ontology.nt', 'a+')
global g
g = rdflib.Graph()
ont_path = ""


def Crawl(URL, path):
    global ont_path
    ont_path=path
    res = requests.get(URL) 
    doc = lxml.html.fromstring(res.content)
    prefix = "https://en.wikipedia.org"
    urls=[]
    for t in doc.xpath("//table/tbody/tr/td[2]/table/tbody//tr/td[1]//span//a"):
        current_url = t.attrib['href']
        urls.append(prefix+current_url)
    c=0
    for x in urls:
        try:
            Get_Country_Info(x)
        except:
            continue

    f.close()
    
    return
    
def process_raw_string(string):
    return string.replace(" ", "_")
    
def deprocess_raw_string(string):
    return string.replace("_", " ")


def Get_Country_Info(url): #IE from one country
    global ont_path
    print(url)
    f = open(ont_path, 'a+')
    raw_name = Extract_Country_Name(url)
    print("Raw Country: " + raw_name)
    name = process_raw_string(raw_name)
    print("Country: " + name)

    raw_popu = Extract_Country_Population(url)
    print("Raw Population: " + raw_popu)
    popu = process_raw_string(raw_popu)

    raw_area = Extract_Country_Area(url)
    print("Raw Area: " + raw_area )
    area = process_raw_string(raw_area)

    raw_capital = Extract_Country_Capital(url)
    print("Raw Capital: " + raw_capital )
    capital = process_raw_string(raw_capital)

    raw_gov = Extract_Country_Government(url)
    print("Goverment: " + raw_gov )
    
    pp = Extract_President(url)
    

    if(pp!=None):
        p = pp
        print("President: " + p )
        p_dob = Extract_President_DOB(pp)
        print("President DOB: " + p_dob)

    pmpm = Extract_Prime_Minister(url)
    
    #There's a problem in the format of the infobox in https://en.wikipedia.org/wiki/Ivory_Coast
    if((pmpm!=None) and (url!="https://en.wikipedia.org/wiki/Ivory_Coast") ):
        pm = pmpm
        print("Prime Minister: " + pm)
        pm_dob = Extract_President_DOB(pmpm)
        print("Prime Minister DOB: " + pm_dob )

    #Connecting together:
    
    f.write("<"+url+"> <https://en.wikipedia.org/wiki/Capital> <" + f"https://en.wikipedia.org/wiki/{capital}" + "> . \n")
    f.write("<"+url+"> <https://en.wikipedia.org/wiki/is-a> <" + f"https://en.wikipedia.org/wiki/Country" + "> . \n")
    #g.add((g_url,g_r_capital,g_capital))
    f.write("<"+url+"> <https://en.wikipedia.org/wiki/Area> " + f"\"{area}\"^^<http://www.w3.org/2001/XMLSchema#positiveInteger>" + " . \n")
    f.write("<"+url+"> <https://en.wikipedia.org/wiki/Population> " + f"\"{popu}\"^^<http://www.w3.org/2001/XMLSchema#positiveInteger>" + " . \n")
    
    print("CHECKPOINT 0.1")
    #print(type(gov))
    gov_list = eval(raw_gov)
    governs = '_'.join(gov_list)
    governs_correct = governs.replace(" ", "_")
    f.write("<"+url+"> <https://en.wikipedia.org/wiki/Government> <" + f"https://en.wikipedia.org/wiki/{governs_correct}" + "> . \n")
    
    print("CHECKPOINT")
    
    if(pp!=None):
        f.write("<"+url+"> <https://en.wikipedia.org/wiki/President> <" + f"https://en.wikipedia.org/wiki/{p}" + "> . \n")
        f.write("<"+p+"> <https://en.wikipedia.org/wiki/Born> " + f"\"{p_dob}\"^^<http://www.w3.org/2001/XMLSchema#date>" + " . \n")
        f.write("<"+p+"> <https://en.wikipedia.org/wiki/President> <" + url + "> . \n")
        f.write("<"+p+"> <https://en.wikipedia.org/wiki/Job> <https://en.wikipedia.org/wiki/President> . \n")
        
    if((pmpm!=None) and (url!="https://en.wikipedia.org/wiki/Ivory_Coast")):
        f.write("<"+url+"> <https://en.wikipedia.org/wiki/Prime_Minister> <" + f"https://en.wikipedia.org/wiki/{pm}" + "> . \n")
        f.write("<"+pm+"> <https://en.wikipedia.org/wiki/Born> " + f"\"{pm_dob}\"^^<http://www.w3.org/2001/XMLSchema#date>" + " . \n")
        f.write("<"+pm+"> <https://en.wikipedia.org/wiki/Prime_Minister> <" + url + "> . \n")
        f.write("<"+pm+"> <https://en.wikipedia.org/wiki/Job> <https://en.wikipedia.org/wiki/Prime_Minister> . \n")

    return None
    
def Extract_Country_Name(url):
    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)
    a = doc.xpath("//table[contains(@class, 'infobox')]")
    try:
        return(a[0].xpath("/html/body/div[3]/div[3]/div[4]/div/table[1]/tbody/tr[1]/th/div[1]/text()")[0].replace(" ", "_"))
    except IndexError:
        if(a[0].xpath("//table//tr//th[contains(@class, 'adr')]")!=[]):
            if(a[0].xpath("//table//tr//th[contains(@class, 'adr')]//text()")[0].replace(" ", "_") != '\n'):
                return(a[0].xpath("//table//tr//th[contains(@class, 'adr')]//text()")[0].replace(" ", "_"))
            else:
                return(a[0].xpath("/html/body/div[3]/div[3]/div[5]/div/table[1]/tbody/tr[1]/th/div/div/div/div/span/text()")[0].replace(" ","_"))
        elif (a[0].xpath("/html/body/div[3]/div[3]/div[5]/div/table[1]/tbody/tr[1]/th/div/text()")!=[]):
            return(a[0].xpath("/html/body/div[3]/div[3]/div[5]/div/table[1]/tbody/tr[1]/th/div/text()")[0].replace(" ", "_"))
        else:
            return(a[0].xpath("/html/body/div[3]/div[3]/div[5]/div/table[2]/tbody/tr[1]/th/div/text()")[0].replace(" ","_"))
    return name

def Extract_President(url):
    res = requests.get(url) 
    doc = lxml.html.fromstring(res.content)
    a = doc.xpath("//table[contains(@class, 'infobox')]")
    if((a[0].xpath("//table//tr//th//a[text()='President']")!=[]) and (a[0].xpath("//table//tr//th//a[contains(text(), 'President')]")!=[])):
        p_url = wiki_prefix+a[0].xpath("//a[text()='President']//following::td//a/@href")[0]
        if("List" in p_url):    
            p_url = wiki_prefix+a[0].xpath("//a[contains(text(),'President')]/@href")[0]

        return p_url

def Extract_President_DOB(President_url):
    res = requests.get(President_url) 
    doc = lxml.html.fromstring(res.content)
    a = doc.xpath("//table[contains(@class, 'infobox')]")
    try:
        if(a[0].xpath("//table//span[@class='bday']//text()")[0] != []):
            return (a[0].xpath("//table//span[@class='bday']//text()")[0])
    except IndexError:
        return( a[0].xpath("//table//th[contains(text(), 'Born')]/./../td[1]/text()")[0].replace(" ", "_") )
    return "Problem in President DOB"

def Extract_Prime_Minister(url):
    res = requests.get(url) 
    doc = lxml.html.fromstring(res.content)
    a = doc.xpath("//table[contains(@class, 'infobox')]")
    if((a[0].xpath("//table//tr//th//a[text()='Prime Minister']")!=[]) and (a[0].xpath("//table//tr//th//a[contains(text(), 'Prime Minister')]")!=[])):
        pm_url = wiki_prefix+a[0].xpath("//a[text()='Prime Minister']//following::td//a/@href")[0]
        if("List" in pm_url):    
            pm_url = wiki_prefix+a[0].xpath("//a[contains(text(),'Prime Minister')]/@href")[0]

        return pm_url

def Extract_Prime_Minister_DOB(PM_url):
    res = requests.get(PM_url) 
    doc = lxml.html.fromstring(res.content)
    a = doc.xpath("//table[contains(@class, 'infobox')]")
    try:
        if(a[0].xpath("//table//span[@class='bday']//text()")[0] != []):
            return (a[0].xpath("//table//span[@class='bday']//text()")[0])
    except IndexError:
        if(a[0].xpath("//table//th[contains(text(), 'Born')]/./../td[1]/text()")==[]): return None
        return( a[0].xpath("//table//th[contains(text(), 'Born')]/./../td[1]/text()")[0].replace(" ", "_") )
    return "Problem in Prime Minister DOB"

def Check_Is_Digit(st):
    st = st.replace(" ", "")
    for x in str(st):
        if (not(((x.isdigit())or(x==",")))): return False
        return True
def Form(st):
    res=""
    for x in st:
        if (not(((x.isdigit())or(x==",")))): continue
        elif (x=="("): return res
        else: res+=x
    return res
    
def Extract_Country_Population(url):
    res = requests.get(url) 
    doc = lxml.html.fromstring(res.content)
    a = doc.xpath("//table[contains(@class, 'infobox')]")
    try:
        if((Form(a[0].xpath("//table//tr//th//a[text()='Population']//following::tr[1]/td/text()")[0])!="")):
            b = a[0].xpath("//table//tr//th//a[text()='Population']//following::tr[1]/td/text()")[0]
        else: b = a[0].xpath("//table//tr//th//a[text()='Population']//following::tr/td//text()")[0]
        if(Check_Is_Digit(b)):
            return Form(b)
        else:
            return Form(a[0].xpath("//table//tr//th//a[text()='Population']//following::tr[1]/td//li/text()")[0]) #For russia

    except IndexError:
        b = a[0].xpath("//table//tr//th[text()='Population']//following::tr[1]/td//text()")[0]
        if(Check_Is_Digit(b)):
            return Form(b)
        else:
            return Form(a[0].xpath("//table//tr//th[text()='Population']//following::tr[1]/td//li/text()")[0]) #For russia


def Extract_Country_Area(url):
    res = requests.get(url) 
    doc = lxml.html.fromstring(res.content)
    a = doc.xpath("//table[contains(@class, 'infobox')]")
    try:
        if(a[0].xpath("//table//tr//th//a[text()='Area ']")!=[]):
            c = a[0].xpath("//a[text()='Area ']//following::tr[1]/td/text()")[0].split()[0]
        else:
            c = a[0].xpath("//table//tr//th[text()='Area']//following::tr[1]/td/text()")[0].split()[0]
    except IndexError:
        if(a[0].xpath("//table//tr//th/a[text()='Area ']")!=[]):
            c = a[0].xpath("//a[text()='Area ']//following::tr[1]/td/text()")[0].split()[0]
        else:
            c = a[0].xpath("//table//tr//th/a[text()='Area']//following::tr[1]/td/text()")[0].split()[0]
    return(c)

def Extract_Country_Government(url):
    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)
    a = doc.xpath("//table[contains(@class, 'infobox')]")
    if(a[0].xpath("//table//tr//th//a[text()='Government']")!=[]):
        g = a[0].xpath("//a[text()='Government']//following::td[1]/a//text()")
        if(g==[]):
            g= a[0].xpath("//table//tr//th/a[text()='Government']//following::td[1]//span/a/text()")
        if(g==[]):
            g = a[0].xpath("//table//tr//th/a[text()='Government']//following::td[1]//a//text()")
    else:
        g = a[0].xpath("//table//tr//th[text()='Government']//following::td[1]/a//text()")
        if(g==[]):
            g= a[0].xpath("//table//tr//th[text()='Government']//following::td[1]//span/a/text()")
        if(g==[]):
            g = a[0].xpath("//table//tr//th/a[text()='Government']//following::td[1]//a//text()")
    if(g==[]):
        g= a[0].xpath("//table//tr//th[text()='Government']//following::td[1]//li//text()")
    return( str(g) )


def Extract_Country_Capital(url):
    res = requests.get(url) 
    doc = lxml.html.fromstring(res.content)
    a = doc.xpath("//table[contains(@class, 'infobox')]")
    if(a[0].xpath("//table//th[contains(text(), 'Capital')]")!=[]):
        d = a[0].xpath("//table//th[contains(text(), 'Capital')]/./../td//a/text()")[0]
        return(d)
    return "No Capital"
    
    
    
    
    
    
    
    
    
Q1="SELECT (COUNT(?p) AS ?count) WHERE { ?c <https://en.wikipedia.org/wiki/is-a> <https://en.wikipedia.org/wiki/Country>. ?p <https://en.wikipedia.org/wiki/Prime_Minister> ?c}"

Q2 = "select (COUNT(?c) AS ?count) where { ?c <https://en.wikipedia.org/wiki/is-a> <https://en.wikipedia.org/wiki/Country>}"



Q3="select (COUNT(?c) AS ?count) where { ?c <https://en.wikipedia.org/wiki/is-a> <https://en.wikipedia.org/wiki/Country>. ?c <https://en.wikipedia.org/wiki/Government> ?g . filter(contains(lcase(str(?g)), \"republic\"))}"


Q4="select (COUNT(?c) AS ?count) where { ?c <https://en.wikipedia.org/wiki/is-a> <https://en.wikipedia.org/wiki/Country>. ?c <https://en.wikipedia.org/wiki/Government> ?g . filter(contains(lcase(str(?g)), \"monarchy\"))}"
    
    
    

    
    
QUERIES = {}

QUERIES['president'] = """SELECT ?person
                            WHERE
                            {
                                ?country <https://en.wikipedia.org/wiki/is-a> <https://en.wikipedia.org/wiki/Country> .
                                FILTER (contains(lcase(str(?country)), "%s"))
                                ?person <https://en.wikipedia.org/wiki/President> ?country .
                            }
                         """
QUERIES['prime_minister'] = """SELECT ?person
                            WHERE
                            {
                                ?country <https://en.wikipedia.org/wiki/is-a> <https://en.wikipedia.org/wiki/Country> .
                                FILTER (contains(lcase(str(?country)), "%s"))
                                ?person <https://en.wikipedia.org/wiki/Prime_Minister> ?country .
                            }
                         """
                         
QUERIES['population'] = """SELECT ?population
                            WHERE
                            {
                                ?country <https://en.wikipedia.org/wiki/is-a> <https://en.wikipedia.org/wiki/Country> .
                                FILTER (contains(lcase(str(?country)), "%s"))
                                ?country <https://en.wikipedia.org/wiki/Population> ?population .
                            }
                            """
QUERIES['area'] = """SELECT ?area
                           WHERE
                           {
                                ?country <https://en.wikipedia.org/wiki/is-a> <https://en.wikipedia.org/wiki/Country> .
                                FILTER (contains(lcase(str(?country)), "%s"))
                                ?country <https://en.wikipedia.org/wiki/Area> ?area .
                           }
                           """
QUERIES['capital'] = """SELECT ?capital
                              WHERE
                              {
                                ?country <https://en.wikipedia.org/wiki/is-a> <https://en.wikipedia.org/wiki/Country> .
                                FILTER (contains(lcase(str(?country)), "%s"))
                                ?country <https://en.wikipedia.org/wiki/Capital> ?capital .
                              }
                              """
QUERIES['president_born'] = """SELECT ?bday
                                 WHERE
                                 {
                                    ?country <https://en.wikipedia.org/wiki/is-a> <https://en.wikipedia.org/wiki/Country> .
                                    FILTER (contains(lcase(str(?country)), "%s"))
                                    ?person <https://en.wikipedia.org/wiki/President> ?country .
                                    ?person <https://en.wikipedia.org/wiki/Born> ?bday .
                                 }
                              """
QUERIES['prime_born'] = """SELECT ?bday
                                 WHERE
                                 {
                                    ?country <https://en.wikipedia.org/wiki/is-a> <https://en.wikipedia.org/wiki/Country> .
                                    FILTER (contains(lcase(str(?country)), "%s"))
                                    ?person <https://en.wikipedia.org/wiki/Prime_Minister> ?country .
                                    ?person <https://en.wikipedia.org/wiki/Born> ?bday .
                                 }
                              """
QUERIES['who'] = """SELECT ?position ?country
                          WHERE
                          {
                           ?cand <https://en.wikipedia.org/wiki/Job> ?position .
                           FILTER (contains(lcase(str(?cand)), "%s"))
                           ?cand ?position ?country
                           }
                        """
QUERIES['gov'] = """SELECT ?gov_type
                          WHERE
                          {
                            ?country <https://en.wikipedia.org/wiki/is-a> <https://en.wikipedia.org/wiki/Country> .
                            FILTER (contains(lcase(str(?country)), "%s"))
                            ?country <https://en.wikipedia.org/wiki/Government> ?gov_type .
                          }
                       """

# regular expressions
PRESIDENT_RE = "^Who(\s+)is(\s+)the(\s+)president(\s+)of(\s+\w+)+(\s*)(\?+)(\s*)$"
PRIME_MINISTER_RE = "^Who(\s+)is(\s+)the(\s+)prime(\s+)minister(\s+)of(\s+\w+)+(\s*)(\?+)(\s*)$"
POPULATION_RE = "^What(\s+)is(\s+)the(\s+)population(\s+)of(\s+\w+)+(\s*)(\?+)$"
AREA_RE = "^What(\s+)is(\s+)the(\s+)area(\s+)of(\s+\w+)+(\s*)(\?+)(\s*)$"
GOVERNMENT_RE = "^What(\s+)is(\s+)the(\s+)government(\s+)of(\s+\w+)+(\s*)(\?+)(\s*)$"
CAPITAL_RE = "^What(\s+)is(\s+)the(\s+)capital(\s+)of(\s+\w+)+(\s*)(\?+)(\s*)$"
PRESIDENT_BORN_RE = "^When(\s+)was(\s+)the(\s+)president(\s+)of((\s\w+)+)(\s)born(\s*)(\?+)(\s*)$"
PRIME_BORN_RE = "^When(\s+)was(\s+)the(\s+)prime(\s+)minister(\s+)of((\s\w+)+)(\s)born(\s*)(\?+)(\s*)$"
WHO_IS_RE = "^Who(\s+)is(\s+)(\w+)(\s*)(\w*)(\s*)(\?+)(\s*)"
    
    


def normalize(text):
    striped = '_'.join(re.split("\s+", text.strip().lower().replace("-", "_")))
    return ''.join([c for c in striped if (c.isalpha() or c == "_")])


def extract_president_query_country(query):
    country = re.split("president(\s+)of(\s+)", query)[-1].replace("?", "")
    return normalize(country)


def extract_prime_query_country(query):
    country = re.split("prime(\s+)minister(\s+)of(\s+)", query)[-1].replace("?", "")
    return normalize(country)


def extract_population_country(query):
    country = re.split("population(\s+)of(\s+)", query)[-1]
    return normalize(country)


def extract_area_country(query):
    country = re.split("area(\s+)of(\s+)", query)[-1]
    return normalize(country)


def extract_government_country(query):
    country = re.split("government(\s+)of(\s+)", query)[-1]
    return normalize(country)


def extract_capital_country(query):
    country = re.split("capital(\s+)of(\s+)", query)[-1]
    return normalize(country)


def extract_birthday_country(query):
    aug_query = query.replace("born", "").replace("?", "")
    country = re.split("of(\s+)", aug_query)[-1]
    return normalize(country)


def extract_who_is_person(query):
    return normalize(re.sub("Who(\s+)is(\s+)", "", query).replace("?", ""))


    
    
def parse_query(query):

    # who is the president of *
    if re.match(PRESIDENT_RE, query):
        country = extract_president_query_country(query)
        #print(f"{country}")
        return "president", country

    # who is the prime minister of *
    elif re.match(PRIME_MINISTER_RE, query):
        country = extract_prime_query_country(query)
        return "prime_minister", country

    # what is the population of *
    elif re.match(POPULATION_RE, query):
        country = extract_population_country(query)
        return "population", country

    # what is the area of *
    elif re.match(AREA_RE, query):
        country = extract_area_country(query)
        return "area", country

    # what is the government of *
    elif re.match(GOVERNMENT_RE, query):
        country = extract_government_country(query)
        return "gov", country

    # what is the capital of *
    elif re.match(CAPITAL_RE, query):
        country = extract_capital_country(query)
        return "capital", country

    # what is the birthday of president of <country>
    elif re.match(PRESIDENT_BORN_RE, query):
        country = extract_birthday_country(query)
        return "president_born", country

    # what is the birthday of prime minister of <country>
    elif re.match(PRIME_BORN_RE, query):
        country = extract_birthday_country(query)
        return "prime_born", country

    # who is <person>
    elif re.match(WHO_IS_RE, query):
        person = extract_who_is_person(query)
        return "who", person

    # no match
    else:
        return None, None
   
   
   
def cut_prefix(ont_entity):
    if WIKI_HTTPS_PREFIX in ont_entity:
        return ont_entity.replace(WIKI_HTTPS_PREFIX, "")
    elif WIKI_HTTP_PREFIX in ont_entity:
        return ont_entity.replace(WIKI_HTTP_PREFIX, "")
    return ""
    
def extract_response(key, result):
    if key == "president" or key == "prime_minister" or key == "gov" or key =="capital":
        raw_response = result[0][0]
        cut_response = cut_prefix(raw_response)
        response = deprocess_raw_string(cut_response)
        
    elif key == "population" or key == "president_born" or key == "prime_born":
        response = result[0][0]
        
    elif key == "area":
        raw_response = result[0][0]
        response = f"{raw_response} km2"
        
    elif key == "who":
        raw_job = result[0][0]
        cut_job = cut_prefix(raw_job)
        response_job = deprocess_raw_string(cut_job)
        raw_country = result[0][1]
        cut_country = cut_prefix(raw_country)
        response_country = deprocess_raw_string(cut_country)
        response = f"{response_job} of {response_country}"
        
    return response
    


def run_s3ef_b():
    country_ontology = rdflib.Graph()
    country_ontology.parse("ontology.nt", format='nt')
    
    query_res1x = list(country_ontology.query(Q1))
    query_res1 = extract_response("population", query_res1x)
    print(f"1: {query_res1}")
    
    query_res2x = list(country_ontology.query(Q2))
    query_res2 = extract_response("population", query_res2x)
    print(f"2: {query_res2}")
    
    query_res3x = list(country_ontology.query(Q3))
    query_res3 = extract_response("president_born", query_res3x)
    print(f"3: {query_res3}")
    
    query_res4x = list(country_ontology.query(Q4))
    query_res4 = extract_response("president_born", query_res4x)
    print(f"4: {query_res4}")

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("function", type=str)
    parser.add_argument("path_query", type=str)
    args = parser.parse_args()
    
    if args.function == "create":
        Crawl(BASE_URL, args.path_query)
    elif args.function == "question":
        if os.path.isfile("ontology.nt"):
            country_ontology = rdflib.Graph()
            country_ontology.parse("ontology.nt", format='nt')
            
            query_key, query_arg = parse_query(args.path_query)
            if query_key is None:
                print("Error: Unrecognizable Query.")
                exit(1)
                
            actual_query = QUERIES[query_key] % (query_arg)
            #print(actual_query)
            query_res = list(country_ontology.query(actual_query))
            print(f"answer: {query_res}")
            if query_res:
                response = extract_response(query_key, query_res)
                print(response)
            else:
                print("No Results Found.")




        
    
    
