from channels.consumer import SyncConsumer,AsyncConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync

class MySyncConsumer(SyncConsumer):
    
    def websocket_connect(self,event):
        self.send({
            'type': 'websocket.accept'
        })
        print("Channel Layer",self.channel_layer)
        print("Channel Name",self.channel_name)
        async_to_sync(self.channel_layer.group_add)('coders',self.channel_name)
        print('WebSocket Connected..')
    
    def websocket_receive(self,event):
        print('WebSocket Receive..',event)
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
        print('WebSocket Disconnected..')
        print("Channel Layer",self.channel_layer)
        print("Channel Name",self.channel_name)
        async_to_sync(self.channel_layer.group_discard)('coders',self.channel_name)
        raise StopConsumer()