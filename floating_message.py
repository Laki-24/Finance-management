def show_floating_message(root, message_text, color="#00ffff"):
    label = tk.Label(
        root,
        text=message_text,
        font=("Helvetica", 14, "bold"),
        fg=color,
        bg=root.cget("background"),
    )
    label.update_idletasks()

    x = (root.winfo_width() - label.winfo_width()) // 2
    y = root.winfo_height() - 40
    label.place(x=x, y=y)

    steps = 90
    fps_delay = 33

    # Extract RGB from hex color, fallback to cyan
    try:
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
    except:
        r, g, b = 0, 255, 255

    def animate(step=0):
        if step > steps:
            label.destroy()
            return

        label.place_configure(y=y + step)
        fade_ratio = max(0, 1 - step / steps)
        faded_color = f"#{int(r * fade_ratio):02x}{int(g * fade_ratio):02x}{int(b * fade_ratio):02x}"
        label.config(fg=faded_color)
        root.after(fps_delay, animate, step + 1)

    animate()
