import tkinter as tk
from tkinter import ttk, messagebox
import heapq
from datetime import datetime

#datetime对象
def datetime_change(date_str, time_str):
    return datetime.strptime(date_str + " " + time_str, "%Y%m%d %H:%M")

class Flight:
    def __init__(self, flight_id, departure_city, destination_city, stop_over,
                 departure_date, departure_time, arrival_time, price,
                 tickets, is_delay, delay_time, is_cancelled, is_for_sale):
        self.flight_id = flight_id
        self.departure_city = departure_city
        self.destination_city = destination_city
        self.stop_over = stop_over
        self.departure_date = departure_date
        self.departure_time = departure_time
        self.arrival_time = arrival_time

        #变量类型转换
        self.price = float(price) if price else 0.0
        self.tickets = int(tickets) if tickets else 0
        self.is_delay = (str(is_delay) == '1')
        self.delay_time = int(delay_time) if delay_time else 0
        self.is_cancelled = (str(is_cancelled) == '1')
        self.is_for_sale = (str(is_for_sale) == '1')

#字符串打印
    def __str__(self):
        return (f"[{self.flight_id}] {self.departure_city} -> {self.destination_city} | "
                f"Date: {self.departure_date} | "
                f"Time: {self.departure_time} - {self.arrival_time} | "
                f"Price: {self.price} | Tickets: {self.tickets} | "
                f"Cancelled: {self.is_cancelled} | OnSale: {self.is_for_sale}")

# 返回时间对象
    @property
    def departure_dt(self):
        return datetime_change(self.departure_date, self.departure_time)
    @property
    def arrival_dt(self):
        return datetime_change(self.departure_date, self.arrival_time)

class FlightManagementSystem:
    def __init__(self):
        self.flights = []  #存放Flight对象的列表
        self.flight_graph = {}  #记录航班时序关系
        self.priority_queue = []  #优先队列，用于预约抢票
        self.user_tickets = {}  #用户的购票信息

#读取数据集
    def read_dataset(self, filename="flightDataset.txt"):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split()
                    if len(parts) < 13:
                        continue  #数据缺失则跳过
                    flight_obj = Flight(*parts)
                    self.flights.append(flight_obj)
            self.build_flight_graph()  #构建基于时刻的航班图
        except Exception as e:
            print(f"读取航班文件出错: {e}")

#构建航班图
    def build_flight_graph(self):
        self.flight_graph.clear()
        self.flight_map = {f.flight_id: f for f in self.flights}
        #初始化每个flight_id在图中对应的空列表
        for f1 in self.flights:
            self.flight_graph[f1.flight_id] = []

        #双层循环，判断是否可衔接
        for f1 in self.flights:
            for f2 in self.flights:
                if f1.flight_id == f2.flight_id:
                    continue
                #同城市且时间顺序正确即可衔接
                if (f1.destination_city == f2.departure_city and
                        f1.arrival_dt and f2.departure_dt and
                        f2.departure_dt >= f1.arrival_dt):
                    self.flight_graph[f1.flight_id].append(f2.flight_id)

#返回航班ID
    def get_flight_by_id(self, flight_id):
        for f in self.flights:
            if f.flight_id == flight_id:
                return f
        return None

#增加航班
    def add_flight(self, flight_obj):
        self.flights.append(flight_obj)
        self.build_flight_graph()

#删除航班
    def delete_flight_by_id(self, flight_id):
        self.flights = [f for f in self.flights if f.flight_id != flight_id]
        self.build_flight_graph()

#更新航班，重建航班图
    def update_flight(self, flight_id, **kwargs):
        flt = self.get_flight_by_id(flight_id)
        if flt:
            for k, v in kwargs.items():
                if hasattr(flt, k):
                    setattr(flt, k, v)
            self.build_flight_graph()

#设置航班延误标记和延误时长
    def delay_flight(self, flight_id, delay_minutes):
        flt = self.get_flight_by_id(flight_id)
        if flt:
            flt.is_delay = True
            flt.delay_time = delay_minutes

