import requests
from bs4 import BeautifulSoup
import re
import copy
import time

# POST 请求的头部, 数据摘自浏览器, 目的是模拟浏览器, 防止暴露真实身份(一个可爱滴小蛛蛛～)
post_headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Content-Length': '57',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://iedu.foxconn.com',
    'Referer': 'https://iedu.foxconn.com/',
    'Sec-Ch-Ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': "macOS",
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}


# 创建一个 Session 会话对象
session = requests.Session()


# 游客(即访客)的 device 数据, 摘自登陆页面. 然后执行游客登录 POST 请求:
# 解释: 之所以这样做, 是因为在未登陆情况下, 当用浏览器访问 iedu.foxconn.com 后, 前端会自动向服务器发送一个下述请求(即游客登陆请求),
# 随后服务器会返回一个 cookies, 后面"真正用户"向服务器发送 POST 登陆请求时, 需要用到此 cookies, 例如需要用到 cookies 中的 JSESSIONID(session) 来与服务器建立会话.
login_user_post_data = 'result={"device":"WEB","deviceid":"W303763230fcd4d0786810dfc76219740"}'
login_user = session.post(url='https://iedu.foxconn.com/myservlet5/LoginUser', data=login_user_post_data, headers=post_headers)


# 打印游客登陆后, 服务器返回的数据信息
print('\n-------------------------------------------------------------------------------------------------')
print(f'*Visitor* Login Form Info: {login_user_post_data}')
print(f'*Visitor* Login Response Status Code: {login_user.text}')
# 检查游客登录是否成功
if login_user.status_code == 200:
    print("*Visitor* Login In Successfully")
    # 使用 "同一会话, 即同一Session" 对象发起访问主页的 GET 请求, 目的是获取游客登陆后, 服务器所返回的 cookies  
    dashboard_url = 'https://iedu.foxconn.com/'
    response = session.get(dashboard_url)
    print(f'Cookies Response Status Code: {response.status_code}')
    # 将 cookies 转换为字典
    login_cookies_dict = session.cookies.get_dict()
    # 补充一个 POST Payload
    login_cookies_dict['zh_choose'] = 'n'
    # 打印 cookies
    print('Cookies Be Shown As Belows: ')
    for key, value in login_cookies_dict.items():
        print(f'\t{key} : {value}')
        # JSESSIONID : E97C96CC957AEB0E263AAF5416838807
        # deviceid : Wba8a1030612b433d9f6044516a5a227d
        # fxbdLocal : en
        # zh_choose : n
    print('-------------------------------------------------------------------------------------------------')
else:
    print("Login failed:", login_user.status_code)


# 模拟浏览器获取登陆验证码
# 使用浏览器点击登陆按钮(会弹出待填写信息的登陆表单), 此时前端会向服务器发送 GET 请求获取验证码,
# 注意1: 第一次提交登陆表单前需先向服务器发送 GET 请求获取验证码, 然后才能提交登陆表单!
# 注意2: 服务器端返回的验证码信息, 与上一步为获取验证码, 而发送的 GET 请求中头部携带 cookies 是相互绑定关系,
#       具体来说, 我觉得应该是验证码与 cookies 中的 JSESSIONID(session) 是相互绑定关系,
#       而真正用户提交登陆表单后, 服务器端验证验证码是否正确的同时, 也会验证客户端 "传过来的验证码" 与 "传过来的 cookies" 是否为相互绑定的关系!!!
#       所以不要通过打开浏览器的方式来获取验证码, 因为只要打开浏览器访问 iedu.foxconn.com, 服务器端每次就会返回不同的 cookies, 
#       例如返回的 cookies 中的 JSESSIONID(session) 每次都不同.
get_verify_code_url2 = 'https://iedu.foxconn.com/action/login/verifyCode?888'
verify_code_response = session.get(url=get_verify_code_url2, cookies=login_cookies_dict)
print(f'\nVerifyCode Response Status Code: \x1b[31m{verify_code_response.status_code}\x1b[0m\n')
if verify_code_response.status_code == 200:
    with open('VerifyCode.jpg', 'wb') as file:
        file.write(verify_code_response.content)
        print('Got VerifyCode.jpg Successfully')
else:
    print('file filure')


# 真正用户(非游客)登陆表单
login_form_jsonObj = {
    'preUrl': '', # 为空
    'userName':'',
    'password':'',
    'verifyCode': '',
}


