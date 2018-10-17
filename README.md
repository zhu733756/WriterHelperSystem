
# WriterHelperSystem

## 功能介绍：
#### 本项目是一个Django和异步爬虫相结合的作家帮助系统，支持的功能如下：
#### 1、本地库目查询（可搜索作者名或者小说名，也可以直接点击搜索）
![python](https://github.com/zhu733756/WriterHelperSystem/raw/master/Src/1.png)
#### 2、在线添加小说（支持单个或多个arg或者kwargs格式添加多个关键词）
![python](https://github.com/zhu733756/WriterHelperSystem/raw/master/Src/2.png)
#### 2.1 点击“+”获取分类：
![python](https://github.com/zhu733756/WriterHelperSystem/raw/master/Src/3.png)
#### 2.2 添加至队列中：
![python](https://github.com/zhu733756/WriterHelperSystem/raw/master/Src/4.png)
#### 2.3 后台进度条：
![python](https://github.com/zhu733756/WriterHelperSystem/raw/master/Src/5.png)
#### 3、搜索索引分词：
![python](https://github.com/zhu733756/WriterHelperSystem/raw/master/Src/6.png)
#### 4、手动分词（tools目录下运行SplitWords.py）：
![python](https://github.com/zhu733756/WriterHelperSystem/raw/master/Src/7.png)

## 依赖安装
#### 所需python第三方包合辑：
```
pip install -r requirements.txt
```

## 开发环境
#### windows 7, python 3.6(作者下载的是对应python3.6版本的anconda)

## 运行准备：
#### 1、 打开数据库连接（redis）
#### 在pycharm中运行start.bat（把两个数据库的路径修改为你的路径）;
![python](https://github.com/zhu733756/WebSpider/blob/spiders/source/7.png)
#### 或者将redis设置为windows服务;

## 2 开启Django后台
#### 进入 manage.py所在目录，开启后台
```
cd WriterHelperSystem/WriterHelper/
python manage.py runserver
```

## 爬虫程序stand by
#### 进入tools目录，运行：
```
python crawler.py
```

## 说明：
#### 本项目用于本人学习，小说乃是采集源于网络免费小说资源，禁止任何商业用途！
