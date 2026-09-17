# -*- coding: utf-8 -*-
"""种子景点库（知识库初始数据）

覆盖多个热门目的地，字段对齐 spots 表 / RAG metadata。同时供规则引擎在 LLM 不可用时兜底。
坐标取自公开地图近似经纬度，仅用于演示路线距离估算。
"""
from typing import List, Dict, Any

# 所有出现过的城市（用于需求解析时的目的地识别）
CITIES: List[str] = [
    "北京", "上海", "成都", "杭州", "西安", "三亚", "重庆", "厦门", "丽江", "广州", "南京", "武汉",
]

SPOTS: List[Dict[str, Any]] = [
    dict(id="bj-gugong", name="故宫博物院", name_en="Forbidden City", city="北京", country="中国",
         category="历史古迹", latitude=39.9163, longitude=116.3972, address="北京市东城区景山前街4号",
         description="明清两代皇家宫殿，世界文化遗产，现存规模最大的木质结构古建筑群。", ticket_info={"price": 60, "type": "门票"}, rating=4.8, review_count=520000,
         recommend_duration=240, tags=["世界遗产", "必去", "历史"], opening_hours={"周一": "闭馆", "周二-周日": "08:30-17:00"}, best_season=["春", "秋"]),

    dict(id="bj-changcheng", name="八达岭长城", name_en="Great Wall (Badaling)", city="北京", country="中国",
         category="自然风光", latitude=40.359, longitude=116.02, address="北京市延庆区八达岭镇",
         description="万里长城最具代表性的一段，雄踞军都山间，登高望远气势恢宏。", ticket_info={"price": 40, "type": "门票"}, rating=4.7, review_count=380000,
         recommend_duration=240, tags=["世界遗产", "必去", "徒步"], opening_hours={"每日": "07:30-16:30"}, best_season=["春", "秋"]),

    dict(id="bj-yiheyuan", name="颐和园", name_en="Summer Palace", city="北京", country="中国",
         category="园林", latitude=39.9999, longitude=116.2755, address="北京市海淀区新建宫门路19号",
         description="清代皇家园林，以昆明湖、万寿山为骨架，融江南园林精巧与北方恢弘。", ticket_info={"price": 30, "type": "门票"}, rating=4.6, review_count=210000,
         recommend_duration=180, tags=["园林", "拍照", "历史"], opening_hours={"每日": "06:30-18:00"}, best_season=["春", "夏"]),

    dict(id="bj-tiananmen", name="天安门广场", name_en="Tiananmen Square", city="北京", country="中国",
         category="城市地标", latitude=39.9055, longitude=116.3976, address="北京市东城区长安街",
         description="世界最大的城市广场之一，见证诸多重大历史时刻，清晨可看升旗。", ticket_info={"price": 0, "type": "免费"}, rating=4.5, review_count=300000,
         recommend_duration=90, tags=["地标", "免费", "必去"], opening_hours={"每日": "05:00-22:00"}, best_season=["全年"]),

    dict(id="bj-nanluoguxiang", name="南锣鼓巷", name_en="Nanluoguxiang", city="北京", country="中国",
         category="美食街区", latitude=39.9372, longitude=116.403, address="北京市东城区南锣鼓巷",
         description="元大都遗留的胡同街区，文艺小店与京味小吃云集，适合闲逛。", ticket_info={"price": 0, "type": "免费"}, rating=4.3, review_count=150000,
         recommend_duration=120, tags=["美食", "拍照", "胡同"], opening_hours={"每日": "全天"}, best_season=["全年"]),

    dict(id="bj-798", name="798艺术区", name_en="798 Art Zone", city="北京", country="中国",
         category="艺术文化", latitude=39.9847, longitude=116.495, address="北京市朝阳区酒仙桥路2号",
         description="由旧工厂改造的当代艺术聚集地，画廊、展览与文创空间密集。", ticket_info={"price": 0, "type": "免费"}, rating=4.4, review_count=120000,
         recommend_duration=150, tags=["艺术", "拍照", "文艺"], opening_hours={"每日": "10:00-19:00"}, best_season=["全年"]),

    dict(id="bj-shichahai", name="什刹海", name_en="Shichahai", city="北京", country="中国",
         category="休闲", latitude=39.9408, longitude=116.383, address="北京市西城区什刹海",
         description="由前海、后海、西海组成的老北京水域，可划船、逛胡同、品酒吧。", ticket_info={"price": 0, "type": "免费"}, rating=4.3, review_count=98000,
         recommend_duration=120, tags=["休闲", "夜景", "胡同"], opening_hours={"每日": "全天"}, best_season=["夏", "秋"]),

    dict(id="bj-niaochao", name="鸟巢（国家体育场）", name_en="Bird's Nest", city="北京", country="中国",
         category="城市地标", latitude=39.9928, longitude=116.3964, address="北京市朝阳区国家体育场南路1号",
         description="2008奥运主会场，钢结构编织外形极具未来感，夜景灯光璀璨。", ticket_info={"price": 50, "type": "参观票"}, rating=4.4, review_count=160000,
         recommend_duration=90, tags=["地标", "夜景", "建筑"], opening_hours={"每日": "09:00-21:00"}, best_season=["全年"]),

    dict(id="sh-bund", name="外滩", name_en="The Bund", city="上海", country="中国",
         category="城市地标", latitude=31.2397, longitude=121.4905, address="上海市黄浦区中山东一路",
         description="黄浦江畔万国建筑博览群，对岸是陆家嘴天际线，夜景堪称一绝。", ticket_info={"price": 0, "type": "免费"}, rating=4.7, review_count=450000,
         recommend_duration=120, tags=["地标", "夜景", "必去"], opening_hours={"每日": "全天"}, best_season=["全年"]),

    dict(id="sh-lujiazui", name="陆家嘴", name_en="Lujiazui", city="上海", country="中国",
         category="城市地标", latitude=31.239, longitude=121.501, address="上海市浦东新区陆家嘴",
         description="东方明珠、上海中心、环球金融中心林立，现代都市丛林的代表。", ticket_info={"price": 0, "type": "免费"}, rating=4.6, review_count=200000,
         recommend_duration=150, tags=["地标", "夜景", "建筑"], opening_hours={"每日": "全天"}, best_season=["全年"]),

    dict(id="sh-yuyuan", name="豫园", name_en="Yu Garden", city="上海", country="中国",
         category="园林", latitude=31.227, longitude=121.492, address="上海市黄浦区安仁街218号",
         description="明代私人园林，亭台楼阁精巧，周边老城厢与城隍庙小吃林立。", ticket_info={"price": 40, "type": "门票"}, rating=4.5, review_count=180000,
         recommend_duration=120, tags=["园林", "历史", "美食"], opening_hours={"每日": "08:30-17:00"}, best_season=["春", "秋"]),

    dict(id="sh-nanjingrd", name="南京路步行街", name_en="Nanjing Road", city="上海", country="中国",
         category="商业街区", latitude=31.2336, longitude=121.479, address="上海市黄浦区南京东路",
         description="中华商业第一街，老字号与新商场并存，霓虹璀璨、人流如织。", ticket_info={"price": 0, "type": "免费"}, rating=4.4, review_count=260000,
         recommend_duration=120, tags=["购物", "夜景", "免费"], opening_hours={"每日": "全天"}, best_season=["全年"]),

    dict(id="sh-tianzifang", name="田子坊", name_en="Tianzifang", city="上海", country="中国",
         category="艺术文化", latitude=31.207, longitude=121.471, address="上海市黄浦区泰康路210弄",
         description="石库门里弄改造的文艺街区，手作小店、咖啡馆与画廊交织。", ticket_info={"price": 0, "type": "免费"}, rating=4.3, review_count=130000,
         recommend_duration=120, tags=["艺术", "拍照", "文艺"], opening_hours={"每日": "全天"}, best_season=["全年"]),

    dict(id="sh-disney", name="上海迪士尼度假区", name_en="Shanghai Disney Resort", city="上海", country="中国",
         category="主题乐园", latitude=31.145, longitude=121.667, address="上海市浦东新区川沙新镇",
         description="中国大陆首座迪士尼乐园，奇幻城堡与游乐项目适合全家出游。", ticket_info={"price": 475, "type": "门票"}, rating=4.6, review_count=300000,
         recommend_duration=480, tags=["亲子", "必去", "乐园"], opening_hours={"每日": "09:00-20:30"}, best_season=["春", "秋"]),

    dict(id="cd-kuanzhai", name="宽窄巷子", name_en="Kuanzhai Alley", city="成都", country="中国",
         category="美食街区", latitude=30.669, longitude=104.056, address="成都市青羊区同仁路",
         description="由宽巷子、窄巷子、井巷子组成的清式古街区，茶馆与小吃云集。", ticket_info={"price": 0, "type": "免费"}, rating=4.5, review_count=320000,
         recommend_duration=150, tags=["美食", "拍照", "免费"], opening_hours={"每日": "全天"}, best_season=["全年"]),

    dict(id="cd-jinli", name="锦里", name_en="Jinli Ancient Street", city="成都", country="中国",
         category="美食街区", latitude=30.641, longitude=104.043, address="成都市武侯区武侯祠大街231号",
         description="川西风情古街，三大炮、糖油果子等地道小吃与民俗表演不断。", ticket_info={"price": 0, "type": "免费"}, rating=4.5, review_count=280000,
         recommend_duration=120, tags=["美食", "历史", "免费"], opening_hours={"每日": "全天"}, best_season=["全年"]),

    dict(id="cd-wuhou", name="武侯祠", name_en="Wuhou Shrine", city="成都", country="中国",
         category="历史古迹", latitude=30.642, longitude=104.044, address="成都市武侯区武侯祠大街231号",
         description="中国唯一的君臣合祀祠庙，纪念诸葛亮与蜀汉君臣，红墙竹影。", ticket_info={"price": 50, "type": "门票"}, rating=4.6, review_count=200000,
         recommend_duration=120, tags=["历史", "必去", "园林"], opening_hours={"每日": "08:00-21:00"}, best_season=["春", "秋"]),

    dict(id="cd-panda", name="大熊猫繁育研究基地", name_en="Chengdu Panda Base", city="成都", country="中国",
         category="自然风光", latitude=30.734, longitude=104.146, address="成都市成华区熊猫大道1375号",
         description="近距离观赏憨态可掬的大熊猫与幼崽，竹林环绕、生态优美。", ticket_info={"price": 55, "type": "门票"}, rating=4.7, review_count=350000,
         recommend_duration=180, tags=["亲子", "必去", "自然"], opening_hours={"每日": "07:30-18:00"}, best_season=["春", "秋"]),

    dict(id="cd-dujiangyan", name="都江堰", name_en="Dujiangyan Irrigation", city="成都", country="中国",
         category="历史古迹", latitude=31.004, longitude=103.616, address="成都市都江堰市公园路",
         description="战国时期大型水利工程，至今仍在灌溉成都平原，世界文化遗产。", ticket_info={"price": 80, "type": "门票"}, rating=4.6, review_count=150000,
         recommend_duration=180, tags=["世界遗产", "历史", "自然"], opening_hours={"每日": "08:00-17:30"}, best_season=["春", "秋"]),

    dict(id="cd-chunxi", name="春熙路", name_en="Chunxi Road", city="成都", country="中国",
         category="商业街区", latitude=30.658, longitude=104.081, address="成都市锦江区春熙路",
         description="成都最繁华的商业中心，太古里潮牌与地道火锅近在咫尺。", ticket_info={"price": 0, "type": "免费"}, rating=4.4, review_count=240000,
         recommend_duration=120, tags=["购物", "美食", "免费"], opening_hours={"每日": "全天"}, best_season=["全年"]),

    dict(id="hz-westlake", name="西湖", name_en="West Lake", city="杭州", country="中国",
         category="自然风光", latitude=30.259, longitude=120.149, address="杭州市西湖区龙井路1号",
         description="世界文化遗产，三面云山一面城，断桥残雪、苏堤春晓名扬天下。", ticket_info={"price": 0, "type": "免费"}, rating=4.8, review_count=600000,
         recommend_duration=240, tags=["世界遗产", "必去", "免费"], opening_hours={"每日": "全天"}, best_season=["春", "秋"]),

    dict(id="hz-lingyin", name="灵隐寺", name_en="Lingyin Temple", city="杭州", country="中国",
         category="宗教文化", latitude=30.241, longitude=120.099, address="杭州市西湖区法云弄1号",
         description="千年古刹，背靠北高峰，飞来峰石刻造像精美，香火鼎盛。", ticket_info={"price": 75, "type": "门票"}, rating=4.6, review_count=220000,
         recommend_duration=150, tags=["宗教", "历史", "必去"], opening_hours={"每日": "07:00-18:00"}, best_season=["春", "秋"]),

    dict(id="hz-xixi", name="西溪湿地", name_en="Xixi Wetland", city="杭州", country="中国",
         category="自然风光", latitude=30.267, longitude=120.077, address="杭州市西湖区天目山路518号",
         description="城市湿地秘境，芦苇摇曳、水网交错，秋雪庵芦花胜景宜人。", ticket_info={"price": 80, "type": "门票"}, rating=4.5, review_count=120000,
         recommend_duration=180, tags=["自然", "拍照", "休闲"], opening_hours={"每日": "08:00-17:30"}, best_season=["春", "秋"]),

    dict(id="hz-songcheng", name="宋城", name_en="Songcheng", city="杭州", country="中国",
         category="主题乐园", latitude=30.183, longitude=120.066, address="杭州市西湖区之江路148号",
         description="以《宋城千古情》演出闻名，复原宋代市井，沉浸式演艺体验。", ticket_info={"price": 320, "type": "演出票"}, rating=4.5, review_count=180000,
         recommend_duration=240, tags=["演出", "亲子", "必去"], opening_hours={"每日": "09:30-21:00"}, best_season=["全年"]),

    dict(id="hz-hefang", name="河坊街", name_en="Hefang Street", city="杭州", country="中国",
         category="美食街区", latitude=30.241, longitude=120.168, address="杭州市上城区河坊街",
         description="清河坊历史街区，胡庆余堂与各类杭州老字号、街头小吃汇聚。", ticket_info={"price": 0, "type": "免费"}, rating=4.3, review_count=140000,
         recommend_duration=120, tags=["美食", "历史", "免费"], opening_hours={"每日": "全天"}, best_season=["全年"]),

    dict(id="hz-qiandao", name="千岛湖", name_en="Qiandao Lake", city="杭州", country="中国",
         category="自然风光", latitude=29.605, longitude=119.039, address="杭州市淳安县千岛湖镇",
         description="人工湖群岛星罗棋布，水质清冽，游船、骑行与农家乐皆宜。", ticket_info={"price": 130, "type": "门票"}, rating=4.5, review_count=160000,
         recommend_duration=300, tags=["自然", "亲子", "休闲"], opening_hours={"每日": "08:00-17:00"}, best_season=["夏", "秋"]),

    dict(id="xa-bingmayong", name="秦始皇兵马俑", name_en="Terracotta Army", city="西安", country="中国",
         category="历史古迹", latitude=34.385, longitude=109.278, address="西安市临潼区秦陵北路",
         description="世界第八大奇迹，千军俑阵栩栩如生，再现秦帝国军容。", ticket_info={"price": 120, "type": "门票"}, rating=4.8, review_count=480000,
         recommend_duration=180, tags=["世界遗产", "必去", "历史"], opening_hours={"每日": "08:30-17:00"}, best_season=["春", "秋"]),

    dict(id="xa-dayan", name="大雁塔", name_en="Giant Wild Goose Pagoda", city="西安", country="中国",
         category="历史古迹", latitude=34.218, longitude=108.964, address="西安市雁塔区雁塔南路",
         description="唐代佛塔，玄奘译经之地，北广场音乐喷泉与夜景交相辉映。", ticket_info={"price": 50, "type": "门票"}, rating=4.6, review_count=260000,
         recommend_duration=120, tags=["历史", "地标", "必去"], opening_hours={"每日": "08:00-21:30"}, best_season=["春", "秋"]),

    dict(id="xa-chengqiang", name="西安城墙", name_en="Xi'an City Wall", city="西安", country="中国",
         category="历史古迹", latitude=34.258, longitude=108.948, address="西安市碑林区南大街",
         description="中国现存最完整的古代城垣，可骑行环城，俯瞰古城格局。", ticket_info={"price": 54, "type": "门票"}, rating=4.6, review_count=230000,
         recommend_duration=120, tags=["历史", "必去", "骑行"], opening_hours={"每日": "08:00-22:00"}, best_season=["春", "秋"]),

    dict(id="xa-huimin", name="回民街", name_en="Muslim Quarter", city="西安", country="中国",
         category="美食街区", latitude=34.262, longitude=108.954, address="西安市莲湖区北院门",
         description="西安美食核心区，肉夹馍、泡馍、凉皮香气四溢，烟火气十足。", ticket_info={"price": 0, "type": "免费"}, rating=4.5, review_count=280000,
         recommend_duration=120, tags=["美食", "免费", "必去"], opening_hours={"每日": "全天"}, best_season=["全年"]),

    dict(id="xa-huaqing", name="华清宫", name_en="Huaqing Palace", city="西安", country="中国",
         category="历史古迹", latitude=34.366, longitude=109.286, address="西安市临潼区华清路",
         description="唐皇家温泉行宫，《长恨歌》实景演出所在地。", ticket_info={"price": 120, "type": "门票"}, rating=4.5, review_count=110000,
         recommend_duration=150, tags=["历史", "演出", "温泉"], opening_hours={"每日": "07:30-18:00"}, best_season=["春", "秋"]),

    dict(id="xa-shaanxi", name="陕西历史博物馆", name_en="Shaanxi History Museum", city="西安", country="中国",
         category="博物馆", latitude=34.225, longitude=108.958, address="西安市雁塔区小寨东路91号",
         description="华夏宝库，周秦汉唐珍宝荟萃，需提前预约。", ticket_info={"price": 0, "type": "免费"}, rating=4.7, review_count=200000,
         recommend_duration=180, tags=["博物馆", "免费", "必去"], opening_hours={"周二-周日": "08:30-18:00"}, best_season=["全年"]),

    dict(id="sy-yalongwan", name="亚龙湾", name_en="Yalong Bay", city="三亚", country="中国",
         category="海滩", latitude=18.219, longitude=109.647, address="三亚市吉阳区亚龙湾",
         description="天下第一湾，沙质细腻、海水清澈，高端度假酒店云集。", ticket_info={"price": 0, "type": "免费"}, rating=4.7, review_count=200000,
         recommend_duration=240, tags=["海滩", "度假", "亲子"], opening_hours={"每日": "全天"}, best_season=["冬", "春"]),

    dict(id="sy-tianya", name="天涯海角", name_en="Tianya Haijiao", city="三亚", country="中国",
         category="自然风光", latitude=18.298, longitude=109.548, address="三亚市天涯区天涯海角",
         description="海滨巨石镌刻天涯海角，浪漫与诗意的象征。", ticket_info={"price": 68, "type": "门票"}, rating=4.4, review_count=180000,
         recommend_duration=120, tags=["海滩", "浪漫", "地标"], opening_hours={"每日": "07:30-18:00"}, best_season=["冬"]),

    dict(id="sy-wuzhizhou", name="蜈支洲岛", name_en="Wuzhizhou Island", city="三亚", country="中国",
         category="海岛", latitude=18.32, longitude=109.77, address="三亚市海棠区蜈支洲岛",
         description="潜水胜地，海水能见度极高，摩托艇、海底漫步项目丰富。", ticket_info={"price": 144, "type": "门票+船票"}, rating=4.6, review_count=150000,
         recommend_duration=300, tags=["海岛", "潜水", "情侣"], opening_hours={"每日": "08:00-17:30"}, best_season=["冬", "春"]),

    dict(id="sy-nanshan", name="南山文化旅游区", name_en="Nanshan Culture Park", city="三亚", country="中国",
         category="宗教文化", latitude=18.297, longitude=109.21, address="三亚市崖州区南山",
         description="108米海上观音圣像庄严，佛教文化主题园区。", ticket_info={"price": 121, "type": "门票"}, rating=4.5, review_count=90000,
         recommend_duration=180, tags=["宗教", "文化", "海滨"], opening_hours={"每日": "08:00-17:30"}, best_season=["冬"]),

    dict(id="sy-dadonghai", name="大东海", name_en="Dadonghai", city="三亚", country="中国",
         category="海滩", latitude=18.238, longitude=109.583, address="三亚市吉阳区大东海",
         description="市区最近的海湾，冬泳胜地，夜生活丰富。", ticket_info={"price": 0, "type": "免费"}, rating=4.3, review_count=120000,
         recommend_duration=180, tags=["海滩", "夜景", "免费"], opening_hours={"每日": "全天"}, best_season=["冬"]),

    dict(id="sy-firstmarket", name="第一市场", name_en="First Market", city="三亚", country="中国",
         category="美食街区", latitude=18.252, longitude=109.51, address="三亚市天涯区新民街",
         description="海鲜加工一条街，现捞现做，平价又鲜活。", ticket_info={"price": 0, "type": "免费"}, rating=4.4, review_count=80000,
         recommend_duration=120, tags=["海鲜", "美食", "平价"], opening_hours={"每日": "全天"}, best_season=["冬"]),

    dict(id="cq-hongya", name="洪崖洞", name_en="Hongyadong", city="重庆", country="中国",
         category="城市地标", latitude=29.563, longitude=106.578, address="重庆市渝中区嘉滨路88号",
         description="依山就势的吊脚楼群，夜景似千与千寻梦境。", ticket_info={"price": 0, "type": "免费"}, rating=4.6, review_count=350000,
         recommend_duration=150, tags=["夜景", "地标", "必去"], opening_hours={"每日": "全天"}, best_season=["全年"]),

    dict(id="cq-jiefangbei", name="解放碑", name_en="Jiefangbei", city="重庆", country="中国",
         category="城市地标", latitude=29.559, longitude=106.577, address="重庆市渝中区解放碑步行街",
         description="重庆中央商务区核心，抗战胜利纪功碑与现代商圈交融。", ticket_info={"price": 0, "type": "免费"}, rating=4.4, review_count=220000,
         recommend_duration=120, tags=["地标", "购物", "免费"], opening_hours={"每日": "全天"}, best_season=["全年"]),

    dict(id="cq-ciqikou", name="磁器口古镇", name_en="Ciqikou", city="重庆", country="中国",
         category="历史古迹", latitude=29.579, longitude=106.456, address="重庆市沙坪坝区磁器口古镇",
         description="嘉陵江畔千年古镇，陈麻花、酸辣粉与巴渝民俗沿街可见。", ticket_info={"price": 0, "type": "免费"}, rating=4.3, review_count=180000,
         recommend_duration=150, tags=["历史", "美食", "免费"], opening_hours={"每日": "全天"}, best_season=["全年"]),

    dict(id="cq-cable", name="长江索道", name_en="Yangtze River Cableway", city="重庆", country="中国",
         category="城市体验", latitude=29.561, longitude=106.588, address="重庆市渝中区新华路",
         description="空中客车横渡长江，俯瞰两江交汇与山城立体交通。", ticket_info={"price": 30, "type": "单程票"}, rating=4.5, review_count=160000,
         recommend_duration=60, tags=["地标", "体验", "必去"], opening_hours={"每日": "07:30-22:30"}, best_season=["全年"]),

    dict(id="cq-liziba", name="李子坝轻轨站", name_en="Liziba Station", city="重庆", country="中国",
         category="城市地标", latitude=29.546, longitude=106.536, address="重庆市渝中区李子坝",
         description="轻轨穿楼而过的魔幻名场面，山城立体交通的网红打卡地。", ticket_info={"price": 0, "type": "免费"}, rating=4.4, review_count=120000,
         recommend_duration=60, tags=["地标", "拍照", "免费"], opening_hours={"每日": "全天"}, best_season=["全年"]),

    dict(id="cq-wulong", name="武隆天生三桥", name_en="Wulong Tiankeng", city="重庆", country="中国",
         category="自然风光", latitude=29.324, longitude=107.755, address="重庆市武隆区仙女山镇",
         description="喀斯特天坑地缝奇观，《变形金刚》取景地，气势磅礴。", ticket_info={"price": 95, "type": "门票"}, rating=4.6, review_count=130000,
         recommend_duration=240, tags=["自然", "世界遗产", "徒步"], opening_hours={"每日": "08:00-17:00"}, best_season=["春", "秋"]),

    dict(id="xm-gulangyu", name="鼓浪屿", name_en="Gulangyu", city="厦门", country="中国",
         category="海岛", latitude=24.447, longitude=118.067, address="厦门市思明区鼓浪屿",
         description="万国建筑博览岛，钢琴之岛，琴声海风与老别墅相映。", ticket_info={"price": 50, "type": "船票+门票"}, rating=4.6, review_count=320000,
         recommend_duration=300, tags=["海岛", "必去", "拍照"], opening_hours={"每日": "全天"}, best_season=["春", "秋"]),

    dict(id="xm-nanputuo", name="南普陀寺", name_en="Nanputuo Temple", city="厦门", country="中国",
         category="宗教文化", latitude=24.438, longitude=118.095, address="厦门市思明区思明南路515号",
         description="闽南名刹，依山面海，素斋与五老峰景致宜人。", ticket_info={"price": 0, "type": "免费"}, rating=4.6, review_count=180000,
         recommend_duration=120, tags=["宗教", "免费", "必去"], opening_hours={"每日": "08:00-17:00"}, best_season=["全年"]),

    dict(id="xm-xmu", name="厦门大学", name_en="Xiamen University", city="厦门", country="中国",
         category="校园", latitude=24.431, longitude=118.097, address="厦门市思明区思明南路422号",
         description="最美大学之一，芙蓉隧道涂鸦、上弦场与白城沙滩相连。", ticket_info={"price": 0, "type": "免费"}, rating=4.5, review_count=200000,
         recommend_duration=150, tags=["校园", "拍照", "免费"], opening_hours={"需预约": "限流开放"}, best_season=["全年"]),

    dict(id="xm-huandao", name="环岛路", name_en="Island Ring Road", city="厦门", country="中国",
         category="自然风光", latitude=24.449, longitude=118.103, address="厦门市思明区环岛路",
         description="海滨骑行画廊，椰风寨至曾厝垵一段海景绝佳。", ticket_info={"price": 0, "type": "免费"}, rating=4.4, review_count=90000,
         recommend_duration=120, tags=["骑行", "海滩", "免费"], opening_hours={"每日": "全天"}, best_season=["春", "秋"]),

    dict(id="xm-zengcuoan", name="曾厝垵", name_en="Zengcuo'an", city="厦门", country="中国",
         category="美食街区", latitude=24.431, longitude=118.107, address="厦门市思明区曾厝垵",
         description="渔村文艺小镇，民宿、小吃与手作小店密集，文艺青年聚集。", ticket_info={"price": 0, "type": "免费"}, rating=4.3, review_count=130000,
         recommend_duration=120, tags=["美食", "文艺", "免费"], opening_hours={"每日": "全天"}, best_season=["全年"]),

    dict(id="xm-jimei", name="集美学村", name_en="Jimei School Village", city="厦门", country="中国",
         category="历史古迹", latitude=24.572, longitude=118.094, address="厦门市集美区鳌园路",
         description="陈嘉庚倾资兴学之地，嘉庚建筑中西合璧，龙舟池畔风光秀。", ticket_info={"price": 0, "type": "免费"}, rating=4.4, review_count=80000,
         recommend_duration=150, tags=["历史", "建筑", "免费"], opening_hours={"每日": "全天"}, best_season=["全年"]),

    dict(id="lj-oldtown", name="丽江古城", name_en="Lijiang Old Town", city="丽江", country="中国",
         category="历史古迹", latitude=26.872, longitude=100.229, address="丽江市古城区纳西族自治县",
         description="世界文化遗产，纳西民居依水而建，四方街夜色迷人。", ticket_info={"price": 0, "type": "免费"}, rating=4.6, review_count=300000,
         recommend_duration=240, tags=["世界遗产", "必去", "古城"], opening_hours={"每日": "全天"}, best_season=["春", "秋"]),

    dict(id="lj-yulong", name="玉龙雪山", name_en="Jade Dragon Snow Mountain", city="丽江", country="中国",
         category="自然风光", latitude=27.099, longitude=100.178, address="丽江市玉龙县雪山景区",
         description="纳西神山，冰川公园与蓝月谷如仙境，索道登临雪线。", ticket_info={"price": 100, "type": "门票+索道"}, rating=4.6, review_count=200000,
         recommend_duration=300, tags=["自然", "必去", "雪山"], opening_hours={"每日": "07:30-17:00"}, best_season=["春", "冬"]),

    dict(id="lj-lugu", name="泸沽湖", name_en="Lugu Lake", city="丽江", country="中国",
         category="自然风光", latitude=27.699, longitude=100.775, address="丽江市宁蒗县泸沽湖镇",
         description="高原明珠，摩梭母系文化走婚桥，猪槽船荡漾碧波。", ticket_info={"price": 70, "type": "门票"}, rating=4.6, review_count=120000,
         recommend_duration=360, tags=["自然", "湖泊", "文化"], opening_hours={"每日": "全天"}, best_season=["春", "秋"]),

    dict(id="lj-shuhe", name="束河古镇", name_en="Shuhe Old Town", city="丽江", country="中国",
         category="历史古迹", latitude=26.883, longitude=100.197, address="丽江市古城区束河古镇",
         description="比大研更清静的纳西古镇，茶马古道遗存，溪流穿巷。", ticket_info={"price": 0, "type": "免费"}, rating=4.4, review_count=90000,
         recommend_duration=180, tags=["古城", "休闲", "免费"], opening_hours={"每日": "全天"}, best_season=["春", "秋"]),

    dict(id="lj-lashihai", name="拉市海", name_en="Lashi Lake", city="丽江", country="中国",
         category="自然风光", latitude=26.83, longitude=100.18, address="丽江市玉龙县拉市海",
         description="高原湿地候鸟栖息地，骑马走茶马古道、划船观鸟。", ticket_info={"price": 0, "type": "免费"}, rating=4.3, review_count=70000,
         recommend_duration=180, tags=["自然", "骑马", "休闲"], opening_hours={"每日": "全天"}, best_season=["春", "秋"]),

    dict(id="lj-mufu", name="木府", name_en="Mu's Residence", city="丽江", country="中国",
         category="历史古迹", latitude=26.871, longitude=100.232, address="丽江市古城区光义街",
         description="纳西土司王府，徐霞客赞其宫室之丽拟于王者，轴对称院落。", ticket_info={"price": 40, "type": "门票"}, rating=4.4, review_count=80000,
         recommend_duration=120, tags=["历史", "建筑", "必去"], opening_hours={"每日": "08:30-17:30"}, best_season=["全年"]),

    dict(id="gz-canton", name="广州塔", name_en="Canton Tower", city="广州", country="中国",
         category="城市地标", latitude=23.106, longitude=113.324, address="广州市海珠区阅江西路222号",
         description="小蛮腰地标，云端观光与摩天轮俯瞰珠江新城夜景。", ticket_info={"price": 150, "type": "观光票"}, rating=4.6, review_count=300000,
         recommend_duration=120, tags=["地标", "夜景", "必去"], opening_hours={"每日": "09:30-22:30"}, best_season=["全年"]),

    dict(id="gz-chenjiaci", name="陈家祠", name_en="Chen Clan Academy", city="广州", country="中国",
         category="历史古迹", latitude=23.128, longitude=113.248, address="广州市荔湾区中山七路恩龙里34号",
         description="岭南建筑装饰巅峰，砖雕木雕灰塑精美绝伦。", ticket_info={"price": 10, "type": "门票"}, rating=4.6, review_count=150000,
         recommend_duration=120, tags=["历史", "建筑", "必去"], opening_hours={"每日": "08:30-17:30"}, best_season=["全年"]),

    dict(id="gz-shamian", name="沙面岛", name_en="Shamian Island", city="广州", country="中国",
         category="历史古迹", latitude=23.108, longitude=113.243, address="广州市荔湾区沙面岛",
         description="珠江中的欧陆风情岛，租界老建筑与榕荫大道恬静。", ticket_info={"price": 0, "type": "免费"}, rating=4.5, review_count=120000,
         recommend_duration=120, tags=["历史", "拍照", "免费"], opening_hours={"每日": "全天"}, best_season=["全年"]),

    dict(id="gz-chimelong", name="长隆欢乐世界", name_en="Chimelong Paradise", city="广州", country="中国",
         category="主题乐园", latitude=23.006, longitude=113.324, address="广州市番禺区汉溪大道东299号",
         description="顶尖游乐设施与长隆野生动物世界相邻，亲子狂欢地。", ticket_info={"price": 250, "type": "门票"}, rating=4.6, review_count=220000,
         recommend_duration=480, tags=["亲子", "乐园", "必去"], opening_hours={"每日": "09:30-18:00"}, best_season=["全年"]),

    dict(id="gz-beijingrd", name="北京路步行街", name_en="Beijing Road", city="广州", country="中国",
         category="商业街区", latitude=23.123, longitude=113.272, address="广州市越秀区北京路",
         description="千年古道遗址之上的商圈，老字号与骑楼霓虹交织。", ticket_info={"price": 0, "type": "免费"}, rating=4.3, review_count=160000,
         recommend_duration=120, tags=["购物", "美食", "免费"], opening_hours={"每日": "全天"}, best_season=["全年"]),

    dict(id="gz-baiyun", name="白云山", name_en="Baiyun Mountain", city="广州", country="中国",
         category="自然风光", latitude=23.184, longitude=113.297, address="广州市白云区广园中路",
         description="羊城第一秀，摩星岭俯瞰全城，缆车与步道皆宜。", ticket_info={"price": 5, "type": "门票"}, rating=4.5, review_count=140000,
         recommend_duration=240, tags=["自然", "徒步", "休闲"], opening_hours={"每日": "06:00-21:00"}, best_season=["春", "秋"]),

    dict(id="nj-zhongshan", name="中山陵", name_en="Sun Yat-sen Mausoleum", city="南京", country="中国",
         category="历史古迹", latitude=32.063, longitude=118.849, address="南京市玄武区石象路7号",
         description="国父孙中山陵寝，392级台阶寓意深远，陵园肃穆壮阔。", ticket_info={"price": 0, "type": "免费"}, rating=4.7, review_count=260000,
         recommend_duration=180, tags=["历史", "必去", "免费"], opening_hours={"每日": "08:30-17:00"}, best_season=["春", "秋"]),

    dict(id="nj-fuzimiao", name="夫子庙", name_en="Confucius Temple", city="南京", country="中国",
         category="历史古迹", latitude=32.028, longitude=118.789, address="南京市秦淮区贡院街",
         description="秦淮风光核心，江南贡院与画舫灯影，小吃琳琅满目。", ticket_info={"price": 0, "type": "免费"}, rating=4.5, review_count=280000,
         recommend_duration=150, tags=["历史", "美食", "夜景"], opening_hours={"每日": "全天"}, best_season=["全年"]),

    dict(id="nj-mingxiao", name="明孝陵", name_en="Ming Xiaoling", city="南京", country="中国",
         category="历史古迹", latitude=32.045, longitude=118.844, address="南京市玄武区石象路7号",
         description="明太祖朱元璋陵，神道石像生蜿蜒，世界文化遗产。", ticket_info={"price": 70, "type": "门票"}, rating=4.6, review_count=160000,
         recommend_duration=150, tags=["世界遗产", "历史", "必去"], opening_hours={"每日": "06:30-18:00"}, best_season=["春", "秋"]),

    dict(id="nj-zongtong", name="总统府", name_en="Presidential Palace", city="南京", country="中国",
         category="历史古迹", latitude=32.042, longitude=118.796, address="南京市玄武区长江路292号",
         description="近代史缩影，江南园林与西式建筑并存，见证民国风云。", ticket_info={"price": 35, "type": "门票"}, rating=4.5, review_count=150000,
         recommend_duration=120, tags=["历史", "必去", "建筑"], opening_hours={"每日": "08:30-18:00"}, best_season=["全年"]),

    dict(id="nj-xuanwu", name="玄武湖", name_en="Xuanwu Lake", city="南京", country="中国",
         category="自然风光", latitude=32.068, longitude=118.795, address="南京市玄武区玄武巷1号",
         description="六朝皇家园林湖泊，五洲相连，城墙辉映、荷香十里。", ticket_info={"price": 0, "type": "免费"}, rating=4.5, review_count=170000,
         recommend_duration=150, tags=["自然", "免费", "休闲"], opening_hours={"每日": "06:00-21:00"}, best_season=["春", "秋"]),

    dict(id="nj-bowu", name="南京博物院", name_en="Nanjing Museum", city="南京", country="中国",
         category="博物馆", latitude=32.044, longitude=118.837, address="南京市玄武区中山东路321号",
         description="中国三大博物馆之一，民国馆复原老南京街景，藏品丰沛。", ticket_info={"price": 0, "type": "免费"}, rating=4.7, review_count=200000,
         recommend_duration=180, tags=["博物馆", "免费", "必去"], opening_hours={"周二-周日": "09:00-17:00"}, best_season=["全年"]),

    dict(id="wh-huanghe", name="黄鹤楼", name_en="Yellow Crane Tower", city="武汉", country="中国",
         category="历史古迹", latitude=30.546, longitude=114.306, address="武汉市武昌区蛇山西山坡特1号",
         description="江南三大名楼之首，崔颢题诗天下闻，登楼俯瞰长江。", ticket_info={"price": 70, "type": "门票"}, rating=4.6, review_count=300000,
         recommend_duration=120, tags=["历史", "必去", "地标"], opening_hours={"每日": "08:30-17:00"}, best_season=["春", "秋"]),

    dict(id="wh-donghu", name="东湖", name_en="East Lake", city="武汉", country="中国",
         category="自然风光", latitude=30.563, longitude=114.391, address="武汉市武昌区东湖路",
         description="中国最大城中湖，绿道骑行、樱园与磨山楚风尽显。", ticket_info={"price": 0, "type": "免费"}, rating=4.5, review_count=200000,
         recommend_duration=240, tags=["自然", "免费", "骑行"], opening_hours={"每日": "全天"}, best_season=["春"]),

    dict(id="wh-hubu", name="户部巷", name_en="Hubu Lane", city="武汉", country="中国",
         category="美食街区", latitude=30.545, longitude=114.307, address="武汉市武昌区自由路",
         description="武汉早点第一巷，热干面、豆皮、糊汤粉过早必打卡。", ticket_info={"price": 0, "type": "免费"}, rating=4.4, review_count=160000,
         recommend_duration=90, tags=["美食", "免费", "必去"], opening_hours={"每日": "全天"}, best_season=["全年"]),

    dict(id="wh-bridge", name="武汉长江大桥", name_en="Wuhan Yangtze Bridge", city="武汉", country="中国",
         category="城市地标", latitude=30.552, longitude=114.295, address="武汉市武昌区临江大道",
         description="万里长江第一桥，双层公路铁路，桥头堡俯瞰两江四岸。", ticket_info={"price": 0, "type": "免费"}, rating=4.5, review_count=140000,
         recommend_duration=90, tags=["地标", "建筑", "免费"], opening_hours={"每日": "全天"}, best_season=["全年"]),

    dict(id="wh-guiyuan", name="归元寺", name_en="Guiyuan Temple", city="武汉", country="中国",
         category="宗教文化", latitude=30.542, longitude=114.279, address="武汉市汉阳区归元寺路20号",
         description="湖北名刹，五百罗汉栩栩如生，数罗汉问前程民俗。", ticket_info={"price": 10, "type": "门票"}, rating=4.5, review_count=110000,
         recommend_duration=120, tags=["宗教", "历史", "必去"], opening_hours={"每日": "08:00-17:00"}, best_season=["全年"]),

    dict(id="wh-hubei", name="湖北省博物馆", name_en="Hubei Museum", city="武汉", country="中国",
         category="博物馆", latitude=30.561, longitude=114.362, address="武汉市武昌区东湖路160号",
         description="曾侯乙编钟、越王勾践剑惊艳世人，楚文化宝库。", ticket_info={"price": 0, "type": "免费"}, rating=4.7, review_count=180000,
         recommend_duration=180, tags=["博物馆", "免费", "必去"], opening_hours={"周二-周日": "09:00-17:00"}, best_season=["全年"]),

]
