import os
from lxml import etree
import urllib3
import json
import time
from apscheduler.schedulers.blocking import BlockingScheduler

http = urllib3.PoolManager()


def get_pbi_list():
    with open('pbi.json', 'r') as f:
        pbi_list = json.load(f)
        return pbi_list


def get_msg(mon, pbi_id):
    url = 'http://172.16.30.125/projects/cloud-ecs/issues?' \
          'utf8=✓&set_filter=1&f[]=status_id&op[status_id]=o&' \
          'f[]=parent_id&op[parent_id]==&v[parent_id][]=%s&' \
          'f[]=tracker_id&op[tracker_id]==&v[tracker_id][]=1&' \
          'f[]=priority_id&op[priority_id]=%s&v[priority_id][]=3&' \
          'key=7132465d1a844d57a7d002dd1d9b4ed434aca8a6'
    request = http.request('GET', url % (str(pbi_id), '='))
    high_data = request.data.decode()
    request = http.request('GET', url % (str(pbi_id), '!'))
    normal_data = request.data.decode()

    tree = etree.HTML(high_data)
    table = tree.xpath('//tbody/tr/td[@class="subject"]')
    high_num = len(table)
    tree = etree.HTML(normal_data)
    table = tree.xpath('//tbody/tr/td[@class="subject"]')
    normal_num = len(table)

    time_mark = time.strftime("%Y-%m-%d", time.localtime())
    js = {
        "high": {
            time_mark: high_num,
        },
        "normal": {
            time_mark: normal_num
        }
    }
    update_data(mon, pbi_id, js)


def update_data(mon, pbi_id, js):
    if not os.path.exists('db'):
        os.mkdir('db')
    if not os.path.exists('db/%s' % mon):
        os.mkdir('db/%s' % mon)

    with open('db/%s/%s.json' % (mon, pbi_id), 'r') as f:
        s = f.read()
        old_js = json.loads(s)
        print('old', old_js)
        f.close()
        with open('db/%s/%s.json' % (mon, pbi_id), 'w') as file:
            if s == '':
                json.dump(js, file)
            else:
                old_js['高优先级'].update(js['high'])
                old_js['普通优先级'].update(js['normal'])
                print('new', old_js)
                json.dump(old_js, file)
                file.close()




def start_job():
    pbi_list = get_pbi_list()
    for i, j in pbi_list.items():
        for task, info in j.items():
            get_msg(i, task)


def main():
    sched = BlockingScheduler()
    sched.add_job(start_job, 'interval', minutes=60)
    sched.start()


if __name__ == '__main__':
    main()
    # start_job()
