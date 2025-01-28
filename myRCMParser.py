import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path
from CategoryDict import categoryDict

# =============================================================================
# Classes
# =============================================================================

class myRCMPilot:
    def capturePicture(self):
        # Capture picture
        # Save picture as carPicPath
        pass
    def __init__(self, ID, name, country, profilePicPath=None, carPicPath=None):
        self.ID = ID                # e.g., race number or unique numeric string
        self.name = name           # pilot name
        self.country = country     # pilot country code
        self.profilePicPath = profilePicPath
        self.carPicPath = carPicPath

    def __repr__(self):
        return f"myRCMPilot(ID={self.ID}, name={self.name}, country={self.country})"

class Serie:
    def __init__(self, serieName, pilotlist=None):
        self.serieName = serieName
        # pilotlist is a list of myRCMPilot objects
        self.pilotlist = pilotlist if pilotlist is not None else []

    def __repr__(self):
        return f"Serie(name={self.serieName}, pilots={len(self.pilotlist)})"

class Category:
    def __init__(self, categoryName, serieList=None):
        self.categoryName = categoryName
        try:
            self.prettyName = categoryDict[categoryName]
        except KeyError:
            self.prettyName = categoryName
        # serieList is a list of Serie objects
        self.serieList = serieList if serieList is not None else []

    def __repr__(self):
        return f"Category(name={self.categoryName}, series={len(self.serieList)})"

# =============================================================================
# Extraction logic
# =============================================================================

def get_codes_and_names(url):
    """
    Return a list of (code1, code2, category_name)
    by looking for links that call openNewWindows(code1, code2) under
    <span class='label'>Catégories:</span>.
    """
    pattern = re.compile(r"openNewWindows\((\d+),\s*(\d+)\)")

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    cat_span = soup.find("span", class_="label", string="Catégories:")
    if not cat_span:
        return []
    parent = cat_span.parent

    a_tags = parent.find_all("a", onclick=True)
    results = []
    for link in a_tags:
        onclick_str = link.get("onclick", "")
        match = pattern.search(onclick_str)
        if match:
            code1 = match.group(1)
            code2 = match.group(2)
            category_name = link.get_text(strip=True)
            results.append((code1, code2, category_name))

    return results


def getReportURL(listOfCodes):
    """
    Takes a list of triplets (code1, code2, category_name)
    and returns [(category_name, report_url), ...].
    Example: (84019, 350756, 'Ligue 4 - TT 4x2 STANDARD')
    -> 'https://www.myrcm.ch/myrcm/report/fr/84019/350756?reportKey=103'
    """
    report_urls = []
    for code1, code2, category_name in listOfCodes:
        url = f"https://www.myrcm.ch/myrcm/report/fr/{code1}/{code2}?reportKey=103"
        report_urls.append((category_name, url))
    return report_urls

def parse_report_page(url):
    """
    Based on the provided HTML structure, each series is indicated by:
      <p id="title">Série X</p>
    followed by a table with columns:
      #, N°, Pilote, Pays, Club, Transpondeur, Chassis, Moteur, Carrosserie, Pneus, Radio

    We only parse (#, Pilote, Pays).

    Return data in the form:
    [
      {
        'serie_name': 'Série 1',
        'pilots': [
            {'num': '#', 'pilot': 'Nom Pilote', 'country': 'Pays'},
            ...
        ]
      },
      ...
    ]
    """
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    series_data = []

    # Locate all <p id="title"> (Série 1, Série 2, etc.)
    p_tags = soup.find_all("p", id="title")

    for p_tag in p_tags:
        serie_name = p_tag.get_text(strip=True)

        # The driver table might be the next <table> after this <p>.
        table = p_tag.find_next("table")
        if not table:
            continue

        pilots_data = []
        rows = table.find_all("tr")
        # row[0] is probably the header, so skip it
        for row in rows[1:]:
            cols = row.find_all("td")
            # We need at least 4 columns to parse (#=0, Pilote=2, Pays=3)
            if len(cols) < 4:
                continue

            num = cols[0].get_text(strip=True)      # Column #
            pilot_name = cols[2].get_text(strip=True)  # Column Pilote
            country = cols[3].get_text(strip=True)     # Column Pays

            pilots_data.append({
                'num': num,
                'pilot': pilot_name,
                'country': country,
            })

        series_data.append({
            'serie_name': serie_name,
            'pilots': pilots_data
        })

    return series_data

def build_categories(url, basePath:Path):
    """
    1) Extract categories from the main page.
    2) For each category, parse all series and pilots.
    3) Return a list of Category objects.
    """
    # Step 1: get category codes
    codes_and_names = get_codes_and_names(url)
    # Step 2: convert to (category_name, category_url)
    urls = getReportURL(codes_and_names)

    categories = []

    for cat_name, cat_url in urls:
        # Create Category object
        category_obj = Category(cat_name, [])

        # Parse the series for this category
        data = parse_report_page(cat_url)

        # Build Serie + myRCMPilot objects
        for serie_dict in data:
            serie_obj = Serie(serie_dict['serie_name'])

            for pilot_dict in serie_dict['pilots']:
                # ID is pilot_dict['num']
                # Name is pilot_dict['pilot']
                # Country is pilot_dict['country']
                pilot_obj = myRCMPilot(
                    ID=pilot_dict['num'],
                    name=pilot_dict['pilot'],
                    country=pilot_dict['country'],
                    profilePicPath=None,
                    carPicPath=Path(basePath, category_obj.prettyName, serie_obj.serieName, f"{category_obj.prettyName}-{serie_obj.serieName}-{pilot_dict['pilot']}.jpg")
                )
                serie_obj.pilotlist.append(pilot_obj)

            category_obj.serieList.append(serie_obj)

        categories.append(category_obj)
    print(categories)
    return categories

# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    main_url = "https://www.myrcm.ch/myrcm/main?dId[O]=53143&pLa=fr&dId[E]=84019&tId=E&hId[1]=org#"
    all_categories = build_categories(main_url)

    # Example: Print out the resulting structure
    for cat in all_categories:
        print("\n== Category ==", cat)
        for serie_obj in cat.serieList:
            print("   ", serie_obj)
            for pilot in serie_obj.pilotlist:
                print("       ", pilot)
