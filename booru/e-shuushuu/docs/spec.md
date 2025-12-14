你需要给图片存档网站`e-shuushuu`开发一个爬虫程序（使用Python），以下是用户使用的时序流程：
1. 用户输入一个tag id（例如`76604`）
2. 拼装出搜索tag的url: 例如`https://e-shuushuu.net/search/results/?tags=76604`。
3. 分析返回的页面DOM，参考[postList.html](./postList.html)，需要注意的是，页面总页数(`totalPage`)不会出现在页面下方分页器中，注意你不断地触发`下一页`按钮，直到最后一页(`document.querySelector(".pagination .next a")`的`href`属性中记载了下一页的url地址)，当找不到这个元素时候，代表已经是最后一页
4. 获取当前页每一个post的id(`document.querySelectorAll(".image_thread.display")`可以拿到当前页下的所有post， post id就在每个返回元素的`id`属性内)，根据post的id来决定图片存储到本地时的唯一标识
5. 每个post的图片资源的链接在`document.querySelector(".image_thread.display").querySelector(".thumb_image")`选中的元素的`href`属性内，比如`<a href="/image/1060480/">Image #1060480</a>`, 注意**找不到这个DOM元素时，抛出异常错误通知用户**
6. 从第一页到最后一页，执行上述4和5步骤，获取全部的图片资源
7. 注意参考[globalSpec.md](../../../globalSpec.md)的开发规范：
   1. 给每个task创建一个task foler
   2. 注意`第一次执行`，`从断点执行`，`重新执行一个已完成任务`三种场景下的业务逻辑
   3. 注意控制请求间隔，避免触发流量防火墙机制

   