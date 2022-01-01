from typing import List
import requests
from bs4 import BeautifulSoup
import pprint
import os

import csvTableWriter

root_url = "https://eschome.net/"

class OptionValue:
    value: str
    text: str

class Option:
    name: str
    values: List[OptionValue]

class Page:
    url: str
    path: str
    options: List[Option]

    def save_all_data(self):
        counts = {}
        for last_option in self.options:
            counts[last_option] = 0
        
        finished = False
        page_count = 0
        while not finished:
            post_data = {}

            for option in self.options:
                post_data[option.name] = option.values[counts[option]].value
            #print("vvv")
            #pprint.pprint(post_data)
            #print("^^^")
            r = requests.post(self.url, data = post_data)

            # write html
            text_file = open(f"results/{self.path.removeprefix('./').removesuffix('.php')}-{page_count}.html", "w")
            n = text_file.write(r.text)
            text_file.close()

            # write csv
            csvTableWriter.writeCsv(f"results/{self.path.removeprefix('./').removesuffix('.php')}-{page_count}.csv", r.text, post_data)

            # scary block to ensure all combinations of options are iterated    
            last_option = self.options[len(self.options) - 1]
            counts[last_option] = counts[last_option] + 1
            if counts[last_option] == len(last_option.values):
                counts[last_option] = 0
                i = len(self.options) - 2
                while i >= 0:
                    next_option = list(counts.keys())[i]
                    counts[next_option] = counts[next_option] + 1
                    if counts[next_option] == len(next_option.values):
                        counts[next_option] = 0
                    else:
                        break
                    if i == 0:
                        finished = True
                    i = i - 1
            page_count = page_count + 1
        print(f"Saved all combinations of {self.url}.")

r = requests.get(root_url)

soup = BeautifulSoup(r.text, 'html.parser')

rows = soup.find_all("tr", "tr_home_tabelle_1")

if not os.path.exists('results'):
    os.makedirs('results')

for row in rows:
    page = Page()
    page.url = f"{root_url}{row.find('form')['action']}"
    page.path = row.find('form')['action']

    page.options = []
    for input_html in row.find_all("input"):
        # we never care about type image
        if input_html["type"] == "image":
            continue
        # pending further investigation
        if input_html["type"] == "hidden":
            continue
        # eh, skip?
        if input_html["type"] == "text":
            continue
        input = Option()
        if input_html["type"] == "checkbox":
            input.name = input_html['name']
            option_true = OptionValue()
            option_true.text = "true"
            option_true.value = "1"
            option_false = OptionValue()
            option_false.text = "false"
            option_false.value = "0"
            input.values = []
            input.values.append(option_true)
            input.values.append(option_false)
        else:
            print(f"Unknown option type \'{input_html['type']}\'")
            input.values = []
        page.options.append(input)

    for select in row.find_all("select"):
        select_name = select["name"]
        option_list = Option()
        option_list.name = select_name
        option_list.values = []
        for option in select.find_all("option"):
            option_list_value = Option()
            option_list_value.value = option["value"]
            option_list_value.text = option.text
            option_list.values.append(option_list_value)
        page.options.append(option_list)

    page.save_all_data()
