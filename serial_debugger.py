import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import serial
import serial.tools.list_ports
import threading
import time
from datetime import datetime
import queue
import re

class SerialDebugger:
    def __init__(self, root):
        self.root = root
        self.root.title("Lite串口调试助手")
        self.root.geometry("800x650")
        
        # 设置窗口最小尺寸
        self.root.minsize(800, 650)
        
        # 串口对象
        self.serial_port = None
        self.is_receiving = False
        
        # 接收数据缓存
        self.receive_buffer = []
        self.last_receive_time = 0
        
        # 文件保存相关
        self.save_file = None
        self.is_saving = False
        
        # 创建主框架并设置权重，使窗口可自适应
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.create_widgets()
        self.update_ports()
        
    def create_widgets(self):
        # 串口设置框架
        settings_frame = ttk.LabelFrame(self.main_frame, text="串口设置", padding="5")
        settings_frame.pack(fill="x", pady=5)
        
        # 第一行：串口选择和波特率
        ttk.Label(settings_frame, text="串口:").grid(row=0, column=0, padx=2)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(settings_frame, textvariable=self.port_var, width=35)
        self.port_combo.grid(row=0, column=1, padx=2)
        
        # 刷新按钮
        ttk.Button(settings_frame, text="刷新", command=self.update_ports).grid(row=0, column=2, padx=2)
        
        # 波特率选择
        ttk.Label(settings_frame, text="波特率:").grid(row=0, column=3, padx=2)
        self.baud_var = tk.StringVar(value="115200")
        self.baud_combo = ttk.Combobox(settings_frame, textvariable=self.baud_var, width=8,
                                     values=["4800", "9600", "19200", "38400", "57600", "115200", 
                                            "230400", "460800", "500000", "576000", "921600", "1000000"])
        self.baud_combo.grid(row=0, column=4, padx=2)
        
        # 打开/关闭串口按钮
        self.connect_button = ttk.Button(settings_frame, text="打开串口", command=self.toggle_connection)
        self.connect_button.grid(row=0, column=5, padx=2)
        
        # 第二行：数据位、停止位、校验位
        bits_frame = ttk.Frame(settings_frame)
        bits_frame.grid(row=1, column=0, columnspan=6, pady=5, sticky="w")
        
        # 数据位
        ttk.Label(bits_frame, text="数据位:").pack(side="left", padx=0)
        self.data_bits_var = tk.StringVar(value="8")
        self.data_bits_combo = ttk.Combobox(bits_frame, textvariable=self.data_bits_var, width=4,
                                          values=["5", "6", "7", "8"])
        self.data_bits_combo.pack(side="left", padx=0)
        
        # 停止位
        ttk.Label(bits_frame, text="停止位:").pack(side="left", padx=0)
        self.stop_bits_var = tk.StringVar(value="1")
        self.stop_bits_combo = ttk.Combobox(bits_frame, textvariable=self.stop_bits_var, width=4,
                                          values=["1", "1.5", "2"])
        self.stop_bits_combo.pack(side="left", padx=0)
        
        # 校验位
        ttk.Label(bits_frame, text="校验位:").pack(side="left", padx=0)
        self.parity_var = tk.StringVar(value="N")
        self.parity_combo = ttk.Combobox(bits_frame, textvariable=self.parity_var, width=4,
                                       values=["N", "E", "O", "M", "S"])
        self.parity_combo.pack(side="left", padx=0)
        
        # 接收区框架
        receive_frame = ttk.LabelFrame(self.main_frame, text="接收区", padding="5")
        receive_frame.pack(fill="both", expand=True, pady=5)
        
        # 创建接收区容器框架
        receive_container = ttk.Frame(receive_frame)
        receive_container.pack(fill="both", expand=True)
        
        # 接收区文本和滚动条
        self.receive_text = tk.Text(receive_container, wrap=tk.WORD, height=8)
        self.receive_text.pack(side="left", fill="both", expand=True)
        
        # 添加滚动条
        receive_scrollbar = ttk.Scrollbar(receive_container, orient="vertical", command=self.receive_text.yview)
        receive_scrollbar.pack(side="right", fill="y")
        
        # 配置文本区域与滚动条的关联
        self.receive_text.configure(yscrollcommand=receive_scrollbar.set)
        
        # 接收区控制框架
        receive_control_frame = ttk.Frame(receive_frame)
        receive_control_frame.pack(fill="x")
        
        # 清空按钮
        ttk.Button(receive_control_frame, text="清空接收区", command=self.clear_receive).pack(side="left", padx=5)
        
        # 显示模式选择
        self.display_mode_var = tk.StringVar(value="ASCII")
        ttk.Radiobutton(receive_control_frame, text="ASCII", variable=self.display_mode_var, 
                       value="ASCII").pack(side="left", padx=5)
        ttk.Radiobutton(receive_control_frame, text="HEX", variable=self.display_mode_var, 
                       value="HEX").pack(side="left", padx=5)
        
        # 时间戳选项
        self.timestamp_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(receive_control_frame, text="时间戳", variable=self.timestamp_var).pack(side="left", padx=5)
        
        # 分包显示选项
        self.packet_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(receive_control_frame, text="分包显示", variable=self.packet_var).pack(side="left", padx=5)
        
        # 超时设置
        ttk.Label(receive_control_frame, text="超时(ms):").pack(side="left", padx=2)
        self.timeout_var = tk.StringVar(value="20")
        self.timeout_entry = ttk.Entry(receive_control_frame, textvariable=self.timeout_var, width=4)
        self.timeout_entry.pack(side="left", padx=2)
        
        # 自动换行选项
        self.auto_wrap_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(receive_control_frame, text="自动换行", variable=self.auto_wrap_var,
                       command=self.toggle_wrap).pack(side="left", padx=5)
        
        # 文件保存相关控件
        self.save_file_var = tk.StringVar(value="未选择文件")
        self.save_file_label = ttk.Label(receive_control_frame, textvariable=self.save_file_var)
        self.save_file_label.pack(side="left", padx=5)
        
        self.save_button = ttk.Button(receive_control_frame, text="选择保存文件", command=self.select_save_file)
        self.save_button.pack(side="left", padx=5)
        
        self.save_status_var = tk.StringVar(value="未保存")
        self.save_status_label = ttk.Label(receive_control_frame, textvariable=self.save_status_var)
        self.save_status_label.pack(side="left", padx=5)
        
        # 发送区框架
        send_frame = ttk.LabelFrame(self.main_frame, text="发送区", padding="5")
        send_frame.pack(fill="x", pady=5)
        
        # 发送区文本
        self.send_text = tk.Text(send_frame, wrap=tk.WORD, height=3)
        self.send_text.pack(fill="x", pady=(0, 5))
        
        # 发送按钮框架
        send_button_frame = ttk.Frame(send_frame)
        send_button_frame.pack(fill="x")
        
        # 循环发送控制
        loop_frame = ttk.Frame(send_button_frame)
        loop_frame.pack(side="left", padx=5)
        
        # 循环发送选择框
        self.loop_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(loop_frame, text="循环发送", variable=self.loop_var,
                       command=self.toggle_loop_send).pack(side="left")
        
        # 延时设置
        ttk.Label(loop_frame, text="延时(ms):").pack(side="left", padx=2)
        self.delay_var = tk.StringVar(value="1000")
        self.delay_entry = ttk.Entry(loop_frame, textvariable=self.delay_var, width=6)
        self.delay_entry.pack(side="left", padx=2)
        
        # 发送按钮
        ttk.Button(send_button_frame, text="发送", command=self.send_data).pack(side="right", padx=5)
        
        # 循环发送线程
        self.loop_thread = None
        self.is_loop_sending = False
        
    def update_ports(self):
        """更新可用串口列表"""
        ports = []
        for port in serial.tools.list_ports.comports():
            # 获取串口描述信息
            description = f"{port.device} - {port.description}"
            ports.append(description)
        
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.set(ports[0])
            
    def toggle_connection(self):
        """打开/关闭串口"""
        if self.serial_port is None:
            try:
                # 从描述中提取实际的端口名
                port_desc = self.port_var.get()
                port = port_desc.split(' - ')[0]  # 获取实际的端口名
                
                baud = int(self.baud_var.get())
                data_bits = int(self.data_bits_var.get())
                stop_bits = float(self.stop_bits_var.get())
                parity = self.parity_var.get()
                
                self.serial_port = serial.Serial(
                    port=port,
                    baudrate=baud,
                    bytesize=data_bits,
                    stopbits=stop_bits,
                    parity=parity,
                    timeout=0.1
                )
                
                self.connect_button.config(text="关闭串口")
                self.is_receiving = True
                threading.Thread(target=self.receive_data, daemon=True).start()
                messagebox.showinfo("成功", "串口打开成功！")
                
            except Exception as e:
                messagebox.showerror("错误", f"打开串口失败：{str(e)}")
                self.serial_port = None
        else:
            self.is_receiving = False
            self.serial_port.close()
            self.serial_port = None
            self.connect_button.config(text="打开串口")
            messagebox.showinfo("成功", "串口已关闭！")
            
    def receive_data(self):
        """接收数据线程"""
        while self.is_receiving:
            if self.serial_port.in_waiting:
                current_time = time.time()
                data = self.serial_port.read(self.serial_port.in_waiting)
                
                # 检查是否需要分包显示
                if self.packet_var.get():
                    try:
                        timeout = int(self.timeout_var.get()) / 1000  # 转换为秒
                        if current_time - self.last_receive_time > timeout:
                            # 超时，显示之前的数据
                            if self.receive_buffer:
                                self._display_received_data(b''.join(self.receive_buffer))
                                self.receive_buffer = []
                    except ValueError:
                        pass
                    
                    self.receive_buffer.append(data)
                    self.last_receive_time = current_time
                else:
                    self._display_received_data(data)
                    
            time.sleep(0.01)
    
    def _display_received_data(self, data):
        """显示接收到的数据"""
        if not data:
            return
            
        # 准备显示文本
        text = ""
        
        # 添加时间戳
        if self.timestamp_var.get():
            # 使用datetime获取当前时间并格式化
            current_time = datetime.now()
            timestamp = current_time.strftime("%H:%M:%S.%f")[:-3]  # 只保留3位毫秒
            text += f"[{timestamp}] "
        
        # 转换数据格式
        if self.display_mode_var.get() == "ASCII":
            text += data.decode('utf-8', errors='ignore')
        else:
            text += ' '.join([f'{b:02X}' for b in data])
        
        # 添加换行
        text += '\n'
        
        # 显示数据
        self.receive_text.insert(tk.END, text)
        self.receive_text.see(tk.END)
        
        # 保存到文件
        if self.is_saving and self.save_file:
            try:
                self.save_file.write(text)
                self.save_file.flush()
            except Exception as e:
                messagebox.showerror("错误", f"保存数据失败：{str(e)}")
                self.is_saving = False
                self.save_status_var.set("保存失败")
                self.save_button.config(text="选择保存文件")
                if self.save_file:
                    self.save_file.close()
                    self.save_file = None
    
    def toggle_loop_send(self):
        """切换循环发送状态"""
        if self.loop_var.get():
            try:
                delay = int(self.delay_var.get())
                if delay < 10:
                    messagebox.showerror("错误", "延时不能小于10ms！")
                    self.loop_var.set(False)
                    return
                
                self.is_loop_sending = True
                self.loop_thread = threading.Thread(target=self.loop_send_data, daemon=True)
                self.loop_thread.start()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的延时值！")
                self.loop_var.set(False)
        else:
            self.is_loop_sending = False
            if self.loop_thread:
                self.loop_thread.join(timeout=0.1)
                self.loop_thread = None
    
    def loop_send_data(self):
        """循环发送数据线程"""
        while self.is_loop_sending:
            try:
                data = self.send_text.get("1.0", tk.END).strip()
                if data and self.serial_port:
                    self.serial_port.write(data.encode())
                delay = int(self.delay_var.get()) / 1000  # 转换为秒
                time.sleep(delay)
            except Exception as e:
                messagebox.showerror("错误", f"循环发送失败：{str(e)}")
                self.loop_var.set(False)
                self.is_loop_sending = False
                break
    
    def send_data(self):
        """发送数据"""
        if self.serial_port is None:
            messagebox.showerror("错误", "请先打开串口！")
            return
            
        try:
            data = self.send_text.get("1.0", tk.END).strip()
            if data:
                self.serial_port.write(data.encode())
        except Exception as e:
            messagebox.showerror("错误", f"发送数据失败：{str(e)}")
            
    def clear_receive(self):
        """清空接收区"""
        self.receive_text.delete("1.0", tk.END)
        self.receive_buffer = []  # 清空接收缓存
        self.last_receive_time = 0  # 重置最后接收时间
        if self.is_saving:
            self.save_file.write("\n=== 清空接收区 ===\n")  # 在文件中添加分隔标记
    
    def toggle_wrap(self):
        """切换自动换行"""
        if self.auto_wrap_var.get():
            self.receive_text.config(wrap=tk.WORD)
        else:
            self.receive_text.config(wrap=tk.NONE)

    def select_save_file(self):
        """选择保存文件"""
        if self.is_saving:
            self.is_saving = False
            self.save_status_var.set("未保存")
            self.save_button.config(text="选择保存文件")
            if self.save_file:
                self.save_file.close()
                self.save_file = None
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            title="选择保存文件"
        )
        
        if file_path:
            try:
                self.save_file = open(file_path, 'a', encoding='utf-8')
                self.save_file_var.set(file_path)
                self.is_saving = True
                self.save_status_var.set("正在保存")
                self.save_button.config(text="停止保存")
            except Exception as e:
                messagebox.showerror("错误", f"无法创建文件：{str(e)}")
                self.save_file = None
                self.save_file_var.set("未选择文件")
                self.save_status_var.set("未保存")
                self.save_button.config(text="选择保存文件")

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialDebugger(root)
    root.mainloop() 