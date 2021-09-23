import requests
from requests.exceptions import HTTPError, Timeout
from bs4 import BeautifulSoup
import pprint
import json
import os


def main():

    # Deletes data file if it exists so new one can be created
    clearFile()

    # URL where scraping will begin, has 19 cars
    baseURL = "https://www.carsales.com.au/cars/?q=Service.carsales.&offset="

    # Storing max number of pages to scrap
    PAGEMAXNUM = 21

    # Used to setting each car objects ID, and limiting amount of carObjs created
    carsNum = 0

    # Storing each page url in a separate list, each url after the base url has 12 cars
    pageUrls = []

    # Storing each car page url in a separate list
    carItemUrls = []

    # Storing each scraped car data in an array/list
    cars = []

    # Storing the website header in the header variable
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
    }

    # Scraping url of each page up to PAGEMAXNUM
    pageUrls = extractPageUrls(pageUrls, PAGEMAXNUM, baseURL)
    # Appending the base url to the front of the list
    # Scraping url for each car on each page
    carItemUrls = extractCarItemUrls(pageUrls, carItemUrls, headers)
    # Scraping data from car item url
    extractCarData(carItemUrls, headers, cars, carsNum)
    # Printing data in car with pretty print

    # Writing the car data to a json file
    pprint.pprint(cars)

    with open('data.json', 'w') as outfile:
        json.dump(cars, outfile)


def clearFile():
    if os.path.exists("data.json"):
        os.remove("data.json")


def extractPageUrls(pageUrls, PAGEMAXNUM, baseURL):
    # Since each url repeats by 12, can simply run a loop to capture each url
    for i in range(2, PAGEMAXNUM):
        num = i * 12
        pageUrls.append(f"{baseURL}{num}")

    return pageUrls


def extractCarItemUrls(pageUrls, carItemUrls, headers):
    for url in pageUrls:
        try:
            response = requests.get(url, headers=headers, timeout=3)
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Python 3.6
        except Exception as err:
            print(f'Other error occurred: {err}')  # Python 3.6
        else:
            content = BeautifulSoup(response.content, "html.parser")

            for link in content.select("a[class=js-encode-search]"):
                href = link['href']
                url = ''.join(('https://www.carsales.com.au', href))
                carItemUrls.append(url)
            # Since each car card has two links to the same car
            # need to remove duplicates
            carItemUrls = list(dict.fromkeys(carItemUrls))
    return carItemUrls


def extractCarData(carItemUrls, headers, cars, carsNum):
    for url in carItemUrls:
        try:
            response = requests.get(url, headers=headers, timeout=3)
            # If the response was successful, no Exception will be raised
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Python 3.6
        except Exception as err:
            print(f'Other error occurred: {err}')  # Python 3.6
        else:
            content = BeautifulSoup(response.content, "html.parser")
            cars.append(extractData(content, carsNum))
            carsNum += 1


def extractData(content, carsNum):
    title = extractTitle(content)
    image = extractImage(content)
    price = extractPrice(content)
    odometer = extractOdometer(content)
    bodyType = extractBody(content)
    transmission = extractTransmission(content)

    carObj = {
        "id": carsNum,
        "title": title,
        "price": price,
        "odometer": odometer,
        "body": bodyType,
        "transmission": transmission,
        "image": image
    }
    #print(f"CarsNum: {carsNum}")
    carsNum += 1
    return carObj


def extractTitle(content):
    # extracting the title to the title variable
    rawText = content.find('h1').text
    # spliting title into a list
    text = rawText.split()
    # removing all but the first three words
    while (text.__len__() > 3):
        del text[-1]
    title = ' '.join(text)
    return title


def extractImage(content):
    for div in content.find_all("div", {"class": "gallery-main"}):
        for image in div.select("img"):
            return str(image['src'])


def extractPrice(content):
    price = content.find("div", {"class": "price"}).text
    # if there isnt an asterisk at the end of the string
    if (price[-1] != "*"):
        return price
    else:
        listPrice = list(price)
        del listPrice[-1]
        price = ''.join(listPrice)
        return price


def extractDetails(content):
    details = content.find_all("div", {"class": "key-details-item-title"})
    while (details.__len__() > 3):
        del details[-1]
    return details


def extractOdometer(content):
    details = extractDetails(content)
    odometer = details[0].text
    return odometer[:-3]


def extractBody(content):
    details = extractDetails(content)
    body = details[1].text
    return body


def extractTransmission(content):
    details = extractDetails(content)
    transmission = details[2].text
    return transmission


if __name__ == "__main__":
    main()
