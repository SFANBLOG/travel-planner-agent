"""种子旅行攻略 / 贴士（知识库 guides 集合）

用于 RAG 攻略检索，也作为规则引擎生成建议文案的来源。
"""
from typing import List, Dict, Any

GUIDES: List[Dict[str, Any]] = [
    dict(id="guide-bj-1", title="北京三日经典行程建议", source="TravelAI攻略库", url="",
         content="北京三日可安排：D1 天安门-故宫-景山-南锣鼓巷；D2 八达岭长城-鸟巢-水立方夜景；"
                 "D3 颐和园-圆明园或798艺术区。春秋最佳，故宫需提前预约，长城建议早班车前往避人流。"),
    dict(id="guide-sh-1", title="上海都市与江南水乡组合", source="TravelAI攻略库", url="",
         content="上海推荐外滩+陆家嘴看夜景、豫园品老城厢小吃、迪士尼亲子一日。时间充裕可半日游朱家角古镇。"
                 "地铁网络发达，下载Metro大都会扫码乘车。"),
    dict(id="guide-cd-1", title="成都慢生活美食地图", source="TravelAI攻略库", url="",
         content="成都主打熊猫基地（早去）、宽窄巷子与锦里小吃、武侯祠三国文化、都江堰一日。火锅与串串必尝，"
                 "辣度可要求微辣。春熙路/太古里购物，人民公园喝茶掏耳朵体验慢生活。"),
    dict(id="guide-hz-1", title="杭州西湖深度游", source="TravelAI攻略库", url="",
         content="西湖建议环湖慢游：断桥-白堤-苏堤-雷峰塔，体力好可登宝石山。灵隐寺需先购香花券。"
                 "龙井村春茶、河坊街小吃。最佳季节春（桃花）与秋（桂花）。"),
    dict(id="guide-xa-1", title="西安历史文化之旅", source="TravelAI攻略库", url="",
         content="西安核心：兵马俑（配华清宫一日）、古城墙骑行、大雁塔喷泉、回民街美食、陕西历史博物馆（免费需预约）。"
                 "肉夹馍、羊肉泡馍、凉皮不可错过。"),
    dict(id="guide-sy-1", title="三亚海岛度假指南", source="TravelAI攻略库", url="",
         content="三亚冬季最佳。亚龙湾/海棠湾高端度假，蜈支洲岛潜水，第一市场海鲜加工平价。注意防晒与台风季（7-9月）。"
                 "度假建议预留预算用于酒店与水上项目。"),
    dict(id="guide-budget-1", title="国内自由行预算控制技巧", source="TravelAI攻略库", url="",
         content="预算分配建议：交通30%、住宿30%、餐饮20%、门票+体验15%、应急5%。提前30天订机票更便宜，"
                 "景点套票与城市通票可省15-30%。美食街区替代景区餐饮更地道省钱。"),
    dict(id="guide-family-1", title="亲子游安排要点", source="TravelAI攻略库", url="",
         content="亲子游每天安排不超过3个景点，预留午休；优先主题乐园、动物园、科技馆、海滩等互动项目；"
                 "备好常用药品与防晒；行程节奏松弛，避免赶场。"),
    dict(id="guide-foodie-1", title="美食之旅如何吃得更地道", source="TravelAI攻略库", url="",
         content="美食游优先夜市、老字号与本地人排队的小店；善用大众点评看人均与招牌菜；每个城市列必吃清单；"
                 "把餐厅分散到每日行程中，避免连续重油。"),
    dict(id="guide-photo-1", title="摄影采风行程建议", source="TravelAI攻略库", url="",
         content="摄影行程重视黄金时刻（日出后/日落前1小时）与蓝调时刻；提前踩点机位；古城/古镇选清晨无人的巷弄；"
                 "高原湖泊注意防晒与高反。"),
]
