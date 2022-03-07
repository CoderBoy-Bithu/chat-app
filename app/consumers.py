import json
from channels.consumer import SyncConsumer,AsyncConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync
from app.models import Chat, Group
from channels.db import database_sync_to_async

# Static Group Name
class MySyncConsumer(SyncConsumer):
    
    def websocket_connect(self,event):
        self.send({
            'type': 'websocket.accept'
        })
        async_to_sync(self.channel_layer.group_add)('coders',self.channel_name)
    
    def websocket_receive(self,event):
        async_to_sync(self.channel_layer.group_send)('coders', {
            'type': 'chat.message',
            'message': event['text']
        })

    def chat_message(self,event):
        self.send({
            'type': 'websocket.send',
            'text': event['message']
        })
    
    def websocket_disconnect(self,event):
        async_to_sync(self.channel_layer.group_discard)('coders',self.channel_name)
        raise StopConsumer()

# Dynamic Group Name
class MyAsyncConsumer(AsyncConsumer):
    
    async def websocket_connect(self,event):
        await self.send({
            'type': 'websocket.accept'
        })
        self.group_name = self.scope['url_route']['kwargs']['groupname']
        await self.channel_layer.group_add(self.group_name,self.channel_name)
    
    async def websocket_receive(self,event):
        data = json.loads(event['text'])
        group = await database_sync_to_async(Group.objects.get)(name = self.group_name)
        
        if self.scope['user'].is_authenticated:
            chat = Chat(
            content = data['msg'],
            group = group
            )
            await database_sync_to_async(chat.save)()
            data['user'] = self.scope['user'].username
            await self.channel_layer.group_send(self.group_name, {
                'type': 'chat.message',
                'message': json.dumps(data)
            })
        else:
            await self.send({
                'type': 'websocket.send',
                'text': json.dumps({"msg": "Login Required", "user": "gest"})
            })
        

    async def chat_message(self,event):
        await self.send({
            'type': 'websocket.send',
            'text': event['message']
        })
    
    async def websocket_disconnect(self,event):
        await self.channel_layer.group_discard(self.group_name,self.channel_name)
        raise StopConsumer()