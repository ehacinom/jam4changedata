import urllib
import re

def load_txt(url):
    """Grab text from string url"""
    
    fp = urllib.urlopen(url)
    text = fp.read()
    fp.close()

    return text

def warning(*args):
    """Print everything as a warning"""
    
    print('WARNING')
    for error in args: 
        print(error)
    print('--------------')

def rm_unicode(text):
    """
    Remove all unicode quotations from text
    
    We are aquiring text from government websites with unicode quotes.
    Because we're writing to csv as well, and csv str()'s everything, 
    this doesn't work well.
    
    One option is to 
        import sys
        reload(sys)
        sys.setdefaultencoding("utf-8")
    
    Setting encoding to unicode is find but not great for the csv module.
    
    """
    
    a = re.sub(u"(\u2018|\u2019)", "'", text)
    b = re.sub(u"(\u201c|\u201d)", '"', a)
    c = re.sub(u"(\u2013)", '-', b)
    d = re.sub(u"(\u2014)", '--', c)

    return str(d)