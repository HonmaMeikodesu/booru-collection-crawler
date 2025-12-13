你需要给图片存档网站`zerochan`开发一个爬虫程序（使用Python），以下是用户使用的时序流程：
1. 用户输入一段关键词（例如`Honma Meiko, Ano Hi Mita Hana no Namae o Bokutachi wa Mada Shiranai.`）
2. 拼装出搜索关键词的url: 例如`https://www.zerochan.net/Honma+Meiko%2C+Ano+Hi+Mita+Hana+no+Namae+o+Bokutachi+wa+Mada+Shiranai.`，可见需要将用户输入的关键字进行以下处理
   1. 将空格字符转换为`+`
   2. 进行URL编码
3. 分析返回的页面DOM，参考[postList.html](./postList.html)，需要注意的是，页面总页数(`totalPage`)不一定会出现在页面下方分页器中，注意你不断地触发`下一页`按钮，直到最后一页(`nav.pagination > a[ref="next"]`的`href`属性中记载了下一页的url地址)
4. 从第1页到最后一页，获取每一个post的id(在`ul#thumbs2 > li`的`li`元素的`data-id`属性内，比如`<li class="" data-id="2941468">`，则post id为2941468)
5. 拼装出获取post内容的url：例如`https://www.zerochan.net/2941468`
6. 分析返回的页面DOM，参考[post.html](./post.html)，获取post的图片资源以及tags并存储在本地。
   1. 图片资源可以通过`JSON.parse(document.querySelector("div#content > script").innerHTML).contentUrl`拿到，例如`'https://static.zerochan.net/Honma.Meiko.full.2941468.jpg'`
   2. **该网站没有tags分类，因此不需要进行tags的解析和存储**
7. 注意参考[globalSpec.md](../../../globalSpec.md)的开发规范：
   1. 给每个task创建一个task foler
   2. 注意`第一次执行`，`从断点执行`，`重新执行一个已完成任务`三种场景下的业务逻辑d，除此之外`断点执行`执行后应当后接一次同步sync最新数据的操作（等同于`重新执行一个已完成任务`）
   3. 注意控制请求间隔，避免触发Zerochan的防火墙机制
   4. 不需要GUI，命令行调用即可
   5. 参考[danbooru_scraper](../../danbooru/danbooru_scraper.py)的实现，二者虽然是针对不同网站，但是功能上大部分可以完全照着复刻