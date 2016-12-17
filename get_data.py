import urllib





def load_xml_data(url):
    """
    INPUT
    str url
    
    OUTPUT
    dict xml data
    
    Retrieves data through URL get
    
    """
    
    url = urllib.urlopen(url)
    return 