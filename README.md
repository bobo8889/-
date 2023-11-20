# ADS-B 即时通后端

## 启动 Dump1090

将交叉编译的 Dump1090 可执行文件拷贝到目标板卡上，然后后台启动 Dump1090，并转发 Raw 格式数据，端口 30002

```shell
$ sudo ./dump1090 --net --net-ro-port 30002 --aggressive --enable-agc >/dev/null 2>&1 &
```
