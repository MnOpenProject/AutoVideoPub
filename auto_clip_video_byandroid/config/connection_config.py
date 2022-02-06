# appium服务监听地址
config_server = "http://localhost:4723/wd/hub"

# ffmpeg 的 release 包的bin目录
ffmpeg_bin_dir = 'C:/ffmpeg-5.0-essentials_build/bin'

# 通用配置：可以用于市场上的大多数机型（可以不用写 "deviceName" 这个属性）
# 必剪 app 参数
config_desired_caps_bijian_app = {
    "platformName": "Android",
    "appPackage": "com.bilibili.studio",
    "appActivity": "com.bcut.homepage.widget.SplashActivity",
    "noReset": "true",
    "newCommandTimeout": 6000,
    "automationName": "UiAutomator2"
}
