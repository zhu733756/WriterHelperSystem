import os
from django.http import JsonResponse
from django.shortcuts import render
from .tools import SearchTools
from .tools.Crawler import crawler_push,getOutQueueEle,check_enqueue,check_outqueue
from .tools.BookListSpider import BookInfoSpider

def index(request):
    return render(request, "menu.html")

def search_dir(request):
    idioms_dir = SearchTools.SearchRes.find_searchKey("idiom")
    verb_dir = SearchTools.SearchRes.find_searchKey("verb")
    idioms_dir.extend(verb_dir)
    author_nov_list = {}
    for path in idioms_dir:
        author_nov_list.setdefault(
            os.path.split(os.path.dirname(path))[-1], []) \
            .append(os.path.split(path)[-1].split(".")[0])
    return JsonResponse(author_nov_list)

def search(request):
    req=request.POST.get("author_s")
    idioms_path = SearchTools.SearchRes.find_searchKey("idiom")
    novels_path = SearchTools.SearchRes.find_searchKey("verb")
    idioms_path.extend(novels_path)
    author_info_path=set([os.path.dirname(path) for path in idioms_path])
    info_dir={}
    if req:
        for path in author_info_path:
            author, book = os.path.split(path)[-1].split("-")[:]
            if  req in path:
                info_dir.setdefault(author,[]).append(book)
    else:
        for path in author_info_path:
            author, book = os.path.split(path)[-1].split("-")[:]
            info_dir.setdefault(author,[]).append(book)
    if info_dir:
        return JsonResponse(info_dir)
    else:
        return JsonResponse("没有检测到可用书籍信息！",safe=False)

def search_form(request):
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
    global d
    url=request.GET.get("url")
    print(url)
    # if not check_enqueue(url) and not check_outqueue(url):
    #     return JsonResponse(100,safe=False)
    if check_enqueue(url):
        return JsonResponse(0, safe=False)
    else:
        if check_outqueue(url):
            print("------")
            req= getOutQueueEle()
            print(req)
            print("------")
            if req is not None:
                _,param=req.split("@")[:]
                if param.isdigit():#给定total，保存下来
                    d.setdefault(url,{}).setdefault("total",int(param))
                elif param=="finished":#信号爬取完成
                    return JsonResponse(100, safe=False)
        if url in d:#爬取过程中
            print("d:",d)
            total=d[url]["total"]
            if "status" not in d[url]:
                d[url]["status"]=0
            status=d[url]["status"]#上次保存的状态值
            status=status+int(10 * 100 /(1.5* total))
            if status>=100:
                status=status-int(10 * 100 /(1.5* total))
            d[url]["status"]=status
            return JsonResponse(status,safe=False)
        return JsonResponse(0, safe=False)#程序间隙响应间







