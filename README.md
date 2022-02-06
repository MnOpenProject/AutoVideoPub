# 自动剪辑视频，自动发布视频

## 前言
    * 最初时自己想难得做点简单的视频发布到B站上，后来接触python就有了想做点自动脚本，随着对脚本功能的执着，想法越来越多，代码越迭代越趋于丰富，现在虽然还没有开发出友好的交互界面，但在我的私人项目的实际使用中还算好用，于是打算把核心功能的主要部分分离成一个独立的开源项目，并分享出来，有需要的Uper朋友可以拿去使用，希望能够适当减轻一点压力，我也做视频，知道做视频很艰难很辛苦
    * 上面说的目前项目因为还没有开发友好的交互界面，所以目前项目适合懂点代码或者愿意自学代码的朋友来使用，后期我会继续维护，也会慢慢设计并开发出友好的交互界面，争取能让更多Uper朋友使用
    * 当然，项目开源出来也非常希望能有高手协助开发，让该项目更好用，单靠我的实力实在难以开发出多好的东西（特别是目前环境准备很麻烦，对于很多人来说很是劝退）

## 功能说明
    * 视频文件分解：使用者把PC上出来好的视频文件(如 .mp4)放到该项目的特定目录下，配置文件里设置好参数后，就可以把视频分解成 N 个 .ts 文件
    * 视频分段剪辑：[视频文件分解]后，根据设置好的参数，就可以把视频自动剪辑成 N 段
    * 视频自动上传：只要该项目的特定目录下有视频文件(如 .mp4)，PC电脑USB连接上手机（处理好的视频放到收集存储里），就能自动通过<必剪 app>上传视频到B站，如此，我们PC端剪辑的视频要想参与<必剪 app>上传视频的活动(得到<必剪 app>的活动收益)也就比较方便了(不需要手动编辑视频和编辑参数了)

    * 【注】：凡是有自己的特殊需求的，比如想对自己视频在<必剪 app>上实现特定的自动化剪辑操作，我也提供了扩展，只需要自己写入代码即可
    * 再次声明：目前项目刚刚起步，虽然我用起来感觉还行，但确实还是比较繁琐，实际使用中还需使用者自行研究，这是我的第一份开源项目，请多包涵

## 环境准备
    * nodejs 环境配置 -- 基础开发环境
    * python 环境配置 -- 基础开发环境，我使用的 python 版本：3.10.0
    * java 环境配置（jre 和 jdk） -- 基础开发环境
    * Android SDK 环境配置 -- 基础开发环境
    * * 下载 Android Studio，通过 Android Studio 下载各个版本的 Android SDK
    * ffmpeg 环境配置 -- 用于视频分解和合并
    * * ffmpeg release 包官网下载地址(找到 release builds 下载 ffmpeg-release-essentials.zip 文件)：https://www.gyan.dev/ffmpeg/builds/
    * * ffmpeg release 包下载教学参考：https://blog.csdn.net/u011027547/article/details/122490254
    * * 下载完成 ffmpeg release包后，一定要在 \auto_clip_video_byandroid\config\connection_config.py 设置好 ffmpeg_bin_dir 参数值(ffmpeg release包的bin目录)
    * appium 环境配置 -- 用于实现移动设备的自动化操作
    * * 安装 appium 的一体版，即找到 1.21.0 版本 Appium-windows-1.21.0-1.exe：https://github.com/appium/appium-desktop/releases/tag/v1.21.0-1
    * * 安装 appium 后，在 appiumn 界面上配置好 JDK 和 Android SDK 所在目录

