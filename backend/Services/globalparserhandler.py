import asyncio
import datetime

from fastapi import HTTPException, BackgroundTasks

from Services.rada_parser import parse_rada


class GlobalParserHandler:
    def __init__(self):
        self.button_disabled = False
        self.last_disable_time = None

    async def re_enable_button_after_4_hours(self):
        await asyncio.sleep(4 * 60 * 60)  # 4 hours
        self.button_disabled = False
        self.last_disable_time = None

    async def globalparserhandler(self, background_tasks: BackgroundTasks):
        if self.button_disabled:
            raise HTTPException(status_code=400, detail="Parse in progress")
        await parse_rada()
        self.button_disabled = True
        self.last_disable_time = datetime.datetime.now()
        background_tasks.add_task(self.re_enable_button_after_4_hours)
