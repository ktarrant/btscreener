from transitions import Machine
import backtrader as bt

class BreakoutDriver(object):

    states = [
        "idle",
        "entry",
        "cancel_entry",
        "start_protect",
        "protect",
        "cancel_protect",
        "close",
    ]
    initial_state = "idle"

    def __init__(self, strategy):
        self.strategy = strategy
        
        self.entry_order = None
        self.protect_order = None
        self.close_order = None

        self.machine = Machine(model=self,
                               states=BreakoutDriver.states,
                               initial=BreakoutDriver.initial_state,
                               send_event=True,
                               ignore_invalid_triggers=True)

        # order is trigger, source, dest
        # from idle
        self.machine.add_transition("next", "idle", "entry",
                                    conditions=["is_entry_signal"],
                                    after=["send_entry_order"])

        # from entry
        self.machine.add_transition("notify_order", "entry", "start_protect",
                                    conditions=[
                                        "is_entry_order_completed",
                                    ],
                                    after=["send_protect_order"])
        self.machine.add_transition("stop", "entry", "cancel_entry",
                                    after=["cancel_entry_order"])

        # from cancel_entry
        self.machine.add_transition("notify_order", "cancel_entry", "idle",
                                    conditions=["is_entry_order_cancelled"])

        # from start_protect
        self.machine.add_transition("notify_order", "start_protect", "idle",
                                    conditions=["is_protect_order_completed"])
        self.machine.add_transition("stop", "start_protect", "cancel_protect",
                                    after=["cancel_protect_order"])
        self.machine.add_transition("notify_order", "start_protect", "protect",
                                    conditions=["is_protect_order_accepted"])

        # from protect
        self.machine.add_transition("notify_order", "protect", "start_protect",
                                    conditions=["is_protect_order_cancelled"],
                                    after=["send_protect_order"])
        self.machine.add_transition("notify_order", "protect", "idle",
                                    conditions=["is_protect_order_completed"])
        self.machine.add_transition("next", "protect", "cancel_protect",
                                    conditions=["is_close_signal"],
                                    after=["cancel_protect_order"])
        self.machine.add_transition("next", "protect", "protect",
                                    conditions=["is_protect_price_changed"],
                                    after=["cancel_protect_order"])

        # from cancel_protect
        self.machine.add_transition("notify_order", "cancel_protect", "close",
                                    conditions=["is_protect_order_cancelled"],
                                    after=["send_close_order"])
        self.machine.add_transition("notify_order", "cancel_protect", "idle",
                                    conditions=["is_protect_order_completed"])

        # from close
        self.machine.add_transition("notify_order", "close", "idle",
                                    conditions=["is_close_order_completed"])


    @staticmethod
    def check_order_status(event, exp_order, status):
        order = event.kwargs.get("order", exp_order)
        if order and order == exp_order:
            if order.status == status:
                return True
            else:
                return False
        else:
            return False


    # entry order handlers
    def is_entry_signal(self, event):
        return self.strategy.entry_signal[0] != 0


    def send_entry_order(self, event):
        if self.strategy.entry_signal[0] > 0:
            self.entry_order = self.strategy.buy()
        elif self.strategy.entry_signal[0] < 0:
            self.entry_order = self.strategy.sell()


    def cancel_entry_order(self, event):
        self.strategy.cancel(self.entry_order)


    def is_entry_order_completed(self, event):
        return self.check_order_status(event,
                                       self.entry_order,
                                       bt.Order.Completed)


    def is_entry_order_cancelled(self, event):
        return self.check_order_status(event,
                                       self.entry_order,
                                       bt.Order.Cancelled)


    # protect order handlers
    def send_protect_order(self, event):
        if self.strategy.position.size > 0:
            self.protect_order = self.strategy.sell(
                exectype=bt.Order.Stop, price=self.strategy.protect_price[0])
        elif self.strategy.position.size < 0:
            self.protect_order = self.strategy.buy(
                exectype=bt.Order.Stop, price=self.strategy.protect_price[0])


    def cancel_protect_order(self, event):
        self.strategy.cancel(self.protect_order)


    def is_protect_order_completed(self, event):
        return self.check_order_status(event,
                                       self.protect_order,
                                       bt.Order.Completed)


    def is_protect_order_cancelled(self, event):
        return self.check_order_status(event,
                                       self.protect_order,
                                       bt.Order.Cancelled)


    def is_protect_order_accepted(self, event):
        return self.check_order_status(event,
                                       self.protect_order,
                                       bt.Order.Accepted)

    def is_protect_price_changed(self, event):
        if self.protect_order:
            if self.protect_order.price == self.strategy.protect_price[0]:
                return False
            else:
                return True
        else:
            return True

    # close order handlers
    def is_close_signal(self, event):
        return self.strategy.close_signal[0] != 0

    def send_close_order(self, event):
        self.close_order = self.strategy.close()

    def is_close_order_completed(self, event):
        return self.check_order_status(event,
                                       self.close_order,
                                       bt.Order.Completed)