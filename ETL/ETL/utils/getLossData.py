import json

def getLossAsin():
    asin_list=[]
    old_res=open('../../basic_info_res.json','r',encoding='utf-8')
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
    with open('../data/loss_asin_2.txt') as f:
        for line in f:
            s.add(line)
    f.close()

    print("共有{}条asin。".format(len(s)))
    with open('../data/loss_asin_1.txt','w') as fi:
        fi.write(''.join(s))
    fi.close()


if __name__=='__main__':
    # getLossAsin()

    quchogn()