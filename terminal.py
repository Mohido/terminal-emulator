import os
import tkinter as tk

def bash_app(tty):
    import sys, termios

    # configuring the tty module/adhoc pseudo terminal
    attrs = termios.tcgetattr(tty)
    attrs[3] &= ~termios.ECHO
    termios.tcsetattr(tty, termios.TCSANOW, attrs)

    os.setsid()

    os.dup2(tty, sys.stdin.fileno())
    os.dup2(tty, sys.stdout.fileno())
    os.dup2(tty, sys.stderr.fileno())

    os.execve(
        "/bin/bash",
        ["/bin/bash", "--norc", "--noprofile", "--noediting"],
        dict(os.environ, PS1="", TERM="dumb"),
    )

def gui_app(teletype):
    os.set_blocking(teletype, False)

    window = tk.Tk()
    window.geometry("600x200")
    prompt, reply = tk.StringVar(value="$ "), tk.StringVar(value="")
    tk.Label(
        window, textvariable=prompt, font=("monospace", 24), justify="left", anchor="w"
    ).pack(fill="x")
    tk.Label(
        window, textvariable=reply, font=("monospace", 24), justify="left", anchor="w"
    ).pack(fill="x")

    command = tk.StringVar(value="")

    def on_key(k):
        if k.keysym == "BackSpace":
            command.set(command.get()[:-1])
        elif k.keysym == "Return":
            os.write(teletype, (command.get() + '\n').encode())
            command.set("")
        elif k.char and k.char.isprintable():
            command.set(command.get() + k.char)
        prompt.set("$ " + command.get())

    def fetch():
        try:
            data = os.read(teletype, 4096)
        except BlockingIOError:
            data = b""
        except Exception:
            window.destroy()
            return
        if data:
            text = data.decode()
            reply.set(text)
        window.after(25, fetch)

    window.after(25, fetch)
    window.bind("<Key>", on_key)
    window.mainloop()

def main():
    teletype, tty = os.openpty()
    pid = os.fork()

    if pid == 0:
        bash_app(tty)
    else:
        os.close(tty)
        gui_app(teletype)

main()