# 手动输入用户名, 密码以及获取的验证码信息
username_str = input('\nPlease Input Your Username: ')
login_form_jsonObj['userName'] = username_str
password_str = input('\nPlease Input Your Password: ')
login_form_jsonObj['password'] = password_str
verify_code_str = input('\nPlease Input Your Verify Code: ')
login_form_jsonObj['verifyCode'] = verify_code_str


print('-----------------------------------------------------------------------------------------------------------')
print(f'\n*User* Login Form Info: {login_form_jsonObj}')


# 提交真正用户(非游客)登录表单的 API
headerPath = 'https://iedu.foxconn.com/'
submint_login_post_url = headerPath + '/action/login/login'


# 提交真正用户(非游客)登录表单
# 注意: 这里并不需要传入 cookies=login_cookies_dict,
# 因为由于会话保持, 使用 "session." 的请求会自动携带之前登录成功后, 所获取的cookies
response = session.post(submint_login_post_url, data=login_form_jsonObj, headers=post_headers)
response.encoding = 'utf-8'


# 打印真正用户(非游客)登陆后, 服务器端所返回的响应状态码和响应内容
print(f'\n*User* Login Response: \x1b[31m{response}\x1b[0m')
print(f'*User* Login Response.encoding : \x1b[31m{response.encoding}\x1b[0m')
print(f'*User* Login Response.status_code : \x1b[31m{response.status_code}\x1b[0m')
print(f'*User* Login Response.text: \x1b[31m{response.text}\x1b[0m')
print('-----------------------------------------------------------------------------------------------------------')


# 获取学习任务列表中各个学习任务的 id
# 学习任务列表页面: https://iedu.foxconn.com/public/user/studyTask
study_task_response = session.get(url='https://iedu.foxconn.com/public/user/studyTask', data={'currentPage': 1}, cookies=login_cookies_dict)
print(f'\nStudy Task Response Status Code: \x1b[31m{study_task_response.status_code}\x1b[0m')
soup = BeautifulSoup(study_task_response.text, 'html.parser')
dts = soup.find_all('dt', class_ = 'fl')
stduy_task_id = []
study_task_id_pattern = r'\(\d+\)'
for dt in dts:
    img = dt.find('img')
    match = re.search(pattern=study_task_id_pattern, string=str(img))
    stduy_task_id.append(match.group().strip('()'))
print(f'Study Task Id: {stduy_task_id}')


# 根据前面获取的 stduy_task_id(存储者各个学习任务 id 的列表),
# 获取各个学习任务中的课程播放页链接.
# 注意: 学习任务1 : 课程数量n
study_task_url = 'https://iedu.foxconn.com/public/user/studyTaskDetail?taskId='
play_course_url = 'https://iedu.foxconn.com/public/user/playCourse?courseId='
study_task_dict = {}
course_company_id_pattern = r'\(\d+[,]\d+\)'
for st_id in stduy_task_id:
    course_list = []
    study_task_url_temp = ''
    study_task_url_temp = study_task_url + st_id
    course_response = session.get(study_task_url_temp)
    print(f'\nCourse Response Status Code: \x1b[31m{course_response.status_code}\x1b[0m\n')
    soup = BeautifulSoup(course_response.text, 'html.parser')
    imgs = soup.find_all('img', class_ = 'dh03')
    for img in imgs:
        play_course_url_temp = ''
        match = re.search(pattern=course_company_id_pattern, string=str(img))
        course_id, company_id = re.split(',', match.group().strip('()'))
        play_course_url_temp = play_course_url + course_id + '&companyId=' + company_id
        course_list.append(play_course_url_temp)
    study_task_dict[study_task_url_temp] = course_list


# 打印日志信息:
# study_task_dict = {
# 学习任务1-url : [课程播放页链接1-url, 课程播放页链接2-url...],
# 学习任务2-url : [课程播放页链接1-url, 课程播放页链接2-url...],
# ...
# }
print(f'\nStudy Task Dict Be Shown As Below:')
for study_task_url, course_url_list in study_task_dict.items():
    print(f'{study_task_url} : {course_url_list}')
print('\n\n')


