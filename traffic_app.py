import tkinter as tk

# ================== THAM SỐ ĐIỀU KHIỂN ==================
TICK_MS = 500       # mỗi bước mô phỏng: 500 ms
MIN_GREEN_TIME = 5  # số tick tối thiểu cho 1 pha đèn xanh
MAX_GREEN_TIME = 20 # số tick tối đa (tránh 1 phía xanh mãi)


class TrafficController:
    """
    Bộ điều khiển logic đèn giao thông (chỉ pha đèn, không sinh xe).
    2 pha:
    - phase = 0: Bắc-Nam xanh, Đông-Tây đỏ
    - phase = 1: Đông-Tây xanh, Bắc-Nam đỏ
    """
    def __init__(self):
        self.phase = 0           # 0: NS xanh, 1: EW xanh
        self.green_ticks = 0     # đã bao nhiêu tick ở pha hiện tại
        self.tick_count = 0      # tổng số tick (thời gian mô phỏng)

    def should_switch_phase(self):
        """
        Quyết định có nên chuyển pha không.
        Ở đây mình giữ đơn giản:
        - Bắt buộc giữ ít nhất MIN_GREEN_TIME tick
        - Nếu vượt MAX_GREEN_TIME thì chuyển pha
        Bạn có thể sửa hàm này để dùng logic riêng (ưu tiên, dữ liệu từ video, v.v.)
        """
        if self.green_ticks < MIN_GREEN_TIME:
            return False
        if self.green_ticks >= MAX_GREEN_TIME:
            return True
        # === CHỖ NÀY BẠN CÓ THỂ THÊM LOGIC RIÊNG ===
        # Ví dụ: nếu video phát hiện hướng Đông-Tây đang rất đông -> return True
        return False

    def switch_phase(self):
        """Chuyển pha đèn."""
        self.phase = 1 - self.phase
        self.green_ticks = 0

    def step(self):
        """
        Thực hiện một bước mô phỏng:
        - Tăng thời gian
        - Quyết định có chuyển pha không
        """
        self.tick_count += 1
        self.green_ticks += 1

        if self.should_switch_phase():
            self.switch_phase()


class TrafficApp(tk.Tk):
    """
    Giao diện Tkinter cho mô phỏng:
    - Hiển thị đèn giao thông cho 2 hướng
    - Có nút Start / Pause / Reset
    - Bạn có thể dùng controller.phase để điều khiển video ở chỗ khác
    """
    def __init__(self):
        super().__init__()
        self.title("Mô phỏng điều phối đèn giao thông (Light only)")
        self.resizable(False, False)

        self.controller = TrafficController()
        self.running = False
        self.after_id = None

        self.build_ui()

    def build_ui(self):
        main_frame = tk.Frame(self, padx=10, pady=10)
        main_frame.pack()

        # ===== TIÊU ĐỀ =====
        title_label = tk.Label(
            main_frame,
            text="ĐIỀU PHỐI ĐÈN GIAO THÔNG",
            font=("Helvetica", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # ===== ĐÈN GIAO THÔNG =====
        lights_frame = tk.Frame(main_frame)
        lights_frame.grid(row=1, column=0, padx=10)

        tk.Label(lights_frame, text="ĐÈN", font=("Helvetica", 12, "bold"))\
            .pack(pady=(0, 5))

        self.ns_light_label = tk.Label(
            lights_frame, text="Bắc-Nam",
            width=12, font=("Helvetica", 12), relief="groove"
        )
        self.ns_light_label.pack(pady=3)

        self.ew_light_label = tk.Label(
            lights_frame, text="Đông-Tây",
            width=12, font=("Helvetica", 12), relief="groove"
        )
        self.ew_light_label.pack(pady=3)

        # ===== THÔNG TIN PHA / THỜI GIAN =====
        info_frame = tk.Frame(main_frame)
        info_frame.grid(row=1, column=1, padx=10)

        tk.Label(info_frame, text="THÔNG TIN", font=("Helvetica", 12, "bold"))\
            .grid(row=0, column=0, columnspan=2, pady=(0, 5))

        tk.Label(info_frame, text="Pha hiện tại: ").grid(row=1, column=0, sticky="e")
        self.phase_value = tk.Label(info_frame, text="Bắc-Nam xanh", width=15)
        self.phase_value.grid(row=1, column=1, sticky="w")

        tk.Label(info_frame, text="Tick pha xanh: ").grid(row=2, column=0, sticky="e")
        self.green_tick_value = tk.Label(info_frame, text="0", width=5)
        self.green_tick_value.grid(row=2, column=1, sticky="w")

        tk.Label(info_frame, text="Tổng tick: ").grid(row=3, column=0, sticky="e")
        self.tick_value = tk.Label(info_frame, text="0", width=5)
        self.tick_value.grid(row=3, column=1, sticky="w")

        # ===== NÚT ĐIỀU KHIỂN =====
        control_frame = tk.Frame(main_frame, pady=10)
        control_frame.grid(row=2, column=0, columnspan=2)

        self.start_button = tk.Button(
            control_frame, text="Start",
            width=10, command=self.toggle_start
        )
        self.start_button.grid(row=0, column=0, padx=5)

        reset_button = tk.Button(
            control_frame, text="Reset",
            width=10, command=self.reset
        )
        reset_button.grid(row=0, column=1, padx=5)

        quit_button = tk.Button(
            control_frame, text="Quit",
            width=10, command=self.destroy
        )
        quit_button.grid(row=0, column=2, padx=5)

        self.update_ui()

    def toggle_start(self):
        if self.running:
            self.running = False
            self.start_button.config(text="Start")
            if self.after_id is not None:
                self.after_cancel(self.after_id)
                self.after_id = None
        else:
            self.running = True
            self.start_button.config(text="Pause")
            self.schedule_step()

    def schedule_step(self):
        if self.running:
            self.after_id = self.after(TICK_MS, self.simulation_step)

    def simulation_step(self):
        # Gọi logic đèn
        self.controller.step()

        # === CHỖ NÀY BẠN CÓ THỂ GỌI LOGIC VIDEO / XE ===
        # Ví dụ: đọc controller.phase và gửi tín hiệu sang thread OpenCV
        # phase = self.controller.phase

        self.update_ui()
        self.schedule_step()

    def reset(self):
        self.running = False
        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None
        self.start_button.config(text="Start")
        self.controller = TrafficController()
        self.update_ui()

    def update_ui(self):
        # Cập nhật màu đèn theo phase
        if self.controller.phase == 0:
            # Bắc-Nam xanh
            self.ns_light_label.config(bg="green", fg="white")
            self.ew_light_label.config(bg="red", fg="white")
            self.phase_value.config(text="Bắc-Nam xanh")
        else:
            # Đông-Tây xanh
            self.ns_light_label.config(bg="red", fg="white")
            self.ew_light_label.config(bg="green", fg="white")
            self.phase_value.config(text="Đông-Tây xanh")

        # Cập nhật tick
        self.green_tick_value.config(text=str(self.controller.green_ticks))
        self.tick_value.config(text=str(self.controller.tick_count))


if __name__ == "__main__":
    app = TrafficApp()
    app.mainloop()
