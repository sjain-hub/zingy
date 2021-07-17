import asyncio
import json
from django.shortcuts import render
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from .models import User, Addresses, Order
from kitchen.models import Kitchens, ComplaintsAndRefunds, UserDiscountCoupons
from datetime import datetime, timedelta
from django.utils import dateparse, timezone
from django.db.models import Q


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
        status = textdata.get('status')
        orderid = textdata.get('orderid')
        order = Order.objects.filter(id=orderid)[0]
        cust = order.customer
        amountPaid = textdata.get('amountPaid')
        balAmount = order.balance
        totalAmount = order.total_amount
        
        if status == "Payment" or status == "Placed":
            if order.coupon_id != None and order.coupon.user != None:
                await self.update_coupon(order.coupon_id, True)

        if status == "Rejected":
            if order.coupon_id != None and order.coupon.user != None:
                await self.update_coupon(order.coupon_id, False)
            if amountPaid != None:
                if int(amountPaid) > 0:
                    refundStatus = "Under Process"
                    comments = msgtocust
                    issue = "Order Rejected by Kitchen."
                    subject = "Refund"
                    await self.raise_refund_request(order.kitchen, order, cust, comments, issue, refundStatus, cust.phone, subject)
        elif status == "Cancelled":
            if order.coupon_id != None and order.coupon.user != None:
                await self.update_coupon(order.coupon_id, False)
            if order.amount_paid > 0:
                refundStatus = "Under Process"
                issue = msgtocust
                comments = ""
                subject = "Refund"
                await self.raise_refund_request(order.kitchen, order, cust, comments, issue, refundStatus, cust.phone, subject)

        if amountPaid == None:
            amountPaid = order.amount_paid
        else:
            balAmount = totalAmount - int(amountPaid)
        
        response = {
            "msgtocust": msgtocust,
            "status": status,
            "orderid": orderid,
        }
        await self.update_order_status(status, msgtocust, orderid, amountPaid, balAmount)
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
        paymentOption = otherDetails.get('paymentOption')
        total = otherDetails.get('total')
        subTotal = otherDetails.get('subTotal')
        deliveryCharge = otherDetails.get('deliveryCharge')
        coupDiscount = otherDetails.get('coupDiscount')
        kitDiscount = otherDetails.get('kitDiscount')
        mode = otherDetails.get('mode')
        if coupDiscount == None:
            coupDiscount = 0
        if kitDiscount == None:
            kitDiscount = 0
        if deliveryCharge == None:
            deliveryCharge = 0
        if mode != 'Delivery':
            mode = "PickUp"
        couponId = otherDetails.get('couponId')

        activeOrders = await self.check_active_orders(me.id)
        
        if activeOrders<2:
            order = await self.create_order(subTotal, total, coupDiscount, kitDiscount, couponId, mode, deliveryCharge, itemswithquantity, deliveryadd, distance, otherDetails.get('message'), scheduledDate, paymentOption, me, kitchen)
        else:
            response = {
                "status": "Order can't be placed, Maximum 2 active orders are allowed."
            }
            await self.send({
                "type": "websocket.send",
                "text": json.dumps(response)
            })

        responseforkit = {
            "items": items,
            "otherdetails": otherDetails,
            "custid": me.id,
            "scheduledDate": scheduledDate,
            "deliveryadd": deliveryadd,
            "distance": distance,
            "orderid": order.id,
            "paymentOption": paymentOption,
            "total": total,
        }
        await self.channel_layer.group_send(
            f"notification_group_{kituser}",
            {
                "type": "send_notification",
                "text": json.dumps(responseforkit)
            }
        )
        responseforcust = {
            "orderId": order.id
        }
        await self.send({
            "type": "websocket.send",
            "text": json.dumps(responseforcust)
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
        return Order.objects.filter(Q(status="Placed") | Q(status="Packed") | Q(status="Preparing") | Q(status="Dispatched") | Q(status="Waiting") | Q(status="Payment"), customer_id=custid).count()

    @database_sync_to_async
    def create_order(self, subTotal, total, coupDiscount, kitDiscount, couponId, mode, deliveryCharge, itemswithquantity, add, dist, msg, scheduledDate, paymentOption, cust, kit):
        currentDate = datetime.now()
        if scheduledDate:
            var = dateparse.parse_datetime(scheduledDate)
            scheduledDate = currentDate.replace(var.year, var.month, var.day, var.hour, var.minute)
            return Order.objects.create(sub_total=subTotal, total_amount=total, coup_discount=coupDiscount, kit_discount=kitDiscount, coupon_id=couponId, balance=total, mode=mode, delivery_charge=deliveryCharge, itemswithquantity=itemswithquantity, delivery_addr=add, dist_from_kit=dist, message=msg, scheduled_order=scheduledDate, paymentOption=paymentOption, customer=cust, kitchen=kit, created_at=currentDate)
        else:
            return Order.objects.create(sub_total=subTotal, total_amount=total, coup_discount=coupDiscount, kit_discount=kitDiscount, coupon_id=couponId, balance=total, mode=mode, delivery_charge=deliveryCharge, itemswithquantity=itemswithquantity, delivery_addr=add, dist_from_kit=dist, message=msg, scheduled_order=currentDate + timedelta(minutes=kit.deliveryTime), paymentOption=paymentOption, customer=cust, kitchen=kit, created_at=currentDate)

    @database_sync_to_async
    def update_order_status(self, status, msgtocust, orderid, amount_paid, balAmount):
        currentDate = datetime.now()
        return Order.objects.filter(id=orderid).update(status=status, msgtocust=msgtocust, amount_paid=amount_paid, balance=balAmount, completed_at=currentDate)

    @database_sync_to_async
    def raise_refund_request(self, kitchen, order, cust, comments, issue, refundStatus, paytmNo, subject):
        currentDate = datetime.now()
        ComplaintsAndRefunds.objects.create(kit=kitchen, order=order, user=cust, comments=comments, issue=issue, status=refundStatus, paytmNo=paytmNo, request_date=currentDate, subject=subject)

    @database_sync_to_async
    def update_coupon(self, couponId, redeemed):
        print(couponId, redeemed)
        UserDiscountCoupons.objects.filter(id=couponId).update(redeemed=redeemed)