import asyncio
import json
from django.shortcuts import render
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from .models import User, Addresses, Order
from kitchen.models import Kitchens
from datetime import datetime, timedelta
from django.utils import dateparse, timezone


currentDate = datetime.now()


class Customer(AsyncConsumer):
    async def websocket_connect(self, event):
        print("connected", event)
        await self.channel_layer.group_add(
            f"notification_group_{self.scope['url_route']['kwargs']['otheruserid']}",
            self.channel_name
        )

        await self.send({
            "type": "websocket.accept"
        })

    async def websocket_receive(self, event):
        print("receive", event)
        me = self.scope['user']
        text = event.get('text', None)
        if text is not None:
            textdata = json.loads(text)
            if me.is_customer:
                if textdata.get('status') != None:
                    await self.kitchenFunction(textdata)
                else:
                    await self.customerFunction(textdata, me)
            elif me.is_kitchen:
                await self.kitchenFunction(textdata)


    async def send_notification(self, event):
        print("sending..............", event)
        await self.send({
            "type": "websocket.send",
            "text": event['text']
        })


    async def websocket_disconnect(self, event):
        print("disconnected", event)

    
    async def kitchenFunction(self, textdata):
        msgtocust = textdata.get('msgtocust')
        custid = textdata.get('custid')
        status = textdata.get('status')
        orderid = textdata.get('orderid')
        cust = User.objects.filter(id=custid)[0]
        response = {
            "msgtocust": msgtocust,
            "status": status,
            "orderid": orderid,
        }
        await self.update_order_status(status, msgtocust, orderid)
        await self.channel_layer.group_send(
            f"notification_group_{cust}",
            {
                "type": "send_notification",
                "text": json.dumps(response)
            }
        )

    
    async def customerFunction(self, textdata, me):
        items = textdata.get('items')

        itemswithquantity = ""
        for i in items:
            itemswithquantity = itemswithquantity + \
                i.get('itemName') + "  X  " + i.get('quantity') + ", "

        otherDetails = textdata.get('otherdetails')
        kituserid = otherDetails.get('kituserid')
        kituser = User.objects.filter(id=kituserid)[0]

        kitid = otherDetails.get('kitid')
        kitchen = Kitchens.objects.filter(id=kitid)[0]
        addid = otherDetails.get('address')
        context = await self.calc_distance(kitchen, addid)
        distance = json.loads(context).get('distance')
        deliveryadd = json.loads(context).get('deliveryadd')
        scheduledDate = otherDetails.get('scheduledDate')
        

        activeOrders = await self.check_active_orders(me.id)
        
        if activeOrders<2:
            order = await self.create_order(otherDetails.get('total'), otherDetails.get('mode'), itemswithquantity, deliveryadd, distance, otherDetails.get('message'), scheduledDate, me, kitchen)
        else:
            response = {
                "status": "Order can't be placed, Maximum 2 active orders are allowed."
            }
            await self.send({
                "type": "websocket.send",
                "text": json.dumps(response)
            })

        response = {
            "items": items,
            "otherdetails": otherDetails,
            "custid": me.id,
            "scheduledDate": scheduledDate,
            "deliveryadd": deliveryadd,
            "distance": distance,
            "orderid": order.id
        }
        await self.channel_layer.group_send(
            f"notification_group_{kituser}",
            {
                "type": "send_notification",
                "text": json.dumps(response)
            }
        )
        response = {
            "orderId": order.id
        }
        await self.send({
            "type": "websocket.send",
            "text": json.dumps(response)
        })



    @database_sync_to_async
    def calc_distance(self, kitchen, addid):
        deliveryaddress = Addresses.objects.filter(id=addid)[0]
        distance = deliveryaddress.location.distance(kitchen.location) * 100
        context = {
            "distance": round(distance,1),
            "deliveryadd": deliveryaddress.address + ", Floor No.- " + deliveryaddress.floorNo,
        }
        return json.dumps(context)

    @database_sync_to_async
    def check_active_orders(self, custid):
        return Order.objects.filter(customer_id=custid, status="Placed").count() + Order.objects.filter(customer_id=custid, status="Packed").count() + Order.objects.filter(customer_id=custid, status="Preparing").count() + Order.objects.filter(customer_id=custid, status="Dispatched").count() + Order.objects.filter(customer_id=custid, status="Waiting").count()

    @database_sync_to_async
    def create_order(self, total, mode, itemswithquantity, add, dist, msg, scheduledDate, cust, kit):
        if scheduledDate:
            var = dateparse.parse_datetime(scheduledDate)
            scheduledDate = currentDate.replace(var.year, var.month, var.day, var.hour, var.minute)
            return Order.objects.create(total_amount=total, mode=mode, itemswithquantity=itemswithquantity, delivery_addr=add, dist_from_kit=dist, message=msg, scheduled_order=scheduledDate, customer=cust, kitchen=kit, created_at=currentDate)
        else:
            return Order.objects.create(total_amount=total, mode=mode, itemswithquantity=itemswithquantity, delivery_addr=add, dist_from_kit=dist, message=msg, scheduled_order=currentDate, customer=cust, kitchen=kit, created_at=currentDate)

    @database_sync_to_async
    def update_order_status(self, status, msgtocust, orderid):
        return Order.objects.filter(id=orderid).update(status=status, msgtocust=msgtocust, completed_at=currentDate)
