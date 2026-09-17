"""天气查询工具（无 Key 时返回确定性模拟数据，有 Key 时调用真实 API）"""
import random
from datetime import date, timedelta
from typing import Dict, Any, Optional

from app.config import settings
import logging

logger = logging.getLogger(__name__)

_WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
_WEATHER_TYPES = [
    {"type": "晴", "icon": "☀", "temp": (18, 28)},
    {"type": "多云", "icon": "⛅", "temp": (16, 25)},
    {"type": "阴", "icon": "☁", "temp": (14, 22)},
    {"type": "小雨", "icon": "🌧", "temp": (15, 23)},
]


class WeatherTool:
    """天气查询工具"""

    def get_weather(self, city: str, start_date: Optional[date] = None,
                    end_date: Optional[date] = None) -> Dict[str, Any]:
        if settings.WEATHER_API_KEY:
            return self._fetch_from_api(city, start_date, end_date)
        return self._get_mock_weather(city, start_date, end_date)

    def _fetch_from_api(self, city, start_date, end_date):
        # 预留真实 API 接入点（高德/和风等）；失败回退模拟
        try:
            import urllib.request, json
            url = f"https://api.weather.example.com/forecast?city={city}&key={settings.WEATHER_API_KEY}&days=7"
            with urllib.request.urlopen(url, timeout=10) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            logger.warning("天气 API 调用失败：%s，使用模拟数据", e)
            return self._get_mock_weather(city, start_date, end_date)

    def _get_mock_weather(self, city, start_date, end_date):
        base = start_date or date.today()
        num_days = 7 if not end_date else max(1, (end_date - base).days + 1)
        # 以城市名产生稳定种子，保证同城市结果一致（演示友好）
        seed = sum(ord(c) for c in city) or 1
        rng = random.Random(seed)
        forecasts = []
        for i in range(min(num_days, 14)):
            w = rng.choice(_WEATHER_TYPES)
            day = base + timedelta(days=i)
            forecasts.append({
                "date": day.isoformat(),
                "weekday": _WEEKDAYS[day.weekday()],
                "weather": w["type"],
                "icon": w["icon"],
                "temp_high": rng.randint(*w["temp"]),
                "temp_low": rng.randint(w["temp"][0] - 4, w["temp"][0]),
                "wind": f"{rng.randint(1, 3)}级",
                "pm25": rng.randint(20, 80),
            })
        return {
            "city": city,
            "forecasts": forecasts,
            "tips": self._generate_weather_tips(forecasts),
        }

    def _generate_weather_tips(self, forecasts):
        tips = []
        rainy = [f for f in forecasts if "雨" in f.get("weather", "")]
        if rainy:
            tips.append(f"行程中有 {len(rainy)} 天可能有雨，建议携带雨具。")
        all_temps = [f["temp_high"] for f in forecasts] + [f["temp_low"] for f in forecasts]
        avg_high = sum(all_temps) / len(all_temps)
        if avg_high > 30:
            tips.append("气温较高，注意防暑防晒，多补充水分。")
        elif avg_high < 15:
            tips.append("气温较低，建议携带外套和保暖衣物。")
        return " ".join(tips) if tips else "天气总体良好，适合出行。"


class WeatherToolLangChain:
    """LangChain 风格天气工具"""

    name = "get_weather"
    description = "查询天气预报。当用户输入某地某时间的天气，或需根据天气安排行程时使用。"

    def run(self, city: str, start_date: str = "", end_date: str = "") -> str:
        from app.utils.helpers import parse_flexible_date
        start = parse_flexible_date(start_date) if start_date else None
        end = parse_flexible_date(end_date) if end_date else None
        w = WeatherTool().get_weather(city, start, end)
        result = f"**{city} 天气预报：**\n\n"
        for d in w.get("forecasts", []):
            result += f"📅 {d['date']} ({d['weekday']})\n   {d['icon']} {d['weather']} 🌡 {d['temp_low']}°C ~ {d['temp_high']}°C\n\n"
        if w.get("tips"):
            result += f"\n💡 **出行建议：** {w['tips']}"
        return result
