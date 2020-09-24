from lxml import etree
import requests
import time

API_KEY = "YOUR API KEY"
DOMAIN = "DOMAIN.COM"


class Namesilo:
    def __init__(self):
        self.key = API_KEY
        self.ip = ""
        self.domain = DOMAIN
        self.record_ids = []
        self.hosts = []
        self.session = requests.Session()
        self.start()

    def start(self):
        while(True):
            ip = self.lst()
            if self.ip == ip:
                time.sleep(3600)
                continue

            print('New ip address: ' + ip)
            for i in range(len(self.record_ids)):
                rrid = self.record_ids[i]
                host = self.hosts[i].replace('.'+self.domain, '')
                self.upd(rrid, host)

    def lst(self):
        url = 'https://www.namesilo.com/api/dnsListRecords'
        params = {
            'version': '1',
            'type': 'xml',
            'key': self.key,
            'domain': self.domain
        }
        r = self.session.get(url, params=params)
        tree = etree.HTML(r.text)
        ip = tree.xpath('//namesilo/request/ip/text()')[0]
        self.record_ids = tree.xpath('//namesilo/reply/resource_record[value="' + self.ip + '"]/record_id/text()')
        self.hosts = tree.xpath('//namesilo/reply/resource_record[value="' + self.ip + '"]/host/text()')
        return ip

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
        self.session.get(url, params=params)

n = Namesilo()
