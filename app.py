from flask import Flask
from flask import render_template

from bs4 import BeautifulSoup
from requests import get
from datetime import date

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

        for sibling in day_tag.parent.parent.next_siblings:
            if sibling != "\n":
                for child in sibling.children:
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
            # structure meals into dict
            dict_listek[n] = [x[0], x[1]]
            n += 1

        return dict_listek

    return _

get_pizza = get_zdrava_pizza("http://www.vse.cz/menza/jidelni_listek_Pizza.php#3")
get_zdrava = get_zdrava_pizza("http://www.vse.cz/menza/jidelni_listek_Zdrava_vyziva.php#5")

get_menza_obed = get_menza("http://www.vse.cz/menza/obedy.php#5")
get_menza_vecere = get_menza("http://www.vse.cz/menza/vecere.php#5")

def get_text():
    text = "<br>".join(get_menza_obed()) + "<br><br>" + "<br>".join(get_menza_vecere())
    text += "<br>".join(get_pizza()) + "<br><br>" + "<br>".join(get_zdrava())

    return text


@app.route('/')
def main():
    # return render_template("index.html", obed=get_menza_obed(),
    #                         vecere=get_menza_vecere(),
    #                         pizza=get_pizza(),
    #                         zdrava=get_zdrava())
    return "Hello world"


if __name__ == '__main__':
	app.run(debug=True)   