#标记被取消航班
    def cancel_flight(self, flight_id):
        flt = self.get_flight_by_id(flight_id)
        if flt:
            flt.is_cancelled = True
            flt.is_for_sale = False
            self.canceled_flight_tuipiao(flight_id)

#取消航班自动退票
    def canceled_flight_tuipiao(self, flight_id):
        sign = []
        #遍历所有用户的购买记录
        for user_id, flight_dict in self.user_tickets.items():
            if flight_id in flight_dict:
                count = flight_dict[flight_id]
                # 删除该用户的航班购票信息
                del flight_dict[flight_id]
                sign.append((user_id, count))

        #如果有用户受影响，则在界面弹窗提示
        if sign:
            lines = ["以下用户已自动退票："]
            for (uid, c) in sign:
                lines.append(f"用户 {uid} 已自动退票 {c} 张")
            messagebox.showinfo("航班取消", "\n".join(lines))

#返回用户对指定航班的已购票数量
    def get_tickets_number(self, user_id, flight_id):
        if user_id not in self.user_tickets:
            return 0
        return self.user_tickets[user_id].get(flight_id, 0)

#返回用户购买的航班数量
    def get_flights_number(self, user_id):
        if user_id not in self.user_tickets:
            return 0
        return len(self.user_tickets[user_id])

#购票处理
    def buy_ticket(self, user_id, flight_id, quantity):
        flt = self.get_flight_by_id(flight_id)
        if not flt:
            return (False, "航班不存在")
        if flt.is_cancelled or not flt.is_for_sale:
            return (False, "该航班不可售票")
        if flt.tickets < quantity:
            return (False, "余票不足")

        user_flight_count = self.get_flights_number(user_id)
        already = self.get_tickets_number(user_id, flight_id)
        if already == 0 and user_flight_count >= 10:
            return (False, "您已购买了10个不同航班，无法再购买新的航班")

        #扣减余票，更新用户信息
        flt.tickets -= quantity
        if user_id not in self.user_tickets:
            self.user_tickets[user_id] = {}
        self.user_tickets[user_id][flight_id] = \
            self.user_tickets[user_id].get(flight_id, 0) + quantity

        return (True, "购票成功")

#退票处理
    def refund_ticket(self, user_id, flight_id, quantity):
        flt = self.get_flight_by_id(flight_id)
        if not flt:
            return (False, "该航班不存在")
        owned = self.get_tickets_number(user_id, flight_id)
        if owned == 0:
            return (False, "您未购买过此航班，无法退票")
        if owned < quantity:
            return (False, "退票数量超过已购数量，无法退票")
        if not flt.is_cancelled:
            flt.tickets += quantity

        self.user_tickets[user_id][flight_id] = owned - quantity
        if self.user_tickets[user_id][flight_id] == 0:
            del self.user_tickets[user_id][flight_id]

        return (True, "退票成功")

#预约抢票
    def reserve_ticket(self, user_id, flight_id, priority=0, quantity=1):
        heapq.heappush(self.priority_queue, (priority, user_id, flight_id, quantity))

#抢票优先队列处理
    def do_priority_queue(self):
        results = []
        while self.priority_queue:
            priority, user_id, flight_id, qty = heapq.heappop(self.priority_queue)
            flt = self.get_flight_by_id(flight_id)
            if (not flt) or flt.is_cancelled or not flt.is_for_sale:
                results.append((user_id, flight_id, qty, False, "航班不可售票"))
                continue
            if flt.tickets < qty:
                results.append((user_id, flight_id, qty, False, "余票不足"))
                continue
            user_flight_count = self.get_flights_number(user_id)
            already = self.get_tickets_number(user_id, flight_id)
            if already == 0 and user_flight_count >= 10:
                results.append((user_id, flight_id, qty, False, "已购买10个航班"))
                continue

            # 扣减余票、更新
            flt.tickets -= qty
            if user_id not in self.user_tickets:
                self.user_tickets[user_id] = {}
            self.user_tickets[user_id][flight_id] = \
                self.user_tickets[user_id].get(flight_id, 0) + qty
            results.append((user_id, flight_id, qty, True, "抢票成功"))
        return results

