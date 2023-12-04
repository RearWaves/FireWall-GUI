#####################################
# 网络空间安全学院2023网络安全课程设计
# 作者: 华中科技大学网安2005班 XXX
# Linux 下状态检测防火墙的设计与实现
# 本代码功能[图形化界面]
#####################################

import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from tkinter import simpledialog
import os
import subprocess

# 弹窗样式类
class StyledDialog(simpledialog.Dialog):
    
    def __init__(self, parent, title=None):
        self.style = ttk.Style()
        super().__init__(parent, title=title)

    def body(self, master):
        # 弹窗设置
        self.geometry("650x500")  # 宽度 x 高度
        master.configure(bg='#080e23')  # 设置弹窗主体的背景颜色
        self.configure(bg='#080e23')  # 深色背景

        # 设置ttk按钮的样式
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TLabel",
            background="#080e23",
            foreground="#12fdff",
            font=("Arial", 12, "bold")
            )
        self.style.configure("TEntry",
            background="#080e23",
            # foreground="#fe764c",
            insertbackground='#fe764c',  # 光标颜色
            fieldbackground='#080e23',  # 输入框背景颜色
            font=("Arial", 12, "bold")
            )           
        self.style.configure("TCombobox",
            background="#080e23",  # 背景颜色
            foreground="#fe764c",  # 前景颜色
            fieldbackground="#080e23",  # 下拉框的背景颜色
            selectbackground="#fe764c",  # 选中项的背景颜色
            selectforeground="#080e23",  # 选中项的前景颜色
            font=("Arial", 12, "bold")  # 字体
            )
        self.style.configure("TRadiobutton",  # 设置单选按钮的样式
            background="#080e23",  # 背景颜色
            foreground="#fe764c",  # 前景颜色
            font=("Arial", 12, "bold")
            )
        self.style.configure("TCheckbutton",  # 设置复选框的样式
            background="#080e23",  # 背景颜色
            foreground="#fe764c",  # 前景颜色
            font=("Arial", 12, "bold")
            )
        self.style.configure("TScale",  # 设置拖动条的样式
            troughcolor="#080e23",  # 背景颜色
            sliderrelief="flat",  # 设置拖动按钮的边框风格为"flat"
            sliderthickness=20  # 设置拖动按钮的宽度
            )
        self.style.configure("TButton",
            background="#11192b",
            foreground="#09fbff",
            bordercolor="#ee5f26",
            highlightthickness=0,
            bd=2,  # 设置按钮的边框宽度
            relief="raised",  # 设置按钮边框风格为"flat"
            font=("Arial", 12, "bold")
            )
        self.style.map("TButton",
            background=[('pressed', '#27637b'), ('active', '#1f3b4e')],
            foreground=[('pressed', '#09fbff'), ('active', '#09fbff')],
            bordercolor=[('pressed', '#ee5f26'), ('active', '#ee5f26')]  # 设置按钮边框颜色
            )

