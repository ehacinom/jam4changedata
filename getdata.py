
from utils import *
import re
from bs4 import BeautifulSoup
import lxml
import csv

from random import randint

class GetData(object):
    """
    
    Example
    
    from getdata import GetData
    obj = GetData()
    obj.getlegislators()
    
    """
    
    def __init__(self):
        """
        Setup
        """

        self.year = str(2017)
        self.docs = r'http://docs.legis.wisconsin.gov'
        self.site = r'http://legis.wisconsin.gov'
        
        # set up regex for legislators webscraping
        # left side of official legislator page
        # https://regex101.com/r/6er3zh/2 
        regex = r'^\n+\w+? (.+?) (\w+?)\n+((.+?)|)\n+\w+ District ' + \
                r'(\d+?) \((R|D) - (.+?)\)(\s|\S)+?Madison Office:' + \
                r'\s+(.+?)\s+Telephone:\n\s+(.+)\s*(Fax:\n\s+(.+)|)' + \
                r'\s+(District Phone:\s+(.+)|)\s+Email:\n(.+)\s+' + \
                r'(District Address:\s+(.+)|)\s+(Voting Address:\s+' + \
                r'(.+)|)\s*(Staff:\n((\s|\S)+?)|)\n(Current Committees' + \
                r'\n((\s|\S)+?)|)\n\s+(Biography\n((.| |\n)+)|)$'
        self.leftlegisregex = re.compile(regex)
    
    def _getlegislators_replist(self, house_list):
        '''
        Got to the list of all legislators in chosen house, house_list
        Parse html using BeautifulSoup
        Return list of text.
        
        INPUT
        house_list, str url of the list of representatives in chosen house
        
        OUTPUT
        replist, list of text w/out html for each legislator 
        
        '''

        # got to main list and parse html
        text = load_txt(house_list)
        parser = BeautifulSoup(text, "lxml")
        replist = parser.body.find_all('div', attrs={'class':'rounded'})
        
        return replist
    
    def _getlegislators_official_html(self, official):
        """
        Get HTML from official website
        Return (left, right) information
        Currently ignoring the right information
        
        INPUT
        official, a str url
        
        OUTPUT
            website data, list of left, right
            to get text, right = rm_unicode(info[1].get_text())

        """
        
        # parse html
        text = load_txt(official)
        parser = BeautifulSoup(text, 'lxml')
        info = parser.body.find_all('div', attrs={'class':'span6'})

        if len(info) != 2:
            warn = 'This site does not have 2 <div class="span6">'
            for i in info: 
                print '--\n', i
            warning(warn, len(info) + ' div retrieved', official)

        return info
    
    def _getlegislators_edit_address(self, txt):
        """Reformat address"""
    
        if txt == None: 
            return txt
    
        # too many spaces before zip, and missing newline
        address = re.sub(r'\s+', ' ', txt)
        address = re.sub(r'([A-Z])([A-Z][a-z])', r'\1;\2', address)
        return re.sub(r'([a-z]{2}|\d|[a-z]\.)([A-Z])', r'\1;\2', address)

    def _getlegislators_edit_telephones(self, txt):
        """Reformat Telephones"""
    
        if txt == None: 
            return txt
        
        return re.sub(r'(\d)\(', r'\1;(', txt)

    def _getlegislators_edit_districtphone(self, txt):
        """Reformat DistrictPhone"""
    
        if txt == None: 
            return txt
    
        return txt.lstrip()

    def _getlegislators_edit_email(self, txt):
        """Reformat Email"""
    
        if txt == None: 
            return txt
        
        return txt.split('@')[0]

    def _getlegislators_edit_staff(self, txt):
        """
        Reformat Staff
    
        All staffers ; delimited: name,email;
        
        """
    
        if txt == None: 
            return txt
        
        # iterate through [name, email]
        info = filter(None, txt.rstrip().split('\n'))
        staff = ''
        
        for item in info:
            tmp = item.split('@')
            lentmp = len(tmp)
            if lentmp == 1:
                staff += ';' + tmp[0] + ','
            else:
                staff += tmp[0]
        
        if staff:
            return staff[1:]
        else:
            return None

    def _getlegislators_edit_com(self, txt):
        """Reformat Committees"""
        
        if txt == None: 
            return txt, txt
        
        # PositionedCommittees or Committees
        comlist = txt.split('\n')
        pcom, com = '', ''
        for cl in comlist:
            if cl[-1] == ')':
                pcom += cl
            else:
                com += cl
        
        if not pcom: pcom = None
        if not com: com = None
        
        return pcom, com

    def _getlegislators_edit_bio(self, txt):
        """Reformat Bio"""
    
        if txt == None: 
            return txt
        
        return txt.rstrip().lstrip().replace("\n", "\\n")

    def _getlegislators_edit_left(self, mleft):
        """
        Reduce data for Representatives/Senators
    
        INPUT
        mleft the regex search matches, retrieve with match.group(i)
    
        OUTPUT
        left, list
            0 FirstName 
            1 LastName 
            2 Position ()
            3 District short int
            4 Party char
            5 City  
            6 MadisonOffice 
            7 Telephones 
            8 Fax ()
            9 DistrictPhone ()
            10 Email 
            11 DistrictAddress ()
            12 VotingAddress ()
            13 Staff ()
            14 PositionedCommittees ()
            15 Committees ()
            16 Biography ()

        """
        
        # get matches
        left = list(mleft.group(1, 2, 4, 5, 6, 7, 9, 10, 12,
                               14, 15, 17, 19, 21, 24, 27))
        
        # Addresses
        # Room 113 NorthState CapitolP.O. Box 8952Madison, WI 53708
        # 10 Division St.Milton, WI 53563
        left[6] = self._getlegislators_edit_address(left[6])
        left[11] = self._getlegislators_edit_address(left[11])
        left[12] = self._getlegislators_edit_address(left[12])
    
        # Telephones
        left[7] = self._getlegislators_edit_telephones(left[7])
        # left[9] = self._getlegislators_edit_districtphone(left[9])
    
        # Email, Staff
        # left[10] = self._getlegislators_edit_email(left[10])
        left[13] = self._getlegislators_edit_staff(left[13])
        
        # Committees, Biography
        left[14], com = self._getlegislators_edit_com(left[14])
        bio = self._getlegislators_edit_bio(left[15])
        left[15] = com
        left.append(bio)
        
        return left 
    
    def _getlegislators_edit_right(self, right):
        '''
        Reduce data for legislators
        
        INPUT
        right, the right side of official web page
        
        OUTPUT
        cosponsored, the list of cosponsored proposals
        
        '''
        
        
        # ignoring all other tabs
        # AuthoredCo-authoredCosponsoredAmendmentsVotes
        links = right.find('div', {'id': 'cosponsoredProposals'})
        if not links:
            return ''
        
        cosponsored = ''
        for link in links.find_all('a'):
            tmp = ';' + link.get('href')[16:]
            cosponsored += tmp
        
        return cosponsored
    
    def _getlegislators_authorindex(self, author_url):
        """
        Get data from authorindex website
        
        INPUT
        author_url, a str url
        
        OUTPUT
        authorindex, 

        """
        
        # parse html
        text = load_txt(author_url)
        parser = BeautifulSoup(text, 'lxml')
        info = parser.body.find_all('div', attrs={'class':'authorindex'})
        # info is length 1 ResultSet
        
        authorindex = -1
        for inf in info[0].find_all('a'):
            
            # skip first link
            if authorindex == -1:
                authorindex = ''
                continue
            elif not authorindex:
                authorindex = inf.get('rel')[0][17:]
            else:
                authorindex += ';' + inf.get('rel')[0][17:]
            
        return authorindex
    
    def getlegislators(self):
        """
        Get data from official websites of legislators and move it to CSV
        Outputs all fields to 'house.csv'
        Outputs reps to 'house_list.txt'
        
        """
        
        legislators = []
        for house in ['assembly', 'senate']:
            
            # Each representative has official website, and most have personal
            # official is your 4digit ID at the end of
            #     http://docs.legis.wisconsin.gov/ YEAR/legislators/HOUSE/
            # personal is your (District)/LastName at the end of
            #     http://legis.wisconsin.gov/HOUSE/            
            ow = r'^/' + self.year + r'/legislators/' + house + r'/'
            pw = self.site + r'/' + house + r'/'
            official_web = re.compile(ow)
            personal_web = re.compile(pw)
            
            # author index setup
            author_base = self.docs + r'/' + self.year + \
                          r'/related/author_index/' + house + r'/'
            
            # list of all representatibes
            house_list = self.docs + r'/' +  self.year + r'/legislators/' + house + r'/'
            
            # get html into parsed data
            replist = self._getlegislators_replist(house_list)
            
            # iterate over each legislator
            for rep in replist:
                # ignore class="breadcrumb rounded"
                if rep['class'][0] == 'breadcrumb': continue

                # find the websites of this legislator
                official, personal = None, None
                for link in rep.find_all('a'):
                    if official and personal: break
                    tmp = link.get('href')
                    if tmp:
                        if official_web.match(tmp):
                            official = self.docs + tmp #tmp[-4:]
                        elif personal_web.match(tmp):
                            personal = tmp
                
                # go to official site and grab all other information
                if official:
                    officialinfo = self._getlegislators_official_html(official)

                    # left
                    # retrieve text from two sides 
                    # and remove \u2018 | \u2019 to make csv happy
                    left = rm_unicode(officialinfo[0].get_text())
                    mleft = self.leftlegisregex.search(left)
                    if mleft:
                        overview = self._getlegislators_edit_left(mleft)
                    else:
                        warn = 'No data parsed for representative. No regex match.'
                        warn1 = 'NO DATA ADDED.'
                        warning(warn, warn1, official, left)
                        continue
                    
                    # right
                    # AmendmentsVotes TODO
                    # AuthoredCo-authoredCosponsoredAmendmentsVotes
                    cosponsored = self._getlegislators_edit_right(officialinfo[1])
                else:
                    warn = 'Website missing of a legislator: official'
                    warning(warn, official, rep.find_all('a'))
                    continue
                
                # go to feed websites TODO
                
                # go to author index website
                # for authored/co-authored bills
                author_url = author_base + official[-4:] + r'?view=section'
                authorindex = self._getlegislators_authorindex(author_url)
                # these bills are found at
                # http://docs.legis.wisconsin.gov/2017/proposals/BILL
                
                # get some random stuff
                # get an HID index for each user
                hid = house[0].upper() + "%02d" % int(overview[3])
                # get the PID
                pid = official[-4:]
                # get the region
                region = str(randint(0,5)) # TODO
                # get the picture:: picture is official.jpg so nevermind!
                
                # data
                legis = [hid, pid] + overview + \
                        [official, personal, region, authorindex+cosponsored]
                # print legis
                legislators.append(legis)
                
        # save list of legislators to file
        with open('legislators.txt', 'w') as f:
            for leg in legislators:
                row = leg[0] + ',' + leg[1] + ',' + leg[1] + ' ' + leg[2] + \
                      ',' + leg[21] + '\n'
                f.write(row)

        # write house to csv
        header = ['HID', 'PID', # 01
                  'FirstName', 'LastName', 'Position', 'District', 'Party', #23456
                  'City', 'MadisonOffice', 'Telephones', 'Fax', 'DistrictPhone', #7891011
                  'Email', 'DistrictAddress', 'VotingAddress', 'Staff', #12131415
                  'PositionedCommittees', 'Committees', 'Biography', #161718
                  'OfficialWeb', 'PersonalWeb', 'Region', 'BillIndex'] #19202122
        with open('legislators.csv', 'wb') as f:
            #quotechar="'", lineterminator = '\r\n'
            # also see utils.py rm_unicode()
            writer = csv.writer(f, delimiter='|', quoting = csv.QUOTE_NONE, 
                                escapechar = '\\')
            writer.writerow(header)
            writer.writerows(house)

        return len(legislators)