#航班查询
    def query_flights(self, dep=None, des=None, only_for_sale=False, sort_by=None):
        filtered = []
        for f in self.flights:
            if dep and f.departure_city != dep:
                continue
            if des and f.destination_city != des:
                continue
            if only_for_sale:
                if f.tickets <= 0 or f.is_cancelled or not f.is_for_sale:
                    continue
            filtered.append(f)
        if sort_by == "票价":
            filtered.sort(key=lambda x: x.price)
        elif sort_by == "出发时间":
            filtered.sort(key=lambda x: x.departure_time)
        return filtered

#返回指定航班对象
    def find_flight_by_id(self, flight_id):
        return self.get_flight_by_id(flight_id)

#替代航班推荐，BFS
    def alternate_flights(self, dep_city, des_city):
        #收集所有起点航班
        start_flights = []
        for f in self.flights:
            if f.departure_city == dep_city:
                start_flights.append(f.flight_id)

        results = []
        from collections import deque
        visited = set()
        queue = deque()
        #入队时记录(当前航班, 路径)
        for sfid in start_flights:
            queue.append((sfid, [sfid]))

        while queue:
            current_fid, path = queue.popleft()
            if current_fid in visited:
                continue
            visited.add(current_fid)

            cur_flight = self.flight_map.get(current_fid)
            if cur_flight and cur_flight.destination_city == des_city:
                results.append(path)

            #继续拓展
            next_list = self.flight_graph.get(current_fid, [])
            for nxt_fid in next_list:
                if nxt_fid not in path:  #避免环
                    queue.append((nxt_fid, path + [nxt_fid]))

        return results

#图像化GUI界面
class FlightApp:
    def __init__(self, root):
        # 设置主窗口
        self.root = root
        self.root.title("飞机票管理系统")
        self.root.geometry("500x700")

        self.fms = FlightManagementSystem()
        self.fms.read_dataset("flightDataset.txt")

        self.notebook = ttk.Notebook(root)  #创建多页签Notebook
        self.notebook.pack(fill="both", expand=True)

        #7个功能页面
        self.frame_flight_info = ttk.Frame(self.notebook)
        self.frame_dynamic = ttk.Frame(self.notebook)
        self.frame_ticket = ttk.Frame(self.notebook)
        self.frame_user = ttk.Frame(self.notebook)
        self.frame_ticket_find = ttk.Frame(self.notebook)
        self.frame_flightid_find = ttk.Frame(self.notebook)
        self.frame_alternate = ttk.Frame(self.notebook)

        #将页面添加到Notebook
        self.notebook.add(self.frame_flight_info, text=" 航班信息管理 ")
        self.notebook.add(self.frame_dynamic, text=" 航班动态管理 ")
        self.notebook.add(self.frame_ticket, text=" 票务管理 ")
        self.notebook.add(self.frame_user, text=" 用户界面 ")
        self.notebook.add(self.frame_ticket_find, text=" 票务查询 ")
        self.notebook.add(self.frame_flightid_find, text=" 航班查询 ")
        self.notebook.add(self.frame_alternate, text=" 替代航班推荐 ")

        # 分别初始化各个功能的UI
        self.create_flightUI()
        self.create_dynamicUI()
        self.create_ticketUI()
        self.create_userUI()
        self.create_findUI()
        self.create_flightid_findUI()
        self.create_alternateUI()

