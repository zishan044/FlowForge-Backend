import json
import asyncio
from fastapi import WebSocket
from redis.asyncio import Redis
from app.core.redis import redis

class ConnectionManager:
    def __init__(self, redis: Redis):
        self.__active_connections: dict[int, list[WebSocket]] = {}
        self.__redis: Redis = redis
        self.__pubsub_tasks: dict[int, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket, project_id: int):
        await websocket.accept()
        if project_id not in self.__active_connections:
            self.__active_connections[project_id] = []
            self.__pubsub_tasks[project_id] = asyncio.create_task(self.__listen_to_redis(project_id))
        self.__active_connections[project_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, project_id: int):
        if project_id in self.__active_connections:
            
            if websocket in self.__active_connections[project_id]:
                self.__active_connections[project_id].remove(websocket)

            if not self.__active_connections[project_id]:
                task = self.__pubsub_tasks.pop(project_id, None)
                if task:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

                del self.__active_connections[project_id]

    async def broadcast(self, message: dict, project_id: int):
        channel = f'project_{project_id}_whiteboard'
        await self.__redis.publish(channel, json.dumps(message))

    async def __listen_to_redis(self, project_id: int):
        pubsub = self.__redis.pubsub()
        channel = f'project_{project_id}_whiteboard'
        await pubsub.subscribe(channel)

        try:
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    data = json.loads(message['data'])
                    if project_id in self.__active_connections:
                        for connection in self.__active_connections[project_id]:
                            await connection.send_json(data)
        except asyncio.CancelledError:
            await pubsub.unsubscribe(channel)
            await pubsub.close()

connection_manager = ConnectionManager(redis)
