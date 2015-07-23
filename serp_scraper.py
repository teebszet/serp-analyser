#!/usr/bin/env python

import sys
import argparse
import json
import re
import requests
import codecs
from bs4 import BeautifulSoup

""" Synopsis

To Run:
    ./serp_scraper.py -q "review barnyard london"

Then view your results like:
    cat ./search_results_dishoom.json | python -m json.tool

Use a bash loop through queries like:
    for r in dishoom barnyard "voodoo rays";
        do ./serp_scraper.py -q "review $r london";
    done;

Iterate through a file with queries like:
    for r in `cat queries.txt`;
        do ./serp_scraper.py -q "review $r london";
    done;

"""

def cleanse_href (href):
    """ cleanse the google href of extra tracking params and junk
    """
    url = re.sub(r'^/url\?q=', r'', href)
    url = re.sub(r'&sa=.*$', r'', url)
    url = re.sub(r'^.*&adurl=', r'', url) #TODO do we want to include the ad headings? probably not
    print "cleansed href -> url {0}".format(url) 
    return url

if __name__ == '__main__':

    # parse arguments
    ap = argparse.ArgumentParser(
        description="Save the search results of a google query to json")
    ap.add_argument(
        '-q',
        '--query',
        dest='query',
        required=True,
        help='search query to google')
    ap.add_argument(
        '-d',
        '--search-domain',
        dest='search_domain',
        default='com',
        help='google domain to use')
    args = ap.parse_args()
    print "START of {0}".format(sys.argv[0])

    # get request
    query = args.query
    search_domain = args.search_domain
    url = "https://www.google.{0}/search".format(search_domain) 
    params = {'q': query}
    r = requests.get(url, params=params)
    print "..scraping search results at {0}".format(r.url)

    # parse raw results
    soup = BeautifulSoup(r.text, 'html.parser', from_encoding='utf-8')

    # write out raw results
    query_name = re.sub(r"\s", '_', query)
    raw_filepath = "raw_search_results_{0}.html".format(query_name)
    print "..writing to {0}".format(raw_filepath)
    with codecs.open(raw_filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(soup.prettify())

    # parse interesting fields
    all_links = []
    count = 0
    for link in soup.find_all('h3'):
        count += 1
        data = {}
        data['url'] = cleanse_href(link.find('a')['href'])

        title = ' '.join(link.find('a').stripped_strings)
        data['name'] = title

        all_links.append(data)

    print "..found {0} results".format(count)

    # write out json to file
    query_name = re.sub(r"\s", '_', query)
    filepath = "search_results_{0}.json".format(query_name)
    print "..writing to {0}".format(filepath)
    with open(filepath, 'w') as outfile:
        json.dump(all_links, outfile)
