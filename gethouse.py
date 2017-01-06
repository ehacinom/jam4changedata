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

        Notes on html grab from each individual official website
            str all but can be otherwise denoted
            () optional
            regex match, tuple https://regex101.com/r/6er3zh/1
                1 FirstName 
                2 LastName 
                3 
                4 Position ()
                5 District short int
                6 Party char
                7 City 
                8 
                9 MadisonOffice 
                10 Telephones 
                11 Fax
                12 
                13 DistrictPhone ()
                14 Email
                15 
                16 DistrictAddress ()
                17 
                18 VotingAddress ()
                19 
                20 Staff ()
                21 
                22 
                23 Committees ()
                24
                25
                26 Biography ()

        TODO
        There is overlap between the following three.
        1. Author Index http://docs.legis.wisconsin.gov/
            - 2015/related/author_index/assembly/1362?view=section
            - 2017/related/author_index/senate/1501
            - 2015/related/author_index/senate
        2. Feed Websites on their details/official website
            http://docs.legis.wisconsin.gov/feed/
            Authored Proposals 
                - 2015/legislators/assembly/1362?kind=authored_proposals
                - 2017/legislators/senate/1501?kind=authored_proposals
            All Related Items
                - 2017/legislators/senate/1501
                - 2015/legislators/assembly/1362
        3. info[1].get_text(): information on the right-hand side:
            Authored
            Coauthored
            Cosponsored
            Amendments
            Votes

        """

        if out not in ['assembly', 'senate']:
            warning('Input must be either "assembly" or "senate".')
            return 0
        
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

        # set up regex for official webpage
        # https://regex101.com/r/6er3zh/1
        regex = r'^\n+\w+? (.+?) (\w+?)\n+((.+?)|)\n+\w+ District ' + \
                r'(\d+?) \((R|D) - (.+?)\)(\s|\S)+?Madison Office:' + \
                r'\s+(.+?)\s+Telephone:\n\s+(.+)\s+Fax:\n\s+(.+)\s' + \
                r'+(District Phone:\s+(.+)|)\s+Email:\n(.+)\s+(Dist' + \
                r'rict Address:\s+(.+)|)\s+(Voting Address:\s+(.' + \
                r'+)|)\s*(Staff:\n((\s|\S)+?)|)\n(Current Committe' + \
                r'es\n((\s|\S)+?)|)\n\s+(Biography\n((.| |\n)+)|)$'
        self.regex = re.compile(regex)

        # Go to main list and parse html
        url = 'https://docs.legis.wisconsin.gov/2015/legislators/' + out
        text = load_txt(url)
        parser = BeautifulSoup(text, "lxml")
        legislators = parser.body.find_all('div', attrs={'class':'rounded'})

        # for each legislator
        house = []
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
                left, _ = self.get_official_html(official)
                # ignore right for now TODO
                
                # match for data
                match = self.regex.search(left)
                if not match:
                    warn = 'No data parsed for representative. No regex match.'
                    warning(warn, 'HTML below.', left, official)
                    continue
                
                # retrieve data
                rep = self.edit_left(match)
                
                for i, r in enumerate(rep):
                    if i ==  9 and r: print 'district phone'
                    elif i == 13: break
                    print r
                print '---'
                
                rep.extend([official, personal])
                # also feed websites, see TODO
                house.append(rep)
            else:
                warn = 'Website missing of a legislator: official'
                warning(warn, official, legis.find_all('a'))
                continue
        
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
                  'Committees', 'Biography', 'OfficiaWeb', 'PersonalWeb']
        with open(fn, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(house)

        print len(house)
        return None


    def get_official_html(self, official):
        """
        Get HTML from official website
        Return (left, right) information
        Currently ignoring the right information
        
        INPUT
        official, a str url
        
        OUTPUT
            left, right: text from website

        """
        
        # parse html
        text = load_txt(official)
        parser = BeautifulSoup(text, 'lxml')
        info = parser.body.find_all('div', attrs={'class':'span6'})

        if len(info) != 2:
            warn = 'This site does not have 2 <div class="span6">'
            for i in info: 
                print '--'
                print i
            warning(warn, len(info) + ' div retrieved', official)

        # retrieve text from left side  (info[0])
        # and remove \u2018 | \u2019 to make csv happy
        left = info[0].get_text()
        left = rm_unicode(left)
        
        # retrive text from right side
        #right = info[1].get_text()
        #right = rm_unicode(right)
        right = None
        
        return left, right


    def edit_address(self, txt):
        """Reformat address"""
    
        if txt == None: 
            return txt
    
        # too many spaces before zip, and missing newline
        address = re.sub(r'\s+', ' ', txt)
        address = re.sub(r'([A-Z])([A-Z][a-z])', r'\1\\n\2', address)
        return re.sub(r'([a-z]{2}|\d|[a-z]\.)([A-Z])', r'\1\\n\2', address)


    def edit_telephones(self, txt):
        """Reformat Telephones"""
    
        if txt == None: 
            return txt
        
        return re.sub(r'(\d)\(', r'\1\\n(', txt)


    def edit_districtphone(self, txt):
        """Reformat DistrictPhone"""
    
        if txt == None: 
            return txt
    
        return txt.lstrip()


    def edit_email(self, txt):
        """Reformat Email"""
    
        if txt == None: 
            return txt
        
        return txt.split('@')[0]


    def edit_staff(self, txt):
        """
        Reformat Staff
    
        All staffers comma delimited.
        Staffer name, with periods instead of spaces, is the tag of their email,
            except the names like Name;Tag
        Email is tag@
    
        NOTES
        Very unclean. Do original split, then save only the name of staffer
        + optional email tag if tag differs from standard 
            FirstName.LastName@legis.wisconsin.gov
    
        Original:
            # returned list of str tuples
            # tmp = filter(None, staff.rstrip().split('\n'))
            # return [(tmp[j], tmp[j+1]) for j in xrange(0, len(tmp), 2)]

        TO DO
        Rewrite
    
        """
    
        if txt == None: 
            return txt
        
        # output
        fin = None
        
        # iterate through [name, email, ...]
        staff = filter(None, txt.rstrip().split('\n'))
        for j in xrange(0, len(staff), 2):
            # email tag
            tag = staff[j+1].split('@')[0]
        
            if tag == staff[j].replace(' ', '.'):
                if fin: fin = fin + ', ' + staff[j]
                else: fin = staff[j]
            else:
                #warning('Email does not match', tmp[j], tmp[j+1])
                if fin: fin = fin + ', ' + staff[j] + ';' + tag
                else: fin = staff[j] + ';' + tag
    
        return fin


    def edit_com(self, txt):
        """Reformat Committees"""
        
        if txt == None: 
            return txt
        
        return txt.replace("\n", "\\n")


    def edit_bio(self, txt):
        """Reformat Bio"""
    
        if txt == None: 
            return txt
        
        return txt.rstrip().lstrip().replace("\n", "\\n")


    def edit_left(self, match):
        """
        Reduce data for Representatives/Senators
    
        INPUT
        match the regex search matches, retrieve with match.group(i)
    
        OUTPUT
        rep
            0 FirstName 
            1 LastName 
            2 Position ()
            3 District short int
            4 Party char
            5 City  
            6 MadisonOffice 
            7 Telephones 
            8 Fax 
            9 DistrictPhone ()
            10 Email 
            11 DistrictAddress ()
            12 VotingAddress ()
            13 Staff ()
            14 Committees ()
            15 Biography ()

        """
        
        # get matches
        rep = list(match.group(1, 2, 4, 5, 6, 7, 9, 10, 11,
                               13, 14, 16, 18, 20, 23, 26))
        
        # Addresses
        # Room 113 NorthState CapitolP.O. Box 8952Madison, WI 53708
        # 10 Division St.Milton, WI 53563
        rep[6] = self.edit_address(rep[6])
        rep[11] = self.edit_address(rep[11])
        rep[12] = self.edit_address(rep[12])
    
        # Telephones
        rep[7] = self.edit_telephones(rep[7])
        # rep[9] = self.edit_districtphone(rep[9])
    
        # Email, Staff, Committees, Biography
        rep[10] = self.edit_email(rep[10])
        rep[13] = self.edit_staff(rep[13])
        rep[14] = self.edit_com(rep[14])
        rep[15] = self.edit_bio(rep[15])
    
        return rep