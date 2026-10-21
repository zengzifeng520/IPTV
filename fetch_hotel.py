"""
酒店源抓取模块 — 从 IPTV 列表 API（如 api.809899.xyz）获取酒店直播节点并按区域解析

接口说明（对接 IPTV 搜索神器同款 Cloudflare Worker）：
    GET {hotel_api}/extract_hotel?keyword={keyword}
    Header: X-App-Auth: {hotel_api_auth}
    返回 JSON: {"results": [{"ip": ..., "region": "广东省 电信", "channels": [{"name": ..., "url": ...}]}]}
"""
import asyncio
import json
import logging
import aiohttp
import config

logger = logging.getLogger(__name__)

DEFAULT_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def _api_headers():
    """列表/提取 API 的请求头：签名头来自配置，可随上游变更调整。"""
    auth = config.hotel_config.get("hotel_api_auth", "iptv-tools-official-v1")
    return {"User-Agent": DEFAULT_UA, "Connection": "close", "X-App-Auth": auth}


async def _fetch_json(session, url, timeout):
    """通用 JSON 请求（带签名头）"""
    try:
        async with session.get(url, headers=_api_headers(), timeout=timeout) as resp:
            resp.raise_for_status()
            text = await resp.text()
            return json.loads(text)
    except Exception as e:
        logger.warning("[酒店源] 请求失败: %s", e)
        return None


async def fetch_all_from_hotel():
    """
    主入口：调用列表提取 API（/extract_hotel），返回 channels 格式。
    返回: {category: {channel_name: [urls]}}
    category 使用节点区域命名（如 "酒店源-广东省 电信"）
    """
    hotel_api = (config.hotel_config.get("hotel_api") or "").rstrip("/")
    if not hotel_api:
        logger.warning("[酒店源] 未配置 hotel_api")
        return {}
    keyword = config.hotel_config.get("hotel_keyword", "") or ""
    url = f"{hotel_api}/extract_hotel?keyword={keyword}"
    timeout = aiohttp.ClientTimeout(total=60)
    connector = aiohttp.TCPConnector(limit=5, ssl=False)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        data = await _fetch_json(session, url, 60)
    if not data or "results" not in data:
        logger.warning("[酒店源] 未获取到节点数据")
        return {}
    results = data["results"] or []
    channels = {}
    for node in results:
        region = (node.get("region") or "").strip()
        cat = f"酒店源-{region}" if region else "酒店源"
        for ch in node.get("channels") or []:
            name = (ch.get("name") or "").strip()
            channel_url = (ch.get("url") or "").strip()
            if name and channel_url:
                channels.setdefault(cat, {}).setdefault(name, []).append(channel_url)
    # 按 频道名 去重（同名频道保留不同 URL）
    for cat in channels:
        for name in channels[cat]:
            channels[cat][name] = list(dict.fromkeys(channels[cat][name]))
    total = sum(len(urls) for ch in channels.values() for urls in ch.values())
    logger.info(f"[酒店源] 解析完成，共 {len(channels)} 个分类、{total} 个频道-URL 组合")
    return channels
