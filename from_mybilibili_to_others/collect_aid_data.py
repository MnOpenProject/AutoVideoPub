''' 从我的投稿视频数据里收集所有需要上传的视频 aid 数据 '''
from globalvars import __ROOTPATH__
import os,requests,progressbar,threadpool,json
from datetime import datetime
from .common_config import bilibili_request_headers
from .common_util import write_request_remember_txt,write_redeal_config_txt,get_video_name_by_title,is_in_exclude_txt,read_blibli_cookie_from_txt

my_request_headers = bilibili_request_headers

# 时间戳转日期时间字符串
def timestamp2datetime(timestamp_val):
    # 使用datetime
    date_array = datetime.fromtimestamp(timestamp_val)
    datetime_str = date_array.strftime("%Y-%m-%d %H:%M:%S")
    # print(datetime_str)   # 2013--10--10 23:40:00
    return datetime_str

# cookie 包含的是登录信息，所以若登录信息失效了，就需要到网站上重新登录，把最新的 cookie 复制到 cookie.txt 里

def read_cookie_from_txt():
    return read_blibli_cookie_from_txt()

def collect_aid_data():
    # 收集 aid 和 title
    aid_data = []
    title_list = []
    redeal_json_list = []
    # cur_page_data_count = 0 # 当前请求的数据量（当请求数据量小于 page_size 时，就说明这是最后一页了，如果当前请求数量为0，则说明上一页是最后一页）
    continue_request_data = True
    page_num = 1 # 页码
    page_size = 10 # 一页的最大数据量
    # 请求稿件分页列表        
    headers=my_request_headers
    headers['Cookie'] = read_cookie_from_txt()
    
    while continue_request_data:
        # status=pubed 表示查询的是 已通过(审核) 的视频数据列表
        url = f'https://member.bilibili.com/x/web/archives?status=pubed&pn={page_num}&ps={page_size}&coop=1&interactive=1'
        r = requests.request(method='GET',url=url,headers=headers)
        res_data = json.loads(r.content)['data']

        arc_audits = res_data['arc_audits']
        # 当前请求的数据量（当请求数据量小于 page_size 时，就说明这是最后一页了，如果当前请求数量为0，则说明上一页是最后一页）
        cur_page_data_count = len(arc_audits)
        print(f'正在请求数据：第 [{page_num}] 页')
        if not isinstance(arc_audits,list) or cur_page_data_count < page_size or cur_page_data_count == 0:
            # 若到了最后一页，则终止循环
            continue_request_data = False
        if cur_page_data_count > 0:
            for arc_item in arc_audits:
                aid_data_item = {
                    'aid': str(arc_item['Archive']['aid']),
                    'title': get_video_name_by_title(arc_item['Archive']['title']),
                    'datetime': timestamp2datetime(arc_item['Archive']['ptime'])
                }
                # 排除 title 相同的视频资源
                find_list = [i for i in aid_data if i['title'] == aid_data_item['title']]
                if len(find_list) < 1:
                    aid_data.append(aid_data_item)
                find_list = [i for i in title_list if i == aid_data_item['title']]
                if len(find_list) < 1:
                    title_list.append(aid_data_item['title'])
                redeal_json_item = {
                    'aid': aid_data_item['aid'],
                    'title': aid_data_item['title'],
                    'rm_header_tail_time_long': '' # (在重新处理视频时会使用到)'rm_header_tail_time_long':'00:01:01,00:01:01' 就是重新处理视频时，需要选取的视频的时间范围 '需要减去的开头时长,需要减去的结尾时长'
                }
                find_list = [i for i in redeal_json_list if i['title'] == redeal_json_item['title']]
                if len(find_list) < 1:
                    redeal_json_list.append(redeal_json_item)
            page_num +=1
    # 把请求到的所有视频的title都记录到文本中，便于查看
    write_request_remember_txt(title_list)
    write_redeal_config_txt(redeal_json_list)
    print(f'收集到的数据：\n{aid_data}')
    # 把收集到 aid 倒过来排序（因为请求的方式是从第1页开始请求的，得到的数据是 新到旧 的顺序排序的，但是我要的是 旧视频到最新视频 的顺序进行排序）
    aid_data = aid_data[::-1]
    print(f'收集到的数据量(倒序后)：\n{aid_data}')
    print(f'收集到的数据量：\n{len(aid_data)}')
    print(f'len(title_list) = {len(title_list)}')
    print(f'len(redeal_json_list) = {len(redeal_json_list)}')

    return aid_data

def collect_need_aid_data():
    aid_data = collect_aid_data()
    # 从 video_exclude.tx 中进行排除不需要下载的数据
    need_data = [d for d in aid_data if not is_in_exclude_txt(d['title'])]
    print(f'经过排除处理后的 aid_data: \n{need_data}')
    return need_data

def main_func():
    return collect_need_aid_data()
