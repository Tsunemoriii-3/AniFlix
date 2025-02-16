from pyrogram import Client, __version__

from Powers.config import FSUB_CHANNEL, OWNER_ID, REQ_FSUB, SUDO
from Powers.database.force_sub_db import FSUB_LINK, FSUBS, OREDERED
from Powers.database.sudo_db import SUPPORTS
from Powers.functions.caching import CACHE
from Powers.logger import LOGGER

order_cache = CACHE.kb_order


async def load_channels(c: Client):
    fsubss = FSUBS()
    for i in FSUB_CHANNEL:
        x = await c.get_chat(int(i), False)
        fsubss.inser_fsub(int(i), "direct", x.title)
        order_cache[str(i)] = {"type": "direct", "btn_name": x.title}
    for i in REQ_FSUB:
        x = await c.get_chat(int(i))
        order_cache[str(i)] = {"type": "request", "btn_name": x.title}
        fsubss.inser_fsub(int(i), "request", x.title)


async def load_support_users():
    LOGGER.info("ADDING SUPPORT USERS")
    support = SUPPORTS()
    try:
        SUDO.remove(OWNER_ID)
    except ValueError:
        pass
    if not SUDO:
        LOGGER.info("No sudo user found")
        return
    txt = ""
    for i in SUDO:
        support.insert_support_user(int(i))
        txt += f"Added {i} authorized users\n"
    support.insert_support_user(OWNER_ID)
    LOGGER.info("ADDED OWNER")

    LOGGER.info(
        f"{txt}\nAdded total of {len(SUDO)} authorized users + 1 Owner")

    return


async def update_cache(upstream = False):
    if upstream:
        OREDERED().update_order(order_cache)
        return

    if cache := OREDERED().get_order():
        order_cache.clear()
        order_cache.update(cache)
        return
    else:
        channels = FSUBS().get_fsubs()
        for channel in channels:
            order_cache[str(channel["c_id"])] = {"type": channel["type"], "btn_name": channel.get("btn_name", None)}
        links = FSUB_LINK().get_all()

        for link in links:
            order_cache[link['link']] = link['btn_name']
    OREDERED().insert_initial(order_cache)
    return