## 使用说明
    * (1) - 安装需要的第三方工具包：
    ```cmd
    # 工程根目录下执行安装脚本
    py install-script.py
    ```

    * (2) - \auto_clip_video_byandroid\config\upload_config_files\ 目录下先添加视频的配置参数脚本，按照美剧的方式命名，即 剧名+分季的数字，比如 《屌丝男士 第一季》 的配置脚本就命名为 dsns1.py，其中 dsns 是"屌丝男士"的简写字母，数字1表示"第一季"，推荐复制已给的脚本，然后改文件名，再根据自己的视频需求，改其中的参数，其中参数说明脚本里都已写好，自己看即可

    * (3) - \auto_clip_video_byandroid\video_action\ 目录下添加视频的 appiumn 自动化剪辑脚本，创建规则就按照目前已给的案例 -- 剧名/剧名+分季的数字；一般没有自己的特殊需求，只要复制已给的案例脚本，改一下文件名即可

    * (4) - 启动脚本
    ```cmd
    # 工程根目录下执行功能脚本，然后根据提示执行相应的功能
    py go_main_spider.py
    ```

    * (5) - 视频文件放置位置 和 自动分解和分段剪辑：
    * * 该操作必须确保已经配置好了视频的参数脚本（即 第(2)步操作）
    * * 在终端的第二段询问中，选择[5]选项，即可得到类似这样的目录 \downloadvideo\dsns\dsns1\fullvideo
    ```cmd
    [5] - 创建用于存放*完整*视频文件的目录（如果要上传发布的视频文件还没有放到该项目的指定目录下，则请先执行该操作）
    ```
    * * 把要进行分段剪辑视频放到这个 fullvideo 目录下，然后重新执行 py go_main_spider.py 
    * * 在终端的第二段询问中，选择[4]选项，即可得到类似这样的目录 \downloadvideo\dsns\dsns1\tsfiles\dsns1_01，即得到了视频文件被分解后的切片文件(.ts文件)
    ```cmd
    [4] - 视频分解（比如将 .mp4 视频文件分解成 .ts 切片文件，输出目录在 downloadvideo/ 目录下）
    ```
    * * 然后再重新执行 py go_main_spider.py 
    * * 再在第二段询问中，选择[1]选项，在随后的询问中，选择要分段剪辑的视频配置脚本，等待自动完成后，就会发现 \auto_clip_video_byandroid\ 目录下多了一个 video\ 目录，其中就有刚才分段剪辑好的视频文件
    ```cmd
    [1] - 视频分段剪辑
    ```

    * (6) - 自动通过 appiumn 自动操作<必剪 app>上传视频到B站
    * * 首先PC端通过USB连接上Android手机，并打开Android手机的开发者模式，且允许调试
    * * 手机存储的根目录下新建一个文件夹命名为：autopy_for_bijian(即 这里\auto_clip_video_byandroid\config\upload_config_files 中配置脚本里的 mobile_storage_folder 变量值)，把 \auto_clip_video_byandroid\video\ 文件夹复制到这个 autopy_for_bijian 目录下【注：每次只复制本次需要的视频，目录结构一定与\auto_clip_video_byandroid\video\ 的保持一致，自动化脚本会根据这个结构进行查找手机存储里的视频文件，而且目前脚本功能不够强大，如果视频文件太多，会遇到找不到的情况】
    * * 启动 appiumn 客户端
    * * 执行 py go_main_spider.py 在终端的第二段询问中，选择[3]选项
    ```cmd
    [3] - 自动通过<必剪 app>上传分段视频
    ```
    * * 最后等待自动上传视频操作即可（初次使用时，appiumn会在手机上安装 appiumn 的 app）
    ***（备注：在上传过程中，凡是通过脚本完成自动发布到B站的，都会在\auto_clip_video_byandroid\upload_rember\ 目录下存有记录，自动发布过程中凡是遇到异常问题的也会存有记录，只是记录带有 _error 后缀）***

    * (7) - 如果视频文件不需要分段，想直接使用自动上传功能
    * * 那么执行 py go_main_spider.py 后，第二段询问中，选择[6]选项，会根据配置参数脚本，在 \auto_clip_video_byandroid\ 目录下自动生成一个 video\dsns\dsns1\fullfiles\dsns1_01_01 类似这样的空文件夹，只需要把要上传的视频放到这样的文件夹下
    ```cmd
    [6] - 创建用于存放*分段*视频文件的目录（如果要上传发布的视频文件还没有放到该项目的指定目录下，则请先执行该操作）
    ```
    * * 让后再安装这个 video\dsns\dsns1\fullfiles\dsns1_01_01 目录结构，把视频也存放到手机存储的 autopy_for_bijian\ 目录下（即 第(6)步操作）
    * * 接下来就是继续安装 第(6)步操作继续下去即可

    *【特别说明】：更多功能，请自行研究，兴许实力强大的你会有更多好用的功能去实现

## 使用说明 -- 视频教程
    * 后续补上

## 附加说明
    * auto_clip_video_byandroid\logs\ 目录说明：在使用过程中终端打印的内容会也会在该目录下生成相应的 .log 日志文件，为了方便调试，如果不想输出，则修改 \auto_clip_video_byandroid\config\connection_config.py 中的 out_log_file 变量为 False 即可