# 新建规则弹窗
class RuleAddDialog(StyledDialog):

    def body(self, master):
        super().body(master)

        # 前两个参数
        self.prev_label = ttk.Label(master, text="请输入上个规则名称: ")
        self.prev_label.grid(row=0, column=0, pady=10)
        self.prev_rule_name_var = tk.StringVar()
        self.prev_entry = ttk.Entry(master, textvariable=self.prev_rule_name_var)
        self.prev_entry.grid(row=0, column=1, pady=10)

        self.name_label = ttk.Label(master, text="请为你的新规则命名: ")
        self.name_label.grid(row=1, column=0, pady=10)
        self.rule_name_var = tk.StringVar()
        self.name_entry = ttk.Entry(master, textvariable=self.rule_name_var)
        self.name_entry.grid(row=1, column=1, pady=10)

        # 默认参数
        self.src_ip_var = tk.StringVar(value="192.168.152.2/24")
        self.src_port_var = tk.StringVar(value="any")
        self.dst_ip_var = tk.StringVar(value="192.168.164.2/24")
        self.dst_port_var = tk.StringVar(value="any")

        ttk.Label(master, text="请您输入源IP和掩码: ").grid(row=2, column=0, pady=10)
        ttk.Label(master, text="请输入源端口的范围: ").grid(row=3, column=0, pady=10)
        ttk.Label(master, text="请输入目标IP和掩码: ").grid(row=4, column=0, pady=10)
        ttk.Label(master, text="请输入目标端口范围: ").grid(row=5, column=0, pady=10)
        ttk.Label(master, text="请输入具体协议名称: ").grid(row=6, column=0, pady=10)

        self.src_ip_entry = ttk.Entry(master, textvariable=self.src_ip_var)
        self.src_ip_entry.grid(row=2, column=1, pady=10)
        self.src_port_entry = ttk.Entry(master, textvariable=self.src_port_var)
        self.src_port_entry.grid(row=3, column=1, pady=10)
        self.dst_ip_entry = ttk.Entry(master, textvariable=self.dst_ip_var)
        self.dst_ip_entry.grid(row=4, column=1, pady=10)
        self.dst_port_entry = ttk.Entry(master, textvariable=self.dst_port_var)
        self.dst_port_entry.grid(row=5, column=1, pady=10)

        # 更新协议选择部分为下拉选择框
        self.protocol_var = tk.StringVar(value="any")
        self.protocol_options = ['ICMP', 'TCP', 'UDP', 'any']
        self.protocol_combobox = ttk.Combobox(master, textvariable=self.protocol_var, values=self.protocol_options, state="readonly", width=18)
        self.protocol_combobox.grid(row=6, column=1, pady=10)

        # 使用trace方法来监听协议选择框的值变化
        self.protocol_var.trace('w', self.update_port_visibility)

        # 单选按钮
        self.action_var = tk.IntVar(value=0)  # 默认为0 (drop)
        self.log_var = tk.IntVar(value=1)     # 默认为1 (yes)

        self.accept_radiobtn = ttk.Radiobutton(master, text="Accept", variable=self.action_var, value=1)
        self.accept_radiobtn.grid(row=7, column=0, pady=10)
        self.drop_radiobtn = ttk.Radiobutton(master, text="Drop", variable=self.action_var, value=0)
        self.drop_radiobtn.grid(row=7, column=1, pady=10)

        self.log_checkbox = ttk.Checkbutton(master, text="使用日志(推荐勾选)", variable=self.log_var)
        self.log_checkbox.grid(row=9, columnspan=2, pady=10)

        return self.prev_entry  # 初始焦点设置在第一个输入框上

    def apply(self):
        self.prev_rule_name = self.prev_rule_name_var.get()
        self.rule_name = self.rule_name_var.get()
        self.src_ip = self.src_ip_var.get()
        self.src_port = self.src_port_var.get()
        self.dst_ip = self.dst_ip_var.get()
        self.dst_port = self.dst_port_var.get()
        self.protocol = self.protocol_var.get()
        self.action = str(self.action_var.get())
        self.log = str(self.log_var.get())

    # 新方法用于根据协议选择框的值来决定是否显示端口输入框
    def update_port_visibility(self, *args):
        if self.protocol_var.get() == "ICMP":
            self.src_port_entry.grid_remove()
            self.dst_port_entry.grid_remove()
        else:
            self.src_port_entry.grid()
            self.dst_port_entry.grid()

# 新建NAT弹窗
class NatAddDialog(StyledDialog):

    def body(self, master):
        super().body(master)
        self.geometry("500x245")  # 宽度 x 高度
        # 默认参数
        self.src_ip_var = tk.StringVar(value="192.168.164.2/24")
        self.nat_ip_var = tk.StringVar(value="192.168.152.130")
        self.nat_port_var = tk.StringVar(value="any")

        ttk.Label(master, text="请输入源IP和掩码: ").grid(row=0, column=0, pady=10)  # 增加间距
        ttk.Label(master, text="请输入NAT转换IP: ").grid(row=1, column=0, pady=10)
        ttk.Label(master, text="请输入端口的范围: ").grid(row=2, column=0, pady=10)

        self.src_ip_entry = ttk.Entry(master, textvariable=self.src_ip_var)
        self.src_ip_entry.grid(row=0, column=1, pady=10)  # 增加间距
        self.nat_ip_entry = ttk.Entry(master, textvariable=self.nat_ip_var)
        self.nat_ip_entry.grid(row=1, column=1, pady=10)
        self.nat_port_entry = ttk.Entry(master, textvariable=self.nat_port_var)
        self.nat_port_entry.grid(row=2, column=1, pady=10)

        return self.src_ip_entry  # 初始焦点设置在第一个输入框上

    def apply(self):
        self.src_ip = self.src_ip_var.get()
        self.nat_ip = self.nat_ip_var.get()
        self.nat_port = self.nat_port_var.get()

