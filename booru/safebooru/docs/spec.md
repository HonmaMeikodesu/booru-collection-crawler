你需要给图片存档网站`Safebooru`开发一个爬虫程序（使用Python），以下是用户使用的时序流程：
1. 用户输入一段单数或复数的tags（例如`honma_meiko`, `honma_meiko ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai.`）
2. 拼装出搜索tags的url: 例如`https://safebooru.org/index.php?page=post&s=list&tags=honma_meiko`, `https://safebooru.org/index.php?page=post&s=list&tags=honma_meiko+ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai.`。**可见根据用户输入的tags构建url时，需要对复数的tags进行`+`拼接，同时每个tag需要进行URL编码**
3. 分析返回的页面DOM，参考[postList.html](./postList.html)，需要注意的是，页面总页数(`totalPage`)不会出现在页面下方分页器中，注意你不断地触发`下一页`按钮，直到最后一页(`document.querySelector("#paginator a[alt='next']")`的`href`属性中记载了下一页的url地址)，当找不到这个元素时候，代表已经是最后一页
4. 从第1页到最后一页，获取每一个post的id(`document.querySelectorAll("#post-list .image-list a")`可以拿到当前页下的所有post)
5. 拼装出获取post内容的url：例如`https://safebooru.org/index.php?page=post&s=view&id=6256119`
6. 分析返回的页面DOM，参考[post.html](./post.html)，获取post的图片资源以及tags并存储在本地。
   1. 图片资源的链接可以通过`[...document.querySelectorAll("li a")].find(item => item.textContent.includes("Original image"))`找到一个`a`标签，在它的`href`属性内，注意**找不到这个DOM元素时，抛出异常错误通知用户**
   2. tags在`#tag-sidebar`的`li`元素下，分为`Copyright`, `Character`, `Artist`, `General`, `Meta`五个类别
7. 注意参考[globalSpec.md](../../../globalSpec.md)的开发规范：
   1. 给每个task创建一个task foler
   2. 注意`第一次执行`，`从断点执行`，`重新执行一个已完成任务`三种场景下的业务逻辑
   3. 注意控制请求间隔，避免触发流量防火墙机制

   