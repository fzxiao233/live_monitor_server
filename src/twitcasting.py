import asyncio
import logging
import time

from config import config
from daemon import VideoDaemon
from tools import get_json


class Twitcasting(VideoDaemon):
    def __init__(self, target_id):
        super().__init__(target_id)
        self.logger = logging.getLogger('run.twitcasting')
        self.module = 'Twitcasting'

    async def live_info(self):
        live_js = await get_json(
            f"https://twitcasting.tv/streamserver.php?target={self.target_id}&mode=client")
        try:
            is_live = live_js['movie']['live']
        except KeyError:
            return {'Is_live': False}
        vid = str(live_js['movie']['id'])
        live_info = {"Is_live": is_live,
                     "Vid": vid}
        return live_info

    def get_hsl(self, live_info):
        # html = get(f"https://twitcasting.tv/{twitcasting_id}")
        # dom = etree.HTML(html)
        # title = dom.xpath('/html/body/div[3]/div[2]/div/div[2]/h2/span[3]/a/text()')[0]
        title = f"{self.target_id}#{live_info.get('Vid')}"
        ref = f"https://twitcasting.tv/{self.target_id}/metastream.m3u8"
        target = f"https://twitcasting.tv/{self.target_id}"
        date = time.strftime("%Y-%m-%d", time.localtime())
        return {'Title': title,
                'Ref': ref,
                'Target': target,
                'Date': date}

    async def check(self):
        while True:
            live_info = await self.live_info()
            if live_info.get('Is_live'):
                video_dict = self.get_hsl(live_info)
                video_dict['Provide'] = self.module
                video_dict['User'] = self.user_config['name']
                self.send_to_sub(video_dict)
            else:
                self.logger.info(f'{self.target_id}: Not found Live')
                self.set_no_live()
            await asyncio.sleep(config['sec'])
