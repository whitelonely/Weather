import logging

class NoStaticFilter(logging.Filter):
    """过滤掉静态资源的请求日志"""
    def filter(self, record):
        return 'GET /static/' not in record.getMessage()

logging.getLogger('werkzeug').addFilter(NoStaticFilter())

CITY_NAME_MAP = {
    'Beijing': '北京',
    'Shanghai': '上海',
    'Guangzhou': '广州',
    'Shenzhen': '深圳',
    'Chengdu': '成都',
    'Hangzhou': '杭州',
    'Wuhan': '武汉',
    'Nanjing': '南京',
    'Chongqing': '重庆',
    'Tianjin': '天津',
    'Xi\'an': '西安',
    'Changsha': '长沙',
    'Kunming': '昆明',
    'Xiamen': '厦门',
    'Qingdao': '青岛',
    'Dalian': '大连',
    'Suzhou': '苏州',
    'Ningbo': '宁波',
    'Fuzhou': '福州',
    'Zhengzhou': '郑州',
    'Shenyang': '沈阳',
    'Harbin': '哈尔滨',
    'Changchun': '长春',
    'Shijiazhuang': '石家庄',
    'Taiyuan': '太原',
    'Jinan': '济南',
    'Hefei': '合肥',
    'Nanchang': '南昌',
    'Guiyang': '贵阳',
    'Lanzhou': '兰州',   # 别忘了你自己的城市
    'Haikou': '海口',
    'Urumqi': '乌鲁木齐',
    'Lhasa': '拉萨',
    'Xining': '西宁',
    'Yinchuan': '银川',
    'Hohhot': '呼和浩特',
    'Nanning': '南宁',
}