# 删除规则弹窗
class DeleteRuleDialog(StyledDialog):
    def body(self, master):
        super().body(master)
        self.geometry("550x260")
        
        # 标签和输入行
        ttk.Label(master, text="请输入规则完整名称: ").grid(row=0, pady=20)
        self.rule_name_entry = ttk.Entry(master)
        self.rule_name_entry.grid(row=0, column=1)
        
        # 提示文本框1
        prompt1_text = tk.Text(master, height=1, width=38, wrap=tk.WORD, bg='#080e23', fg='#fe764c', insertbackground='#fe764c', font=("Arial", 12))
        prompt1_text.insert(tk.END, "请输入系统中的规则完整名称,输入错误无法删除")
        prompt1_text.grid(row=1, columnspan=2, pady=10)
        
        # 提示文本框2
        prompt2_text = tk.Text(master, height=1, width=38, wrap=tk.WORD, bg='#080e23', fg='#fe764c', insertbackground='#fe764c', font=("Arial", 12))
        prompt2_text.insert(tk.END, "系统规则删除后无法撤销,请谨慎考虑后进行删除")
        prompt2_text.grid(row=2, columnspan=2, pady=20)
        
        return self.rule_name_entry

    def apply(self):
        self.result = self.rule_name_entry.get()

# 删除NAT规则弹窗
class DeleteNatDialog(StyledDialog):
    def body(self, master):
        super().body(master)
        self.geometry("550x260")
        
        # 标签和输入行
        ttk.Label(master, text="请输入NAT规则序号: ").grid(row=0, pady=20)
        self.nat_number_entry = ttk.Entry(master)
        self.nat_number_entry.grid(row=0, column=1)
        
        # 提示文本框1
        prompt1_text = tk.Text(master, height=1, width=38, wrap=tk.WORD, bg='#080e23', fg='#fe764c', insertbackground='#fe764c', font=("Arial", 12))
        prompt1_text.insert(tk.END, "请输入系统中的NAT规则序号,输入错误无法删除")
        prompt1_text.grid(row=1, columnspan=2, pady=10)
        
        # 提示文本框2
        prompt2_text = tk.Text(master, height=1, width=38, wrap=tk.WORD, bg='#080e23', fg='#fe764c', insertbackground='#fe764c', font=("Arial", 12))
        prompt2_text.insert(tk.END, "NAT规则删除后无法撤销,请谨慎考虑后进行删除")
        prompt2_text.grid(row=2, columnspan=2, pady=20)

        return self.nat_number_entry

    def apply(self):
        self.result = self.nat_number_entry.get()

