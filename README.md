![EPG-Server](https://socialify.git.ci/zengzifeng520/IPTV/image?description=1&descriptionEditable=Docker%F0%9F%90%B3%E9%83%A8%E7%BD%B2%EF%BC%8C%E5%B8%A6%E8%AE%BE%E7%BD%AE%E7%95%8C%E9%9D%A2%E3%80%81%E5%8F%B0%E6%A0%87%E7%AE%A1%E7%90%86%EF%BC%8C%E6%94%AF%E6%8C%81DIYP%E3%80%81%E8%B6%85%E7%BA%A7%E7%9B%B4%E6%92%AD%E5%8F%8Axmltv%E3%80%82&font=Inter&forks=1&issues=1&language=1&owner=1&pattern=Circuit%20Board&pulls=1&stargazers=1&theme=Auto)

# 📺 EPG-Server
![Build](https://github.com/zengzifeng520/IPTV/actions/workflows/docker-image.yml/badge.svg)

PHP 实现的 EPG（电子节目指南）服务端， `Docker` 部署，自带设置界面、台标管理、直播源管理，支持 **DIYP & 百川** 、 **超级直播** 以及 **xmltv** 格式。

> 本仓库基于 [yqnext/epg](https://github.com/yqnext/epg) 部署，镜像由 GitHub Actions 自动构建并推送到 [ghcr.io/zengzifeng520/iptv](https://github.com/zengzifeng520/IPTV/pkgs/container/iptv)。

## 💻 主要功能

📡 **多直播格式**：支持返回 DIYP & 百川、超级直播以及 xmltv 格式文件。
  
🐳 **多架构支持**：提供适用于 amd64、arm64 和 armv7 架构的 Docker 镜像，兼容电视盒子等设备使用。

📦 **小体积镜像**：基于 Alpine 构建，压缩后仅 20 MB。

🗃️ **数据库管理**：采用先构建后存数据库的策略，减少冗余、提升读取速度。支持 SQLite 和 MySQL 数据库，内置 phpLiteAdmin 管理工具。

🖼️ **台标管理**：支持台标模糊匹配，便于匹配台标资源。

➰ **直播源管理**：支持聚合 TXT/M3U 直播源，并定时更新。

🔒 **访问权限控制**：支持设置 TOKEN ，限制访问 EPG 服务及直播源。

⏱️ **缓存支持**：集成 Memcached，可自定义缓存时间。

🔄 **频道匹配**：支持繁体中文频道匹配，可进行双向模糊匹配；支持频道别名（可使用正则表达式）和指定 EPG 源。

⏳ **定时任务**：支持定时更新数据。

📝 **节目单生成**：支持生成指定频道节目单并匹配 M3U 的 xmltv 格式文件。

🗂️ **兼容多种格式**：支持不同标准格式的 XMLTV 文件。

🛠️ **文件管理**：集成 tinyfilemanager 以便于文件管理。

🌐 **界面设置**：包含简单易用的网页设置页面，便于操作和管理。

> [!TIP]
> `xmltv` 用户搭配 [【一键生成】匹配 M3U 文件的 XML 节目单](https://www.right.com.cn/forum/thread-8392662-1-1.html) 使用。

<picture>
  <source
    media="(prefers-color-scheme: dark)"
    srcset="/pic/management-dark.png"
  />
  <source
    media="(prefers-color-scheme: light)"
    srcset="/pic/management.png"
  />
  <img
    alt="设置页面"
    src="/pic/management.png"
  />
</picture>

> **内置正则表达式说明：**
> - 包含 `regex:`
> - 示例：
>   - `CCTV$1 => regex:/^CCTV[-\s]*(\d{1,2}(\s*P(LUS)?|[K\+])?)(?![\s-]*(美洲|欧洲)).*/i` ：将 `CCTV 1综合`、`CCTV-4K频道`、`CCTV - 5+频道`、`CCTV - 5PLUS频道` 等替换成 `CCTV1`、`CCTV4K`、`CCTV5+`、`CCTV5PLUS`（排除 `CCTV4美洲` 和 `CCTV4欧洲`）

## 📝 更新日志

### [CHANGELOG.md](./CHANGELOG.md)

## TODO：

- [x] 支持返回超级直播格式
- [x] 整合更轻量的 `alpine-apache-php` 容器
- [x] 整合生成 `xml` 文件
- [x] 支持多对一频道映射
- [x] 支持繁体频道匹配
- [x] 仅保存指定频道列表节目单
- [x] 导入/导出配置
- [x] 频道指定 `EPG` 源
- [x] 生成台标信息
- [x] 直播源管理

## 🚀 部署步骤

1. 配置 `Docker` 环境

2. 若已安装过，先删除旧版本并拉取新版本（**⚠️注意备份数据：`更多设置` -> `数据导出` / `数据导入`**）

   ```bash
   docker rm php-epg -f && docker pull ghcr.io/zengzifeng520/iptv:latest
   ```

3. 拉取镜像并运行：

   ```bash
   docker run -d \
     --name php-epg \
     -p 5678:80 \
     --restart always \
     ghcr.io/zengzifeng520/iptv:latest
   ```

    > 默认端口为 `5678` ，根据需要自行修改（注意端口占用）
    > 
    > 可选参数：`-e PHP_MEMORY_LIMIT=512M` ，设置 PHP 内存限制，默认 `512M`
    > 
    > 镜像由本仓库的 GitHub Actions 自动构建并推送到 `ghcr.io/zengzifeng520/iptv`

<details>

<summary>（可选）数据持久化</summary>

- 执行以下指令，`./data` 可根据自己需要更改
    ```bash
    docker run -d \
      --name php-epg \
      -v ./data:/htdocs/data \
      -p 5678:80 \
      --restart always \
      ghcr.io/zengzifeng520/iptv:latest
    ```

</details>

<details>

<summary>（可选）同时部署 MySQL 、 phpMyAdmin 及 php-epg</summary>

- **方法1：** 新建 [`docker-compose.yml`](./docker-compose.yml) 文件后，在同目录执行 `docker-compose up -d`
- **方法2：** 依次执行以下指令：
    ```bash
    docker run -d \
      --name mysql \
      -p 3306:3306 \
      -e MYSQL_ROOT_PASSWORD=root_password \
      -e MYSQL_DATABASE=phpepg \
      -e MYSQL_USER=phpepg \
      -e MYSQL_PASSWORD=phpepg \
      --restart always \
      mysql:8.0
    ```
    ```bash
    docker run -d \
      --name phpmyadmin \
      -p 8080:80 \
      -e PMA_HOST=mysql \
      -e PMA_PORT=3306 \
      --link mysql:mysql \
      --restart always \
      phpmyadmin/phpmyadmin:latest
    ```
    ```bash
    docker run -d \
      --name php-epg \
      -v ./data:/htdocs/data \
      -p 5678:80 \
      --restart always \
      --link mysql:mysql \
      --link phpmyadmin:phpmyadmin \
      ghcr.io/zengzifeng520/iptv:latest
    ```
 
</details>

## 🛠️ 使用步骤

1. 在浏览器中打开 `http://{服务器IP地址}:5678/manage.php`
2. **默认密码为空**，根据需要自行设置
3. 添加 `EPG 源地址`， GitHub 源确保能够访问，点击 `更新配置` 保存
4. 点击 `更新数据库` 拉取数据，点击 `数据库更新日志` 查看日志，点击 `查看数据库` 查看具体条目
5. 设置 `定时任务` ，点击 `更新配置` 保存，点击 `定时任务日志` 查看定时任务时间表

    > 建议从 `凌晨1点` 左右开始抓，很多源 `00:00 ~ 00:30` 都是无数据。
    > 隔 `6 ~ 12` 小时抓一次即可。

6. 点击 `更多设置` ，选择是否 `生成xml文件` 、`生成方式` ，设置 `限定频道节目单`
7. 用浏览器测试各个接口的返回结果是否正确：

- `xmltv` 接口： `http://{服务器IP地址}:5678/index.php`
- `DIYP&百川` 接口： `http://{服务器IP地址}:5678/index.php?ch=CCTV1`
- `超级直播` 接口： `http://{服务器IP地址}:5678/index.php?channel=CCTV1`

8. 将 **`http://{服务器IP地址}:5678/index.php`** 填入 `DIYP`、`TiviMate` 等软件的 `EPG 地址栏`

- ⚠️ 直接使用 `docker run` 运行的话，可以将 `:5678/index.php` 替换为 **`:5678/`**。
- ⚠️ 部分软件不支持跳转解析 `xmltv` 文件，可直接使用 **`:5678/t.xml.gz`** 或 **`:5678/t.xml`** 访问。

> **快捷键：**
>
> - `Ctrl + S`：保存设置
> - `Ctrl + /`：对选中 EPG 地址设置（取消）注释

## ☕ Buy Me a Coffee

<picture>
  <source
    media="(prefers-color-scheme: dark)"
    srcset="/pic/buymeacofee-dark.png"
  />
  <source
    media="(prefers-color-scheme: light)"
    srcset="/pic/buymeacofee.png"
  />
  <img
    alt="Buy Me a Coffee"
    src="/pic/buymeacofee.png"
  />
</picture>

## ⭐ Star History

<picture>
  <source
    media="(prefers-color-scheme: dark)"
    srcset="https://api.star-history.com/svg?repos=zengzifeng520/IPTV&type=Date&theme=dark"
  />
  <source
    media="(prefers-color-scheme: light)"
    srcset="https://api.star-history.com/svg?repos=zengzifeng520/IPTV&type=Date"
  />
  <img
    alt="Star History Chart"
    src="https://api.star-history.com/svg?repos=zengzifeng520/IPTV&type=Date"
  />
</picture>

## 👍 特别鸣谢
- [ChatGPT](https://chatgpt.com/)
- [celetor/epg](https://github.com/celetor/epg)
- [sparkssssssssss/epg](https://github.com/sparkssssssssss/epg)
- [Black_crow/xmlgz](https://gitee.com/Black_crow/xmlgz)
- [112114](https://diyp.112114.xyz/)
- [EPG 51zmt](http://epg.51zmt.top:8000/)
- [fanmingming/live](https://github.com/fanmingming/live)
- [wanglindl/TVlogo](https://github.com/wanglindl/TVlogo)