# 更新 study_task_dict, 更新后:
# study_task_dict = {
# 学习任务1-url : [课程播放页1-中可以考试的考试页面链接-url, 课程播放页2-中可以考试的考试页面链接-url...],
# 学习任务2-url : [课程播放页1-中可以考试的考试页面链接-url, 课程播放页2-中可以考试的考试页面链接-url...],
# ...
# }
exam_url = 'https://iedu.foxconn.com/public/play/examUI?courseId='
course_id_pattern = r'\d+'
for study_task_url, course_url_list in study_task_dict.items():
    print(f'📄Study Task Url: {study_task_url}')
    exam_url_temp_list = []
    for course_url in course_url_list:
        exam_url_temp = ''
        match = re.search(pattern=course_id_pattern, string=course_url)
        course_id = match.group()
        exam_url_temp = exam_url + course_id
        exam_response = session.get(url=exam_url_temp)
        if len(exam_response.text) == 7:
            print(f"\t❌ Course ID({course_id}): No Examination")
        elif len(exam_response.text) == 29:
            print(f"\t❌ Course ID({course_id}): Can't Do Examination Because The Cosurse You Don't Finsh")
        else:
            print(f"\t✅ Course ID({course_id}): Can Do Examination")
            exam_url_temp_list.append(exam_url_temp)
        print(f'\t\t🔗 Exam Url: \x1b[4m{exam_url_temp}\x1b[0m')
    # 仅存储可以考试的考试页面 url
    study_task_dict[study_task_url] = exam_url_temp_list


# 打印日志信息:
# study_task_dict = {
# 学习任务1-url : [课程播放页链接1-考试页面-url, 课程播放页链接2-考试页面-url...],
# 学习任务2-url : [课程播放页链接1-考试页面-url, 课程播放页链接2-考试页面-url...],
# ...
# }
print(f'\n\n(Updated)Study Task Dict Be Shown As Below:')
for study_task_url, exam_url_list in study_task_dict.items():
    print(f'{study_task_url} : {exam_url_list}')
print('\n\n')


# 准备交卷, 即提交试卷表单
def post_exam_form(exam_url, j_type, s_m_type, j_s_m_type, exam_payload):
    # 拷贝副本, 之所以拷贝副本是因为:
    # fake_exam_question_answer(..) 方法中对 exam_payload 中的内容做了修改,
    # 若不拷贝副本, 会影响 create_post_exam_payload(..) 对 exam_payload 的使用!
    exam_payload_copy = copy.deepcopy(exam_payload)
    post_exam_form_url = 'https://iedu.foxconn.com/public/play/submitExam'
    # 存储本次试卷中所出现的不同题目 ID 及其对应的正确答案 
    all_questionIDs_and_answers_dict = {}
    # 动态拟造不同题型试卷的答案
    post_exam_payload = fake_exam_question_answer(j_type, s_m_type, j_s_m_type, exam_payload=exam_payload)
    # 是否继续考试的标志
    not_pass_exam = True
    # 注意: 每次提交的试卷表单中, Exam Payload 中的 startDate, examToken 的值是动态变换的!
    while not_pass_exam:
        # 注意: 休眠 1 秒, 防止因短时间内发送大量 POST 请求而导致网页响应崩溃 / 被服务器发现俺是小蛛蛛!
        time.sleep(1)
        # 提交试卷表单
        post_exam_form_response = session.post(url=post_exam_form_url, data=post_exam_payload, headers=post_headers)
        print(f'\t\t---> 1.Post Exam Payload Then Response Status Code Is: {post_exam_form_response.status_code}')
        # 解析响应数据
        questionIDs_and_answers_dict, previous_exam_score = parse_response_answer(post_exam_form_response.text)
        # 存储本此考试试卷中的题目 ID 及其对应的答案
        all_questionIDs_and_answers_dict.update(questionIDs_and_answers_dict)
        all_questionID_num = len(all_questionIDs_and_answers_dict)
        print(f'\t\t\t--->> 4.This Exam Question ID: {exam_payload_copy['questionID']}')
        print(f'\t\t\t--->> 5.All Question ID and Answers Of This Exam(num : {all_questionID_num}): {all_questionIDs_and_answers_dict}')
        # 若上次考试满分则结束考试
        if previous_exam_score == '100':
            not_pass_exam = False
        else:
            post_exam_payload = create_post_exam_payload(exam_url, exam_payload_copy, all_questionIDs_and_answers_dict)