#航班信息管理界面
    def create_flightUI(self):
        self.frame_flight_info.rowconfigure(99, weight=1)
        self.frame_flight_info.columnconfigure(0, weight=1)

        label_frame = ttk.LabelFrame(self.frame_flight_info, text=" 航班信息增删 ", labelanchor='n')
        label_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        def _add_label_entry(parent, r, text):
            lbl = ttk.Label(parent, text=text, anchor='center', justify='center')
            lbl.grid(row=r, column=0, padx=5, pady=5, sticky="e")
            ent = ttk.Entry(parent, justify='center')
            ent.grid(row=r, column=1, padx=5, pady=5)
            return ent

        self.entry_flight_id = _add_label_entry(label_frame, 0, "航班ID:")
        self.entry_departure_city = _add_label_entry(label_frame, 1, "出发城市:")
        self.entry_destination_city = _add_label_entry(label_frame, 2, "目的城市:")
        self.entry_stop_over = _add_label_entry(label_frame, 3, "经停地点:")
        self.entry_departure_date = _add_label_entry(label_frame, 4, "出发日期(YYYYMMDD):")
        self.entry_departure_time = _add_label_entry(label_frame, 5, "出发时间(HH:MM):")
        self.entry_arrival_time = _add_label_entry(label_frame, 6, "到达时间(HH:MM):")
        self.entry_price = _add_label_entry(label_frame, 7, "票价:")
        self.entry_tickets = _add_label_entry(label_frame, 8, "可售余票:")
        self.entry_is_delay = _add_label_entry(label_frame, 9, "延误(0/1):")
        self.entry_delay_time = _add_label_entry(label_frame, 10, "延误时长(分钟):")
        self.entry_is_cancelled = _add_label_entry(label_frame, 11, "是否取消(0/1):")
        self.entry_is_for_sale = _add_label_entry(label_frame, 12, "是否售票(0/1):")

        btn_frame = ttk.Frame(label_frame)
        btn_frame.grid(row=13, column=0, columnspan=2, pady=10)

        btn_add = ttk.Button(btn_frame, text=" 新增航班 ", command=self.add_flight_action)
        btn_add.pack(side="left", padx=10)
        btn_delete = ttk.Button(btn_frame, text=" 删除航班 ", command=self.delete_flight_action)
        btn_delete.pack(side="left", padx=10)

#新增航班
    def add_flight_action(self):
        fields = [
            self.entry_flight_id.get().strip(),
            self.entry_departure_city.get().strip(),
            self.entry_destination_city.get().strip(),
            self.entry_stop_over.get().strip(),
            self.entry_departure_date.get().strip(),
            self.entry_departure_time.get().strip(),
            self.entry_arrival_time.get().strip(),
            self.entry_price.get().strip(),
            self.entry_tickets.get().strip(),
            self.entry_is_delay.get().strip(),
            self.entry_delay_time.get().strip(),
            self.entry_is_cancelled.get().strip(),
            self.entry_is_for_sale.get().strip()
        ]
        if any(len(x) == 0 for x in fields):
            messagebox.showerror("错误", "新增航班需要完整填写所有信息")
            return
        flt = Flight(*fields)
        self.fms.add_flight(flt)
        messagebox.showinfo("成功", f"已添加航班 {flt.flight_id}")

#删除航班
    def delete_flight_action(self):
        fid = self.entry_flight_id.get().strip()
        if not fid:
            messagebox.showerror("错误", "删除航班需要航班ID")
            return
        self.fms.delete_flight_by_id(fid)
        messagebox.showinfo("成功", f"已删除航班 {fid}")

#管理航班的延误和取消
    def create_dynamicUI(self):
        self.frame_dynamic.rowconfigure(99, weight=1)
        self.frame_dynamic.columnconfigure(0, weight=1)

        frame = ttk.LabelFrame(self.frame_dynamic, text=" 航班动态管理 ", labelanchor='n')
        frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        lbl_id = ttk.Label(frame, text="航班ID:", anchor='center')
        lbl_id.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_dyn_flight_id = ttk.Entry(frame, justify='center')
        self.entry_dyn_flight_id.grid(row=0, column=2, padx=5, pady=5)

        lbl_delay = ttk.Label(frame, text="延误时长(分钟):", anchor='center')
        lbl_delay.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_dyn_delay_time = ttk.Entry(frame, justify='center')
        self.entry_dyn_delay_time.grid(row=1, column=2, padx=5, pady=5)

        btn_delay = ttk.Button(frame, text=" 设置延误 ", command=self.set_delay_action)
        btn_delay.grid(row=2, column=1, padx=5, pady=5, sticky="e")

        btn_cancel = ttk.Button(frame, text=" 取消航班 ", command=self.cancel_flight_action)
        btn_cancel.grid(row=2, column=2, padx=5, pady=5, sticky="w")

