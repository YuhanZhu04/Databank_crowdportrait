import requests
import time
import requests
import time
import re
import pandas as pd

# 每次运行前更新 COOKIE
# COOKIE = 'cna=WIexINCop1QCAdzEYl5r2INI; dnk=; lgc=; cookie2=1ef899b7fcec50ad0875edd6269ddcb2; _nk_=; cancelledSubSites=empty; t=5bb8e5b44717c3ebd6b19fffa2f6a626; _tb_token_=e3e54d5aaeebe; xlly_s=1; welcomeShownTime=1776075897020; uc1=cookie21=UIHiLt3xSalX&cookie14=UoYZbLAyI7jpCQ%3D%3D; lid=icebreaker%E6%97%97%E8%88%B0%E5%BA%97%3Amax; unb=2212454123853; sgcookie=E100lYZ%2BNb0Dk%2Fx1XYkvZuJq0%2BnCsKYS4rRk3B8q0WVADeiSmylMC4mqJTE42d0%2Fuez9ShR4YeBvXx58OojowlGGC%2FMtR0ngrlAy82T%2BWZ6rF0PoRrMsL0CHdyxW3PB1A%2Bku; csg=b4e22988; sn=icebreaker%E6%97%97%E8%88%B0%E5%BA%97%3Amax; db_base=50b02bb98c3037e7c3d8250f3f6ce510; db_smart=6b2ef51015a15b5881f11d97df505e5f; isg=BHh4l9YYZQclcoh1-4DujUMASSYK4dxrOHzydbLpxLNmzRi3WvGs-47-h8X9nZRD; __YSF_SESSION__={"baseId":"8c3037e7c3d8250f","brandId":"6ca96e7e7b375583","departmentId":"839e97c85da40a0d","smartId":"d98652764cdabb54","databankProjectId":"7eae325ba969c6d3"}; tfstk=gSZjvNqnsIAXcBWA6IWyFO7T3TisoTSUMdMTKRK2BmnxCcw31OX0QSzSB7PsbcyOi5ZswfcY0xlqB5NzfVW0_ElOfRnxSrlZgfi_IW6PTMSUn-miD65FYphrPfieXxdZBLn-bA6VNVRan-mMEuVqzT2cfUxmqAnT60h-Kvm9Dj3OF4HEBcKxWnL-wbDtXchxk0L-3Ac96qHAF8hoBchT6qBS2bDtXfFtXACGNYbjM-6TYYU5x9fUBbt9XuMRsfefehD8vxgj9-EXXhBihqGLHb1Aba7IyR0_jdxs7-U3svFvM1GgV8EYJWCyujUICJz_9O8mUVZmVfEAxpG8cRZSozRvkvijG2ExJG6QpVU7VmrAse2zFj3I4z7lgVobGycnkafu18G46ogJG_la88rxPWCyV50_Woo8D_IC4aKEOwP95LgHfYGFFTTMS4oUETIdC3QikYDzYT6WGF0xEYGFFTTMSqHoU2W5FITG.'
TARGET_NAMES = ["ib_buyer_2601_03"] #修改名字！！
BASE_URL = "https://databank.tmall.com/api/paasapi"

import rookiepy
import requests

def get_browser_cookie():
    print("🚀 正在通过 rookiepy 尝试静默提取 Edge Cookie...")
    try:
        # 直接调用 edge 方法，rookiepy 会处理复杂的解密和读取逻辑
        # 可以通过 domains 参数过滤，加快速度
        cookies = rookiepy.edge(domains=["tmall.com"])
        
        # 将对象列表转换为 standard cookie 字符串格式
        cookie_parts = []
        for c in cookies:
            cookie_parts.append(f"{c['name']}={c['value']}")
        
        cookie_str = "; ".join(cookie_parts)
        
        if "_tb_token_" not in cookie_str:
            print("⚠️ 提取成功但未发现登录标识，请确保 Edge 中已登录。")
            return ""
            
        print("✅ Edge Cookie 提取成功！")
        return cookie_str
    except Exception as e:
        print(f"❌ 获取失败: {e}")
        return ""

# 使用
COOKIE = get_browser_cookie()

def get_token(cookie):
    m = re.search(r'_tb_token_=([^;]+)', cookie)
    return m.group(1) if m else ""

HEADERS = {
    "accept": "*/*",
    "content-type": "application/json",
    "referer": "https://databank.tmall.com/",
    "user-agent": "Mozilla/5.0", 
    "x-requested-with": "XMLHttpRequest",
    "x-csrf-token": get_token(COOKIE),
    "cookie": COOKIE
}


