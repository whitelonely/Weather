import logging

class NoStaticFilter(logging.Filter):
    """过滤掉静态资源的请求日志"""
    def filter(self, record):
        return 'GET /static/' not in record.getMessage()

logging.getLogger('werkzeug').addFilter(NoStaticFilter())