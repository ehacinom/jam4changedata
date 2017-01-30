from bs4 import BeautifulSoup
import csv
import lxml
import re
from utils import *

class GetHouse(object):
    """
    Get data from website and move it to CSV
    Outputs 18 fields to 'out.csv'
    Outputs legislatures to 'out_list.txt'
    
    
    Example
    
    from gethouse import GetHouse
    GetHouse('assembly', 2015)
    GetHouse('senate', 2017)
    
    """
    
    def __init__(self, out = 'assembly', year = 2015):
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
            regex match, tuple https://regex101.com/r/6er3zh/1 and 2
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
                11 
                12 Fax ()
                13
                14 DistrictPhone ()
                15 Email
                16 
                17 DistrictAddress ()
                18 
                19 VotingAddress ()
                10 
                21 Staff ()
                22 
                23 
                24 Committees ()
                25
                26
                27 Biography ()

        TODO
        There is overlap between the following four.
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
        4. right, the text from the right side html of the official website

        """

        if out not in ['assembly', 'senate']:
            warning('Input house must be either "assembly" or "senate".')
            return None
        
        if year not in [2015, 2017]:
            warning('Input year must be either 2015 or 2017.')
        
        self.out = out
        self.year = str(year)
        
        # set up regex for websites
        ow = r'/' + self.year + r'/legislators/' + self.out + r'/'
        pw = r'http://legis.wisconsin.gov/' + self.out + r'/'
        official_web = re.compile(ow)
        personal_web = re.compile(pw)

        # Each representative has official website, and most have personal website
        # official is your 4digit ID at the end of 
        #     http://docs.legis.wisconsin.gov/YEAR/legislators/OUT/
        # personal is your (District)/LastName at the end of
        #     http://legis.wisconsin.gov/OUT/
        off_header = 'http://docs.legis.wisconsin.gov'

        # set up regex for official webpage
        # https://regex101.com/r/6er3zh/2
        # regex = r'^\n+\w+? (.+?) (\w+?)\n+((.+?)|)\n+\w+ District ' + \
        #         r'(\d+?) \((R|D) - (.+?)\)(\s|\S)+?Madison Office:' + \
        #         r'\s+(.+?)\s+Telephone:\n\s+(.+)\s*(Fax:\n\s+(.+)|' + \
        #         r')\s+(District Phone:\s+(.+)|)\s+Email:\n(.+)\s+(' + \
        #         r'District Address:\s+(.+)|)\s+(Voting Address:\s+' + \
        #         r'(.+)|)\s*(Staff:\n((\s|\S)+?)|)\n(Current Commit' + \
        #         r'tees\n((\s|\S)+?)|)\n\s+(Biography\n((.| |\n)+)|)$'
        regex = r'^\n+\w+? (.+?) (\w+?)\n+((.+?)|)\n+\w+ District ' + \
                r'(\d+?) \((R|D) - (.+?)\)(\s|\S)+?Madison Office:' + \
                r'\s+(.+?)\s+Telephone:\n\s+(.+)\s*(Fax:\n\s+(.+)|)' + \
                r'\s+(District Phone:\s+(.+)|)\s+Email:\n(.+)\s+' + \
                r'(District Address:\s+(.+)|)\s+(Voting Address:\s+' + \
                r'(.+)|)\s*(Staff:\n((\s|\S)+?)|)\n(Current Committees' + \
                r'\n((\s|\S)+?)|)\n\s+(Biography\n((.| |\n)+)|)$'
        self.regex = re.compile(regex)

        # Go to main list and parse html
        url = 'https://docs.legis.wisconsin.gov/' + \
              self.year + '/legislators/' + self.out
        text = load_txt(url)
        parser = BeautifulSoup(text, "lxml")
        legislators = parser.body.find_all('div', attrs={'class':'rounded'})

        # for each legislator
        tag = self.out[0].upper()        # get an ID index for each user
        house = []
        for legis in legislators:
            # ignore class="breadcrumb rounded"
            if legis['class'][0] == 'breadcrumb': continue
    
            # find the websites of this legislator
            official, personal = None, None
            for link in legis.find_all('a'):
                tmp = link.get('href')
                if tmp:
                    if official and personal: break
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
                
                # retrieve data
                if match:
                    # retrieve data
                    rep = self.edit_left(match)
                else:             
                    warn = 'No data parsed for representative. No regex match.'
                    warn1 = 'NO DATA ADDED.'
                    warning(warn, warn1, official, left)
                    # rep = ['', ''] + [None for i in xrange(14)]
                    # if this is added, tag no longer works (duplicate, also None)
                    continue
                
                # also feed websites, see TODO
                
                # index is S/A District
                tag + "%02d" % int(rep[3])
                rep = [tmp] + rep + [official, personal]
                house.append(rep)
            else:
                warn = 'Website missing of a legislator: official'
                warning(warn, official, legis.find_all('a'))
                continue
        
        # save list of legislators to file
        fn = out + '_list.txt'
        with open(fn, 'w') as f:
            for h in house:
                f.write(h[1] + ' ' + h[2] + '\n')

        # write house to csv
        fn = out + '.csv'
        header = ['ID', 'FirstName', 'LastName', 'Position', 'District', 
                  'Party', 'City', 'MadisonOffice', 'Telephones', 'Fax', 
                  'DistrictPhone', 'Email', 'DistrictAddress', 
                  'VotingAddress', 'Staff', 'Committees', 'Biography', 
                  'OfficiaWeb', 'PersonalWeb']
        with open(fn, 'wb') as f:
            #quotechar="'", lineterminator = '\r\n'
            # also see utils.py rm_unicode()
            writer = csv.writer(f, delimiter='|', quoting = csv.QUOTE_NONE, 
                                escapechar = '\\')
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
        rep = list(match.group(1, 2, 4, 5, 6, 7, 9, 10, 12,
                               14, 15, 17, 19, 21, 24, 27))
        
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