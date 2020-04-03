# python_scp_file_to_backup_server
进入/data/logs目录，并对三天前的日志进行打包为tar.gz格式，通过scp传递到备份服务器/data/logs目录下，并删除源文件和源压缩文件。
config.ini 可以修改源和目标目录
