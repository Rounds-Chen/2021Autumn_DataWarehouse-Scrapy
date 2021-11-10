import json

def getAsin(filename):
    asin=set()
    with open(filename) as f:
        for line in f:
            meta = json.loads(line)
            asin.add(meta['asin'])

    with open(r"data/asin.txt",'w') as fi:
        fi.write('\n'.join(asin))
    fi.close()

if __name__=='__main__':
    filename=r'data/Movies_and_TV_5.json'
    getAsin(filename)