# 设置时间弹窗
class TimeSetDialog(StyledDialog):

    def body(self, master):
        super().body(master)
        self.geometry("550x260")
        ttk.Label(master, text="请输入规则完整名称: ").grid(row=0, column=0, pady=10)
        self.rule_entry = ttk.Entry(master)
        self.rule_entry.grid(row=0, column=1, pady=10)
        
        self.pattern_var = tk.StringVar(value="Time")
        ttk.Label(master, text="选择规则过期的方式: ").grid(row=1, column=0, pady=10)
        self.pattern_combobox = ttk.Combobox(master, textvariable=self.pattern_var, values=["Time", "Date"], state="readonly", width=18)
        self.pattern_combobox.grid(row=1, column=1, pady=10)
        self.pattern_combobox.bind("<<ComboboxSelected>>", self.update_visibility)
        
        ttk.Label(master, text="请设置作用时间 (秒) :").grid(row=2, column=0, pady=10)
        self.time_entry = ttk.Entry(master)
        self.time_entry.grid(row=2, column=1, pady=10)
        self.time_entry.insert(0, "6")  # 默认时间为6秒
        
        ttk.Label(master, text="请设置规则有效日期:").grid(row=3, column=0, pady=10)
        self.date_entry = ttk.Entry(master)
        self.date_entry.grid(row=3, column=1, pady=10)
        self.date_entry.insert(0, "2024/01/01")  # 默认日期为2024年1月1日
        
        self.update_visibility(None)
        
        return self.rule_entry

    def apply(self):
        self.rule_name = self.rule_entry.get()
        if self.pattern_var.get() == "Time":
            try:
                self.time = int(self.time_entry.get())
            except ValueError:
                self.time = 5  # 如果输入的不是数字, 默认为5秒
            self.date = None
        else:
            self.time = None
            self.date = self.date_entry.get()

    def update_visibility(self, event):
        if self.pattern_var.get() == "Time":
            self.time_entry.grid()
            self.date_entry.grid_remove()
        else:
            self.time_entry.grid_remove()
            self.date_entry.grid()
      
# 保存文件弹窗
class SaveFileDialog(StyledDialog):
    def body(self, master):
        super().body(master)
        self.geometry("550x260")
        
        # 标签和输入行
        ttk.Label(master, text="请输入保存文件名: ").grid(row=0, pady=20)
        self.file_name_entry = ttk.Entry(master)
        self.file_name_entry.grid(row=0, column=1)
        
        # 提示文本框1
        prompt1_text = tk.Text(master, height=1, width=38, wrap=tk.WORD, bg='#080e23', fg='#fe764c', insertbackground='#fe764c', font=("Arial", 12))
        prompt1_text.insert(tk.END, "规则和日志将分别存储于后缀为TXT和LOG文件")
        prompt1_text.grid(row=1, columnspan=2, pady=10)
        
        # 提示文本框2
        prompt2_text = tk.Text(master, height=1, width=38, wrap=tk.WORD, bg='#080e23', fg='#fe764c', insertbackground='#fe764c', font=("Arial", 12))
        prompt2_text.insert(tk.END, "相应的规则和日志仅保存在本地且不会上传网络")
        prompt2_text.grid(row=2, columnspan=2, pady=20)
        
        return self.file_name_entry

    def apply(self):
        self.result = self.file_name_entry.get()

# 用户反馈弹窗
class FeedbackDialog(StyledDialog):
    def body(self, master):
        super().body(master)
        self.geometry("650x500")

        ttk.Label(master, text="请根据使用体验给软件评分:").grid(row=0, pady=20)

        # self.style.configure("TScale",  # 设置拖动条的样式
        #     troughcolor="#080e23",  # 背景颜色
        #     sliderrelief="flat",  # 设置拖动按钮的边框风格为"flat"
        #     sliderthickness=20  # 设置拖动按钮的宽度
        #     )
        
        # 创建一个可拖动的滑块来实现评分
        self.rating_var = tk.DoubleVar()
        rating_slider = tk.Scale(master, variable=self.rating_var, from_=1, to=10, orient="horizontal", 
                                bg='#0c1124', fg='#ee5f26', length=300, troughcolor="#080e23", font=("Courier", 14, "bold"))
        rating_slider.grid(row=1, columnspan=2, pady=15)

        ttk.Label(master, text="请提出您的使用感受或建议:").grid(row=2, pady=10)
        
        # 创建一个多行输入框
        self.suggestion_text = tk.Text(master, height=8, width=40, wrap=tk.WORD, bg='#0c1124', fg='#ee5f26', insertbackground='#ee5f26', font=("Courier", 14, "bold"))
        self.suggestion_text.grid(row=3, columnspan=2, pady=20)
        
        return rating_slider

    def apply(self):
        rating = self.rating_var.get()
        suggestion = self.suggestion_text.get(1.0, tk.END)

        messagebox.showinfo("谢谢", "感谢您的反馈！")

