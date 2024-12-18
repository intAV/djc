import requests
import time
import datetime
import calendar
import schedule

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from aes_utils import AESCipher

import logging


########################下面是日志设置##########################

logger = logging.getLogger('djc_helper')
logger.setLevel(level=logging.DEBUG)

formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s',datefmt="%Y-%m-%d %H:%M:%S")

file_handler = logging.FileHandler(r'./djc_helper.log', encoding='utf-8')
file_handler.setLevel(level=logging.INFO)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)
#logger.info('info信息')
#logger.info('{} {} {}'.format("aa","bb",111))
#########################日志设置结束###########################



class Djc:
    def __init__(self,openid,access_token):
        aes_key = "se35d32s63r7m23m"
        rsa_public_key_file = "djc_rsa_public_key_new.der"
        self.sDeviceID = "78825c39040f8c87d3e65b6e6eb9d9a7217dac8dbe88e801f8d50d163fe00462"
        self.p_tk = self.get_p_tk(access_token)
        self.openid = openid
        self.sVersionName = "v4.6.9.0"

        self.djc_headers = {
            "Content-Type":"application/x-www-form-urlencoded",
            "User-Agent":"TencentDaojucheng=v4.6.9.0&appSource=android&appVersion=145&ch=10000&sDeviceID=" + self.sDeviceID + "&firmwareVersion=7.1.2&phoneBrand=samsung&phoneVersion=SM-G988N&displayMetrics=1080 * 1920&cpu=ARMv7 Processor rev 0 (v7l)&net=wifi&sVersionName=v4.6.9.0&plNo=163",
            "Cookie":'djc_appSource=android; djc_appVersion=145; acctype=qc; appid=1101958653; openid='+ openid +'; access_token='+ access_token +';',
        }

        #获取签名
        nowMillSecond = self.getMillSecondsUnix()

        dataToSign = f"{openid}+{self.sDeviceID}+{nowMillSecond}+{self.sVersionName}"

        # aes
        encrypted = AESCipher(aes_key).encrypt(dataToSign)

        # rsa
        rasPublicKey = RSA.import_key(open(rsa_public_key_file, "rb").read())
        encrypted3 = PKCS1_v1_5.new(rasPublicKey).encrypt(encrypted)

        self.sign = encrypted3.hex()



    def get_p_tk(self,access_token):
        #access_token 32位登录凭证
        s = access_token[22:32]
        hash = 5381
        for i in range(len(s)):
            hash += (hash << 5) + ord(s[i])
        return str(hash & 0x7fffffff)


    def getMillSecondsUnix(self):
        return int(time.time() * 1000.0)

    # 查询豆子
    def get_douzi(self):
        sDjcSign = self.sign
        url = "https://djcapp.game.qq.com/daoju/igw/main/?_service=app.bean.balance&iAppId=1001&_app_id=1001&method=balance&page=0&w_ver=29&w_id=45&sDeviceID={}&djcRequestId={}-{}-287&appVersion=145&p_tk={}&osVersion=Android-25&ch=10000&sVersionName=v4.6.9.0&appSource=android&sDjcSign={}".format(self.sDeviceID,self.sDeviceID,self.getMillSecondsUnix(),self.p_tk,sDjcSign)
        # print(self.djc_headers,url)
        douzi = -1
        while True:
            if douzi > -1:
                break
            try:
                res = requests.get(url=url,headers=self.djc_headers,timeout=10).json()
                r_res = "豆子:" + str(res.get("data").get("balance"))
                logger.info(r_res)
                douzi = int(res.get("data").get("balance"))
                time.sleep(1)
            except Exception as e:
                r_res = "1.get_douzi error..."
                logger.info(r_res,e)
                time.sleep(1)

        return douzi

    # 每日签到
    def djc_qiandao(self):
        sDjcSign = self.sign
        url = "https://comm.ams.game.qq.com/ams/ame/amesvr?ameVersion=0.3&sServiceType=dj&iActivityId=11117&sServiceDepartment=djc&set_info=newterminals&&appSource=android&appVersion=145&ch=10000&sDeviceID={}&osVersion=Android-25&p_tk={}&sVersionName=v4.6.9.0".format(self.sDeviceID,self.p_tk)
        post_data1 = "djcRequestId={}-{}-357&appVersion=145&sign_version=1.0&ch=10000&iActivityId=11117&sDjcSign={}&sDeviceID={}&p_tk={}&month=202310&osVersion=Android-25&iFlowId=96939&sVersionName=v4.6.9.0&sServiceDepartment=djc&sServiceType=dj&appSource=android&g_tk=1842395457".format(self.sDeviceID,self.getMillSecondsUnix(),sDjcSign,self.sDeviceID,self.p_tk)
        # print(post_data)
        post_data2 = "djcRequestId={}-{}-357&appVersion=145&ch=10000&iActivityId=11117&sDjcSign={}&sDeviceID={}&p_tk={}&osVersion=Android-25&iFlowId=324410&sVersionName=v4.6.9.0&sServiceDepartment=djc&sServiceType=dj&appSource=android&g_tk=1842395457".format(self.sDeviceID,self.getMillSecondsUnix(),sDjcSign,self.sDeviceID,self.p_tk)
        # print(post_data1,post_data2)
        try:
            res = requests.post(url=url,data=post_data1,headers=self.djc_headers,timeout=10).json()
            time.sleep(0.5)
            res2 = requests.post(url=url,data=post_data2,headers=self.djc_headers,timeout=10).json()
            # print(res)
            if "modRet" in str(res2):
                ss = res2.get("modRet").get("sMsg")
            else:
                ss = ""
            r_res = "1.每日签到:" + res.get("modRet").get("msg") + " " + ss
            logger.info(r_res)
            return r_res
        except Exception as e:
            r_res = "1.djc_qiandao error..."
            logger.info(e)
            return r_res


    # 任务一:打卡活动中心
    def task_one(self):
        sDjcSign = self.sign
        url = "https://djcapp.game.qq.com/daoju/igw/main/?_service=app.task.report&iAppId=1001&_app_id=1001&task_type=activity_center&sDeviceID={}&djcRequestId={}-{}-492&appVersion=145&p_tk={}&osVersion=Android-25&ch=10000&sVersionName=v4.6.9.0&appSource=android&sDjcSign={}".format(self.sDeviceID,self.sDeviceID,self.getMillSecondsUnix(),self.p_tk,sDjcSign)
        try:
            r_res2 = ''
            while True:
                if "恭喜您" in r_res2 or "不能重复" in r_res2:
                    break
                res = requests.get(url=url,headers=self.djc_headers,timeout=10).json()

                #领取奖励
                time.sleep(1)
                url_task_one_ok = "https://djcapp.game.qq.com/daoju/igw/main/?_service=welink.usertask.swoole&djcRequestId={}-{}-200&appVersion=145&ch=10000&_app_id=1001&sDjcSign={}&sDeviceID={}&optype=receive_usertask&p_tk=1853943881&output_format=json&osVersion=Android-25&sVersionName=v4.6.9.0&iruleId=100040&appSource=android".format(self.sDeviceID,self.getMillSecondsUnix(),sDjcSign,self.sDeviceID)
                res = requests.get(url=url_task_one_ok,headers=self.djc_headers,timeout=10).json()
                if "modRet" in str(res):
                    # print("task_one {} {}豆子\n".format(res.get("msg"),res.get("data").get("ams_data").get("modRet").get("all_item_list")[0].get("iItemCount")))
                    douzi = res.get("data").get("ams_data").get("modRet").get("all_item_list")[0].get("iItemCount")
                else:
                    douzi = ""
                r_res2 = "2.任务一:领取奖励 " + res.get("msg") + douzi
                logger.info(r_res2)
            return r_res2
        except Exception as e:
            r_res = "2.task_one error..."
            logger.info(r_res,e)
            return r_res


    # 任务二：浏览3个活动页面 docid=活动id
    def task_two(self):
        sDjcSign = self.sign
        url_1 = "https://djcapp.game.qq.com/daoju/igw/main/?_service=app.activity.comment_list&iAppId=1001&_app_id=1001&docid=926446&page=1&_biz_code=lol&s_type=firstComment&creater=145058234058452&w_ver=32&w_id=113&sDeviceID={}&djcRequestId={}-{}-99&appVersion=145&p_tk={}&osVersion=Android-25&ch=10000&sVersionName=v4.6.9.0&appSource=android&sDjcSign={}".format(self.sDeviceID,self.sDeviceID,self.getMillSecondsUnix(),self.p_tk,sDjcSign)
        url_2 = "https://djcapp.game.qq.com/daoju/igw/main/?_service=app.activity.comment_list&iAppId=1001&_app_id=1001&docid=911146&page=1&_biz_code=actdaoju&s_type=firstComment&creater=145058234058452&w_ver=32&w_id=113&sDeviceID={}&djcRequestId={}-{}-881&appVersion=145&p_tk={}&osVersion=Android-25&ch=10000&sVersionName=v4.6.9.0&appSource=android&sDjcSign={}".format(self.sDeviceID,self.sDeviceID,self.getMillSecondsUnix(),self.p_tk,sDjcSign)
        url_3 = "https://djcapp.game.qq.com/daoju/igw/main/?_service=app.activity.comment_list&iAppId=1001&_app_id=1001&docid=922577&page=1&_biz_code=fz&s_type=firstComment&creater=145058234058452&w_ver=32&w_id=113&sDeviceID={}&djcRequestId={}-{}-90&appVersion=145&p_tk={}&osVersion=Android-25&ch=10000&sVersionName=v4.6.9.0&appSource=android&sDjcSign={}".format(self.sDeviceID,self.sDeviceID,self.getMillSecondsUnix(),self.p_tk,sDjcSign)

        # 任务上报
        url_report = "https://djcapp.game.qq.com/daoju/igw/main/?_service=app.task.report&iAppId=1001&_app_id=1001&task_type=activity_detail&w_ver=32&w_id=113&sDeviceID={}&djcRequestId={}-{}-139&appVersion=145&p_tk={}&osVersion=Android-25&ch=10000&sVersionName=v4.6.9.0&appSource=android&sDjcSign={}".format(self.sDeviceID,self.sDeviceID,self.getMillSecondsUnix(),self.p_tk,sDjcSign)
        # print(url_report)
        try:
            r_res2 = ''
            num = 0
            while True:
                if "恭喜您" in r_res2 or "不能重复" in r_res2 or num >= 10:
                    break
                time.sleep(1)
                res_1 = requests.get(url=url_1,headers=self.djc_headers,timeout=10).json().get("data").get("msg")
                # print(res_1)
                time.sleep(1)
                report_1 = requests.get(url=url_report,headers=self.djc_headers,timeout=10).json().get("msg")
                # print(report_1)
                time.sleep(1)
                res_2 = requests.get(url=url_2,headers=self.djc_headers,timeout=10).json().get("data").get("msg")
                # print(res_2)
                time.sleep(1)
                report_2 = requests.get(url=url_report,headers=self.djc_headers,timeout=10).json().get("msg")
                # print(report_2)
                time.sleep(1)
                res_3 = requests.get(url=url_3,headers=self.djc_headers,timeout=10).json().get("data").get("msg")
                # print(res_3)
                time.sleep(1)
                report_3 = requests.get(url=url_report,headers=self.djc_headers,timeout=10).json().get("msg")
                # print(report_3)

                #领取奖励
                time.sleep(1)
                url_task_two_ok = "https://djcapp.game.qq.com/daoju/igw/main/?_service=welink.usertask.swoole&djcRequestId={}-{}-478&appVersion=145&ch=10000&_app_id=1001&sDjcSign={}&sDeviceID={}&optype=receive_usertask&p_tk={}&output_format=json&osVersion=Android-25&sVersionName=v4.6.9.0&iruleId=327102&appSource=android".format(self.sDeviceID,self.getMillSecondsUnix(),sDjcSign,self.sDeviceID,self.p_tk)
                res = requests.get(url=url_task_two_ok,headers=self.djc_headers,timeout=10).json()
                # print(res)
                if "modRet" in str(res):
                    # print("task_two {} {}豆子\n".format(res.get("msg"),res.get("data").get("ams_data").get("modRet").get("all_item_list")[0].get("iItemCount")))
                    douzi = res.get("data").get("ams_data").get("modRet").get("all_item_list")[0].get("iItemCount")
                else:
                    douzi = ""
                r_res2 = "3.任务二:领取奖励 " + res.get("msg") + douzi
                num += 1
                logger.info(r_res2)
            return r_res2
        except Exception as e:
            r_res = "3.task_two error..."
            logger.info(r_res,e)
            return r_res


    # 活跃度到达20领取奖励
    def hy20_lingjiang(self):
        sDjcSign = self.sign
        url = "https://djcapp.game.qq.com/daoju/igw/main/?_service=welink.usertask.swoole&djcRequestId={}-{}-522&appVersion=145&ch=10000&_app_id=1001&sDjcSign={}&sDeviceID={}&optype=receive_usertask&p_tk={}&output_format=json&osVersion=Android-25&sVersionName=v4.6.9.0&iruleId=100001&appSource=android".format(self.sDeviceID,self.getMillSecondsUnix(),sDjcSign,self.sDeviceID,self.p_tk)
        try:
            r_res = ''
            while True:
                if "恭喜您" in r_res or "用尽" in r_res or "未完成" in r_res:
                    break
                res = requests.get(url=url,headers=self.djc_headers,timeout=10).json()
                r_res = "4.活跃度到达20领取奖励:" + res.get("msg")
            logger.info(r_res)
            return r_res
        except Exception as e:
            r_res = "4.hy20_lingjiang error..."
            logger.info(e)
            return r_res

    # 活跃度到达35领取奖励
    def hy35_lingjiang(self):
        sDjcSign = self.sign
        url = "https://djcapp.game.qq.com/daoju/igw/main/?_service=welink.usertask.swoole&djcRequestId={}-{}-522&appVersion=145&ch=10000&_app_id=1001&sDjcSign={}&sDeviceID={}&optype=receive_usertask&p_tk={}&output_format=json&osVersion=Android-25&sVersionName=v4.6.9.0&iruleId=100002&appSource=android".format(self.sDeviceID,self.getMillSecondsUnix(),sDjcSign,self.sDeviceID,self.p_tk)
        try:
            r_res = ''
            while True:
                if "恭喜您" in r_res or "用尽" in r_res or "未完成" in r_res:
                    break
                res = requests.get(url=url,headers=self.djc_headers,timeout=10).json()
                r_res = "7.活跃度到达35领取奖励:" + res.get("msg")
            logger.info(r_res)
            return r_res
        except Exception as e:
            r_res = "7.hy35_lingjiang error..."
            logger.info(e)
            return r_res



    # 兑换命运方舟交易牌
    def djc_buy_jyp(self):
        sDjcSign = self.sign

        try:
            #查询绑定角色
            bind_url = "https://djcapp.game.qq.com/daoju/igw/main/?_service=app.role.bind_list"
            bind_str = requests.get(url=bind_url,headers=self.djc_headers,timeout=10).json().get("data")[0].get("sRoleInfo")
            #角色id
            roleCode = bind_str.get("roleCode")
            #角色名称
            roleName = bind_str.get("roleName")
            #区
            partition = bind_str.get("partition")
            logger.info("6.[角色id:{},角色名称:{},区:{}]".format(roleCode,roleName,partition))
        except Exception as e:
            r_res = "6.查询绑定角色出错"
            logger.info(r_res)
            return r_res

        time.sleep(1)


        #iGoodsSeqId=4375 交易牌
        #iGoodsSeqId=4373 跳跃精华
        url = "https://djcapp.game.qq.com/daoju/igw/main/?_service=buy.plug.swoole.judou&iAppId=1001&_app_id=1003&_output_fmt=1&_plug_id=9800&_from=app&iGoodsSeqId=4373&iActionId=29657&iActionType=26&_biz_code=fz&biz=fz&platid=2&iZone=50&partition={}&lRoleId={}&rolename={}&p_tk={}&_cs=2&sDeviceID={}&djcRequestId={}-{}-163&appVersion=145&osVersion=Android-25&ch=10000&sVersionName=v4.6.9.0&appSource=android&sDjcSign={}".format(partition,roleCode,roleName,self.p_tk,self.sDeviceID,self.sDeviceID,self.getMillSecondsUnix(),sDjcSign)
        try:
            res = requests.get(url=url,headers=self.djc_headers,timeout=10).json()
            r_res = "6.兑换命运方舟交易牌:" + res.get("msg")
            
            # 兑换有礼
            time.sleep(1)
            url_buy_ok = "https://djcapp.game.qq.com/daoju/igw/main/?_service=welink.usertask.swoole&iAppId=1001&_app_id=1001&optype=receive_usertask&output_format=json&iruleId=327091&w_ver=29&w_id=45&sDeviceID={}&djcRequestId={}-{}-131&appVersion=145&p_tk={}&osVersion=Android-25&ch=10000&sVersionName=v4.6.9.0&appSource=android&sDjcSign={}".format(self.sDeviceID,self.sDeviceID,self.getMillSecondsUnix(),self.p_tk,sDjcSign)
            res2 = requests.get(url=url_buy_ok,headers=self.djc_headers,timeout=10).json()

            if "modRet" in str(res2):
                douzi = res2.get("data").get("ams_data").get("modRet").get("all_item_list")[0].get("iItemCount")
            else:
                douzi = ""
            r_res2 = "6.兑换有礼:" + res2.get("msg") + douzi
            r_res3 = r_res + "\n" + r_res2
            logger.info(r_res3)
            return r_res3
        except Exception as e:
            r_res = "6.djc_buy_jyp error..."
            logger.info(e)
            return r_res


    # 获取签到天数
    def get_qiandao_num(self):
        sDjcSign = self.sign
        url = "https://comm.ams.game.qq.com/ams/ame/amesvr?ameVersion=0.3&sServiceType=dj&iActivityId=11117&sServiceDepartment=djc&set_info=newterminals&&appSource=android&appVersion=145&ch=10000&sDeviceID={}&osVersion=Android-25&p_tk={}&sVersionName=v4.6.9.0".format(self.sDeviceID,self.p_tk)
        month = datetime.datetime.now().strftime("%Y%m")
        post_data = "djcRequestId={}-{}-444&appVersion=145&sign_version=1.0&ch=10000&iActivityId=11117&sDjcSign={}&sDeviceID={}&p_tk=1853943881&month={}&osVersion=Android-25&iFlowId=96938&sVersionName=v4.6.9.0&sServiceDepartment=djc&sServiceType=dj&appSource=android&g_tk=1842395457".format(self.sDeviceID,self.getMillSecondsUnix(),sDjcSign,self.sDeviceID,month)
        try:
            res = requests.post(url=url,data=post_data,headers=self.djc_headers,timeout=10).json()
            num = len(res.get("modRet").get("data"))
            return num
        except Exception as e:
            r_res = "get_qiandao_num error..."
            logger.info(e)
            return 0


    # 签到总计领奖 month_num=当月总天数
    def qiandao_lingjiang(self,num,month_num):
        if num == 3:
            iFlowId = "322021"
        elif num == 7:
            iFlowId = "322036"
        elif num == 10:
            iFlowId = "322037"
        elif num == 15:
            iFlowId = "322038"
        elif num == 20:
            iFlowId = "322039"
        elif num == 25:
            iFlowId = "322040"
        elif num == month_num:
            iFlowId = "881740"

        sDjcSign = self.sign
        url = "https://comm.ams.game.qq.com/ams/ame/amesvr?ameVersion=0.3&sServiceType=dj&iActivityId=11117&sServiceDepartment=djc&set_info=newterminals&w_ver=29&w_id=45&appSource=android&appVersion=145&ch=10000&sDeviceID={}&osVersion=Android-25&p_tk={}&sVersionName=v4.6.9.0".format(self.sDeviceID,self.p_tk)

        post_data = "djcRequestId={}-{}-132&appVersion=145&ch=10000&iActivityId=11117&sDjcSign={}&sDeviceID={}&p_tk={}&osVersion=Android-25&iFlowId={}&sVersionName=v4.6.9.0&sServiceDepartment=djc&sServiceType=dj&appSource=android&g_tk=1842395457".format(self.sDeviceID,self.getMillSecondsUnix(),sDjcSign,self.sDeviceID,self.p_tk,iFlowId)
        try:
            res = requests.post(url=url,data=post_data,headers=self.djc_headers,timeout=10).json()
            # print("qiandao_lingjiang {}\n".format(res))
            if "modRet" in str(res):
                res = "5.签到总计{}天领奖:".format(num) + res.get("msg") + res.get("flowRet").get("sMsg") + " 奖励豆子:" + res.get("modRet").get("iPackageNum")
            else:
                res = "5.签到总计{}天领奖:".format(num) + res.get("msg") + res.get("flowRet").get("sMsg")
            logger.info(res)
            return res
        except Exception as e:
            r_res = "5.qiandao_lingjiang error..."
            logger.info(e)
            return r_res


    def go(self):
        # 0.查询豆子
        douzi_1 = self.get_douzi()
        time.sleep(0.5)
        # 1.签到
        s1 = self.djc_qiandao()
        time.sleep(0.5)
        # 2.打卡活动中心
        s2 = self.task_one()
        time.sleep(0.5)
        # 3.浏览3个活动页面
        s3 = self.task_two()
        time.sleep(0.5)
        # 4.活跃度到达20领取奖励
        s4 = self.hy20_lingjiang()
        time.sleep(0.5)
        # 5.签到总计领奖
        qiandao_num = self.get_qiandao_num()
        month_num = calendar.monthrange(datetime.datetime.today().year,datetime.datetime.today().month)[1]
        time.sleep(0.5)
        if qiandao_num == 3:
            s5 = self.qiandao_lingjiang(3,month_num)
        elif qiandao_num == 7:
            s5 = self.qiandao_lingjiang(7,month_num)
        elif qiandao_num == 10:
            s5 = self.qiandao_lingjiang(10,month_num)
        elif qiandao_num == 15:
            s5 = self.qiandao_lingjiang(15,month_num)
        elif qiandao_num == 20:
            s5 = self.qiandao_lingjiang(20,month_num)
        elif qiandao_num == 25:
            s5 = self.qiandao_lingjiang(25,month_num)
        elif qiandao_num == month_num:
            s5 = self.qiandao_lingjiang(qiandao_num,month_num)
        else:
            s5 = "5.未达到签到总计领奖"
            logger.info(s5)
        # 6.如果豆子大于50，兑换交易牌
        douzi_2 = self.get_douzi()
        if douzi_2 >= 50:
            time.sleep(0.5)
            s6 = self.djc_buy_jyp()
            # 活跃度到达35领取奖励
            time.sleep(0.5)
            s6 = s6 + "\n" + self.hy35_lingjiang()
            time.sleep(0.5)
            douzi_3 = self.get_douzi()
        else:
            s6 = "6.未兑换交易牌"
            douzi_3 = douzi_2

        ss = "豆子:{}".format(douzi_1) + "\n" + s1 + "\n" + s2 + "\n" + s3 + "\n" + s4 + "\n" + "签到天数:{} ".format(qiandao_num) + "\n" + s5 + "\n" + s6 + "\n" + "豆子:{}".format(douzi_3)
        # print(ss)
        # push_msg(ss)


# 消息推送
def push_msg(msg):
    pass


if __name__ == "__main__":
    def main():
        # openid,access_token
        user1 = Djc('DE274A7B868C41878E288EB349969FD5','02EA063591F139FADC36F0577A4C98B5')
        user1.go()

        user2 = Djc('4CCCFB2844D6EEDBB6DCC6FF2546B680','AAA4C48DE381BA5C7ED784E885100B96')
        user2.go()

    main()
    # schedule.every().day.at("12:02").do(main,)
    # # schedule.every(10).seconds.do(main)
    # while True:
    #     #tt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     #logger.info("************************[{}]**********************".format(tt))
    #     schedule.run_pending()
    #     time.sleep(1)
