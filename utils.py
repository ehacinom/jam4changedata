import urllib

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