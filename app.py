from flask import Flask
from flask import render_template

from bs4 import BeautifulSoup
from requests import get
from datetime import date
from pickle import Pickler
from pickle import Unpickler

import ceny

app = Flask(__name__)


def get_day_tag(url):
    r = get(url)
    soup = BeautifulSoup(r.content)

    day_number = date.today().strftime("%w")

    if day_number == "0" or day_number == "6":
        day_number = "5"

    return soup.find(attrs={"name": day_number})


def get_table(url):
    def _():

        day_tag = get_day_tag(url)

        if day_tag is None:
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


def get_list(url):
    """Fetching data from a menu in a list"""
    def _():

        day_tag = get_day_tag(url)

        if day_tag is None:
            return {}

        listek = []
        for sibling in day_tag.parent.next_siblings:
            try:
                if sibling.name == "ol":
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
            # structure meals into dict, add whitespaces after every comma
            dict_listek[n] = [x[0], x[1].replace(",", ", ").replace("(", " (")]
            n += 1

        return dict_listek

    return _

def get_new_table(url):
    """Gets the new style tables for zdrava vyziva and pizzaVsem."""
    r = get(url)
    soup = BeautifulSoup(r.content)

    tables = soup.find_all('table')

    return tables



def check_current():
    """ Checks if the menu was last retrieved in the
        current day. If yes, returns True, else, returns False."""

    day_number = date.today().strftime("%w")

    with open("last_updated", "rb") as f:
        p = Unpickler(f)

        last_updated = p.load()

    if day_number == last_updated:
        return True
    else:
        return False


def get_last_updated():
    with open("last_updated", "rb") as f:
        p = Unpickler(f)

        return p.load()


def get_menu():
    """Checks if menu is current, if yes, load menu from file,
        if not, downloads data from internet and saves them to file,
        and updates last_updated"""
    d = {}

    if check_current():
        with open("menu", "rb") as f:
            p = Unpickler(f)
            d = p.load()
    else:
        d = {
            "obed": get_menza_zizkov_obed(),
            "pizza": get_pizza(),
            "zdrava": get_zdrava(),
            "vecere": get_menza_zizkov_vecere(),
            "jarov": get_jarov(),
            "volha": get_volha()
        }

        # write new menu to file
        with open("menu", "wb") as f:
            f.truncate()
            p = Pickler(f, 0)
            p.dump(d)

        # update last_updated
        with open("last_updated", "wb") as f:
            f.truncate()
            p = Pickler(f, 0)
            p.dump(date.today().strftime("%w"))

    return d

def get_souce_color():
    pass


get_pizza = get_list("http://www.vse.cz/menza/jidelni_listek_Pizza.php#3")
get_zdrava = get_list("http://www.vse.cz/menza/jidelni_listek_Zdrava_vyziva.php#5")
get_menza_zizkov_obed = get_table("http://www.vse.cz/menza/obedy.php#5")
get_menza_zizkov_vecere = get_table("http://www.vse.cz/menza/vecere.php#5")

get_akademicky = get_table("http://www.vse.cz/menza/jidelni_listek_AK.php#2")

get_jarov = get_list("http://www.vse.cz/menza/jidelni_listek_Jarov.php")
get_volha = get_list("http://www.vse.cz/menza/jidelni_listek_Volha.php")


@app.route('/')
def main():
    menu = get_menu()
    return render_template("index.html", obed=menu["obed"],
                            pizza=menu["pizza"],
                            zdrava=menu["zdrava"],
                            vecere=menu["vecere"],
                            ceny=ceny.ceny,
                            last_updated=get_last_updated())


@app.route('/koleje')
def koleje():
    menu = get_menu()
    return render_template("koleje.html",
                           jarov=menu["jarov"],
                           volha=menu["volha"])

@app.route('/souce')
def souce():
    """Show colors of the souces in pizzaVsem."""
    menu_pizza = get_menu()['pizza']
    table = get_new_table('http://www.pizza-vegetvsem.cz/jidelni-listek/pizza-a-pasta')[1]

    tags = table.find_all('strong')

    def get_parent_text(tag):
        return tag.parent.text

    def get_color(pasta):
        """Search text for keywords and determine the color of
        a souce."""

        if 'napoli' in pasta[2] and 'bešamel' in pasta[2]:
            pasta[2] = 'background-color: #FFA4AD'
        elif 'napoli' in pasta[2]:
            pasta[2] = 'background-color: #7A0000'
        elif 'bešamel' in pasta[2]:
            pasta[2] = 'background-color: #FFFFD6'
        else:
            pasta[2] = 'background-image: url(static/pattern.png)'

        return pasta

    def parse_pasta(text):
        """Parse pasta info text into number, name and contents."""
        from re import split

        text = text.replace(u'\xa0', u' ')  # remove non-breaking spaces

        pasta_list =  list(filter(None, split(r'(\s?/\s?Těstoviny\s?)|(\s?\|\s?)', text)))  # filter out empty strings and make a list

        return [x for x in pasta_list[::2]]  # return list with every other item from pasta_list

    pasta_tags = filter(lambda x: 'Těstoviny' in x.text, tags)
    pastas = map(get_color, map(parse_pasta, map(get_parent_text, pasta_tags)))
    


    return render_template('souce.html', 
            menu=menu_pizza,
            pastas=pastas)

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
