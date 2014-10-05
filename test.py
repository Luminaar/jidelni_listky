from bs4 import BeautifulSoup
import requests
from datetime import date
import re

r= requests.get("http://www.vse.cz/menza/obedy.php#1")

soup = BeautifulSoup(r.content)

#print(soup.prettify())
#print(soup.find_all("table"))
text = soup.get_text()

today = date.today().strftime("%d\\. %m\\. %Y")
today = today[0:5] + today[6:]

pattern = today + "[\S\s]*?(?=\n\n)"

m = re.search(pattern, text)
print(m.group(0))