# 根据之前考试中存储的 all_questionIDs_and_answers_dict = {question-id-1 : answer, question-id-2 : answer, ...},
# 构造新的, 用于提交试卷表单所需的 Exam Payload
def create_post_exam_payload(exam_url, exam_payload, all_questionIDs_and_answers_dict):
    previous_four_item_exam_payload_str = ''
    question_payload_str = ''
    # 1.获取本次考试中, 用于提交试卷表单所需的新的 exam_payload
    # 注意: 之所以获取新的 Exam Payload, 是因为每次提交试卷表单, Exam Payload 中的 startDate, examToken 的值是动态变换的!
    new_exam_payload = get_exam_payload(exam_url)
    # 2.更新 startDate, examToken
    previous_four_item_exam_payload = ['examId', 'startDate', 'examToken', 'userName']
    for item in previous_four_item_exam_payload:
        previous_four_item_exam_payload_str += item + '=' + new_exam_payload[item] + '&'
    # 3.遍历其中的题目 ID 列表, 通过在题目 ID 在 all_questionIDs_and_answers_dict 查找其对应的答案, 
    # 既为各个题目 ID 设置好对应的正确答案, eg.{'M-xxx':'ABCD'}.
    # 注意: 若在 all_questionIDs_and_answers_dict 未找到某个题目 ID, 则填写默认答案
    DEFAULT_S_M_ANSWER = 'A'
    DEFAULT_J_ANSWER = '0'
    J_exam_type_pattern = r'J-\d+'
    S_exam_type_pattern = r'S-\d+'
    M_exam_type_pattern = r'M-\d+'
    # 注意: 不同 Exam Payload 对应的题目不同, 两者为相互对应关系,
    # 所以前面既然使用了 new_exam_payload 中的前四项 examId, startDate, examToken, userName,
    # 这里也应该使用 new_exam_payload 中的题目, 而不是 exam_payload 中的题目!!!
    questionID_list = new_exam_payload['questionID']
    for question_id in questionID_list:
        j_match = re.search(J_exam_type_pattern, question_id)
        s_match = re.search(S_exam_type_pattern, question_id)
        m_match = re.search(M_exam_type_pattern, question_id)
        if question_id in all_questionIDs_and_answers_dict.keys():
            question_id_answer = all_questionIDs_and_answers_dict[question_id]
            # 判断 question_id 的类型
            if j_match or s_match:
                question_payload_str += question_id + '=' + question_id_answer + '&'
            if m_match:
                if len(question_id_answer) > 1: # eg. ABCD
                    for answer in question_id_answer:
                        question_payload_str += question_id + '=' + answer + '&'
                else: # eg. A
                    question_payload_str += question_id + '=' + answer + '&'
        # question_id not in all_questionIDs_and_answers_dict.keys()
        else: 
            if j_match:
                question_payload_str += question_id + '=' + DEFAULT_J_ANSWER + '&'
            if s_match or m_match:
                question_payload_str += question_id + '=' + DEFAULT_S_M_ANSWER + '&'
    # 删除最后一个字符'&'
    question_payload_str = question_payload_str[:-1]
    # 4.将 2 和 3 合并, 且将其转换为 'key=xxx&key2=...' 类型的 Post Payload 格式
    exam_post_payload = previous_four_item_exam_payload_str + question_payload_str
    print(f'\t\t\t--->> 6.Create A Exam Payload With Before Answers: {exam_post_payload}')
    # 5.将封装好的, 用于提交试卷的 Exam Payload 返回
    return exam_post_payload


# 动态拟造不同题型试卷的答案(是假滴答案哟～)
def fake_exam_question_answer(j_type, s_m_type, j_s_m_type, exam_payload):
    J_exam_type_pattern = r'J-\d+'
    S_exam_type_pattern = r'S-\d+'
    M_exam_type_pattern = r'M-\d+'
    DEFAULT_S_M_ANSWER = 'A' # 选择题(单选/多选/单选+多选)的默认答案
    DEFAULT_J_ANSWER = '0' # 单选题的默认答案
    exam_question_id_list = exam_payload['questionID']
    if j_type: # 仅判断
        for question_id in exam_question_id_list:
            exam_payload[question_id] = DEFAULT_J_ANSWER
    if s_m_type: # 选择(单选+多选)
        for question_id in exam_question_id_list:
            exam_payload[question_id] = DEFAULT_S_M_ANSWER
        pass
    if j_s_m_type: # 判断+选择(单选+多选)
        for question_id in exam_question_id_list:
            s_match = re.search(pattern=S_exam_type_pattern, string=question_id)
            m_match = re.search(pattern=M_exam_type_pattern, string=question_id)
            j_match = re.search(pattern=J_exam_type_pattern, string=question_id)
            if s_match or m_match:
                exam_payload[question_id] = DEFAULT_S_M_ANSWER
            if j_match: 
                exam_payload[question_id] = DEFAULT_J_ANSWER
    # 删除多余数据, 即删除其中的键 questionID 及其对应的 value(列表)
    del exam_payload['questionID']
    # -4: examId, startDate, examToken, userName
    print(f'\t\t---> Get Exam Question Num: {len(exam_payload) - 4}')
    print(f'\t\t---> Create The First Fake Exam Payload For Get Answers: {exam_payload}')
    # 返回已填充(准备)就绪的 exam_payload, 待 POST 的试卷表单
    return exam_payload


