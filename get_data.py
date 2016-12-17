import urllib
import xmltodict
import csv

def load_txt(url):
    """
    Grab text from url
    
    INPUT
    url of text/xml data
    
    OUTPUT
    text/xml data
        
    """
    # load txt
    fp = urllib.urlopen(url)
    text = fp.read()
    fp.close()
    
    return text

def edit_JointCommittee(item):
    """
    Dealing with Joint Committee reports
    (esp from the Joint Legislative Audit Committee)
    
    In the future, check that the information skipped is reasonable
    
    INPUT
    item, the list of OrderedDicts with metadata on each committee
    Parameters and example data:
        (u'guid', OrderedDict([(u'@isPermaLink', u'false'), ('#text', u'5b7a05a6-a615-4dd9-94d6-7346f51a1363')]))
        (u'link', u'http://docs.legis.wisconsin.gov/document/committee/2015/1475')
        (u'title', u'University of Wisconsin Hospitals and Clinics Authority - 2016-12-17')
        (u'description', u'University of Wisconsin Hospitals and Clinics Authority')
        (u'pubDate', u'Sat, 17 Dec 2016 07:35:58 -0600')
        (u'a10:updated', u'2016-12-17T07:35:58-06:00')
    
    OUTPUT
    boolean, if data will be used
    
    """
    
    OtherJointCommitteeCrap = 'records'
    AnnoyingJointCommittees = ['Presentation', 'Report', 'Proceedings', 
                               'Minutes', 'Proposed', 'Audio', 'Agenda']
    
    name = item['description']
    title = item['title']

    if not name: 
        return False
    
    if OtherJointCommitteeCrap in name:
        return False
    
    for ajc in AnnoyingJointCommittees:
        if ajc in title:
            return False
    
    return True

def get_meta_committee(text, committee_type):
    """
    Get metadata for committees
    
    INPUT
    text from load_txt(url)
    
    INTERMEDIARIES
    x is a list of items/OrderedDicts with metadata on each committee
    Parameters and example data:
        (u'guid', OrderedDict([(u'@isPermaLink', u'false'), ('#text', u'5b7a05a6-a615-4dd9-94d6-7346f51a1363')]))
        (u'link', u'http://docs.legis.wisconsin.gov/document/committee/2015/1475')
        (u'title', u'University of Wisconsin Hospitals and Clinics Authority - 2016-12-17')
        (u'description', u'University of Wisconsin Hospitals and Clinics Authority')
        (u'pubDate', u'Sat, 17 Dec 2016 07:35:58 -0600')
        (u'a10:updated', u'2016-12-17T07:35:58-06:00')
    
    OUTPUT
    data, [name, committee_type, link]
    
    """
    
    # x is a list of OrderedDict
    # should do some error catching here
    # find format of data through testing / pretty xml
    x = xmltodict.parse(text)['rss']['channel']['item']
    
    # iterate for relevant information
    data = []
    for item in x:
        name = item['description']
        
        interest = True
        if not name: 
            interest = False
        
        # dealing with Joint Committee reports
        if committee_type == 'Joint':
            interest = edit_JointCommittee(item)
        
        # add to data
        if interest:
            data.append([name, committee_type, item['link']])
    
    return data

def get_committee(out = 'committees.csv'):
    """
    Get all data for committees
    
    INPUT
    out the output file
    
    SAVE TO FILE out.
    [name, link, Y-M-D]
    
    SAVE TO FILE committee_list.txt
    names of all the committees
    
    """
    
    root = 'http://docs.legis.wisconsin.gov/feed/2015/committees/'
    committee_type = ['Senate', 'Assembly', 'Joint', 'Other']
    
    data = []
    for ct in committee_type:
        # metadata
        text = load_txt(root+ct)
        metadata = get_meta_committee(text, ct)
        
        # do some other research
        # follow some links
        
        # add to data
        data.extend(metadata)

    # save list of committees to file
    with open('committee_list.txt', 'w') as f:
        for m in data:
             f.write(m[0]+'\n')
    
#     # write
#     with open(out, 'a') as f:
#         f.write()