# 步骤 1: 稳定检索 subjectId
def search_crowd_id(crowd_name):
    print(f"\n🔍 [步骤1] 开始检索人群包IDz:【{crowd_name}】...")
    list_headers = HEADERS.copy()
    list_headers["x-custom-router"] = "databank-customAnalysis" 
    
    for page in range(1, 50):
        params = {
            "path": "/api/v1/custom/list", "source": "CUSTOM",
            "page": page, "pageSize": 50, "qualityReportOpened": "all",
            "keyword": "", "type": "4", "category2NotEqualList": "scene_crowd"
        }
        try:
            res = requests.get(BASE_URL, headers=list_headers, params=params, timeout=10)
            res_json = res.json()
            
            items = res_json.get("data", {}).get("list", [])
            if not items:
                if page == 1: print("❌ 接口返回空数据，请检查 Cookie 是否已过期！")
                break
                
            for item in items:
                name = item.get("name", item.get("crowdName", ""))
                if crowd_name.strip() == name.strip():
                    sid = str(item.get("id", item.get("subjectId")))
                    print(f"✅ 成功命中！提取到 subjectId: {sid}")
                    return sid
        except Exception as e:
            print("❌ 检索列表异常:", e)
            break
            
    print(f"❌ 未找到名为【{crowd_name}】的人群包")
    return None

# 步骤 2: 画像生成（注入省份、城市、购买力）
def get_snapshot_id(subject_id, subject_name):
    print(f"⏳ [步骤2] 正在向服务器提交【自定义标签】画像生成指令...")
    body = {
        "path": "/api/perspectiveV3/snapshotDetail",
        "contentType": "application/json", "subjectType": "0",
        "subjectId": subject_id, "subjectName": subject_name,
        "snapshotRequestRegions": [
            {
                "regionKey": "basicTag", "tagConditions": {},
                "tagEnames": [
                    "daas_tag_pred_gender_20200415091417",   # 性别
                    "daas_tag_pred_age_level_20200415093010",  # 年龄
                    "daas_tag_resident_province_tb_userid",    # 省份
                    "daas_tag_resident_city_tb_userid"         # 城市
                ]
            },
            {
                "regionKey": "consumerTag", "tagConditions": {},
                "tagEnames": [ "pref_purchasing_power" ] # 购买力
            }
        ]
    }
    
    try:
        res = requests.post(BASE_URL, headers=HEADERS, json=body, timeout=15)
        snapshot_id = res.json().get("data", {}).get("snapshotId")
        if snapshot_id:
            print("✅ 标签注入成功，快照ID:", snapshot_id)
            return snapshot_id
    except Exception as e:
        print("❌ 申请快照出错:", e)
        
    print("❌ 申请快照失败，服务器未返回有效数据。")
    return None


