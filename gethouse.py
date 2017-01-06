from bs4 import BeautifulSoup
import csv
import lxml
import re
from utils import *

class GetHouse(object):
    """
    Get data from website and move it to CSV
    Outputs 16 fields to 'out.csv'
    Outputs legislatures to 'out_list.txt'
    
    
    Example
    
    from gethouse import GetHouse
    GetHouse('assembly')
    GetHouse('senate')
    
    """
    
    def __init__(self, out = 'assembly'):
        """
        Get all data for Representatives/Senators

        INPUT
        out the legislative house

        SAVE TO FILE out.csv
        data

        SAVE TO FILE out_list.txt
        names of all the representatives

        TO DO
        There is overlap between the following three.
        Author Index http://docs.legis.wisconsin.gov/
            - 2015/related/author_index/assembly/1362?view=section
            - 2017/related/author_index/senate/1501
            - 2015/related/author_index/senate
        Feed Websites on their details/official website
            http://docs.legis.wisconsin.gov/feed/
            Authored Proposals 
                - 2015/legislators/assembly/1362?kind=authored_proposals
                - 2017/legislators/senate/1501?kind=authored_proposals
            All Related Items
                - 2017/legislators/senate/1501
                - 2015/legislators/assembly/1362
        info[1].get_text(): information on the right-hand side:
            Authored
            Coauthored
            Cosponsored
            Amendments
            Votes

        """

        if out not in ['assembly', 'senate']:
            warning('Input must be either "assembly" or "senate".')
            return 0

        # store
        house = []

        # Go to main list and parse html
        url = 'https://docs.legis.wisconsin.gov/2015/legislators/' + out
        text = load_txt(url)
        parser = BeautifulSoup(text, "lxml")
        legislators = parser.body.find_all('div', attrs={'class':'rounded'})

        # set up regex for websites
        ow = r'/2015/legislators/' + out + r'/'
        pw = r'http://legis.wisconsin.gov/' + out + '/'
        official_web = re.compile(ow)
        personal_web = re.compile(pw)

        # Each representative has official website, and most have personal website
        # official is your 4digit ID at the end of 
        #     http://docs.legis.wisconsin.gov/2015/legislators/OUT/
        # personal is your District/LastName at the end of
        #     http://legis.wisconsin.gov/OUT/
        off_header = 'http://docs.legis.wisconsin.gov'

        # once into official website with legislator details
        # set up regex
        # https://regex101.com/r/d36hI9/1
        regex = r'\n\w+? (\w+?) (\w+?)\s+((.+?)|)\n+\w+ District ' + \
                 '(\d+?) \((R|D) - (.+?)\)(\s|\S)+?Madison Office' + \
                 ':\s+(.+?)\s+Telephone:\n\s+(.+)\s+Fax:\n\s+(.+)' + \
                 '\s+(District Phone:\n(.+)|)\s+Email:\n(.+)\s+(V' + \
                 'oting Address:\n\s+(.+)|)\s+Staff:\n((\s|\S)+?)' + \
                 '\n(Current Committees\n((\s|\S)+?)|)\n\s+Biogra' + \
                 'phy\n((.| |\n)+)'
        regex = re.compile(regex)

        # for each legislator
        for legis in legislators:
            # ignore class="breadcrumb rounded"
            if legis['class'][0] == 'breadcrumb': continue
    
            # find the websites of this legislator
            official, personal = None, None
            for link in legis.find_all('a'):
                tmp = link.get('href')
                if tmp:
                    if official and personal: 
                        break
            
                    if official_web.match(tmp) is not None:
                        official = off_header + tmp #tmp[-4:]
                    if personal_web.match(tmp):
                        personal = tmp
    
            # go to official site and grab all other information
            if official: 
                # parse html
                text = load_txt(official)
                parser = BeautifulSoup(text, 'lxml')
                info = parser.body.find_all('div', attrs={'class':'span6'})

                if len(info) != 2:
                    warn = 'This site does not have 2 <div class="span6">'
                    warning(warn, 'No data was retrieved', official)
        
                # retrieve text from left side  (info[0])
                # and remove \u2018 | \u2019 to make csv happy
                inf = info[0].get_text()
                inf = rm_unicode(inf)
        
                # match for data
                match = regex.search(inf)
                if not match:
                    warn = 'No data parsed for representative. HTML below.'
                    warning(warn, inf, official)
                    continue
              
                # edit data
                rep = edit_house(match)
                # other data
                rep.extend([official, personal])
                # also feed websites, see above the 'for' loop for notes
        
                # save data
                house.append(rep)
            else: 
                warn = 'Website missing: official'
                warning(warn, official, legis.find_all('a'))

        # save list of legislators to file
        fn = out + '_list.txt'
        with open(fn, 'w') as f:
            for h in house:
                f.write(h[0] + ' ' + h[1] + '\n')

        # write house to csv
        fn = out + '.csv'
        header = ['FirstName', 'LastName', 'Position', 'District', 'Party', 
                  'City', 'MadisonOffice', 'Telephones', 'Fax', 
                  'DistrictPhone', 'Email', 'VotingAddress', 'Staff', 
                  'Committees', 'Biography']
        with open(fn, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(house)

        print len(house)
        return house