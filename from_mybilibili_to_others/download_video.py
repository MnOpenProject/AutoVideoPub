''' 参考资料：https://www.bilibili.com/read/cv9646821/ '''
import os,requests,progressbar
from .collect_aid_data import main_func as collect_need_aid_data
from .common_config import ffmpeg_bin_dir,download_file_dir,covert_file_dir,video_download_exclude_txt,video_upload_menu_xiaohongshu_txt_name
from .common_util import is_int_str,input_selection,is_in_exclude_txt,get_video_name_by_title,create_upload_video_menu

class Bilibili_Video_Getter:
    def open_url(self, url):
        headers = {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36',
          'Referer': 'https://www.bilibili.com/'
          }
        res = requests.request(method='GET', url=url, headers=headers)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        return res
    
    # ffmpeg 下载完成后，解压到某个目录下，这里配置好 ffmpeg 的 bin 目录
    # ffmpeg release 包官网下载地址(找到 release builds 下载 ffmpeg-release-essentials.zip 文件)：https://www.gyan.dev/ffmpeg/builds/
    ffmpeg_bin_dir = ffmpeg_bin_dir
    filelist_name = 'filelist.txt'
    def write_filelist_into_txt(self, filelist_path,video_file_list):
        if os.path.exists(filelist_path):
            os.remove(filelist_path)
        str_content = ''
        ts_end_idx = len(video_file_list) - 1    
        f_path = filelist_path
        for file_idx,file_path in enumerate(video_file_list):
            rn_str = ''
            if file_idx < ts_end_idx:
                rn_str = '\n'
            # 写入文本
            str_content = "file '{0}'".format(file_path)
            str_content = str_content.replace('/','\\')
            str_content = f'{str_content}{rn_str}'
            fp = open(f_path,"a",encoding="utf-8")
            fp.write('{0}'.format(str_content))
            fp.close()

    # ffmpeg 官网：http://ffmpeg.org/download.html#build-windows
    # 【注意】：使用该方案的前提是：windows 环境中已经安装好了 ffmpeg 环境，安装参考：http://www.360doc.com/content/21/0204/15/54508727_960674843.shtml
    # ffmpeg 合并文件方案参考（这里选用的就是参考地址里的 <方案三>）：https://www.cnblogs.com/duanxiaojun/articles/6904878.html
    # FFmpeg concat 分离器 合并文件方案
    # 这种方法成功率很高，也是最好的，但是需要 FFmpeg 1.1 以上版本。先创建一个文本文件filelist.txt
    def combine_video_by_ffmpeg(self, video_file_dir, video_file_list, save_file_path):
        save_file_path = save_file_path.replace('\\','/')
        # 若输出的文件已存在，则删除（为了做到直接覆盖原文件功能，不删除的话，ffmpeg发现已存在相同的文件会在终端询问是否覆盖）
        if os.path.exists(save_file_path):
            os.remove(save_file_path)
        # drive 参数是设定的输出的磁盘
        drive_name = save_file_path[0] # 输出的盘符就是当前工程所在的盘符

        print('准备合并的文件列表----------------------------')
        # 把要合并的所有 .ts 文件都预先排列好的写入到一个 txt 文件中
        print('把要合并的所有视频文件依次排列好的写入到一个 txt 文件中----------------------------')
        filelist_path = f'{video_file_dir}/{self.filelist_name}'
        self.write_filelist_into_txt(filelist_path,video_file_list)
        # 然后通过 ffmpeg 指令合并文件
        tsvideoDirCmdStr = f'{drive_name}: && cd {video_file_dir}'
        cmdStr = f'{tsvideoDirCmdStr} && {self.ffmpeg_bin_dir}/ffmpeg -f concat -safe 0 -i {filelist_path} -c copy {save_file_path}'
        print("CMD合成指令：{}".format(cmdStr))
        os.system(cmdStr)
        print("{}视频合成完成".format(save_file_path))
        
        # 移除合并文件时，临时使用的 filelist.txt 文件
        os.remove(filelist_path)

    def BV_to_AV(self, bv):
        # 把 bvid 处理成 avid
        if bv.isdigit():
            return bv
        bv = list(bv[2:])
        keys = {'1': 13, '2': 12, '3': 46, '4': 31, '5': 43, '6': 18, '7': 40, '8': 28, '9': 5,
                'A': 54, 'B': 20, 'C': 15, 'D': 8, 'E': 39, 'F': 57, 'G': 45, 'H': 36, 'J': 38, 'K': 51, 'L': 42, 'M': 49, 'N': 52, 'P': 53, 'Q': 7, 'R': 4, 'S': 9, 'T': 50, 'U': 10, 'V': 44, 'W': 34, 'X': 6, 'Y': 25, 'Z': 1,
                'a': 26, 'b': 29, 'c': 56, 'd': 3, 'e': 24, 'f': 0, 'g': 47, 'h': 27, 'i': 22, 'j': 41, 'k': 16, 'm': 11, 'n': 37, 'o': 2, 'p': 35, 'q': 21, 'r': 17, 's': 33, 't': 30, 'u': 48, 'v': 23, 'w': 55, 'x': 32, 'y': 14, 'z': 19}
        for i in range(len(bv)):
            bv[i] = keys[bv[i]]
        bv[0] *= (58 ** 6)
        bv[1] *= (58 ** 2)
        bv[2] *= (58 ** 4)
        bv[3] *= (58 ** 8)
        bv[4] *= (58 ** 5)
        bv[5] *= (58 ** 9)
        bv[6] *= (58 ** 3)
        bv[7] *= (58 ** 7)
        bv[8] *= 58
        return str((sum(bv) - 100618342136696320) ^ 177451812)

    def get_video_info(self, aid, cid):
        url = f"https://api.bilibili.com/x/web-interface/view?aid={aid}&cid={cid}"
        res = self.open_url(url).json()
        # 没想好这部分怎么用
        if res['message'] == '0':
            res = res['data']
            info = {}
            info['title'] = res['title']
            info['intro'] = res['desc']
            info['author'] = res['owner']['name']
            info['stat'] = res['stat']
            return info
        return False

    def get_cid(self, aid):
        res = self.open_url(f"https://api.bilibili.com/x/player/pagelist?aid={aid}&jsonp=jsonp").json()
        if res['message'] == '0':
            cid = res["data"][0]["cid"]
            return cid
        return False
    
    # 下载文件（显示进度值）
    def download_with_process(self, url, dst, headers, aid):
        # verify=False 可解决此类问题：(Caused by SSLError(SSLError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:833)'),)
        # r = requests.request(method='GET',url=url,stream=True,verify=False)
        r = requests.request(method='GET',url=url,stream=True,headers=headers)
        # 有的服务端header里并没有提供 'Content-Length'，则设置一个超大的值即可，让下面的进度条一直往前走就好了
        content_length = r.headers.get('Content-Length')
        total_length = 9999999999999 if content_length == None else int(content_length)
        process_val = 0
        with open(dst, 'ab') as f:
            # progressbar 输出的时候会按照 widgets 数组内容进行输出，下面有空格符，就是为了每个输出内容都有间隔
            # 注：不要把空格改成换行，否则会发现 progressbar 的打印进度内容每次在换新行打印，而我们要的效果时只在当前行更新进度值
            widgets = []
            # 若服务端能提供 'Content-Length' 则显示详细的进度提示
            if not content_length == None:
                widgets = [
                    f'aid={aid}; Progress: ', progressbar.Percentage(),
                    # ' ',
                    # progressbar.Bar(marker='>', left='[', right=']'),
                    ' ',
                    progressbar.ETA(),
                    ' ',
                    progressbar.Timer(),
                    ' ',
                    progressbar.FileTransferSpeed()
                ]
            else:
                # 若服务端能未能提供 'Content-Length' 则只能显示模式的下载进度（即进度条只会一直往前）
                widgets = [
                    'Progress: ', '正在下载'
                    ' ',
                    progressbar.Bar(marker='>', left='', right=''),
                    ' ',
                    progressbar.FileTransferSpeed()
                ]
            pbar = progressbar.ProgressBar(widgets=widgets, maxval=total_length).start()
            speed = 1000 # 可控制下载速度上限（并非越大就真的越快，还是要取决于真实的网络情况）
            for chunk in r.iter_content(chunk_size=speed):
                # chunk 为 0 时，说明文件已下载完毕
                if chunk:
                    f.write(chunk)
                    # 刷新缓冲区
                    f.flush()
                process_val += len(chunk) + speed
                process_val = total_length - 1 if process_val >= (total_length - 1) else process_val
                # print('进度：{}'.format(process_val))
                # # 清除终端缓冲区，让打印用于在当前行更新内容
                # sys.stdout.flush()
                # 刷新进度条的进度值
                pbar.update(process_val)
            pbar.finish()

            print(" 第{}文件 --- 保存成功".format(dst))
        print(" 第{}文件 --- 下载结束".format(dst))

    def download_video(self, aid, cid, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
        res = self.open_url(f"https://api.bilibili.com/x/player/playurl?avid={aid}&cid={cid}&qn=64").json()
        url = res["data"]["durl"][0]["url"]
        print(f"aid={aid}; 准备下载{file_path}...")
        headers = {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36',
          'Referer': 'https://www.bilibili.com/'
          }
        self.download_with_process(url,file_path,headers,aid)
    
    def main(self, aid_,download_file_dir,covert_file_dir,is_convert2mp4=True):        
        bv = ''
        if aid_ == None:
            bv = input(f"aid={aid}; 请输入视频BV或AV号：")
        else:
            bv = aid_
        aid = self.BV_to_AV(bv)
        print(f'aid={aid}; 程序热身中，请稍等...')
        cid = self.get_cid(aid)
        if not cid:
            print(f"aid={aid}; 您输入的BV或AV号有误！")
            return False
        info = self.get_video_info(aid, cid)
        video_title =  get_video_name_by_title(info["title"]) # 把空格转为下划线，因为在转MP4方法中文件名不允许出现空格符
        # 判断当前视频是否需在排除项里，不排除的才进行下载
        if not is_in_exclude_txt(video_title):
            file_name = video_title
            source_file_path = f'{download_file_dir}/{file_name}.flv'
            self.download_video(aid, cid, source_file_path)
            if is_convert2mp4:
                # 把下载完成的 .flv 格式视频文件 通过 ffmpeg 转换成 .mp4 文件便可用任意播放器播放视频了
                # .flv 的视频需要特定的播放器才能解析，不适用于大多数播放器        
                video_file_list = [source_file_path]
                save_file_path = f'{covert_file_dir}/{file_name}.mp4'
                self.combine_video_by_ffmpeg(covert_file_dir, video_file_list, save_file_path)
        else:
            print(f'aid={aid}; title={video_title}; \n已在排除列表中，无需下载！')
        return True

# 实例化视频获取对象
video_getter = Bilibili_Video_Getter()

# 输出一份针对《小红书 平台》视频上传菜单（后续的上传视频操作会根据该菜单中的顺序依次上传视频）
def create_xiaohongshu_upload_video_menu():
    create_upload_video_menu(video_upload_menu_xiaohongshu_txt_name)

def download_and_convert2mp4():
    # aid 来源：打开一个视频页面链接，然后 F12 打开 Debug 窗口，
    # 在 Network 画面里的 Fetch/XHR 里仔细查找一个类似这样的请求 https://api.bilibili.com/x/player/online/total?aid=680930025&cid=493892120&bvid=BV1tS4y1L7nz&ts=54815817
    # 其中就可以看到带有 aid 了
    # 如果是番剧（多集的那种）就找 avid，这是代表当前正在播放的那一集视频，找类似这样的请求地址 https://api.bilibili.com/pgc/player/web/playurl?avid=590132584&bvid=BV1jq4y1U7wT&cid=487915225&qn=80&fnver=0&fnval=2000&fourk=1&ep_id=409867&session=46fd65ef401f06103bd76a74a3fd064c
    # aid案例 = 680930025

    # 这里填入要下载视频的 aid 值，然后在该目录下执行该脚本
    aid_list = collect_need_aid_data() # 请求<B站 我的稿件> 已通过审核的 数据列表
    for aid_item in aid_list:
        video_getter.main(str(aid_item['aid']),download_file_dir,covert_file_dir)
    
    # 输出一份针对《小红书 平台》视频上传菜单（后续的上传视频操作会根据该菜单中的顺序依次上传视频）
    create_upload_video_menu(video_upload_menu_xiaohongshu_txt_name)

def download_video():
    # 这里填入要下载视频的 aid 值，然后在该目录下执行该脚本
    aid_list = collect_need_aid_data()
    for aid_item in aid_list:
        video_getter.main(str(aid_item['aid']),download_file_dir,covert_file_dir,False)

    # 输出一份针对《小红书 平台》视频上传菜单（后续的上传视频操作会根据该菜单中的顺序依次上传视频）
    create_upload_video_menu(video_upload_menu_xiaohongshu_txt_name)

def video_flv_convert2mp4():
    flv_list =  os.listdir(download_file_dir)
    print('[*] - 选择要转为MP4的文件：')
    for idx,file_name in enumerate(flv_list):
        print(f'[{idx+1}] - {file_name}')
    selection = input_selection()

    # 把下载完成的 .flv 格式视频文件 通过 ffmpeg 转换成 .mp4 文件便可用任意播放器播放视频了
    # .flv 的视频需要特定的播放器才能解析，不适用于大多数播放器 
    selected_file = flv_list[selection-1]
    source_file_path = f'{download_file_dir}/{selected_file}'
    video_file_list = [source_file_path]
    save_file_path = f'{covert_file_dir}/{selected_file.replace(".flv",".mp4")}'
    video_getter.combine_video_by_ffmpeg(covert_file_dir, video_file_list, save_file_path)

    # 输出一份针对《小红书 平台》视频上传菜单（后续的上传视频操作会根据该菜单中的顺序依次上传视频）
    create_upload_video_menu(video_upload_menu_xiaohongshu_txt_name)
    