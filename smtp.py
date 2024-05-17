import tkinter as tk
from tkinter import messagebox
import smtplib
import socks
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading


class EmailSenderApp:
    def __init__(self, master):
        self.master = master
        master.title("SMTP Email Sender")
        self.sent_count = 0
        self.email_count = 0
        self.sending_flag = False  # Flag to control the sending process

        self.from_label = tk.Label(master, text="From:")
        self.from_label.grid(row=0, column=0, sticky="w")

        self.from_entry = tk.Entry(master)
        self.from_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.subject_label = tk.Label(master, text="Subject:")
        self.subject_label.grid(row=1, column=0, sticky="w")

        self.subject_entry = tk.Entry(master)
        self.subject_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.server_label = tk.Label(master, text="SMTP Host:")
        self.server_label.grid(row=2, column=0, sticky="w")

        self.server_entry = tk.Entry(master)
        self.server_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.port_label = tk.Label(master, text="Port:")
        self.port_label.grid(row=3, column=0, sticky="w")

        self.port_entry = tk.Entry(master)
        self.port_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        self.user_label = tk.Label(master, text="Username:")
        self.user_label.grid(row=4, column=0, sticky="w")

        self.user_entry = tk.Entry(master)
        self.user_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        self.password_label = tk.Label(master, text="Password:")
        self.password_label.grid(row=5, column=0, sticky="w")

        self.password_entry = tk.Entry(master, show="*")
        self.password_entry.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

        self.message_label = tk.Label(master, text="Message (HTML):")
        self.message_label.grid(row=6, column=0, sticky="w")

        self.message_text = tk.Text(master, height=5, width=50)
        self.message_text.grid(row=6, column=1, padx=5, pady=5, sticky="ew")

        self.email_label = tk.Label(master, text="Emails List:")
        self.email_label.grid(row=7, column=0, sticky="w")

        self.email_text = tk.Text(master, height=5, width=50)
        self.email_text.grid(row=7, column=1, padx=5, pady=5, sticky="ew")

        self.email_count_label = tk.Label(master, text="Email Count: 0")
        self.email_count_label.grid(row=8, column=1, sticky="w")

        self.update_email_count()

        self.interval_label = tk.Label(master, text="Interval (seconds):")
        self.interval_label.grid(row=9, column=0, sticky="w")

        self.interval_entry = tk.Entry(master)
        self.interval_entry.grid(row=9, column=1, padx=5, pady=5, sticky="ew")

        self.emails_per_interval_label = tk.Label(master, text="Emails per interval:")
        self.emails_per_interval_label.grid(row=10, column=0, sticky="w")

        self.emails_per_interval_entry = tk.Entry(master)
        self.emails_per_interval_entry.grid(row=10, column=1, padx=5, pady=5, sticky="ew")

        self.proxy_label = tk.Label(master, text="Proxy (host:port):")
        self.proxy_label.grid(row=11, column=0, sticky="w")

        self.proxy_entry = tk.Entry(master)
        self.proxy_entry.grid(row=11, column=1, padx=5, pady=5, sticky="ew")

        self.send_button = tk.Button(master, text="Send", command=self.send_email)
        self.send_button.grid(row=12, column=0, pady=10)

        self.stop_button = tk.Button(master, text="Stop", command=self.stop_sending)
        self.stop_button.grid(row=12, column=1, pady=10)

        self.status_label = tk.Label(master, text="Status:")
        self.status_label.grid(row=13, column=0, sticky="w")

        self.status_text = tk.Text(master, height=5, width=50)
        self.status_text.grid(row=13, column=1, padx=5, pady=5, sticky="ew")

        self.sent_count_label = tk.Label(master, text="Sent Count:")
        self.sent_count_label.grid(row=14, column=0, sticky="w")

        self.sent_count_value = tk.Label(master, text="0")
        self.sent_count_value.grid(row=14, column=1, padx=5, pady=5, sticky="w")

    def send_email(self):
        # Set the sending flag to True to indicate that the sending process is ongoing
        self.sending_flag = True
        threading.Thread(target=self.send_email_thread).start()

    def stop_sending(self):
        # Set the sending flag to False to indicate that the sending process should be stopped
        self.sending_flag = False

    def send_email_thread(self):
        from_address = self.from_entry.get()
        subject = self.subject_entry.get()
        server = self.server_entry.get()
        port = int(self.port_entry.get())
        username = self.user_entry.get()
        password = self.password_entry.get()
        message = self.message_text.get("1.0", "end-1c")
        emails = self.email_text.get("1.0", "end-1c").split("\n")
        interval = int(self.interval_entry.get())
        emails_per_interval = int(self.emails_per_interval_entry.get())
        proxy_info = self.proxy_entry.get().split(":")

        proxy_host = proxy_info[0] if len(proxy_info) > 1 else None
        proxy_port = int(proxy_info[1]) if len(proxy_info) > 1 else None

        try:
            smtp_server = smtplib.SMTP(server, port)
            smtp_server.starttls()
            smtp_server.login(username, password)

            for i in range(0, len(emails), emails_per_interval):
                batch_emails = emails[i:i + emails_per_interval]
                for email in batch_emails:
                    # Check if the sending flag is still True, if not, break out of the loop
                    if not self.sending_flag:
                        break

                    msg = MIMEMultipart()
                    msg['From'] = from_address
                    msg['To'] = email
                    msg['Subject'] = subject

                    # Create a MIMEText object with the HTML content
                    html_message = MIMEText(message, 'html')
                    msg.attach(html_message)

                    if proxy_host and proxy_port:
                        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, proxy_host, proxy_port)
                        socks.wrapmodule(smtplib)

                    try:
                        smtp_server.send_message(msg)
                        self.sent_count += 1
                        self.update_sent_count()

                        # Display status
                        self.status_text.insert("end", f"{email}: OK\n", "ok")
                        self.master.update()
                    except Exception as e:
                        # If an error occurs, log the error but continue sending other emails
                        self.status_text.insert("end", f"{email}: Failed - {e}\n", "failed")
                        self.master.update()

                    # Wait for the specified interval before sending the next email
                    self.master.after(interval * 1000)

                # Check if the sending flag is still True, if not, break out of the loop
                if not self.sending_flag:
                    break

            smtp_server.quit()
            self.status_text.insert("end", "Email(s) sent successfully!\n", "ok")
        except Exception as e:
            self.master.deiconify()
            messagebox.showerror("Error", str(e))
            self.status_text.insert("end", f"Failed to send email(s): {e}\n", "failed")

        # Apply coloring
        self.status_text.tag_config("ok", foreground="green")
        self.status_text.tag_config("failed", foreground="red")

    def update_sent_count(self):
        self.sent_count_value.config(text=str(self.sent_count))

    def update_email_count(self):
        emails = self.email_text.get("1.0", "end-1c").split("\n")
        self.email_count = sum(1 for email in emails if email.strip())
        self.email_count_label.config(text=f"Email Count: {self.email_count}")


root = tk.Tk()
app = EmailSenderApp(root)
root.mainloop()
