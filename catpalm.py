"""
版本 2023/01/18
協議 https://catpalm.gitbook.io/webapi/
"""
import json
import time

import requests
from websocket import WebSocketApp

_host = "web.catpalm.net"


# 主體
class Client:
    def __init__(self, id, token):
        self.id = id
        self.token = token
        self.valve = {}
        pass

    def group(self, id):
        return PalmGroup(self, id)

    def land(self, id):
        return PalmLand(self, id)

    def map(self, id):
        return PalmMap(self, id)

    def player(self, id):
        return PalmPlayer(self, id)

    def search(self):
        return PalmSearch(self)

    def server(self):
        return PalmServer(self)

    def icon(self):
        return PalmIcon(self)

    # https://catpalm.gitbook.io/webapi/gateway
    def gateway(self,
                on_open=None,
                on_error=None,
                on_close=None,
                server_message=None,
                player_join=None,
                player_quit=None,
                player_new=None,
                player_link=None,
                player_separate=None,
                player_phone=None,
                player_message=None,
                player_nick=None,
                ban_add=None,
                ban_remove=None,
                group_message=None,
                group_join=None,
                group_quit=None):
        events = []
        if server_message is not None:
            events.append("server_message")
        if player_join is not None:
            events.append("player_join")
        if player_quit is not None:
            events.append("player_quit")
        if player_new is not None:
            events.append("player_new")
        if player_link is not None:
            events.append("player_link")
        if player_separate is not None:
            events.append("player_separate")
        if player_phone is not None:
            events.append("player_phone")
        if player_message is not None:
            events.append("player_message")
        if player_nick is not None:
            events.append("player_nick")
        if ban_add is not None:
            events.append("ban_add")
        if ban_remove is not None:
            events.append("ban_remove")
        if group_message is not None:
            events.append("group_message")
        if group_join is not None:
            events.append("group_join")
        if group_quit is not None:
            events.append("group_quit")
        call = ""
        for event in events:
            if len(call) > 0:
                call += ","
            call += event

        def on_message(app, data):
            obj = json.loads(data)
            fun = obj["event"]
            if fun == "SERVER_MESSAGE":
                server_message(obj)
            elif fun == "PLAYER_JOIN":
                player_join(obj)
            elif fun == "PLAYER_QUIT":
                player_quit(obj)
            elif fun == "PLAYER_NEW":
                player_new(obj)
            elif fun == "PLAYER_LINK":
                player_link(obj)
            elif fun == "PLAYER_SEPARATE":
                player_separate(obj)
            elif fun == "PLAYER_PHONE":
                player_phone(obj)
            elif fun == "PLAYER_MESSAGE":
                player_message(obj)
            elif fun == "PLAYER_NICK":
                player_nick(obj)
            elif fun == "BAN_ADD":
                ban_add(obj)
            elif fun == "BAN_REMOVE":
                ban_remove(obj)
            elif fun == "GROUP_MESSAGE":
                group_message(obj)
            elif fun == "GROUP_JOIN":
                group_join(obj)
            elif fun == "GROUP_QUIT":
                group_quit(obj)

        socket = WebSocketApp(
            f"wss://{_host}/gateway/{call}",
            header={"Authorization": self.authorization()},
            on_message=on_message,
            on_open=(lambda app: on_open()) if on_open is not None else None,
            on_error=(lambda app: on_error()) if on_open is not None else None,
            on_close=(lambda app, ex: on_close(ex)) if on_open is not None else None,
        )
        return socket.run_forever(ping_interval=10, reconnect=5)

    def authorization(self):
        return f"Cat {self.id} {self.token}"

    def delay(self, key, delay):
        last = self.valve.get(key)
        if last is not None:
            gap = last + delay - time.time()
            if gap > 0:
                time.sleep(gap)
        pass

    def let(self, key):
        self.valve[key] = time.time()
        pass

    def request(self, target, method, data=None):
        headers = {"Authorization": self.authorization()}
        output = None
        if type(data) == str:
            output = data.encode("utf-8")
        elif type(data) == dict:
            output = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = requests.request(
            method,
            f"https://{_host}/{target}",
            data=output,
            headers=headers
        )
        return request.status_code, request.content


