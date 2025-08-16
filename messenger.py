import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import pyautogui
import os
import sys

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("自动化点击工具")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # 尝试设置窗口图标
        try:
            if getattr(sys, 'frozen', False):
                # 打包后的exe路径
                base_path = sys._MEIPASS
            else:
                # 普通脚本路径
                base_path = os.path.dirname(os.path.abspath(__file__))
                
            icon_path = os.path.join(base_path, "message1.ico")
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"无法加载图标: {e}")

        # 位置存储变量
        self.pos1 = None
        self.pos2 = None
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        # 输入字符串
        ttk.Label(self.root, text="输入内容:").pack(pady=(10, 0), anchor="w", padx=20)
        self.entry_str = ttk.Entry(self.root, width=40)
        self.entry_str.pack(pady=(0, 10), padx=20, fill="x")
        
        # 输入点击次数
        ttk.Label(self.root, text="点击次数:").pack(anchor="w", padx=20)
        self.spin_count = ttk.Spinbox(self.root, from_=1, to=100, width=5)
        self.spin_count.pack(anchor="w", padx=20)
        self.spin_count.set(5)
        
        # 位置记录区域
        frame_pos = ttk.Frame(self.root)
        frame_pos.pack(pady=20, padx=20, fill="x")
        
        # 位置1按钮和状态
        self.btn_pos1 = ttk.Button(frame_pos, text="记录位置1", command=self.start_record_pos1)
        self.btn_pos1.grid(row=0, column=0, padx=(0, 10))
        self.lbl_pos1_status = ttk.Label(frame_pos, text="未记录")
        self.lbl_pos1_status.grid(row=0, column=1)
        
        # 位置2按钮和状态
        self.btn_pos2 = ttk.Button(frame_pos, text="记录位置2", command=self.start_record_pos2, state="disabled")
        self.btn_pos2.grid(row=1, column=0, padx=(0, 10), pady=10)
        self.lbl_pos2_status = ttk.Label(frame_pos, text="未记录")
        self.lbl_pos2_status.grid(row=1, column=1, pady=10)
        
        # 确认按钮
        self.btn_confirm = ttk.Button(frame_pos, text="确认位置", command=self.confirm_positions, state="disabled")
        self.btn_confirm.grid(row=2, column=0, columnspan=2, pady=10)
        
        # 执行按钮
        self.btn_execute = ttk.Button(self.root, text="开始执行", command=self.start_execution, state="disabled")
        self.btn_execute.pack(pady=10)
        
        # 状态栏
        self.status_var = tk.StringVar(value="准备就绪")
        ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w").pack(
            side="bottom", fill="x", padx=10, pady=10)
    
    def start_record_pos1(self):
        self.status_var.set("请在1秒内将鼠标移动到位置1...")
        self.btn_pos1.config(state="disabled")
        threading.Thread(target=self.record_position, args=(1,), daemon=True).start()
    
    def start_record_pos2(self):
        self.status_var.set("请在1秒内将鼠标移动到位置2...")
        self.btn_pos2.config(state="disabled")
        threading.Thread(target=self.record_position, args=(2,), daemon=True).start()
    
    def record_position(self, pos_num):
        time.sleep(1)  # 给用户1秒时间移动鼠标
        x, y = pyautogui.position()
        
        if pos_num == 1:
            self.pos1 = (x, y)
            self.root.after(0, lambda: self.lbl_pos1_status.config(text=f"已记录: ({x}, {y})"))
            self.root.after(0, lambda: self.btn_pos2.config(state="normal"))
            self.root.after(0, lambda: self.status_var.set("位置1已记录。请记录位置2"))
        elif pos_num == 2:
            self.pos2 = (x, y)
            self.root.after(0, lambda: self.lbl_pos2_status.config(text=f"已记录: ({x}, {y})"))
            self.root.after(0, lambda: self.btn_confirm.config(state="normal"))
            self.root.after(0, lambda: self.status_var.set("位置2已记录。请确认位置"))
    
    def confirm_positions(self):
        self.status_var.set("位置已确认。准备执行")
        self.btn_confirm.config(state="disabled")
        self.btn_execute.config(state="normal")
    
    def start_execution(self):
        # 获取输入值
        text = self.entry_str.get()
        try:
            count = int(self.spin_count.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return
        
        if not text:
            messagebox.showerror("错误", "请输入内容")
            return
        
        if self.pos1 is None or self.pos2 is None:
            messagebox.showerror("错误", "请先记录两个位置")
            return
        
        # 禁用界面并开始执行
        self.toggle_ui_state(False)
        self.status_var.set("执行中...请勿操作鼠标键盘")
        threading.Thread(target=self.execute_actions, args=(text, count), daemon=True).start()
    
    def execute_actions(self, text, count):
        try:
            for i in range(count):
                # 点击位置1
                pyautogui.click(self.pos1[0], self.pos1[1])
                time.sleep(0.2)
                
                # 输入文本
                pyautogui.write(text, interval=0.05)
                time.sleep(0.2)
                
                # 点击位置2
                pyautogui.click(self.pos2[0], self.pos2[1])
                time.sleep(0.2)
                
                # 更新状态
                self.root.after(0, lambda idx=i+1: self.status_var.set(f"执行进度: {idx}/{count}"))
            
            self.root.after(0, lambda: self.status_var.set(f"完成! 已执行 {count} 次操作"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"执行过程中出错: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.toggle_ui_state(True))
    
    def toggle_ui_state(self, enabled):
        state = "normal" if enabled else "disabled"
        self.entry_str.config(state=state)
        self.spin_count.config(state=state)
        self.btn_pos1.config(state=state if self.pos1 is None else "disabled")
        self.btn_pos2.config(state=state if self.pos1 and not self.pos2 else "disabled")
        self.btn_confirm.config(state=state if self.pos1 and self.pos2 else "disabled")
        self.btn_execute.config(state=state if self.pos1 and self.pos2 else "disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