# ==========================================
# 步骤 2: 【精准词根匹配版】画像快照下发函数
# ==========================================
def get_snapshot_id(subject_id, subject_name):
    print(f"⏳ [步骤2] 正在执行标签精准词根匹配并下发生成指令...")
    
    # ---------------------------------------------------------
    # 📚 1. 你的“全量标签大字典” (假设以后你从阿里接口拉到了几百个)
    # ---------------------------------------------------------
    ALL_ALI_TAGS = [
        "daas_tag_pred_gender_20200415091417",   # 用户性别
        "daas_tag_child_gender_20210101",        # 子女性别 (假设有这个)
        "daas_tag_pred_age_level_20200415093010",  # 用户年龄
        "daas_tag_child_age_20210101",           # 子女年龄 (假设有这个)
        "daas_tag_resident_province_tb_userid",    # 常住省份
        "daas_tag_resident_city_tb_userid",        # 常住城市
        "common_receive_city_level_180d",          # 收货城市线级
        "pref_purchasing_power",                   # 购买力
        "stage",                                   # 人生阶段
        "complete_stage",                          # 完整人生阶段
        "SHOP_USER_GMV",                           # 消费者客单价
        "PRICE_PER_BYR",                           # 笔单价
        "dkx_strategy_crowd",                      # 八大人群
        "daas_tag_cate1_high_preference"           # 一级类目偏好
    ]
    
    # ---------------------------------------------------------
    # 🎯 2. 升级版：“精准词根”关键词
    # 不要用宽泛的单词，带上前缀，完美避开子女性别、子女年龄的干扰！
    # ---------------------------------------------------------
    my_fuzzy_keywords = [
        "pred_gender",       # 🎯 明确指定是预测(用户)性别，避开 child_gender
        "pred_age_level",    # 🎯 明确指定是预测(用户)年龄，避开 child_age
        "resident_province", # 🎯 明确指定是常住省份
        "resident_city",     # 🎯 明确指定是常住城市
        "purchasing_power",  # 购买力
        "strategy_crowd"     # 策略人群
    ]
    
    # ---------------------------------------------------------
    # ⚙️ 3. 核心匹配引擎
    # ---------------------------------------------------------
    matched_tags = []
    for tag in ALL_ALI_TAGS:
        for keyword in my_fuzzy_keywords:
            if keyword in tag and tag not in matched_tags:
                matched_tags.append(tag)
                
    print(f"🎯 词根匹配成功！精准提取到 {len(matched_tags)} 个真实标签：")
    for t in matched_tags: print(f"   -> {t}")

    # ---------------------------------------------------------
    # 🚀 4. 将匹配好的全称列表打包发给阿里
    # ---------------------------------------------------------
    body = {
        "path": "/api/perspectiveV3/snapshotDetail",
        "contentType": "application/json", "subjectType": "0",
        "subjectId": subject_id, "subjectName": subject_name,
        "snapshotRequestRegions": [
            {
                "regionKey": "basicTag", "tagConditions": {},
                "tagEnames": matched_tags 
            }
        ]
    }
    
    try:
        res = requests.post(BASE_URL, headers=HEADERS, json=body, timeout=15)
        snapshot_id = res.json().get("data", {}).get("snapshotId")
        if snapshot_id:
            print(f"✅ 包含 {len(matched_tags)} 个维度的快照注入成功，快照ID: {snapshot_id}")
            return snapshot_id
    except Exception as e:
        print("❌ 申请快照出错:", e)
        
    print("❌ 申请快照失败，服务器未返回有效数据。")
    return None

print("✅ [Cell 3] 精准词根匹配及快照下发函数加载完毕！")

# ==========================================
# 步骤 3: 提取真实画像数据 
# ==========================================
def get_dataset(snapshot_id, subject_id):
    print(f"📥 [步骤3] 正在拉取画像详细数据...")
    params = {
        "path": "/api/snapshot/getDataset",
        "snapshotId": snapshot_id, "subjectId": subject_id
    }
    
    for i in range(1, 7):
        try:
            res = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=15)
            data = res.json()
            if data.get("data") and len(data.get("data", [])) > 0:
                print("✅ 成功拉取到画像 JSON 数据！")
                return data
        except Exception:
            pass
        time.sleep(10)
        
    print("❌ 拉取失败：超时未能获取到计算结果")
    return None


# 步骤 4: 导出 Excel
def json_to_excel(json_data, excel_filename):
    print(f"📊 [步骤4] 正在解析数据并导出为明细 Excel...")
    try:
        data = json_data.get("data", {})
        subject_id = data.get("subject", {}).get("subjectId", data.get("subjectId", "未知ID"))
            
        rows = []
        for top_region in data.get("snapshotResponseRegions", []):
            region_key = top_region.get("regionKey", "")
            for sub_region in top_region.get("snapshotResponseRegions", []):
                tag_name = sub_region.get("tagCname") or sub_region.get("tagEname", "")
                for res in sub_region.get("tagValueResults", []):
                    value_name = res.get("tagValueName") if res.get("tagValueName") is None else res.get("tagValueName")
                    if not value_name: value_name = res.get("tagValue", "")
                        
                    rows.append({
                        "subject_id": subject_id,
                        "region": region_key,
                        "tag": tag_name,
                        "value": value_name,
                        "count": res.get("count", 0),
                        "rate": res.get("rate", 0)
                    })
        if rows:
            df = pd.DataFrame(rows)
            df.to_excel(excel_filename, index=False)
            print(f"🎉 任务完美结束！Excel已保存为: {excel_filename}\n")
        else:
            print("⚠️ 未找到有效的打标数据，可能是因为该人群包暂无这些标签分布。")
    except Exception as e:
        print(f"❌ 转换为 Excel 时出错: {e}")

for name in TARGET_NAMES:
    print(f"🚀 开始处理: 【{name}】")

    sid = search_crowd_id(name)
    if not sid:
        continue
    snap_id = get_snapshot_id(sid, name)
    if not snap_id:
        continue
    dataset = get_dataset(snap_id, sid)
    if not dataset:
        continue

    json_to_excel(dataset, f"{name}_画像结果.xlsx")
    
    time.sleep(3) # 不同人群之间稍微停顿