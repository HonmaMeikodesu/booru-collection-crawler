你需要给图片存档网站`Danbooru`开发一个爬虫程序（使用Python），以下是用户使用的时序流程：
1. 用户输入一段单数或复数的tags（例如`honma_meiko`, `ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai.`）
2. 拼装出搜索tags的url: 例如`https://danbooru.donmai.us/posts?page=1&tags=honma_meiko+ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai.`
3. 分析返回的页面DOM，参考[postList.html](./postList.html)，获取总页数（`.paginator-next`元素的前一个`a`元素就是最后一页，也即总页数）
4. 从第1页到最后一页，获取每一个post的id(在`.post-preview-link`的`a`元素的`href`属性内，比如`/posts/10200019?q=honma_meiko+ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai.`，则post id为10200019)
5. 拼装出获取post内容的url：例如`https://danbooru.donmai.us/posts/10200019`
6. 分析返回的页面DOM，参考[post.html](./post.html)，获取post的图片资源以及tags并存储在本地。
   1. 图片资源在`.image-view-original-link`的`a`元素的`href`属性内，比如`https://cdn.donmai.us/original/1c/a6/__honma_meiko_ano_hi_mita_hana_no_namae_wo_bokutachi_wa_mada_shiranai_drawn_by_maruyo__1ca68fe1a9dfb3d8857c83734b7e00c2.jpg`，
   2. tags在`#tag-list`的`section`元素下，分为`Artist`, `Copyright`, `General`, `Meta`四个类别
7. 注意参考[globalSpec.md](../../../globalSpec.md)的开发规范：
   1. 给每个tags创建一个task foler
   2. 注意`第一次执行`，`从断点执行`，`重新执行一个已完成任务`三种场景下的业务逻辑
   3. 注意控制请求间隔，避免触发Danbooru的防火墙机制