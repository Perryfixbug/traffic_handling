import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # dùng sau này để hiển thị frame video


class TrafficAppFrame:
    def __init__(self, root):
        self.root = root
        self.root.title("Traffic Monitoring Dashboard")

        # 🔹 Kích thước cửa sổ & cho phép kéo to/nhỏ
        self.root.geometry("1400x800")   # cửa sổ ban đầu
        self.root.minsize(1200, 700)     # không cho nhỏ hơn mức này
        self.root.resizable(True, True)  # cho phép kéo resize

        # Màu nền tổng thể mang hơi hướng "đường xá"
        self.root.configure(bg="#1b1f27")  # xám đậm như mặt đường ban đêm

        self.setup_style()
        self.build_ui()

    def setup_style(self):
        """Thiết lập theme màu cho giao diện."""
        style = ttk.Style()
        # thử dùng theme 'clam' để màu mè hơn 'default'
        style.theme_use("clam")

        # Màu cho các LabelFrame (khung Video / Stats)
        style.configure(
            "TLabelframe",
            background="#1b1f27",
            foreground="#f0f0f0",
            borderwidth=1
        )
        style.configure(
            "TLabelframe.Label",
            background="#1b1f27",
            foreground="#f9f9f9",
            font=("Segoe UI", 11, "bold")
        )

        # Màu cho Label, Button…
        style.configure(
            "TLabel",
            background="#1b1f27",
            foreground="#e0e0e0",
            font=("Segoe UI", 10)
        )
        style.configure(
            "TButton",
            font=("Segoe UI", 10, "bold")
        )

    # ======================= UI STRUCTURE =========================
    def build_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Cho phép 2 cột co giãn theo cửa sổ
        main_frame.columnconfigure(0, weight=3)  # video to
        main_frame.columnconfigure(1, weight=2)  # panel bên phải
        main_frame.rowconfigure(0, weight=1)

        # ========== KHUNG VIDEO ==========
        video_frame = ttk.LabelFrame(main_frame, text=" Live Video ", padding=10)
        video_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Placeholder khung video
        self.video_label = tk.Label(
            video_frame,
            text="VIDEO HERE",
            bg="#000000",
            fg="#00ff66",                 # xanh lá kiểu đèn giao thông
            font=("Consolas", 20, "bold"),
            bd=2,
            relief="sunken"
        )
        self.video_label.pack(fill="both", expand=True)

        # ========== KHUNG THỐNG KÊ ==========
        stats_frame = ttk.LabelFrame(main_frame, text=" Vehicle Statistics ", padding=10)
        stats_frame.grid(row=0, column=1, sticky="nsew")

        # Dòng trạng thái tổng thể (như header nhỏ)
        status_header = tk.Label(
            stats_frame,
            text="REAL-TIME TRAFFIC STATUS",
            bg="#1b1f27",
            fg="#ffcc00",
            font=("Segoe UI", 11, "bold")
        )
        status_header.grid(row=0, column=0, columnspan=2, sticky="we", pady=(0, 10))

        # Current vehicle count
        ttk.Label(stats_frame, text="Current Vehicles:")\
            .grid(row=1, column=0, sticky="w")
        self.current_count_var = tk.StringVar(value="0")
        lbl_curr = ttk.Label(stats_frame, textvariable=self.current_count_var)
        lbl_curr.grid(row=1, column=1, sticky="w")
        lbl_curr.configure(font=("Segoe UI", 14, "bold"))

        # Total unique IDs
        ttk.Label(stats_frame, text="Total Unique IDs:")\
            .grid(row=2, column=0, sticky="w", pady=(5, 0))
        self.unique_count_var = tk.StringVar(value="0")
        lbl_uni = ttk.Label(stats_frame, textvariable=self.unique_count_var)
        lbl_uni.grid(row=2, column=1, sticky="w", pady=(5, 0))
        lbl_uni.configure(font=("Segoe UI", 14, "bold"))

        # Divider
        sep = ttk.Separator(stats_frame, orient="horizontal")
        sep.grid(row=3, column=0, columnspan=2, sticky="we", pady=10)

        # List of active IDs
        ttk.Label(stats_frame, text="Active Vehicle IDs:")\
            .grid(row=4, column=0, columnspan=2, sticky="w")

        self.id_listbox = tk.Listbox(
            stats_frame,
            height=18,
            width=26,
            bg="#11141b",
            fg="#00e0ff",          # xanh dương neon
            selectbackground="#00ff66",
            selectforeground="#000000",
            font=("Consolas", 11),
            bd=2,
            relief="sunken"
        )
        self.id_listbox.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=(5, 10))

        # Làm cho listbox co giãn theo chiều dọc
        stats_frame.rowconfigure(5, weight=1)
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)

        # ========== THANH NÚT ĐIỀU KHIỂN DƯỚI CÙNG ==========
        control_frame = ttk.Frame(main_frame, padding=5)
        control_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))

        # Nút kiểu giao thông (Start = xanh, Stop = đỏ, Reset = vàng)
        self.btn_start = ttk.Button(control_frame, text="Start")
        self.btn_start.grid(row=0, column=0, padx=5)

        self.btn_pause = ttk.Button(control_frame, text="Pause")
        self.btn_pause.grid(row=0, column=1, padx=5)

        self.btn_reset = ttk.Button(control_frame, text="Reset")
        self.btn_reset.grid(row=0, column=2, padx=5)

        self.btn_quit = ttk.Button(control_frame, text="Quit", command=self.root.destroy)
        self.btn_quit.grid(row=0, column=3, padx=5)

        # Có thể tự tô màu nền dưới nút nếu muốn
        for child in control_frame.winfo_children():
            child.configure(width=12)

    # ======================= PUBLIC API (bạn dùng sau này) =========================

    def set_video_image(self, img: ImageTk.PhotoImage):
        """
        DÙNG CHO VIDEO:
        - Sau này bạn xử lý frame video bằng OpenCV -> chuyển sang PIL -> ImageTk.PhotoImage
        - Rồi gọi hàm này để hiển thị frame mới lên self.video_label
        """
        self.video_label.imgtk = img      # giữ reference tránh bị GC
        self.video_label.configure(image=img, text="")

    def update_stats(self, current_count: int, unique_count: int, id_list):
        """
        DÙNG CHO LOGIC THỐNG KÊ:
        - current_count: số xe đang được theo dõi trong frame hiện tại
        - unique_count: tổng số ID duy nhất xuất hiện từ đầu tới giờ
        - id_list: danh sách các ID đang active, ví dụ [1, 2, 5, 7]
        """
        self.current_count_var.set(str(current_count))
        self.unique_count_var.set(str(unique_count))

        self.id_listbox.delete(0, tk.END)
        for vid in id_list:
            self.id_listbox.insert(tk.END, f"ID {vid}")


# ======================= ENTRY POINT =========================
if __name__ == "__main__":
    root = tk.Tk()
    app = TrafficAppFrame(root)
    root.mainloop()
