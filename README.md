<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
</p>

<div align="center">

# nonebot-plugin-mediawiki

_适用于 [NoneBot2](https://v2.nonebot.dev) 的 MediaWiki 查询插件_

</div>

------

<div align="center">

![Python](https://img.shields.io/badge/python-3.8%2B-lightgrey)
![nonebot2](https://img.shields.io/badge/nonebot2-2.0.0b2-yellowgreen)
[![GitHub license](https://img.shields.io/github/license/KoishiMoe/nonebot-plugin-mediawiki)](https://github.com/KoishiMoe/nonebot-plugin-mediawiki/blob/main/LICENSE)
[![pypi](https://img.shields.io/pypi/v/nonebot-plugin-mediawiki?color=blue)](https://pypi.org/project/nonebot-plugin-mediawiki/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/nonebot-plugin-mediawiki)

[![GitHub issues](https://img.shields.io/github/issues/KoishiMoe/nonebot-plugin-mediawiki)](https://github.com/KoishiMoe/nonebot-plugin-mediawiki/issues)
[![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/KoishiMoe/nonebot-plugin-mediawiki?include_prereleases)](https://github.com/KoishiMoe/nonebot-plugin-mediawiki/releases)
![GitHub contributors](https://img.shields.io/github/contributors/KoishiMoe/nonebot-plugin-mediawiki)
![GitHub Repo stars](https://img.shields.io/github/stars/KoishiMoe/nonebot-plugin-mediawiki?style=social)

</div>

------

本项目是 [Flandre](https://github.com/KoishiMoe/Flandre) 的
[wiki](https://github.com/KoishiMoe/Flandre/tree/main/src/plugins/wiki) 组件，经简单修改成为独立插件发布

## 旧版本用户请注意
本插件在1.0版本进行了一次重构，同时更改了设置命令的语法（查询不受影响），请阅读文档的相应部分

## 关于更新

这个插件是我很久之前写的，由于个人精力有限，目前**并未**积极跟进上游更新，也**没有**进行兼容性测试。如果你在最新版的nonebot2上使用它时出现了问题，请在issue区指出。

功能更新会在后续有时间的时候在进行。当前计划中的有：跟进最新版nonebot，解除onebot适配器依赖，添加条目跟踪等功能，以及简化命令、优化管理相关操作，并对整个项目进行重构以优化性能、提升可维护性。

ETA：无



## FAQ

<details>
<summary>这个插件是干什么的？</summary> 

* 在**群聊**中查wiki用的。此处的wiki特指基于[mediawiki](https://mediawiki.org)开设的wiki网站
* 对大多数群可能都有用，但是使用频率大概会很低。从功能上说，我是为了一些具有特定的专业性话题的讨论群设计的。
例如Linux群，成员如果问了一个Wiki上已经写的很详细的问题，其他成员就可以直接利用bot来指引提问者去查看对应页面，而非自己去wiki上找，
然后再复制链接发出来。另外，对于一些wiki项目的编辑交流群来说，这种插件也可能有助于提高编辑间的交流效率
  > 简单举例：
  > 
  > A: dalao们，我这钓鱼怎么钓不出来附魔书啊
  > 
  > B: 参考[[钓鱼#垃圾与宝藏]]
  > 
  > Bot: https://minecraft.fandom.com/zh/index.php?curid=10554#%E5%9E%83%E5%9C%BE%E4%B8%8E%E5%AE%9D%E8%97%8F
</details>

<details>
<summary>这个插件和其他wiki插件有什么不同吗？</summary>

* 在我发布这个插件时，nonebot还没有这类插件，而我在的群用得上这个，因此就顺便搓了一个发布了。现在nb市场也有些其他的wiki插件（或者包含wiki功能的bot），
其中的一些是适配特定wiki的，不具有通用性（但它们可能适配了本插件无法适配的wiki，例如scpwiki——它使用的系统是wikidot，且不开放api）；
另一些（目前插件市场里只有一个，叫nonebot-plugin-wiki）同样针对mediawiki设计，意味着它们和本插件的功能在相当程度上可能是重叠的，
此时你可以比较差异功能、更新频率、兼容性、稳定性等选择适合自己的（例如前面提到的插件，接入了bwiki的api，可以获取bwiki上条目的简介之类）
* 而对于其他的bot平台，我了解的只有koishi，上面有小鱼君写的koishi-plugin-mediawiki，
这个插件应当是为wiki编辑交流群设计的，单个群只能绑定一个wiki，且只能使用api查询 ~~（这样被萌百娘WAF之后就会直接炸掉）~~
</details>

<details>
<summary>MediaWiki是啥？API是啥？条目路径是啥？</summary>

* MediaWiki是维基媒体基金会 ~~（喂鸡霉体鸡精会）~~ 开发的一套wiki引擎，大名鼎鼎的维基百科就是由它驱动的。
目前世界上有很多wiki网站均使用不同版本的该引擎驱动，尤其是很多游戏、动漫等的wiki
* 本插件提到的API都指MediaWiki的API。利用API，bot可以与wiki站点通信，来快速从wiki站点获取想要的信息。在本插件中，bot就利用api搜索指定标题是否存在、
获取页面的链接、查询消歧义义项等。
* 部分wiki出于各种原因可能不开放API，或者有非常严格的使用限制，这使得利用API获取链接的方法无法使用。所幸MediaWiki的链接格式非常稳定，
都是 `一个固定链接/条目名`，基于此，在已知这个固定链接的前提下，我们可以直接将其和条目名拼接生成链接。当然，这样bot就无法检查条目是否存在，
损失了一部分功能。在MediaWiki中，这个固定链接一般被叫做`条目路径`
</details>

<details>
<summary>我怎么知道我要查的wiki用的是不是MediaWiki？</summary>

* 直接在目标wiki搜索框搜`Special:Version`就行，一般会跳到版本页面；没有搜索功能的wiki也可以直接把浏览器地址栏末尾的条目名改成前面的那一串然后回车。
如果提示没有权限访问、不存在的特殊页面之类，应该也是MediaWiki
* 其实一般的MediaWiki站点不会刻意隐藏自己使用了MediaWiki，没什么意义，所以一般在网站的关于、版权信息之类的地方也能找到相关说明
</details>

<details>
<summary>查询命令怎么这么奇怪</summary>

* ~~因为别人都是这样整的~~ 因为MediaWiki中，同wiki内部互相引用条目用的就是双方括号，引用模板则是双花括号，这样设计是为了和wiki保持一致。
* 至于圆括号，MediaWiki中确实没有，不过上面都用了其他两种括号了，下面用圆括号也比较自然（确信）
* 为了方便手机查询 (issue#1) ，本插件也有简化的条目查询命令，即 `wiki xxx`
</details>

<details>
<summary>这插件怎么用</summary>

* 如果你是一般路过群友，只需要知道 `wiki 前缀:条目名` 这种查询语法一般就可以了，前缀的定义在下面有写。如果你的群只绑定了一个wiki，前缀是可以省略的
* 如果你是群管理员……看下面文档的说明吧～
</details>

## 使用说明

### TL;DR

查询条目： `[[条目名]]` `[[prefix:条目名]]`

查询条目（方法2）： `wiki 条目名` `wiki prefix:条目名`

查询模板： `{{模板名}}` `{{prefix:模板名}}`

绕过api查询条目： `((条目名))` `((prefix:条目名))`

页面截图： `wiki.shot prefix:条目名`

添加：wiki.add <前缀> <api地址（可选）> <通用url地址> < -g（添加该参数表示操作全局wiki)>

删除：wiki.delete <前缀> < -g >

列表：wiki.list < -g >

设置默认：wiki.default <前缀> < -g >

**其中所有非全局指令均需要在目标群中进行，所有全局指令（除查询）均只有Bot管理员能执行**

### 查询功能

查询功能的语法和标准的mediawiki内链格式基本一致：

使用半角中括号包裹要查询的条目名，如 `[[帮助]]`

使用半角大括号包裹要查询的模板名，如 `{{测试模板}}` 

（PS：直接使用`[[Template:模板名]]`也是可行的）

此外，方便起见，也可以用`wiki 条目名` `wiki prefix:条目名`的方法查询

使用`wiki.shot prefix:条目名`可以获取对应页面的截图 **（测试版功能，使用时请注意安全风险，如调取敏感条目，泄漏服务器ip，或者使用浏览器漏洞对服务器进行攻击。如不需要本功能，请先使用pypi上的正式版）**

Bot会尝试去调取目标wiki的api,并获取对应标题的页面信息（默认允许重定向、跨wiki、简繁转换）。如果未找到对应条目，或者对应页面是消歧义页面，
则会提供数字来选择。如果调用api失败或者未配置api，会回落到字符串拼接的方式生成链接。

> Tip：如果api返回的结果不是你想要的，可以使用半角小括号包裹条目名以绕过api，如 ((帮助))

当绑定了多个wiki时，需要指定前缀以查询默认wiki之外的wiki，例如，假如将某个wiki的前缀设置为flan，且不是默认wiki，则查询命令对应为[[flan:帮助]]

### 管理功能

* wiki列表
  * 权限：所有人可用
  * 语法：`wiki.list`
  * 返回：当前群绑定的wiki列表，以及全局wiki列表


* 添加wiki
  * 语法 `wiki.add`
  * 参数：
    * 前缀：用于区分wiki的前缀，仅支持字母、数字和下划线，不能和本群已有的重复，但可以和全局已有的重复，此时本地设置优先。另外，为了防止和mediawiki的名字空间冲突，bot默认屏蔽了部分名字空间名作为前缀的能力，也请在绑定前先了解目标wiki的名字空间情况。
    * api地址（可选）：目标wiki的mediawiki api的地址。某些wiki可能限制api调用，此时可以不设置api。该地址通常可以在目标wiki的`Special:版本#接入点URL`页面中找到。或者也可以尝试这些一般的格式：
    
    > https://www.example.org/api.php （如萌娘百科）
    >     
    > https://www.example.org/w/api.php (如维基百科）
    
    * 通用url：目标wiki的条目路径。通常来讲，在该url后加上正确的条目名即可访问目标条目。可以在目标wiki的`Special:版本#接入点URL`中找到（“条目路径”中的$1即条目名）
    
    > 例如，对维基百科：https://www.example.org/wiki
    >
    > 对萌百等：https://www.example.org/
    


* 删除wiki
  * 语法 `wiki.delete`
  * 参数：
    * 前缀：要删除的wiki的前缀


* 设置默认wiki
  * 语法 `wiki.default`
    * 参数：
      * 前缀：要设置默认的wiki的前缀
  
  > Tip：本群/全局绑定的的一个wiki将被自动设置为本地/全局的默认wiki,当本地/全局绑定的默认wiki被删除时会自动清除对应的默认wiki设置，无需手动操作。
  

### 附加说明
#### 本地和全局

bot管理员可以设置全局的wiki，全局wiki的设计意图在于回落，换句话说，本地设置无条件优先于全局设置。当且仅当在以下情况下，全局设置会被应用：

1. 本地没有绑定任何wiki
2. 本地没有设置默认前缀，而查询请求中又不包含前缀

> 注意：如果本地有和全局默认前缀相同的wiki时，本地的wiki仍将被优先调用

3. 本地设置了默认前缀，但是本地不存在该wiki

> 注意：当前缀在全局中也不存在时，前缀将被视为名字空间，直接和条目名一并传入api进行查询

4. 查询请求中包含的前缀在本地不存在

#### API调用

为了提供更准确的结果，默认情况下bot会调用mediawiki api查询条目。当api无法正常调用时，会使用通用url和条目名拼接作为回落。
如果返回了错误的结果，可以使用小括号查询来绕过api。

在某些情况下，你可能希望限制调用频率，如目标Wiki的api调用频率限制严格，或者目标wiki的防火墙会阻断高频请求 ~~（萌百：你报我域名算了）~~ 。
为简化查询流程，本插件并不提供对应功能，~~(不然频率限制比核心功能代码还长了)~~ 。如果确有需求，可以考虑使用[Flandre](https://github.com/KoishiMoe/Flandre) ，她带有频率限制以及适配了频率限制的wiki组件。如果你将本插件独立使用，可以考虑使用其他频率限制插件来解决（不过nonebot目前似乎还没有这类插件……）。

根据我个人在一些wiki项目的QQ群观摩 ~~（潜伏）~~  的经验来说，群bot的wiki功能被调用的频率并不会很高，因此除非你将bot同时置于多个群，
并且都连接到同一个wiki,或者有人恶意利用bot（事实上由于bot不响应私聊的查询请求，要达到这种效果只能在群聊中刷屏），不然碰上调用频率限制的可能性还是很低的
