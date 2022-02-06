# 通过 Appiumn 访问 Android 设备的<必剪 app>自动上传视频到 Bilibili 的功能脚本

* 注：该脚本只提供给有一定编程基础的或者愿意自学编程的使用者，如果一点的都不懂的又不愿意自学的，则不做推荐
* 这里只是对操作步骤进行了关键性的说明，具体对该脚本功能的使用效果，还是要看各位使用者的能力了，毕竟我的代码实力也就一般，并不能提供完美的脚本，也许未来可以，但是目前确实仅限如此 

## 一、准备说明

* 使用者，请自行网上自学如何安装 Appium 以及如何使用 Appium（电脑上需要安装 JDK ADK 的并在 Appium 配置好），我这里已经为程序添加了通用的 Android 手机连接参数（auto_clip_video_byandroid/config/connection_config.py）一般情况下市场上的大多数手机都适用
* 用于连接的手机上请一定安装好 《必剪》app

### Appiumn 的大致参考资料
* 通过 appium 实现 Android 移动端自动化操作
参考资料：https://www.cnblogs.com/lsdb/p/10108165.html

* * 安装 appium 的一体版，即找到 1.21.0 版本
下载地址：https://github.com/appium/appium-desktop/releases/tag/v1.21.0-1

```
# 安装appium
npm install -g appium

#使用appium-doctor确认环境配置无误
npm install -g appium-doctor
# 检查 appinum
appium-doctor --android
```

手机连接appium  
启动 appium Desktop App，再通过 appium Desktop App 启动 appium-inspector Desk App  

cmd 上执行下面指令，查询当前连接的 Android 设备信息
```
adb devices -l
```
比如 cmd 中会查出这样的信息
```
8cba128f               device product:A33m model:OPPO_A33m device:A33m transport_id:13
```
上面的 devices 信息中的 device:A33m 就是下面要用到的 deviceName 参数的值


然后在 appium-inspector Desk App 中的 JSON Representation 位置填入以下信息
```
{
  "platformName": "Android",
  "deviceName": "HWEVA",
  "appPackage": "com.tencent.mm",
  "appActivity": ".ui.LauncherUI"
}
```
上面的参数说明如下
```
platformName---设备平台。填Android或IOS
deviceName----设备名。按上边adb查出的设备名填写即可
appPackage----要启动的app的包名。微信是"com.tencent.mm"
appActivity----要启动的界面。微信启动界面是".ui.LauncherUI"
```

 【*】以上必要参数的获取方式如下
 Android 设备连接电脑后，在 Android 设备中只启动想要操作的 app
 然后在电脑的 cmd 里输入以下指令，查询出 Android 设备中当前正在运行的 app 信息，其中就包含 app 的包名称（即上面的 appPackage 的参数值）
 ```
 adb shell dumpsys activity | findstr "intent={"
 ```
 例如这个 番茄小说 app 的信息如下（其中 cmp=对应的内容表示 【 app包名/第一展示的刷新活动页，即 appPackage参数值/appActivity参数值 】）
 ```
 intent={act=android.intent.action.MAIN cat=[android.intent.category.LAUNCHER] flg=0x10200000 cmp=com.dragon.read/.pages.splash.SplashActivity}
 ```


填写好参数后，点击 appium-inspector Desk App 中的 Start Session


## 二、具体操作步骤
### 1、为你要上传的视频进行命名（想一个英文名）

* 视频名称分两级，跟美剧一样的规则，比如：一部美剧叫硅谷，分N季，那么两级英文名为：silliconvalley 和 silliconvalley1
* 第二级的英文名必须与第一级的英文完全一致（包括大小写都必须保持一致），第二级英文名只是后面加个数字，表示第N季

* 接下来的说明，都将以《美剧：硅谷》silliconvalley 和 silliconvalley1 为例进行说明

### 2、配置脚本准备

* 1 - 在 auto_clip_video_byandroid/config/upload_config_files/ 目录下添加对应的"上传参数配置脚本"（只要复制提供的 silliconvalley1.py 案例脚本，然后更改文件名为你视频的英文名和其中内容即可 [比如你的视频叫 abc 的 第一季，那么命名为 abc1.py]）
* * 层配置的脚本只需要根据视频"季"进行脚本即可，即对应"硅谷第一季"的视频，就添加一个 silliconvalley1.py 即可，如果需要上传第二季，则添加 silliconvalley2.py
* 2 - 在 auto_clip_video_byandroid/video_action/ 目录下添加对应的"视频剪辑功能脚本"（只要复制提供的 silliconvalley/silliconvalley1.py 案例脚本，然后更改文件夹和文件名即可）
* * 该目录下提供的案例脚本并未带有视频剪辑操作，我提供该脚本空壳是为了提示给使用者可以自行发挥，对自己的视频写入特定的自动剪辑脚本

