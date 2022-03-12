import discord.http; discord.http.Route.BASE = "https://discordapp.com/api/v9"

import os
import asyncio
import multiprocessing
import requests
import signal
import logging; log = logging.getLogger(__name__)

from backend import ShardedBotInstance, config



class Supervisor(object):
    def __init__(self, loop):
        self.cluster_queue = []
        self.clusters = []
        self.loop = loop
        self.future = None
        self.alive = True
        self.keep_alive = None


    def shard_count(self):
        d = requests.get(
            "https://discordapp.com/api/v9/gateway/bot",
            headers={
                "Authorization": "Bot " + config["token"],
            }
        )
        d.raise_for_status()
        return (d.json())["shards"]


    def start(self):
        self.future = asyncio.ensure_future(self.boot(), loop=self.loop)
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            self.loop.run_until_complete(self.kill())
        finally:
            self.clean()
        
    
    def clean(self):
        self.loop.stop()
        self.loop.close()


    def task_done(self, t):
        if t.execption():
            t.print_stack()
            self.keep_alive = self.loop.create_task(self.rebooter())
            self.keep_alive.add_done_callback(self.task_done)


    async def boot(self):
        shards = list(range(self.shard_count()))
        size = [shards[x:x+4] for x in range(0, len(shards), 4)]

        log.info(f"Starting with {len(size)} cluster{'' if len(size) == 1 else 's'}")
        for sids in size:
            self.cluster_queue.append(Cluster(self, next(iter(config["cluster_names"])), sids, len(shards)))

        await self.boot_cluster()
        self.keep_alive = self.loop.create_task(self.rebooter())
        self.keep_alive.add_done_callback(self.task_done)
        log.info(f"Startup finished")


    async def kill(self):
        log.info("Shutting down clusters")
        self.alive = False
        if self.keep_alive:
            self.keep_alive.cancel()
        for cluster in self.clusters:
            cluster.kill()
        self.clean()


    async def rebooter(self):
        while self.alive:
            if not self.clusters:
                log.warning("Seems like all clusters are down")
                asyncio.ensure_future(self.kill())
            for cluster in self.clusters:
                if not cluster.process.is_alive():
                    log.info(f"Cluster#{cluster.name} exited with code {cluster.process.exitcode}")
                    log.info(f"Restarting cluster#{cluster.name}")
                    await cluster.start()
            await asyncio.sleep(5)


    async def boot_cluster(self):
        for cluster in self.cluster_queue:
            self.clusters.append(cluster)
            log.info(f"Starting Cluster#{cluster.name}")
            self.loop.create_task(cluster.start())
            await asyncio.sleep(0.5)


class Cluster(object):
    def __init__(self, s, name, sids, max_shards):
        self.supervisor = s
        self.process = None
        self.kwargs = {}
        self.name = name

        self.log = log
        self.log.info(f"Initialized with shard ids {sids}, total shards {max_shards}")


    def wait_close(self):
        return self.process.join()


    async def start(self, *, force=False):
        if self.process and self.process.is_alive():
            if not force:
                return
            self.log.info("Terminating process")
            self.process.terminate()
            self.process.close()

        self.process = multiprocessing.Process(target=ShardedBotInstance, kwargs=self.kwargs, daemon=True)
        self.process.start()
        self.log.info(f"Process started with ID {self.process.pid}")
        return True


    def kill(self, sign=signal.SIGINT):
        self.log.info(f"Shutting down with signal {sign}")
        try:
            os.kill(self.process.pid, sign)
        except ProcessLookupError:
            pass


if __name__ == "__main__":
    ShardedBotInstance()