# 主界面及相关功能
class FirewallGUI(tk.Tk):

    def __init__(self):
        super().__init__() 

        # 窗口设置
        self.title("状态检测防火墙-翟XX(U2020XXXXX)")
        self.geometry("1504x846")  # 宽度 x 高度
        self.configure(bg='#2E2E2E')  # 深色背景

        # 加载背景图
        self.background_image = tk.PhotoImage(file="background.png")
        self.background_label = tk.Label(self, image=self.background_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # 设置ttk按钮的样式
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton",
                             background="#11192b",
                             foreground="#09fbff",
                             bordercolor="#ee5f26",
                             highlightthickness=0,
                             bd=2,  # 设置按钮的边框宽度
                             relief="raised",  # 设置按钮边框风格为"flat"
                             font=("Arial", 12, "bold")
                             )
        self.style.map("TButton",
                       background=[('pressed', '#27637b'), ('active', '#1f3b4e')],
                       foreground=[('pressed', '#09fbff'), ('active', '#09fbff')],
                       bordercolor=[('pressed', '#ee5f26'), ('active', '#ee5f26')]  # 设置按钮边框颜色
                       )
        self.style.configure("TLabel",
                     background="#080e23",
                     foreground="#12fdff",
                     font=("Arial", 12, "bold")
                     )
        self.style.configure("TEntry",
                     background="#080e23",
                     foreground="#fe764c",
                     insertbackground='#fe764c',  # 光标颜色
                     fieldbackground='#080e23',  # 输入框背景颜色
                     font=("Arial", 12)
                     )      

        # 显示登录对话框
        self.show_login_dialog()

    def create_widgets(self):
        # 标题标签
        title = tk.Label(self, text="", font=("Arial", 1), bg='#0c1124', fg="#ee5f26")
        title.pack(pady=30)

        # 按钮的框架
        frame_buttons = tk.Frame(self, bg='#070f24')
        frame_buttons.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=5)

        # TTK按钮
        btn_add = ttk.Button(frame_buttons, text="增加规则", command=self.add_rule)
        btn_delete = ttk.Button(frame_buttons, text="删除规则", command=self.delete_rule)
        btn_view = ttk.Button(frame_buttons, text="显示规则", command=self.view_rules)

        btn_addnat = ttk.Button(frame_buttons, text="增加NAT", command=self.add_nat)
        btn_deletenat = ttk.Button(frame_buttons, text="删除NAT", command=self.delete_nat)
        btn_viewnat = ttk.Button(frame_buttons, text="显示NAT", command=self.view_nat)

        btn_accept = ttk.Button(frame_buttons, text="默认接受", command=self.set_accept)
        btn_drop = ttk.Button(frame_buttons, text="默认丢弃", command=self.set_drop)
        btn_connect = ttk.Button(frame_buttons, text="显示连接", command=self.view_connect)

        btn_logs = ttk.Button(frame_buttons, text="显示日志", command=self.view_logs)
        btn_log = ttk.Button(frame_buttons, text="部分日志", command=self.view_log)
        btn_save = ttk.Button(frame_buttons, text="保存内容", command=self.save_txt)

        btn_time = ttk.Button(frame_buttons, text="设置时间", command=self.set_time)
        btn_back = ttk.Button(frame_buttons, text="用户反馈", command=self.get_back)

        # 使用更多空间包装按钮
        btn_add.pack(fill=tk.X, pady=10)
        btn_delete.pack(fill=tk.X, pady=10)
        btn_view.pack(fill=tk.X, pady=10)

        btn_addnat.pack(fill=tk.X, pady=10)
        btn_deletenat.pack(fill=tk.X, pady=10)
        btn_viewnat.pack(fill=tk.X, pady=10)

        btn_accept.pack(fill=tk.X, pady=10)
        btn_drop.pack(fill=tk.X, pady=10)
        btn_connect.pack(fill=tk.X, pady=10)

        btn_logs.pack(fill=tk.X, pady=10)
        btn_log.pack(fill=tk.X, pady=10)
        btn_save.pack(fill=tk.X, pady=10)

        btn_time.pack(fill=tk.X, pady=10)
        btn_back.pack(fill=tk.X, pady=10)
 
        # 创建垂直窗格
        paned_window = ttk.Panedwindow(self, orient=tk.VERTICAL)
        paned_window.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 带有深色风格的规则显示文本部件
        self.text_rules = tk.Text(paned_window, wrap=tk.WORD, bg='#0c1124', fg='#ee5f26', insertbackground='#ee5f26', font=("Courier", 14, "bold"))
        paned_window.add(self.text_rules, weight=3)  # weight参数决定了初始时的比例

        # 带有深色风格的日志显示文本部件
        self.text_logs = tk.Text(paned_window, wrap=tk.WORD, bg='#0c1124', fg='#ee5f26', insertbackground='#ee5f26', font=("Courier", 14, "bold"))
        paned_window.add(self.text_logs, weight=5)  # weight参数决定了初始时的比例

        self.display_message()

    def display_message(self):
        # 检查文件是否存在
        if os.path.exists("myrules.txt"):
            with open("myrules.txt", "r") as file:
                content = file.read()

            # 清空text_rules文本框并插入文件内容
            self.text_rules.delete(1.0, tk.END)
            self.text_rules.insert(tk.END, content)
        else:
            self.text_rules.delete(1.0, tk.END)
            self.text_rules.insert(tk.END, "myrules.txt 文件不存在.")

        # 检查文件是否存在
        if os.path.exists("mylogs.txt"):
            with open("mylogs.txt", "r") as file:
                content = file.read()

            # 清空text_logs文本框并插入文件内容
            self.text_logs.delete(1.0, tk.END)
            self.text_logs.insert(tk.END, content)
        else:
            self.text_logs.delete(1.0, tk.END)
            self.text_logs.insert(tk.END, "mylogs.txt 文件不存在.")

    def show_login_dialog(self):
        # 创建登录框
        login_frame = tk.Frame(self, bg='#080e23', padx=20, pady=20)
        login_frame.place(relx=0.7, rely=0.3, relwidth=0.25, relheight=0.3)
        login_frame.configure(bg='#080e23', bd=5, relief="ridge")

        ttk.Label(login_frame, text="用户登录", font=("Arial", 24, "bold")).grid(row=0, columnspan=2, pady=10)
        ttk.Label(login_frame, text="请输入账号:", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=10, pady=5)
        ttk.Label(login_frame, text="请输入密码:", font=("Arial", 12, "bold")).grid(row=2, column=0, padx=10, pady=5)

        username_var = tk.StringVar(value="admin")
        password_var = tk.StringVar()

        ttk.Entry(login_frame, textvariable=username_var).grid(row=1, column=1, padx=5, pady=10)
        ttk.Entry(login_frame, textvariable=password_var, show='*').grid(row=2, column=1, padx=5, pady=5)

        def on_login_clicked():
            # 登录成功后
            self.background_label.destroy()  # 销毁背景图
            login_frame.destroy()           # 销毁登录框

            # 加载背景图
            self.background_image = tk.PhotoImage(file="background1.png")
            self.background_label = tk.Label(self, image=self.background_image)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

            self.create_widgets()           # 显示主界面内容


        ttk.Button(login_frame, text="立即登录", command=on_login_clicked).grid(row=3, column=0, padx=20, pady=15)
        ttk.Button(login_frame, text="退出程序", command=self.destroy).grid(row=3, column=1, padx=5, pady=15)

    def add_rule(self):
        self.view_rules()  # 调用view_rules方法
        dialog = RuleAddDialog(self, title="增加规则")  
        if hasattr(dialog, 'prev_rule_name'):
            prev_rule_name = dialog.prev_rule_name
            rule_name = dialog.rule_name
            src_ip = dialog.src_ip
            src_port = dialog.src_port
            dst_ip = dialog.dst_ip
            dst_port = dialog.dst_port
            protocol = dialog.protocol
            action = dialog.action
            log = dialog.log

            # 您现在可以使用这些值来执行您的逻辑
            process_input = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n".format(prev_rule_name, rule_name, src_ip, src_port, dst_ip, dst_port, protocol, action, log)
            process = subprocess.Popen(['./uapp', 'rule', 'add'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate(input=process_input.encode('utf-8'))
            
            self.view_rules()  # 调用view_rules方法
        else:
            print("Dialog did not complete successfully or OK was not pressed.")

    def delete_rule(self):
        self.view_rules()  # 调用view_rules方法
        dialog = DeleteRuleDialog(self, title="删除规则")
        if dialog.result:
            rule_name = dialog.result
            # 执行删除规则的操作
            process = subprocess.Popen(['./ctrl', 'rule', 'del', rule_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            self.view_rules()  # 调用view_rules方法

    def view_rules(self):
        # 执行命令并获取输出
        process = subprocess.Popen(['./ctrl', 'ls', 'rule'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        # 字节转为字符串
        output = stdout.decode('utf-8')
        
        # 清除文本部件并插入新内容
        self.text_rules.delete(1.0, tk.END)
        self.text_rules.insert(tk.END, "下面展示的是【防火墙规则】: \n")
        self.text_rules.insert(tk.END, output)
        self.text_rules.insert(tk.END, "                                                                                          (日期: 2023年10月29日)\n")       

    def add_nat(self):
        self.view_nat()  # 调用view_rules方法
        dialog = NatAddDialog(self, title="增加NAT规则")
        
        # 使用获取到的值
        src_ip = dialog.src_ip
        nat_ip = dialog.nat_ip
        nat_port = dialog.nat_port

        # 您现在可以使用这些值来执行您的逻辑
        process_input = "{}\n{}\n{}\n".format(src_ip, nat_ip, nat_port)
        process = subprocess.Popen(['./ctrl', 'nat', 'add'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(input=process_input.encode('utf-8'))
        
        self.view_nat()  # 调用view_nat方法

    def delete_nat(self):
        self.view_nat()  # 调用view_nat方法
        dialog = DeleteNatDialog(self, title="删除NAT规则")
        if dialog.result:
            nat_number = dialog.result
            # 执行删除NAT规则的操作
            process = subprocess.Popen(['./ctrl', 'nat', 'del', nat_number], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            self.view_nat()  # 调用view_nat方法

    def view_nat(self):
        # 执行命令并获取NAT规则的输出
        process = subprocess.Popen(['./ctrl', 'ls', 'nat'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        # 字节转为字符串
        output = stdout.decode('utf-8')
        
        # 清除文本部件并插入新内容
        self.text_rules.delete(1.0, tk.END)
        self.text_rules.insert(tk.END, "下面展示的是【NAT规则】: \n")
        self.text_rules.insert(tk.END, output)
        self.text_rules.insert(tk.END, "                                             (日期: 2023年10月29日)\n")       

    def set_accept(self):
        # 执行命令并设置默认行为为Accept
        process = subprocess.Popen(['./ctrl', 'rule', 'default', 'accept'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # 字节转为字符串
        output = stdout.decode('utf-8')

        # 显示命令执行的结果
        if process.returncode == 0:
            messagebox.showinfo("成功", "默认动作已设置为Accept")
        else:
            messagebox.showwarning("警告", output)

    def set_drop(self):
        # 执行命令并设置默认行为为Drop
        process = subprocess.Popen(['./ctrl', 'rule', 'default', 'drop'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # 字节转为字符串
        output = stdout.decode('utf-8')

        # 显示命令执行的结果
        if process.returncode == 0:
            messagebox.showinfo("成功", "默认动作已设置为Drop")
        else:
            messagebox.showwarning("警告", output)

    def view_connect(self):
        # 执行命令并获取当前已有连接的输出
        process = subprocess.Popen(['./ctrl', 'ls', 'connect'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # 字节转为字符串
        output = stdout.decode('utf-8')

        # 清除文本部件并插入新内容
        self.text_logs.delete(1.0, tk.END)
        self.text_logs.insert(tk.END, "下面展示的是【建立的连接】: \n")
        self.text_logs.insert(tk.END, output)
        self.text_logs.insert(tk.END, "                                                       (日期: 2023年10月29日)\n")

    def view_logs(self):
        # 执行命令并获取输出
        process = subprocess.Popen(['./ctrl', 'ls', 'log'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        # 字节转为字符串
        output = stdout.decode('utf-8')
        
        # 清除文本部件并插入新内容
        self.text_logs.delete(1.0, tk.END)
        self.text_logs.insert(tk.END, "下面展示的是【全部日志内容】: \n")
        self.text_logs.insert(tk.END, output)
        self.text_logs.insert(tk.END, "                                                                              (日期: 2023年10月29日)\n")       

    def view_log(self):
        # 执行命令并获取输出
        process = subprocess.Popen(['./ctrl', 'ls', 'log', '100'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        # 字节转为字符串
        output = stdout.decode('utf-8')
        
        # 清除文本部件并插入新内容
        self.text_logs.delete(1.0, tk.END)
        self.text_logs.insert(tk.END, "下面展示的是【部分日志内容】: \n")
        self.text_logs.insert(tk.END, output)
        self.text_logs.insert(tk.END, "                                                                              (日期: 2023年10月29日)\n")

    def save_txt(self):
        # 获取text_log部件中的内容
        content_rules = self.text_rules.get(1.0, tk.END)
        content_logs = self.text_logs.get(1.0, tk.END)

        # 使用自定义弹窗来要求用户输入文件名
        dialog = SaveFileDialog(self, title="保存内容")
        if dialog.result:
            filename = dialog.result

            with open(filename + '.txt', 'w', encoding='utf-8') as file:
                file.write(content_rules)
            with open(filename + '.log', 'w', encoding='utf-8') as file:
                file.write(content_logs)
            messagebox.showinfo("成功", "内容已保存到 {}.txt/.log".format(filename))
        else:
            messagebox.showwarning("警告", "未提供文件名, 内容未保存")

    def set_time(self):
        self.view_rules()  # 调用view_rules方法
        dialog = TimeSetDialog(self, title="设置时间")
        rule_name = dialog.rule_name

        # 清空内容并显示设置信息
        self.text_logs.delete(1.0, tk.END)
        self.text_logs.insert(tk.END, "下面展示的是【时间设置信息】: \n")
        self.text_logs.insert(tk.END, "-" * 96 + "\n")
        self.text_logs.insert(tk.END, "| Rule Name   | Create Date        | Pattern         | Delete Time        | Delete Date        |\n")
        self.text_logs.insert(tk.END, "-" * 96 + "\n")
        if dialog.pattern_var.get() == "Time":
            time_delay = dialog.time           
            # 输出至text_logs
            self.text_logs.insert(tk.END, "| {:<10}  | 2023/10/29         | Time            | {:<6} seconds     | no                 |\n".format(rule_name, time_delay))
            self.text_logs.insert(tk.END, "-" * 96 + "\n")
            self.text_logs.insert(tk.END, "                                                                           (日期: 2023年10月29日)\n")
            self.after(time_delay * 1000, self.delayed_delete_rule, rule_name)
        else:
            # 输出至text_logs
            self.text_logs.insert(tk.END, "| {:<10}  | 2023/10/29         | Date            | no                 | {:<15}    |\n".format(rule_name, dialog.date))
            self.text_logs.insert(tk.END, "-" * 96 + "\n")
            self.text_logs.insert(tk.END, "                                                                           (日期: 2023年10月29日)\n")

    def delayed_delete_rule(self, rule_name):
        process = subprocess.Popen(['./ctrl', 'rule', 'del', rule_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        self.view_rules()  # 调用view_rules方法
        self.text_logs.delete(1.0, tk.END)
        self.text_logs.insert(tk.END, "下面展示的是【时间设置信息】: \n")
        self.text_logs.insert(tk.END, "-" * 96 + "\n")       
        self.text_logs.insert(tk.END, "这里没有任何时间设置信息.\n")
        self.text_logs.insert(tk.END, "-" * 96 + "\n")
        self.text_logs.insert(tk.END, "                                                                           (日期: 2023年10月29日)\n")

    def get_back(self):
        dialog = FeedbackDialog(self, title="用户反馈")

if __name__ == "__main__":
    app = FirewallGUI()
    app.mainloop()

