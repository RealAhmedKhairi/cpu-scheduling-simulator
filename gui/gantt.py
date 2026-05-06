import tkinter as tk


def draw_gantt_chart(canvas, timeline, pid_colors, title):
    canvas.delete("all")
    canvas.update_idletasks()

    width = canvas.winfo_width() or int(canvas["width"])
    height = canvas.winfo_height() or int(canvas["height"])
    left_pad = 60
    right_pad = 20
    top_pad = 28
    bottom_pad = 30
    usable_width = max(120, width - left_pad - right_pad)

    total_time = max((end for _, _, end in timeline), default=0)
    if total_time <= 0:
        canvas.create_text(width // 2, height // 2, text="No timeline data", font=("Arial", 12), fill="#333")
        canvas.create_text(width // 2, 14, text=title, font=("Arial", 12, "bold"), anchor="n")
        return

    unit_width = usable_width / total_time
    chart_y0 = top_pad
    chart_y1 = height - bottom_pad - 20
    segment_y0 = chart_y0
    segment_y1 = chart_y1

    for pid, start, end in timeline:
        color = pid_colors.get(pid, "#B0B0B0") if pid != "Idle" else "#B0B0B0"
        x0 = left_pad + start * unit_width
        x1 = left_pad + end * unit_width
        canvas.create_rectangle(x0, segment_y0, x1, segment_y1, fill=color, outline="#333")
        display_text = pid
        text_color = "white" if pid != "Idle" else "black"
        canvas.create_text((x0 + x1) / 2, (segment_y0 + segment_y1) / 2, text=display_text, font=("Arial", 10, "bold"), fill=text_color)

    axis_y = segment_y1 + 10
    canvas.create_line(left_pad, axis_y, left_pad + total_time * unit_width, axis_y, fill="#333")

    label_step = 1
    if unit_width < 30:
        label_step = max(1, int(30 / unit_width))

    for t in range(total_time + 1):
        x = left_pad + t * unit_width
        canvas.create_line(x, axis_y, x, axis_y + 8, fill="#333")
        if t % label_step == 0:
            canvas.create_text(x, axis_y + 18, text=str(t), font=("Arial", 8), anchor="n")

    canvas.create_text(width // 2, 12, text=title, font=("Arial", 12, "bold"), anchor="n")
