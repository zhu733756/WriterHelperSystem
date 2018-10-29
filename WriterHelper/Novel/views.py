import os,random
from django.http import JsonResponse
from django.shortcuts import render
from .tools import SearchTools
from .tools.Crawler import crawler_push,getOutQueueEle,check_enqueue,check_outqueue
from .tools.BookListSpider import BookInfoSpider
from itertools import chain

def index(request):
    '''
    index页面
    :param request:
    :return:
    '''
    return render(request, "menu.html")

def search_dir(request):
    '''
    搜索本地已经建立索引的词库
    :param request:
    :return:
    '''
    req = request.POST.get("author_s")
    idioms_path = SearchTools.SearchRes.find_searchKey("idiom")
    novels_path = SearchTools.SearchRes.find_searchKey("verb")
    all_path=chain(idioms_path,novels_path)
    author_infos = {}
    for path in all_path:
        info = os.path.split(os.path.dirname(path))[-1]
        author_infos.setdefault(info,[]).append(os.path.split(path)[-1].split(".")[0])
    info_dir = {}
    if req:
        for info,v in author_infos.items():
            if req in info:
                author, book = info.split("-")[:]
                info_dir.setdefault(author, []).append(book+"(%s)"%(",".join(v)))
    else:
        for info,v in author_infos.items():
            author, book = info.split("-")[:]
            info_dir.setdefault(author, []).append(book+"(%s)"%(",".join(v)))
    if info_dir:
        return JsonResponse(info_dir)
    else:
        return JsonResponse("没有检测到可用书籍信息！", safe=False)

def search_form(request):
    '''
    搜索匹配词条的结果
    :param request:
    :return:
    '''
    res={}
    res.setdefault("words", request.POST["words"])
    idioms = SearchTools.SearchRes(res).search_idioms()
    novels = SearchTools.SearchRes(res).search_novels()
    data={
        "idioms":idioms,
        "novels":novels,
    }
    return JsonResponse(data)

def search_booklist(request):
    '''
    获取在线书籍信息列表
    :param request:
    :return:
    '''
    book_req=request.POST.get("search_key").strip()
    book_req = book_req.replace("；", ";").replace("：", ":")
    search_spider = BookInfoSpider()
    if ";"  not in book_req:
        if ":" in book_req:
            kwargs = {book_req.split(":")[0]: book_req.split(":")[1] }
            res = search_spider.split_search_key(**kwargs)
            return JsonResponse(res, safe=False)
        res=search_spider.split_search_key(book_req)
        if res:
            return JsonResponse(res)
    if ";" in book_req:
        args=[arg for arg in book_req.split(";")[:] if ":" not in arg and arg]
        kwargs=[arg for arg in book_req.split(";")[:] if arg not in args and arg]
        if kwargs:
            kwargs={item.split(":")[0]:item.split(":")[1] for item in kwargs}
            all_res=search_spider.split_search_key(*args,**kwargs)
            return JsonResponse(all_res,safe=False)
        return JsonResponse(search_spider.split_search_key(*args))

def search_duplicate_url(request):
    '''
    查询是否有重复提交的url
    :param request:
    :return:
    '''
    reqs = request.POST.getlist("array[]")
    reqs=list(set(reqs))
    valid_urls=crawler_push(reqs)
    invalid_urls = [url for url in reqs if url not in valid_urls]
    res={url:"success" for url in valid_urls}
    if invalid_urls:
        res.update({url: "fail" for url in invalid_urls})
        return JsonResponse(res)
    else:
        return JsonResponse(res)

d={}

def search_crawl_status(request):
    '''
    搜索爬取状态，用于构造爬取进度条
    :param request:
    :return:
    '''
    global d
    url=request.GET.get("url")
    if check_enqueue(url):
        return JsonResponse(0, safe=False)
    else:
        if check_outqueue(url):
            req= getOutQueueEle()
            if req is not None:
                href,param=req.split("@")[:]
                if href==url:
                    if param.isdigit():#给定total，保存下来
                        d.setdefault(url,{}).setdefault("total",int(param))
                    elif param=="finished":#信号爬取完成
                        return JsonResponse(100, safe=False)
        if url in d:#爬取过程中
            total=d[url]["total"]
            if "status" not in d[url]:
                d[url]["status"]=0
            status=d[url]["status"]#上次保存的状态值
            addedNum=random.choice(range(12,16))*100/total
            if status+addedNum<100:
                status=round(status+addedNum,1)
                d[url]["status"]=status
            return JsonResponse(status,safe=False)
        return JsonResponse(0, safe=False)#程序间隙响应间







