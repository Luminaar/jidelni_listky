from flask import Flask
from flask import render_template

from bs4 import BeautifulSoup
from requests import get
from datetime import date

import ceny

app = Flask(__name__)

def get_day_tag(url):
    r = get(url)
    soup = BeautifulSoup(r.content)

    day_number = date.today().strftime("%w")

    if day_number == "0" or day_number == "6":
        day_number = "5"

    return soup.find(attrs={"name" : day_number})

def get_menza(url):
    def _():

        day_tag = get_day_tag(url)

        if day_tag == None:
            return {}

        listek = []

        x = False
        for sibling in day_tag.parent.parent.next_siblings:
            if x:
                break
            if sibling != "\n":
                for child in sibling.children:
                    if child.name == "th":
                        x = True
                        break
                    if child != "\n":
                        listek.append(child.text)

        # structure into a dict
        dict_listek = {}

        n = 0
        for i in range(0, len(listek), 2):
            dict_listek[n] = [listek[i][:-1], listek[i+1]]
            n += 1

        return dict_listek

    return _


def get_zdrava_pizza(url):
    def _():

        day_tag = get_day_tag(url)

        if day_tag == None:
            return {}

        listek = []
        for sibling in day_tag.parent.next_siblings:
            try:
                if  sibling.name == "ol":
                    for child in sibling.children:
                        if child != "\n":
                            listek.append(child.text)
                elif sibling.name == "p":
                    break
            except:
                pass

        dict_listek = {}

        n = 0
        for i in listek:
            x = i.split(": ")
            # structure meals into dict, add whitespaces after every comma (with replace)
            dict_listek[n] = [x[0], x[1].replace(",", ", ").replace("(", " (")]
            n += 1

        return dict_listek

    return _

get_pizza = get_zdrava_pizza("http://www.vse.cz/menza/jidelni_listek_Pizza.php#3")
get_zdrava = get_zdrava_pizza("http://www.vse.cz/menza/jidelni_listek_Zdrava_vyziva.php#5")

get_menza_obed = get_menza("http://www.vse.cz/menza/obedy.php#5")
get_menza_vecere = get_menza("http://www.vse.cz/menza/vecere.php#5")

get_menza_akademicky = get_menza("http://www.vse.cz/menza/jidelni_listek_AK.php#2")


@app.route('/')
def main():
    return render_template("index.html", obed=get_menza_obed(),
                            pizza=get_pizza(),
                            zdrava=get_zdrava(),
                            akademicky=get_menza_akademicky(),
                            ceny = ceny.ceny)


if __name__ == '__main__':
	app.run(debug=True)   