from bs4 import BeautifulSoup
import csv
import re
import pprint

def writeCsv(file_output: str, html: str, extra):
    soup = BeautifulSoup(html, "html.parser")

    tables = soup.find_all("table")
    for table in tables:
        theads = table.find("thead")

        # ignore tables with a canvas
        if (table.find("canvas") is not None):
            continue

        headers = []
        rows = []
        if theads is not None:
            # some pages have multiple header rows for italics detail
            for header_row in theads.find_all("tr"):
                for hcol in header_row.find_all("th"):
                    headers.append(hcol.text.strip())
            previous_class = "tr_output_tabelle_1"
            row = []
            for row_html in table.find_all("tr", recursive=False):
                row_class = row_html['class'][0]
                if row_class != previous_class:
                    previous_class = row_class
                    rows.append(row)
                    row = []                
                for col in row_html.find_all("td"):
                    row.append(col.text.strip())
            rows.append(row)

        # clean up empty columns
        cleaned_headers = []
        indexes_to_use = []
        for index, header in enumerate(headers):
            append = False
            if header != "":
                append = True
            else:
                for r in rows:
                    if len(r) > index and r[index] != "":
                        append = True
                        break

            if append:
                cleaned_headers.append(header)
                indexes_to_use.append(index)

        cleaned_rows = []
        for r in rows:
            cleaned_row = []
            for index in indexes_to_use:
                if len(r) > index:
                    cleaned_row.append(r[index])
                else:
                    print(f"{file_output} has unusual number of indexes: {r}")
            cleaned_rows.append(cleaned_row)

        # get title. this seems to work?
        # string join to clean internal whitespace
        title_html = soup.find('span', {'class': re.compile('span_ueberschrift_\d*')})
        title = "unknown title"
        if title_html is not None:
            title = " ".join(title_html.text.split())
        else:
            print(f"{file_output} does not have a title.")

        with open(file_output, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            spamwriter.writerow([ title, pprint.pformat(extra) ])
            spamwriter.writerow(cleaned_headers)
            for row in cleaned_rows:
                spamwriter.writerow(row)

if __name__ == "__main__":
    with open('results/databaseoutput201-0.html') as f:
        html = f.read()
        writeCsv('test.csv', html, None)