# https://catpalm.gitbook.io/webapi/group
class PalmGroup:
    def __init__(self, palm, id):
        self._palm = palm
        self.id = id
        pass

    def info(self):
        return self._palm.request(f"group/{self.id}/info", "get")

    def send(self, text):
        self._palm.delay("group/message put", 5)
        result = self._palm.request(f"group/{self.id}/message", "put", text)
        self._palm.let("group/message put")
        return result


# https://catpalm.gitbook.io/webapi/land
class PalmLand:
    def __init__(self, palm, id):
        self._palm = palm
        self.id = id
        pass

    def info(self):
        return self._palm.request(f"land/{self.id}/info", "get")

    def overlay(self, name=None, players_permissions=None):
        self._palm.delay("land/info put", 0.2)
        data = {}
        if name is not None:
            data["name"] = name
        if players_permissions is not None:
            data["players"] = players_permissions
        result = self._palm.request(f"land/{self.id}/info", "put", data)
        self._palm.let("land/info put")
        return result

    def get(self, player):
        return self._palm.request(f"land/{self.id}/permission/{player}", "get")

    def set(self, player, permissions):
        return self._palm.request(f"land/{self.id}/permission/{player}/{permissions}", "put")


# https://catpalm.gitbook.io/webapi/map
class PalmMap:
    def __init__(self, palm, id):
        self._palm = palm
        self.id = id
        pass

    def render(self, random=""):
        return self._palm.request(f"map/{self.id}/render/{random}", "get")


# https://catpalm.gitbook.io/webapi/player
class PalmPlayer:
    def __init__(self, palm, id):
        self._palm = palm
        self.id = id
        pass

    def data(self):
        return self._palm.request(f"player/{self.id}/data", "get")

    def face(self, random=""):
        return self._palm.request(f"player/{self.id}/face/{random}", "get")

    def info(self):
        return self._palm.request(f"player/{self.id}/info", "get")

    def send(self, text):
        self._palm.delay("player/message put", 0.2)
        result = self._palm.request(f"player/{self.id}/message", "put", text)
        self._palm.let("player/message put")
        return result


# https://catpalm.gitbook.io/webapi/search
class PalmSearch:
    def __init__(self, palm):
        self._palm = palm
        pass

    def block(self, world, x, y, z, page=0):
        return self._palm.request(f"search/block/{world}/{x},{y},{z}/{page}", "get")

    def online(self, world, x_a, y_a, z_a, x_b, y_b, z_b):
        return self._palm.request(f"search/online/{world}/{x_a},{y_a},{z_a}/{x_b},{y_b},{z_b}", "get")

    def player(self, name=None, nick=None, uuid=None, discord=None):
        if name is not None:
            return self._palm.request(f"search/player/name", "post", name)
        elif uuid is not None:
            return self._palm.request(f"search/player/uuid", "post", uuid)
        elif discord is not None:
            return self._palm.request(f"search/player/discord", "post", discord)
        else:
            return self._palm.request(f"search/player/nick", "post", nick)


# https://catpalm.gitbook.io/webapi/server
class PalmServer:
    def __init__(self, palm):
        self._palm = palm
        pass

    def send(self, text, lang="zh_Tw"):
        self._palm.delay("server/message put", 5)
        result = self._palm.request(f"server/message/{lang}", "put", text)
        self._palm.let("server/message put")
        return result

    def online(self):
        self._palm.delay("server/online get", 5)
        result = self._palm.request(f"server/online", "get")
        self._palm.let("server/online get")
        return result

    def statistics(self):
        self._palm.delay("server/statistics get", 5)
        result = self._palm.request(f"server/statistics", "get")
        self._palm.let("server/statistics get")
        return result


# https://catpalm.gitbook.io/webapi/icon
class PalmIcon:
    def __init__(self, palm):
        self._palm = palm
        pass

    def get(self):
        return self._palm.request(f"icon", "get")

    def add(self, world, x, z, type, name, visible=True):
        self._palm.delay("icon put", 0.5)
        result = self._palm.request(f"icon", "put", {
            "world": world,
            "x": x,
            "z": z,
            "type": type,
            "name": name,
            "visible": visible
        })
        self._palm.let("icon put")
        return result
