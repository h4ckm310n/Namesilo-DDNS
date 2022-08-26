from lxml import etree
import requests
import time
import logging

# Modify to your own API key, domain and hosts
API_KEY = "12345"
DOMAIN = "abc.com"
HOSTS = ["aaa.abc.com", "bbb.abc.com", "ccc.abc.com"]

# Log path
LOG_PATH = "/path/to/namesilo_ddns.log"


class Namesilo:
    def __init__(self):
        self.key = API_KEY
        self.ip = ""
        self.domain = DOMAIN
        self.record_ids = []
        self.hosts = HOSTS
        self.logger = self.set_logger()
        self.session = requests.Session()
        self.start()

    def set_logger(self):
        logger = logging.getLogger('namesilo_ddns_logger')
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(LOG_PATH, mode='w')
        formatter = logging.Formatter("%(asctime)s %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger

    def start(self):
        self.get_record_ids()
        while(True):
            ip = self.get_ip()
            if ip == '':
                self.logger.info('Fail to get IP')
                time.sleep(300)
                continue

            if self.ip == ip:
                self.logger.info('IP not changed')
                time.sleep(1200)
                continue

            self.ip = ip
            self.logger.info('New IP address: ' + ip)
            for i in range(len(self.record_ids)):
                rrid = self.record_ids[i]
                host = self.hosts[i].replace('.'+self.domain, '')
                self.upd(rrid, host)

    def get_record_ids(self):
        url = 'https://www.namesilo.com/api/dnsListRecords'
        params = {
            'version': '1',
            'type': 'xml',
            'key': self.key,
            'domain': self.domain
        }
        while True:
            try:
                r = self.session.get(url, params=params)
            except:
                self.logger.info('Fail to get records')
                time.sleep(300)
            else:
                break
        tree = etree.HTML(r.text)
        for host in self.hosts:
            record_id = tree.xpath('//namesilo/reply/resource_record[host="' + host + '"]/record_id/text()')[0]
            self.logger.info(host + ' ' + record_id)
            self.record_ids.append(record_id)

    def get_ip(self):
        try:
            r = requests.get('http://api.ipify.org')
            return r.text
        except:
            return ''

    def upd(self, rrid, host):
        url = 'https://www.namesilo.com/api/dnsUpdateRecord'
        params = {
            'version': '1',
            'type': 'xml',
            'key': self.key,
            'rrid': rrid,
            'domain': self.domain,
            'rrhost': host,
            'rrvalue': self.ip
        }
        try:
            r = self.session.get(url, params=params)
        except:
            self.logger.info("Fail to update: " + host)
            self.ip = ""
        else:
            self.logger.info(r.text)


n = Namesilo()
