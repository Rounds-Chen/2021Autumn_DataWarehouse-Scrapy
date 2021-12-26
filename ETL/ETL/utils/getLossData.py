import json


def  getLossData():
    fj=open('../../result/res_3.json')
    old_res=json.load(fj)
    s=set()
    s2=set()

    for line in old_res:
        # print(line)
        # if len(line.keys())==1:
            s.add(line['id'])
    fj.close()
    # print(s)

    s1=set()
    with open('../data/temp_leaveOut_3.txt','r') as fi:
        for line in fi:
            s1.add(line[:-1])
        fi.close()
    # print(len(s1))
    s2=s1-s
    print(len(s2))
    with open ('../data/temp_leaveOut_4.txt','w') as f:
        f.write('\n'.join(s2))
    f.close()

def getLossAsin():
    asin_list=[]
    old_res=open('../../result/basic_info_res.json', 'r', encoding='utf-8')
    for line in old_res:
        line_x=(line.strip())[:-1]
        try:
            line_x=json.loads(line_x)

            if 'basic_info' not in line_x.keys():
                asin_list.append(line_x['id'])
        except:
            print(line_x)

    print('共有{}空数据'.format(len(asin_list)))

    with open('../data/loss_asin_2.txt', 'w') as f:
        f.write('\n'.join(asin_list))
    f.close()

def quchogn():
    s=set()
    with open('../data/loss_asin_2.txt','r') as f:
        for line in f:
            s.add(line)
    f.close()

    print("共有{}条asin。".format(len(s)))
    with open('../data/loss_asin_1.txt','w') as fi:
        fi.write(''.join(s))
    fi.close()

def get503Page():
    s1=set() # res数据
    s2=set() # all数据
    with open('../../res_3.txt','r',encoding='utf-8') as f:
        for index,line in enumerate(f):
            x=line.strip()[:-1]
            line=json.loads(x)
            print(index)
            s1.add(line['id'])
        # return f.readlines()
    f.close()

    with open('../data/temp_leaveOut_3.txt','r') as fi:
        for line in fi:
            s2.add(line)
    fi.close()

    s=s2.difference(s1)
    with open('../data/temp_leaveOut_4.txt','w') as fw:
        fw.write(''.join(s))
    fw.close()




if __name__=='__main__':
    # getLossAsin()

    # quchogn()
    # get503Page()
    # print(x)
    getLossData()