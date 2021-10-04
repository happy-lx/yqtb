from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import smtplib
from email.utils import formataddr
from email.mime.text import MIMEText
import os

debug = False

class Browser:

    def __init__(self,userid,userpassword,driver_path,log_file_path):
        chrome_options = Options()
        chrome_options.add_argument('window-size=1920x3000')  # 指定浏览器分辨率
        chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
        chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
        chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
        chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
        self.browser = webdriver.Chrome(executable_path=driver_path,options=chrome_options)
        self.userid = userid
        self.userpassword = userpassword
        self.driver_path = driver_path
        self.log_file_path = log_file_path

    def access(self,url):
        self.browser.get(url)
        if(debug) : print("访问页面%s",url)


    def click_by_id(self,id):
        self.browser.find_element_by_id(id).click()
        if (debug): print("点击id为%s 的element", id)

    def click_by_name(self,name):
        self.browser.find_element_by_name(name).click()
        if (debug): print("点击name为%s 的element", name)

    def click_by_css(self,css):
        self.browser.find_element_by_css_selector(css).click()
        if (debug): print("点击css selector为%s 的element", css)

    def write_by_id(self,id,content):
        self.browser.find_element_by_id(id).send_keys(content)
        if (debug): print("给id为%s 的element写入%s ", id,content)

    def write_by_name(self,name,content):
        self.browser.find_element_by_name(name).send_keys(content)
        if (debug): print("给name为%s 的element写入%s ", name, content)

    def write_by_css(self,css,content):
        self.browser.find_element_by_css_selector(css).send_keys(content)
        if (debug): print("给css selector为%s 的element写入%s ", css, content)

    def quit(self):
        self.browser.quit()
        print("用户",self.userid,"填报成功，系统时间：",time.strftime("%Y-%m-%d-%H-%M", time.localtime(time.time())))
        with open(log_file_path,"a+") as file:
            file.write("用户"+self.userid+"填报成功，系统时间："+time.strftime("%Y-%m-%d-%H-%M", time.localtime(time.time()))+"\n")

    def upload(self):
        self.access("http://yqtb.nwpu.edu.cn")

        self.write_by_id("username", self.userid)
        self.write_by_id("password", self.userpassword)

        self.click_by_name("submit")
        self.browser.implicitly_wait(10)
        self.click_by_css("body > div > div.linklist > ul > li:nth-child(1) > a > i")
        self.click_by_css("#rbxx_div > div.weui-btn-area > div > a")
        self.click_by_css(
            "#qrxx_div > div.weui-cells.weui-cells_form > div.weui-cells.weui-cells_checkbox > label > div.weui-cell__hd > i")
        self.click_by_id("save_div")
        self.quit()

def send_email(sender, mail_passwd, receiver, subject, msg, smtp_port, smtp_server):
    """
    邮件通知打卡结果
    """
    try:
        body = MIMEText(str(msg), 'plain', 'utf-8')
        body['From'] = formataddr(["notifier", sender])
        body['To'] = formataddr(["me", receiver])
        body['Subject'] = "NWPU疫情填报助手通知-" + subject

        if smtp_server == "" or smtp_port == "":
            smtp_port = 465
            smtp_server = "smtp.qq.com"
        smtp = smtplib.SMTP_SSL(smtp_server, smtp_port)
        smtp.login(sender, mail_passwd)
        smtp.sendmail(sender, receiver, body.as_string())
        smtp.quit()
        print("邮件发送成功")
    except Exception as ex:
        print("邮件发送失败")
        if debug:
            print(ex)



if __name__ == "__main__":
    user = "xxxxxxxxxx"
    passwd = "xxxxxxxxxx"
    drive_path = "/usr/bin/chromedriver"
    log_file_path = "./auto_upload.log"
    smtp_server = ""
    smtp_port = ""
    sender_email = "xxxxxxxxxx"
    sender_email_passwd = "xxxxxxxxxx"
    receiver_email = "xxxxxxxxxx"

    os.environ["webdriver.chrome.driver"] = drive_path

    if os.environ.get('GITHUB_RUN_ID', None):
        user = os.environ.get('USER_NAME', '')  # 账号
        passwd = os.environ.get('PASSWD', '')  # 密码

        smtp_port = os.environ.get('SMTP_PORT', '465')  # 邮件服务器端口，默认为qq smtp服务器端口
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.qq.com')  # 邮件服务器，默认为qq smtp服务器
        sender_email = os.environ.get('SENDER_EMAIL', '')  # 发送通知打卡通知邮件的邮箱
        sender_email_passwd = os.environ.get('SENDER_EMAIL_PASSWD', "")  # 发送通知打卡通知邮件的邮箱密码
        receiver_email = os.environ.get('RECEIVER_EMAIL', '')  # 接收打卡通知邮件的邮箱


    try:
        mybrowser = Browser(user, passwd, drive_path,log_file_path)
        mybrowser.upload()
        send_email(sender_email,sender_email_passwd,receiver_email,"robot","疫情填报成功",smtp_port,smtp_server)

    except Exception as ex:
        print("填报失败，请手动检查，系统时间： ",time.strftime("%Y-%m-%d-%H-%M",time.localtime(time.time())),ex)
        send_email(sender_email, sender_email_passwd, receiver_email, "robot", "疫情填报失败，请手动检查", smtp_port, smtp_server)
        with open(log_file_path, "a+") as file:
            file.write("填报失败，请手动检查 系统时间："+time.strftime("%Y-%m-%d-%H-%M",time.localtime(time.time()))+"\n")





