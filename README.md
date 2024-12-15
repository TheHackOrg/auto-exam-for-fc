## Intro
a autoExam program for [iedu.foxconn.com](https://iedu.foxconn.com/) in Python3.12.3
> This is my first project in Python, so maybe the codes look like a little bad...


## Flowchart
[PDF file link, Read it online](https://gitee.com/hackorg/fc_auto-exam/raw/master/flowchart/%E5%AF%8C%E5%AD%A6%E5%AE%9D%E5%85%B8%E8%87%AA%E5%8A%A8%E5%88%B7%E9%A2%98%E7%A8%8B%E5%BA%8F%E6%B5%81%E7%A8%8B%E5%9B%BE.pdf)

![Flowchart picture](flowchart/%E5%AF%8C%E5%AD%A6%E5%AE%9D%E5%85%B8%E8%87%AA%E5%8A%A8%E5%88%B7%E9%A2%98%E7%A8%8B%E5%BA%8F%E6%B5%81%E7%A8%8B%E5%9B%BE.png)


## How to use it
1. Install the project dependency.
```shell
pip3 install -r requirements.txt
```

2. Run it, then you will get a verfiyCode.jpg in your current path.
```shell
python3 fc_autoExam.py
```

3. Input your userName, password and verifyCode info into the console.
```shell
Please Input Your Username: 'your-username'
Please Input Your Password: 'your-password'
Please Input Your Verify Code: 'your-verifyCode'
```

Congratulations! take a break bro, just cost one coffee time, it's will help you get a perfect score of 100 points in every exam paper you can do. by the way, please copy the ouput infos from console into a log file([such as fc_autoExam_logs.log](Logs/fc_autoExam_logs.log)) which suffix is `log`, if you want to see neat log infos or check bugs.