### 3、启动脚本
#### 3.1、启动脚本 -- 第一步

* 此时，你要上传的视频还没在工程里建立好对应的文件夹（或者说，你的视频还没有挪到该工程中的规定目录里，当然你此时还一脸懵逼，还不知道该把视频放到哪里）

* 请在项目的根目录下，开启终端，并执行 go_main_spider.py 脚本，然后根据终端提示进行选择
```
py go_main_spider.py
```
* * 此时当看到下面这样的选项时，请先选择第 3 个选项（让程序先根据你在 auto_clip_video_byandroid/config/upload_config_files/ 配置的参数脚本生成用于放置视频的文件夹）
```
----- 请选择操作类型（默认选项：[1]）： -----

[1] - 执行剪辑视频和发布视频的完整操作
[2] - 仅执行该视频节目的发布操作（即仅在发布页面填写表单）
[3] - 创建用于存放视频文件的目录（如果要上传发布的视频文件还没有放到该项目的指定目录下，则请先执行该操作）
```
* * 接着会让你选择要创建哪些文件夹（就是参数里对该视频分了多少集，一集分多少段），当然这是为了满足更多需求才这么订的，如果你的视频就一集一段，那么 auto_clip_video_byandroid/config/upload_config_files/ 里的对应参数都是只配置成1或01就行了（具体情况提供的案例脚本，里面写满了注释，自行查看自行理解）

#### 3.2、启动脚本 -- 第二步

* 此时在 auto_clip_video_byandroid/ 会存在一个 video/xxx/xxx/fulfiles/xxx1_01_01/ 类似这样的多层目录，把你要上传的视频复制到这里对应的文件夹下

* 启动PC端的 Appium

* 请在项目的根目录下，开启终端，并执行 go_main_spider.py 脚本，然后根据终端提示进行选择
```
py go_main_spider.py
```
* * 此时当看到下面这样的选项时，请先选择第 1 个选项（让程序自动访问 Appium 并开始执行自动脚本）
```
----- 请选择操作类型（默认选项：[1]）： -----

[1] - 执行剪辑视频和发布视频的完整操作
[2] - 仅执行该视频节目的发布操作（即仅在发布页面填写表单）
[3] - 创建用于存放视频文件的目录（如果要上传发布的视频文件还没有放到该项目的指定目录下，则请先执行该操作）
```

### 4、视频发布成功

* 当一个视频发布成功之后，会在 auto_clip_video_byandroid/upload_rember/ 目录下生成对应的记录，如果看到有的记录后缀为 _error 说明这个文件在发布之前脚本报错了，要么把这条记录删除（删除记录时，不要在记录之间留空白行），然后查看原因，再重新上传视频即可，总之这个记录脚本可以自行根据特殊情况进行编辑即可，凡是已存在记录的视频奖不宰重复发布

### 5、某段视频发布失败的补救操作

* 由于 Appiumn 并非完全稳定 和 当前项目脚本并不能完全保证稳定的情况下，势必会出现一些报错之类的意外问题，导致某段视频并没有发布成功，需要手动发布，但是我们又并不想一个字一个字的在手机上重复编辑发布内容，此时只需要在下面这个选项中选择第 2 个选项即可

如下操作：
* 在项目的根目录下，开启终端，并执行 go_main_spider.py 脚本，然后根据终端提示进行选择
```
py go_main_spider.py
```
* * 当看到下面这样的选项时，请先选择第 2 个选项（让程序自动访问 Appium 并开始执行自动脚本）
```
----- 请选择操作类型（默认选项：[1]）： -----

[1] - 执行剪辑视频和发布视频的完整操作
[2] - 仅执行该视频节目的发布操作（即仅在发布页面填写表单）
[3] - 创建用于存放视频文件的目录（如果要上传发布的视频文件还没有放到该项目的指定目录下，则请先执行该操作）
```
* * 当选择了第 2 个选项后，待程序通过Appiumn启动到《必剪》app后，并终端提示选择要填写的参数时，此时不要在终端输入选择项，一定要现在《必剪》app里手动点击进入对应视频的发布画面，再在PC的终端里输入对应的选择项编号，此时程序才能在发布画面里自动为你填写对应的发布信息