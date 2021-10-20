import requests
import os
from urllib import parse


def downloadImage(artwork):
    if not validURL(artwork):
        raise ValueError

    data = requests.get(artwork)
    if data.headers['Content-Type'].split('/')[0] == 'image':
        return data

    imgLinks = getImages(artwork)
    for imgLink in imgLinks:
        if 'artworks' in imgLink and '500x500' in imgLink:
            content = requests.get(imgLink)
            return content
    return None


def validURL(url: str) -> bool:
    u = parse.urlparse(url)
    # Check if scheme(http or https) and netloc(domain) are not empty
    return u[0] != '' and u[1] != ''


def getImages(url: str) -> list:
    response = requests.get(url, headers={
        'User-Agent': 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0'})
    html = response.text
    image_extensions = ['.jpg', '.ico', 'png', '.jpeg']
    links = set()
    for element in html.split('"'):
        if '/' in element:
            for img in image_extensions:
                if element.endswith(img):
                    link = element.replace('\\', '')
                    if 'http' != link[:4]:
                        link = os.path.join(url, link)
                    if validURL(link):
                        links.add(element.replace('\\', ''))
    return links


if __name__ == '__main__':
    print(downloadImage('https://soundcloud.com/9v9v/get-low'))
