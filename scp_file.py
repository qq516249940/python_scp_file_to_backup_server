from configparser import ConfigParser
from paramiko import SSHClient
from scp import SCPClient
import tarfile
import os
import time,datetime
import logging
import psutil





cfg = ConfigParser()
cfg.read('config.ini')

ssh = SSHClient()
ssh.load_system_host_keys()
ssh.connect(cfg.get('target_hosts','backup_host'))

logging.basicConfig(
        filename='/opt/shell/scp.log',
        level=logging.INFO,
        format='%(levelname)s:%(asctime)s:%(message)s'
    )


def compare_unix_time(file):
    """
    清除messages系统日志,节省根目录空间.
    """
    # 获取当前时间
    today = datetime.datetime.now()
    # 计算偏移量,前3天
    offset = datetime.timedelta(days=-3)
    # 获取想要的日期的时间,即前3天时间
    re_date = (today + offset)
    # 前3天时间转换为时间戳
    re_date_unix = time.mktime(re_date.timetuple())

    print("当前日期",today.strftime('%Y-%m-%d'))  # 当前日期
    print("前3天日期",re_date.strftime('%Y-%m-%d'))  # 前3天日期

    file_time = os.path.getmtime(file)  # 文件修改时间
    timeArray = time.localtime(file_time)  # 时间戳->结构化时间
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)  #格式化时间
    print("文件修改时间",otherStyleTime)

    if file_time <= re_date_unix:
        print("已经超过3天,需要删除")
        return True
        
    else:
        print("未超过3天,无需处理!")
        return False

def get_hostname():
    myhostname = os.uname()[1]
    return myhostname


def make_tarfile(source_filename, source_dir):
    get_hostname2 = get_hostname()
    output_filename = get_hostname2  + '_' + source_filename + '.tar.gz'
    # tar = tarfile.open("sample.tar.gz", "w:gz")
    os.chdir(source_dir)
    tar = tarfile.open(output_filename, "w:gz")
    tar.add(source_filename)
    tar.close()
    return output_filename


def main():
    for root, dirs, files in os.walk(cfg.get('source_logs_path','im_logs'), topdown=False):
        for name in files:
            # print(name)
            # 判断是否包含log
            if "log" in name and "lxtx" in name and "tar.gz" not in name:
                file_name_path = os.path.join(root, name)
                if compare_unix_time(file_name_path):
                    file_name_dir_path = os.path.dirname(file_name_path)
                    file_name = os.path.split(file_name_path)[1]
                    # print(file_name_path)
                    output_filename = make_tarfile(file_name, file_name_dir_path)
                    output_filename_path = cfg.get('target_logs_path','im_logs')
                    with SCPClient(ssh.get_transport()) as scp:
                        scp.put(output_filename, output_filename_path)
                        logging.info('the file   %s is Transfer succeeded ', output_filename)
                        os.remove(file_name_path)
                        logging.info('the file   %s is removed ', file_name_path)
                        os.remove(output_filename)
                        logging.info('the file   %s is removed ', output_filename)
                        print("当前目录 %s ", os.getcwd())




disk_usage=psutil.disk_usage('/data')
print("硬盘根目录使用率为%s" % disk_usage.percent)
disk_usage=int(disk_usage.percent)
print("硬盘根目录使用率为%s" % disk_usage)
if disk_usage > 81:
    main()
                