# 提取提交试卷表单后, 响应数据中的题目答案
def parse_response_answer(post_exam_form_response_text):
    response_text = post_exam_form_response_text
    # 1.通过 <div class="question_warp"> 获取所有 {'题目ID' : ['正确答案,..,..']}: 
    # {'J/S/M-xxx' : [answer1, answer2,..]}
    # {'J/S/M-xxx' : [answer1, answer2,..]}
    # 2.将上述数据格式转换成 Post Payload 格式, 为下次可能重做试卷做准备, Post Payload 格式示例如下:
    # examId=21192&startDate=1717073797395&examToken=ecaf47e5-a1f7-4d30-93a1-ca9e0f99cf91&userName=F1245363
    # &J-260386=1&J-260389=0&J-260388=1&J-260387=0
    # &S-368483=A&S-368480=B&S-368481=C&S-368482=C
    # &M-168361=A&M-168361=B&M-168361=C&M-168361=D&M-168360=A&M-168360=B&M-168360=C&M-168360=D
    exam_question_answers = {}
    strong_tag_value_pattern = r"<strong.*?>(.*?)<\/strong>"
    question_id__pattern = r'J-\d+|S-\d+|M-\d+'
    soup = BeautifulSoup(response_text, 'html.parser')
    score_div = soup.find('div', class_ = 'exam_result')
    question_divs = soup.find_all('div', class_ = 'question_warp')
    previous_exam_score = re.search(pattern=strong_tag_value_pattern, string=str(score_div)).group(1)
    for div in question_divs:
        question_id = re.search(pattern=question_id__pattern, string=str(div)).group()
        question_answer = re.search(pattern=strong_tag_value_pattern, string=str(div)).group(1)
        if question_answer == 'YES':
            question_answer = '1'
        if question_answer == 'NO':
            question_answer = '0'
        exam_question_answers[question_id] = question_answer
    print(f'\t\t\t--->> 2.Get QuestionID And Answers: {exam_question_answers}')
    if previous_exam_score == '100':
        print(f'\t\t\t--->> 3.Get Previous Exam Score:【{previous_exam_score}】🎉')
    else:
        print(f'\t\t\t--->> 3.Get Previous Exam Score:【{previous_exam_score}】')
    return exam_question_answers, previous_exam_score


# 判断考试页面的题目题型:
# 1.判断: J
# 2.选择(单选/多选/单选+多选): S_M
# 3.判断 + 选择(单选/多选/单选+多选): J_S_M
def get_exam_type(exam_url):
    J = False # Judgment
    S_M = False # Single And Multiple
    J_S_M = False # Judgment, Single And Multiple
    J_exam_type_pattern = r'Judgment'
    S_exam_type_pattern = r'Single'
    M_exam_type_pattern = r'Multiple'
    get_exam_response = session.get(exam_url)
    soup = BeautifulSoup(get_exam_response.text, 'html.parser')
    divs = soup.find_all('div', class_ = 'm-secpart')
    for div in divs:
        j = re.search(pattern=J_exam_type_pattern, string=str(div))
        s = re.search(pattern=S_exam_type_pattern, string=str(div))
        m = re.search(pattern=M_exam_type_pattern, string=str(div))
        if j:
            J = True
        if s or m:
            S_M = True
    if J and S_M:
        J_S_M = True
        print('\t\t---> Get Exam Type: J_S_M')
    if J == True and S_M == False:
        print('\t\t---> Get Exam Type: J')
    if J == False:
        print('\t\t---> Get Exam Type: S_M')
    post_exam_form_dict = get_exam_payload(exam_url)
    post_exam_form(exam_url, J, S_M, J_S_M, post_exam_form_dict)


# 获取考试页面的题目数量(此方法已弃用):
def get_question_num(exam_url):
    exam_num_pattern = r'>(\d+)<'
    get_exam_response = session.get(exam_url)
    soup = BeautifulSoup(get_exam_response.text, 'html.parser')
    divs = soup.find_all('div', class_ = 'tihao_box')
    question_numbers = re.findall(pattern=exam_num_pattern, string=str(divs))
    question_numbers_int = [int(s) for s in question_numbers]
    question_num = max(question_numbers_int)
    return question_num


