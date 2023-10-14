# ADS-B 即时通后端

## 启动 Dump1090

将交叉编译的 Dump1090 可执行文件拷贝到目标板卡上，然后后台启动 Dump1090，并转发 Raw 格式数据，端口 30002

```shell
$ ./dump1090 --net --net-ro-port 30002 --aggressive --enable-agc >/dev/null 2>&1 &
```

## 安装 PyModeS

先配置 pip 镜像源，创建文件 ~/.pip/pip.conf

```
[global]
index-url = https://mirrors.bfsu.edu.cn/pypi/web/simple
[install]
trusted-host = https://mirrors.bfsu.edu.cn
```

对 pip 进行升级，否则可能无法安装 pyModeS

```shell
$ sudo pip3 install --upgrade pip -i https://mirrors.bfsu.edu.cn/pypi/web/simple
```

安装 pyModeS

```shell
$ pip3 install pyModeS
```
