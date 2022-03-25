<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
</p>

<div align="center">

# nonebot-plugin-mediawiki

_适用于 [NoneBot2](https://v2.nonebot.dev) 的 MediaWiki 查询插件_

</div>

------

![Python](https://img.shields.io/badge/python-3.8%2B-lightgrey)
![nonebot2](https://img.shields.io/badge/nonebot2-2.0.0b2-yellowgreen)
[![GitHub license](https://img.shields.io/github/license/KoishiStudio/nonebot-plugin-mediawiki)](https://github.com/KoishiStudio/nonebot-plugin-mediawiki/blob/main/LICENSE)
[![pypi](https://img.shields.io/pypi/v/nonebot-plugin-mediawiki?color=blue)](https://pypi.org/project/nonebot-plugin-mediawiki/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/nonebot-plugin-mediawiki)

[![GitHub issues](https://img.shields.io/github/issues/KoishiStudio/nonebot-plugin-mediawiki)](https://github.com/KoishiStudio/nonebot-plugin-mediawiki/issues)
[![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/KoishiStudio/nonebot-plugin-mediawiki?include_prereleases)](https://github.com/KoishiStudio/nonebot-plugin-mediawiki/releases)
![GitHub contributors](https://img.shields.io/github/contributors/KoishiStudio/nonebot-plugin-mediawiki)
![GitHub Repo stars](https://img.shields.io/github/stars/KoishiStudio/nonebot-plugin-mediawiki?style=social)

------

本项目是 [Flandre](https://github.com/KoishiStudio/Flandre) 的
[wiki](https://github.com/KoishiStudio/Flandre/tree/main/src/plugins/wiki) 组件，经简单修改成为独立插件发布

## 用途
一般来说最需要wikibot的大概是一些wiki项目的交流群，不过鉴于这种群通常都有大佬在，写个bot自然不是什么难事的说～
所以我在本插件开发时更注重于在一般的群聊中能起作用的功能，供交流问题时快速引用。例如游戏的交流群，可能需要经常在wiki上查找角色信息、游戏特性等，
去wiki上手动翻链接显然很麻烦。同时，对很多群来说，交流的话题都很广泛，例如今天聊mc明天聊泰拉后天聊战地等情况都是存在的，
因此我着重设计了对多个wiki的支持。而对一些更加专业的、wiki项目的群才能用到的功能（例如页面更改提醒），则不在开发计划中。当然，如果没有这些需求，
本插件也适合wiki项目的群使用，例如本插件具有的完善的全局管理与回落机制，可以降低群管理人员在管理同一项目的群时的成本，等等。

啊啦，说了这么多，总而言之，欢迎使用！欢迎提交issue！（如果有pr就更好了～）

## 使用说明

### TL;DR

查询条目： `[[条目名]]`

查询模板： `[[模板名]]`

绕过api查询条目： `((条目名))`

添加（全局）Wiki： `wiki.add` `wiki.add.global`

删除（全局）Wiki： `wiki.delete` `wiki.delete.global`

修改（全局）默认Wiki： `wiki.default` `wiki.default.global`

查看Wiki列表： `wiki.list` `wiki.list.global`

**其中所有非全局指令均需要在目标群中进行，所有全局指令均只有Bot管理员能执行**

### 查询功能

查询功能的语法和标准的mediawiki内链格式基本一致：

使用半角中括号包裹要查询的条目名，如 `[[帮助]]`

使用半角大括号包裹要查询的模板名，如 `{{测试模板}}`

Bot会尝试去调取目标wiki的api,并获取对应标题的页面信息（默认允许重定向、跨wiki、简繁转换）。如果未找到对应条目，或者对应页面是消歧义页面，
则会提供数字来选择。如果调用api失败或者未配置api，会回落到字符串拼接的方式生成链接。

```plaintext
Tip：如果api返回的结果不是你想要的，可以使用半角小括号包裹条目名以绕过api，如 ((帮助))
```

当绑定了多个wiki时，需要指定前缀以查询默认wiki之外的wiki，例如，假如将某个wiki的前缀设置为flan，且不是默认wiki，则查询命令对应为[[flan:帮助]]

### 管理功能

* wiki列表
  * 权限：所有人可用
  * 语法：`wiki.list`
  * 返回：当前群绑定的wiki列表，以及全局wiki列表

#### 单个群的管理

以下操作均需在目标群内进行，bot管理员和群管理员均有权限操作

* 添加wiki
  * 语法 `wiki.add`
  * 参数：
    * 前缀：用于区分wiki的前缀，仅支持字母、数字和下划线，不能和本群已有的重复，但可以和全局已有的重复，此时本地设置优先。另外，为了防止和mediawiki的名字空间冲突，bot默认屏蔽了部分名字空间名作为前缀的能力，也请在绑定前先了解目标wiki的名字空间情况。
    * api地址（可选）：目标wiki的mediawiki api的地址。某些wiki可能限制api调用，此时可以回复`0`来不设置api。该地址通常可以在目标wiki的`Special:版本#接入点URL`页面中找到。或者也可以尝试这些一般的格式：
    ```plaintext
    https://www.example.org/api.php （如萌娘百科）
    https://www.example.org/w/api.php (如维基百科）
    ```
    * 通用url：目标wiki的条目路径。通常来讲，在该url后加上正确的条目名即可访问目标条目。可以在目标wiki的`Special:版本#接入点URL`中找到（“条目路径”中的$1即条目名）
    ```plaintext
    例如，对维基百科：https://www.example.org/wiki
    对萌百等：https://www.example.org/
    ```


* 删除wiki
  * 语法 `wiki.delete`
  * 参数：
    * 前缀：要删除的wiki的前缀


* 设置默认wiki
  * 语法 `wiki.default`
    * 参数：
      * 前缀：要设置默认的wiki的前缀
  ```plaintext
  Tip：本群/全局绑定的的一个wiki将被自动设置为本地/全局的默认wiki,当本地/全局绑定的默认wiki被删除时会自动清除对应的默认wiki设置，无需手动操作。
  ```


#### 全局管理

以下操作可以在群内进行，也可以私聊进行，只有bot管理员有权限操作

* 添加全局wiki
  * 语法：`wiki.add.global`
    * 参数同上


* 删除全局wiki
  * 语法：`wiki.delete.global`
    * 参数同上


* 设置全局默认wiki
  * 语法：`wiki.default.global`
    * 参数同上

### 附加说明
#### 本地和全局

bot管理员可以设置全局的wiki，全局wiki的设计意图在于回落，换句话说，本地设置无条件优先于全局设置。当且仅当在以下情况下，全局设置会被应用：

1. 本地没有绑定任何wiki
2. 本地没有设置默认前缀，而查询请求中又不包含前缀

```plaintext
注意：如果本地有和全局默认前缀相同的wiki时，本地的wiki仍将被优先调用
```

3. 本地设置了默认前缀，但是本地不存在该wiki

```plaintext
注意：当前缀在全局中也不存在时，前缀将被视为名字空间，直接和条目名一并传入api进行查询
```

4. 查询请求中包含的前缀在本地不存在

#### API调用

为了提供更准确的结果，默认情况下bot会调用mediawiki api查询条目。当api无法正常调用时，会使用通用url和条目名拼接作为回落。
如果返回了错误的结果，可以使用小括号查询来绕过api。

在某些情况下，你可能希望限制调用频率，如目标Wiki的api调用频率限制严格，或者目标wiki的防火墙会阻断高频请求 ~~（萌百：你报我域名算了）~~ 。
为简化查询流程，本插件并不提供对应功能，在Flandre的开发计划中有全局的频率限制组件，可以用于此用途。如果你将本插件独立使用，可以考虑使用其他频率限制插件来解决。

根据我个人在一些wiki项目的QQ群观摩 ~~（潜伏）~~  的经验来说，群bot的wiki功能被调用的频率并不会很高，因此除非你将bot同时置于多个群，
并且都连接到同一个wiki,或者有人恶意利用bot（事实上由于bot不响应私聊的查询请求，要达到这种效果只能在群聊中刷屏），不然碰上调用频率限制的可能性还是很低的