#设置航班延误
    def set_delay_action(self):
        fid = self.entry_dyn_flight_id.get().strip()
        dtime = self.entry_dyn_delay_time.get().strip()
        if not fid or not dtime.isdigit():
            messagebox.showerror("错误", "请输入航班ID和延误时长(数字)")
            return
        self.fms.delay_flight(fid, int(dtime))
        messagebox.showinfo("成功", f"已设置航班 {fid} 延误 {dtime} 分钟")

#取消航班：触发自动退票
    def cancel_flight_action(self):
        fid = self.entry_dyn_flight_id.get().strip()
        if not fid:
            messagebox.showerror("错误", "请输入航班ID")
            return
        self.fms.cancel_flight(fid)
        messagebox.showinfo("成功", f"已取消航班 {fid}")

#票务管理界面
    def create_ticketUI(self):

        self.frame_ticket.rowconfigure(99, weight=1)
        self.frame_ticket.columnconfigure(0, weight=1)

        frame = ttk.LabelFrame(self.frame_ticket, text=" 票务管理 ", labelanchor='n')
        frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        lbl_u = ttk.Label(frame, text="用户ID:", anchor='center')
        lbl_u.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_user_id = ttk.Entry(frame, justify='center')
        self.entry_user_id.grid(row=0, column=1, padx=5, pady=5)

        lbl_f = ttk.Label(frame, text="航班ID:", anchor='center')
        lbl_f.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_ticket_flight_id = ttk.Entry(frame, justify='center')
        self.entry_ticket_flight_id.grid(row=1, column=1, padx=5, pady=5)

        lbl_q = ttk.Label(frame, text="购/退票数量:", anchor='center')
        lbl_q.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_ticket_quantity = ttk.Entry(frame, justify='center')
        self.entry_ticket_quantity.grid(row=2, column=1, padx=5, pady=5)

        btn_buy = ttk.Button(frame, text=" 立即购票 ", command=self.confirm_action)
        btn_buy.grid(row=3, column=0, padx=5, pady=5, sticky="e")

        btn_refund = ttk.Button(frame, text=" 退票 ", command=self.refund_ticket_action)
        btn_refund.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        lbl_p = ttk.Label(frame, text="优先级(数字越小越高):", anchor='center')
        lbl_p.grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.entry_reserve_priority = ttk.Entry(frame, justify='center')
        self.entry_reserve_priority.grid(row=4, column=1, padx=5, pady=5)

        lbl_rq = ttk.Label(frame, text="预约抢票数量:", anchor='center')
        lbl_rq.grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.entry_reserve_quantity = ttk.Entry(frame, justify='center')
        self.entry_reserve_quantity.grid(row=5, column=1, padx=5, pady=5)

        btn_reserve = ttk.Button(frame, text=" 预约抢票 ", command=self.reserve_ticket_action)
        btn_reserve.grid(row=6, column=0, padx=5, pady=5, sticky="e")

        btn_do = ttk.Button(frame, text=" 开始抢票 ", command=self.do_reservation_action)
        btn_do.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        self.text_ticket_result = tk.Text(frame)
        self.text_ticket_result.grid(row=7, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        frame.rowconfigure(7, weight=1)
        frame.columnconfigure(1, weight=1)

#购票前的确认弹窗，显示航班及价格信息，若点击确认则买票
    def confirm_action(self):
        uid = self.entry_user_id.get().strip()
        fid = self.entry_ticket_flight_id.get().strip()
        q_str = self.entry_ticket_quantity.get().strip()
        if not (uid and fid and q_str.isdigit()):
            messagebox.showerror("错误", "请输入有效的用户ID、航班ID和购票数量")
            return
        q = int(q_str)
        if q <= 0:
            messagebox.showerror("错误", "购票数量需为正数")
            return

        flt = self.fms.get_flight_by_id(fid)
        if not flt:
            messagebox.showerror("错误", "航班不存在")
            return

        total_amount = flt.price * q
        info_text = (f"您即将购买 {q} 张 [{flt.flight_id}] 机票\n"
                     f"航线: {flt.departure_city} -> {flt.destination_city}\n"
                     f"出发: {flt.departure_date} {flt.departure_time}\n"
                     f"票价: {flt.price:.2f}   总额: {total_amount:.2f}\n"
                     "是否确认购买？")
        confirm = messagebox.askyesno("确认购票", info_text)
        if confirm:
            suc, msg = self.fms.buy_ticket(uid, fid, q)
            if suc:
                messagebox.showinfo("成功", f"{msg}\n共计花费: {total_amount:.2f}")
            else:
                messagebox.showwarning("失败", msg)

#退票逻辑：检验用户输入后调用refund_ticket
    def refund_ticket_action(self):
        uid = self.entry_user_id.get().strip()
        fid = self.entry_ticket_flight_id.get().strip()
        q_str = self.entry_ticket_quantity.get().strip()
        if not (uid and fid and q_str.isdigit()):
            messagebox.showerror("错误", "请输入有效的用户ID、航班ID和退票数量")
            return
        q = int(q_str)
        if q <= 0:
            messagebox.showerror("错误", "退票数量需为正数")
            return
        suc, msg = self.fms.refund_ticket(uid, fid, q)
        if suc:
            messagebox.showinfo("成功", msg)
        else:
            messagebox.showwarning("失败", msg)

#预约抢票：向优先队列中插入(优先级, 用户ID, 航班ID, 数量)
    def reserve_ticket_action(self):
        uid = self.entry_user_id.get().strip()
        fid = self.entry_ticket_flight_id.get().strip()
        p_str = self.entry_reserve_priority.get().strip()
        q_str = self.entry_reserve_quantity.get().strip()

        if not (uid and fid and p_str.isdigit() and q_str.isdigit()):
            messagebox.showerror("错误", "请输入有效 用户ID / 航班ID / 优先级 / 抢票数量")
            return
        p = int(p_str)
        q = int(q_str)
        if q <= 0:
            messagebox.showerror("错误", "抢票数量需为正数")
            return

        self.fms.reserve_ticket(uid, fid, p, q)
        messagebox.showinfo("成功", f"已添加到预约抢票队列 (航班: {fid}, 数量: {q})")

    def do_reservation_action(self):
        """
        开始抢票：依次从优先队列中弹出并尝试购票并输出结果
        """
        results = self.fms.do_priority_queue()
        self.text_ticket_result.delete("1.0", tk.END)
        if not results:
            self.text_ticket_result.insert(tk.END, "预约队列为空。\n")
            return
        for uid, fid, qty, suc, msg in results:
            status = "成功" if suc else "失败"
            self.text_ticket_result.insert(tk.END, f"用户{uid} 抢 {qty} 张({fid}) -> {status} ({msg})\n")

#用户界面：左侧列表显示已购票用户ID，右侧Text显示用户购票信息
    def create_userUI(self):
        #设置frame_user行列布局
        for r in range(3):
            self.frame_user.rowconfigure(r, weight=0)
        for c in range(2):
            self.frame_user.columnconfigure(c, weight=0)

        #顶部提示标签
        lbl_info = ttk.Label(
            self.frame_user,
            text=(
                "提示：左侧显示已购票用户ID，点击查看用户购票详情。\n"
                "若列表为空或更新后，请点击“刷新用户列表”按钮。"
            ),
            anchor='center', justify='center'
        )
        lbl_info.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        #设置左侧框架的内容和格式
        left_frame = ttk.Frame(self.frame_user, width=100)
        left_frame.grid_propagate(False)
        left_frame.grid(row=1, column=0, sticky="ns", padx=5, pady=5)

        self.user_listbox = tk.Listbox(left_frame)
        self.user_listbox.pack(fill="both", expand=True)
        self.user_listbox.bind("<<ListboxSelect>>", self.user_selected)

        #设置右侧内容
        self.text_user_info = tk.Text(self.frame_user)
        self.text_user_info.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        #底部“刷新用户列表”按钮
        btn_refresh = ttk.Button(
            self.frame_user,
            text=" 刷新用户列表 ",
            command=self.load_users
        )
        btn_refresh.grid(row=2, column=0, columnspan=2, pady=5)

        self.frame_user.rowconfigure(1, weight=1)
        self.frame_user.columnconfigure(1, weight=1)  #左侧固定宽度100，右侧自适应
        self.load_users()  #刷新用户列表

#刷新用户列表，将所有存在购票信息的用户ID插入Listbox
    def load_users(self):
        self.user_listbox.delete(0, tk.END)
        for uid in self.fms.user_tickets:
            self.user_listbox.insert(tk.END, uid)

#当选中某个用户后，右侧显示其已购航班信息
    def user_selected(self, event):
        idx = self.user_listbox.curselection()
        if not idx:
            return
        user_id = self.user_listbox.get(idx[0])

        self.text_user_info.delete("1.0", tk.END)
        self.text_user_info.insert(tk.END, f"用户 {user_id} 的已购航班信息：\n\n")

        user_dict = self.fms.user_tickets.get(user_id, {})
        if not user_dict:
            self.text_user_info.insert(tk.END, "暂无购票记录\n")
            return

        for fid, num in user_dict.items():
            f = self.fms.get_flight_by_id(fid)
            if f:
                self.text_user_info.insert(tk.END,
                                           f"航班 {fid} ({f.departure_city}->{f.destination_city}), 已购 {num} 张\n"
                                           )
            else:
                self.text_user_info.insert(tk.END, f"航班 {fid} (数据缺失)，已购 {num} 张\n")

    #票务查询
    def create_findUI(self):
        self.frame_ticket_find.rowconfigure(1, weight=1)
        self.frame_ticket_find.columnconfigure(0, weight=1)

        frame = ttk.LabelFrame(self.frame_ticket_find, text=" 票务查询 ", labelanchor='n')
        frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        lbl_dep = ttk.Label(frame, text="出发城市:", anchor='center')
        lbl_dep.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_find_dep = ttk.Entry(frame, justify='center')
        self.entry_find_dep.grid(row=0, column=1, padx=5, pady=5)

        lbl_des = ttk.Label(frame, text="目的城市:", anchor='center')
        lbl_des.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_find_des = ttk.Entry(frame, justify='center')
        self.entry_find_des.grid(row=1, column=1, padx=5, pady=5)

        lbl_sort = ttk.Label(frame, text="排序依据:", anchor='center')
        lbl_sort.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.combo_sort_by = ttk.Combobox(frame, values=["票价", "出发时间"], justify='center')
        self.combo_sort_by.current(0)
        self.combo_sort_by.grid(row=2, column=1, padx=5, pady=5)

        self.only_for_sale_var = tk.BooleanVar(value=False)
        chk_for_sale = ttk.Checkbutton(frame, text="仅查看可购票航班", variable=self.only_for_sale_var)
        chk_for_sale.grid(row=3, column=0, columnspan=2, pady=5)

        btn_search = ttk.Button(frame, text=" 查询 ", command=self.find_flights_action)
        btn_search.grid(row=4, column=0, columnspan=2, pady=5)

        self.text_find_result = tk.Text(frame)
        self.text_find_result.grid(row=5, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        frame.rowconfigure(5, weight=1)
        frame.columnconfigure(1, weight=1)

#根据输入的出发城市、目的城市、排序方式、可售票筛选进行查询
    def find_flights_action(self):
        dep = self.entry_find_dep.get().strip()
        des = self.entry_find_des.get().strip()
        sort_by = self.combo_sort_by.get()
        only_for_sale = self.only_for_sale_var.get()

        flights = self.fms.query_flights(
            dep=dep if dep else None,
            des=des if des else None,
            only_for_sale=only_for_sale,
            sort_by=sort_by
        )
        self.text_find_result.delete("1.0", tk.END)
        if not flights:
            self.text_find_result.insert(tk.END, "没有找到符合条件的航班。\n")
            return
        for f in flights:
            self.text_find_result.insert(tk.END, str(f) + "\n")

    #航班查询，输入航班号，点击查询，显示该航班完整信息
    def create_flightid_findUI(self):
        self.frame_flightid_find.rowconfigure(1, weight=1)
        self.frame_flightid_find.columnconfigure(0, weight=1)

        frame = ttk.LabelFrame(self.frame_flightid_find, text=" 航班查询(根据航班号) ", labelanchor='n')
        frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        lbl = ttk.Label(frame, text="航班ID:", anchor='center')
        lbl.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_flightid_find = ttk.Entry(frame, justify='center')
        self.entry_flightid_find.grid(row=0, column=1, padx=5, pady=5)

        btn = ttk.Button(frame, text=" 查询航班 ", command=self.search_flightid_action)
        btn.grid(row=1, column=0, columnspan=2, pady=5)

        self.text_flightid_result = tk.Text(frame)
        self.text_flightid_result.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        frame.rowconfigure(2, weight=1)
        frame.columnconfigure(1, weight=1)

#查询指定的航班ID并输出详情。
    def search_flightid_action(self):
        fid = self.entry_flightid_find.get().strip()
        self.text_flightid_result.delete("1.0", tk.END)
        if not fid:
            self.text_flightid_result.insert(tk.END, "请输入航班ID。\n")
            return
        f = self.fms.find_flight_by_id(fid)
        if not f:
            self.text_flightid_result.insert(tk.END, f"未找到航班 {fid}\n")
        else:
            self.text_flightid_result.insert(tk.END, str(f) + "\n")

#输入出发城市和目的城市，可用flight_graph图BFS搜索合适的航班组合
    def create_alternateUI(self):
        self.frame_alternate.rowconfigure(3, weight=1)
        self.frame_alternate.columnconfigure(0, weight=1)

        frame = ttk.LabelFrame(self.frame_alternate, text=" 替代航班推荐 ", labelanchor='n')
        frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        lbl_dep = ttk.Label(frame, text="出发城市:", anchor='center')
        lbl_dep.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_alt_dep_city = ttk.Entry(frame, justify='center')
        self.entry_alt_dep_city.grid(row=0, column=1, padx=5, pady=5)

        lbl_des = ttk.Label(frame, text="目的城市:", anchor='center')
        lbl_des.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_alt_des_city = ttk.Entry(frame, justify='center')
        self.entry_alt_des_city.grid(row=1, column=1, padx=5, pady=5)

        btn_alt = ttk.Button(frame, text=" 查找替代航班 ", command=self.alternate_action)
        btn_alt.grid(row=2, column=0, columnspan=2, pady=5)

        self.text_alternate_result = tk.Text(frame)
        self.text_alternate_result.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        frame.rowconfigure(3, weight=1)
        frame.columnconfigure(1, weight=1)

#输出符合要求的推荐航班
    def alternate_action(self):
        dep = self.entry_alt_dep_city.get().strip()
        des = self.entry_alt_des_city.get().strip()
        self.text_alternate_result.delete("1.0", tk.END)
        if not dep or not des:
            self.text_alternate_result.insert(tk.END, "请输入出发城市和目的城市。\n")
            return

        path_list = self.fms.alternate_flights(dep, des)
        if not path_list:
            self.text_alternate_result.insert(tk.END, "未找到可行的替代航班组合(时刻顺序)。\n")
            return

        for idx, path in enumerate(path_list, start=1):
            self.text_alternate_result.insert(tk.END, f"方案{idx}:\n")
            for fid in path:
                flt = self.fms.flight_map.get(fid)
                if flt:
                    self.text_alternate_result.insert(tk.END, "   " + str(flt) + "\n")
            self.text_alternate_result.insert(tk.END, "\n")


def main():  #程序入口
    root = tk.Tk()
    app = FlightApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()