# 获取提交试卷表单所需的 Payload: 即examId, startDate, examToken, userName,
# 其中还包含着存储着考试页面中各个题目 ID 的列表,
# 即 post_exam_form_dict = 
# {
# 'examId' : 'xxx',
# 'startDate' : 'xxx',
# 'examToken' : 'xxx',
# 'userName' : 'xxx',
# 'questionID' : [question_id_list]
# }
def get_exam_payload(exam_url):
    question_id_list = []
    post_exam_form_dict = {}
    EXAM_ID = 'examId'
    START_DATE = 'startDate'
    EXAM_TOCKEN = 'examToken'
    USER_NAME = 'userName'
    QUESTION_ID = 'questionID'
    get_exam_response = session.get(exam_url)
    soup = BeautifulSoup(get_exam_response.text, 'html.parser')
    inputs = soup.find_all('input')
    for input in inputs:
        if input.get('name') == EXAM_ID:
            post_exam_form_dict[EXAM_ID] = input.get('value')
        if input.get('name') == START_DATE:
            post_exam_form_dict[START_DATE] = input.get('value')
        if input.get('name') == EXAM_TOCKEN:
            post_exam_form_dict[EXAM_TOCKEN] = input.get('value')
        if input.get('name') == USER_NAME:
            post_exam_form_dict[USER_NAME] = input.get('value')
        question_id__pattern = r'J-\d+|S-\d+|M-\d+'
        match = re.search(question_id__pattern, input.get('name'))
        if match:
            question_id = match.group()
            if question_id not in question_id_list: # 去重
                question_id_list.append(question_id)
    post_exam_form_dict[QUESTION_ID] = question_id_list
    return post_exam_form_dict


# 程序运行入口
# 注意: study_task_url 为学习任务链接, exam_url_list 为可以考试的页面链接
for study_task_url, exam_url_list in study_task_dict.items():
    print(f'📄 Study Task Url: {study_task_url}')
    # 遍历可以考试的页面链接
    for exam_url in exam_url_list:
        if exam_url:
            print(f'\t🔗 {exam_url}')
            # 获取本次考试中试卷的题目类型
            get_exam_type(exam_url=exam_url)


# 扩展程序, 解决如下 bug 及新需求:
#
# 1.bug: 学习任务列表页中缺少学习任务.
# 原因分析: 因为在上述程序中, 真正用户登陆(非游客)后, 
# 服务器所返回的 cookies 中的 fxbdLocal 为 en, 并且随后我在 cookies 中补充了一个 Playload 数据, 即{zh_choose : n},
# 又因不同语言, 即不同国家发布的学习任务不同, 故若将页面设置成英文, 可能会缺少专门为中国地区发布的学习任务.
#
# 2.新需求: 上述程序只能刷 "学习任务列表页" 的课程, 而无法刷 "晋升课程列表页" 的课程.
# 注: 学习任务列表页: https://iedu.foxconn.com/public/user/studyTask
# 注: 晋升课程列表页: https://iedu.foxconn.com/public/user/promotionCourse
#
# 3.上述 bug 及新需求的解决方案如下:
# 通过修改 exam_url 中的 courseId 可解决上述 bug 及新需求,
# 注: eg.exam_url = 'https://iedu.foxconn.com/public/play/examUI?courseId=32383'
#
# 4.注意: 若要运行下述程序, 请先注释掉 461～468 的代码
# def program_extension():
#     print('\n\n------------------- Program Extension -------------------')
#     # 存储 courseId 的列表
#     # 注意: 一定要是看完课件的 courseId, 即可以考试的 courseId, 因为这里没有做校验
#     courseId_list = [45552, 45554]
#     # 考试页面前缀
#     url = 'https://iedu.foxconn.com/public/play/examUI?courseId='
#     # 存储考试页面的列表
#     exam_url_list = []
#     # 拼接出完整的考试页面, 并逐个存储到 exam_url_list
#     for courseId in courseId_list:
#         exam_url = ''
#         exam_url = url + str(courseId)
#         exam_url_list.append(exam_url)
#     print(exam_url_list)
#     # 遍历 exam_url_list, 逐个刷题
#     for exam_url in exam_url_list:
#         get_exam_type(exam_url=exam_url)

# # 运行扩展程序
# program_extension()
