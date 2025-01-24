import json
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from datetime import datetime, timedelta
import csv
import os
import configparser

__version__ = '2.1'

# Dados para armazenar o estado dos dispositivos
devices = {}
LOG_FILE = f"logs/test24h_{datetime.now().strftime('%Y-%m-%d')}.csv"
STATE_FILE = "state.json"

GROUP_1 = ["A", "B", "C", "D"]
GROUP_2 = ["E", "F", "G", "H"]
COLS_PER_ROW = 10

# Carregar motivos de falha do arquivo config.ini
config = configparser.ConfigParser()
config.read("config.ini")
FALHAS = config.get("FALHAS", "motivos", fallback="Motivo desconhecido").split(", ")


def save_log(device_id, status, reason=None, comment=None):
    """Salva o log de teste no arquivo CSV."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')  # Definir o delimitador para ';'
        if not file_exists:
            # Alterar os nomes das colunas para os desejados
            writer.writerow(
                ["Serial", "Data_Inicio", "Hora_Inicio", "Data_Fim", "Hora_Fim", "Tempo_de_Teste", "Status", "Motivo",
                 "Comentario"])

        # Obter os tempos e formatá-los
        start_time = devices[device_id]['start_time']
        end_time = datetime.now()
        test_duration = str(end_time - start_time).split('.')[0]  # Tempo de teste formatado

        # Construir as colunas de dados
        log = [
            devices[device_id]['serial'],  # Serial
            start_time.strftime("%Y-%m-%d"),  # Data de início
            start_time.strftime("%H:%M:%S"),  # Hora de início
            end_time.strftime("%Y-%m-%d"),  # Data de fim
            end_time.strftime("%H:%M:%S"),  # Hora de fim
            test_duration,  # Tempo de teste
            "1" if status == "Aprovado" else "0",  # Status (1 para aprovado, 0 para reprovado)
            reason or "",  # Motivo
            comment or ""  # Comentário
        ]

        # Escrever os dados no arquivo CSV
        writer.writerow(log)

def save_state():
    """Salva o estado atual dos dispositivos."""
    with open(STATE_FILE, 'w') as file:
        json.dump(devices, file, default=str)

def load_state():
    """Carrega o estado salvo dos dispositivos."""
    global devices
    if os.path.isfile(STATE_FILE):
        with open(STATE_FILE, 'r') as file:
            saved_state = json.load(file)
            for device_id, data in saved_state.items():
                data['start_time'] = datetime.fromisoformat(data['start_time']) if data['start_time'] else None
                devices[int(device_id)] = data

                # Verifique se o estado foi "testing" e se o tempo já ultrapassou 24 horas
                if devices[int(device_id)]["state"] == "testing":
                    elapsed_time = datetime.now() - devices[int(device_id)]["start_time"]
                    if elapsed_time.total_seconds() >= 86400:
                        devices[int(device_id)]["state"] = "completed"
                        update_button(int(device_id), "completed")
                    else:
                        # Iniciar o cronômetro se estiver em "testing"
                        update_timer(int(device_id))

                # Se o dispositivo já estava em "completed", atualize o botão
                elif devices[int(device_id)]["state"] == "completed":
                    update_button(int(device_id), "completed")


def start_test(device_id):
    """Inicia ou finaliza o teste para o dispositivo selecionado."""
    if devices[device_id]["state"] == "idle":
        serial = simpledialog.askstring("Serial", "Serial do Produto:")
        if not serial:
            return

        devices[device_id] = {
            "serial": serial,
            "start_time": datetime.now(),
            "state": "testing",
            "retests": devices[device_id]["retests"]
        }
        update_button(device_id, "testing")
        check_24_hours(device_id)
        save_state()

    elif devices[device_id]["state"] == "testing" or  devices[device_id]["state"] == "completed":
        finalize_test(device_id)


def finalize_test(device_id):
    """Exibe a janela para finalizar o teste."""

    def handle_result(result):
        if result == "ok":
            # Salvar como aprovado
            save_log(device_id, "Aprovado")
            reset_device(device_id)
        elif result == "nok":
            # Exibir janela de falha para registrar o motivo
            handle_failure(device_id)
        finalize_window.destroy()

    finalize_window = tk.Toplevel(root)
    finalize_window.title("Finalizar Teste")
    center_window(finalize_window, 400, 200)

    tk.Label(finalize_window, text=f"Serial: {devices[device_id]['serial']}", font=("Arial", 14)).pack(pady=10)
    tk.Button(finalize_window, text="OK", bg="green", fg="white", font=("Arial", 16, "bold"),
              command=lambda: handle_result("ok")).pack(side="left", expand=True, fill="both", padx=10, pady=10)
    tk.Button(finalize_window, text="NOK", bg="red", fg="white", font=("Arial", 16, "bold"),
              command=lambda: handle_result("nok")).pack(side="right", expand=True, fill="both", padx=10, pady=10)


def handle_failure(device_id):
    """Abre uma janela para registrar o motivo da falha."""

    def save_failure():
        selected_indices = failure_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Erro", "Selecione pelo menos um motivo para a falha.")
            return

        selected_reasons = [failure_listbox.get(i) for i in selected_indices]
        comment = comment_box.get("1.0", "end").strip()

        save_log(device_id, "Reprovado", reason=", ".join(selected_reasons), comment=comment)
        reset_device(device_id)
        failure_window.destroy()

    def cancel_failure():
        failure_window.destroy()

    failure_window = tk.Toplevel(root)
    failure_window.title(f"Registrar Falha - Placa - {devices[device_id]['serial']}")
    center_window(failure_window, 400, 400)
    failure_window.grab_set()

    tk.Label(failure_window, text="Motivos da Falha:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
    failure_listbox = tk.Listbox(failure_window, selectmode="multiple", height=10)
    for falha in FALHAS:
        failure_listbox.insert(tk.END, falha)
    failure_listbox.pack(padx=10, pady=5, fill="both", expand=True)

    tk.Label(failure_window, text="Comentário (opcional):", font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
    comment_box = tk.Text(failure_window, height=5, width=40)
    comment_box.pack(padx=10, pady=5)

    button_frame = ttk.Frame(failure_window)
    button_frame.pack(pady=10)

    save_button = ttk.Button(button_frame, text="Salvar", command=save_failure)
    save_button.pack(side="left", padx=10)

    cancel_button = ttk.Button(button_frame, text="Cancelar", command=cancel_failure)
    cancel_button.pack(side="right", padx=10)


def reset_device(device_id):
    """Reseta o dispositivo para o estado inicial."""
    devices[device_id] = {
        "serial": None,
        "start_time": None,
        "state": "idle",
        "retests": devices[device_id]["retests"]
    }
    update_button(device_id, "idle")
    save_state()


def update_button(device_id, state, elapsed_time=None):
    """Atualiza o botão correspondente ao dispositivo."""
    button = device_buttons[device_id]

    if state == "idle":
        button.config(text=f"P{device_id}", style="Idle.TButton", image=icon, compound="left")
    elif state == "testing":
        elapsed = f"\n{elapsed_time}" if elapsed_time else ""
        button.config(
            text=f"Testando\n{devices[device_id]['serial']}{elapsed}",
            style="Testing.TButton",
            image=icon_yellow,
            compound="left",
        )
    elif state == "completed":
        button.config(
            text=f"Concluído\n{devices[device_id]['serial']}",
            style="Testing.TButton",
            image=icon_green,
            compound="left",
        )


def check_24_hours(device_id):
    """Verifica se o teste atingiu o tempo limite e atualiza o botão."""
    if devices[device_id]["state"] != "testing":
        return  # Interrompa se o estado não for 'testing'

    elapsed_time = datetime.now() - devices[device_id]["start_time"]
    elapsed_seconds = elapsed_time.total_seconds()

    # Se o tempo limite for atingido, altere o estado do dispositivo
    if elapsed_seconds >= 86400:  # (86400 para 24 horas)
        devices[device_id]["state"] = "completed"
        update_button(device_id, "completed")
    else:
        elapsed_formatted = str(elapsed_time).split('.')[0]
        update_button(device_id, "testing", elapsed_formatted)
        root.after(1000, check_24_hours, device_id)


def update_timer(device_id):
    """Atualiza o cronômetro do teste."""
    if devices[device_id]["state"] == "testing":
        elapsed_time = str(datetime.now() - devices[device_id]["start_time"]).split('.')[0]
        update_button(device_id, "testing", elapsed_time)

        # Verifica se o tempo de teste atingiu o limite de 24 horas
        if (datetime.now() - devices[device_id]["start_time"]).total_seconds() >= 86400:
            devices[device_id]["state"] = "completed"
            update_button(device_id, "completed")
        else:
            root.after(1000, update_timer, device_id)


def center_window(window, width, height):
    """Centraliza a janela na tela."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")


def init_log_file():
    """Inicializa o arquivo de log."""
    log_dir = os.path.dirname(LOG_FILE)  # Obtém o diretório do arquivo de log
    if not os.path.exists(log_dir):  # Verifica se o diretório existe
        os.makedirs(log_dir)  # Cria o diretório se não existir

    if not os.path.isfile(LOG_FILE):  # Verifica se o arquivo não existe
        with open(LOG_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(  # Escreve o cabeçalho no CSV
                ["Serial", "Data_Inicio", "Hora_Inicio", "Data_Fim", "Hora_Fim", "Tempo_de_Teste", "Status", "Motivo",
                 "Comentario"]
            )


def on_closing():
    """Impede o fechamento da aplicação se houver testes em andamento e pergunta se o usuário deseja realmente fechar."""
    # Verifica se há algum dispositivo em estado 'testing' ou 'completed'
    testing_devices = [device for device, data in devices.items() if data["state"] == "testing"]
    completed_devices = [device for device, data in devices.items() if data["state"] == "completed"]

    if testing_devices or completed_devices:
        # Pergunta ao usuário se deseja realmente fechar a aplicação com testes em andamento
        answer = messagebox.askyesno(
            "Atenção",
            "Existem testes em andamento. Você realmente deseja fechar a aplicação?"
        )
        if answer:
            root.destroy()
    else:
        # Fecha a aplicação se não houver testes em andamento
        root.destroy()


# Configuração da interface
root = tk.Tk()
root.title(f"Controle de Testes Transdata24H v{__version__}")
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
root.protocol("WM_DELETE_WINDOW", on_closing)

# Carregar ícones
icon_path = "img/graphic-tablet.png"  # Caminho para o ícone
icon = tk.PhotoImage(file=icon_path)
icon_yellow = tk.PhotoImage(file="img/graphic-tablet - yellow.png")
icon_green = tk.PhotoImage(file="img/graphic-tablet - green.png")
icon = icon.subsample(12, 12)  # O valor 2, 2 reduz o ícone para metade do tamanho
icon_yellow = icon_yellow.subsample(12, 12)
icon_green = icon_green.subsample(12, 12)

style = ttk.Style()
style.configure("TButton", font=("Arial", 10), padding=6)
style.configure("Idle.TButton", background="lightgray", foreground="black", width=7, height=11)
style.configure("Testing.TButton",
                background="lightgray",
                foreground="black",
                width=7,
                height=11
                )

device_buttons = {}
frame_title = ttk.Label(root, text=f"Controle de Testes Transdata24H v{__version__}", font=("Arial", 16, "bold"),
                        anchor="center")
frame_title.grid(row=0, column=0, columnspan=2, pady=10, sticky="nsew")
# Criar os frames para cada grupo
frame_group_1 = ttk.LabelFrame(root, text="Grupo Front")
frame_group_1.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
frame_group_2 = ttk.LabelFrame(root, text="Grupo Rear")
frame_group_2.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
frame_title = ttk.Label(root, text="Desenvolvido em Python por Marcos Tullio", font=("Arial", 8, "bold"),
                        anchor="center")
frame_title.grid(row=3, column=0, columnspan=2, pady=10, sticky="nsew")

# Adicionar botões para os dispositivos no Grupo 1
device_id = 1
for group in GROUP_1:
    group_frame = ttk.Frame(frame_group_1)
    group_frame.pack(fill="x", padx=5, pady=5)
    group_label = ttk.Label(group_frame, text=f"{group}:", font=("Arial", 12, "bold"))
    group_label.pack(side="left", padx=5)
    for col in range(COLS_PER_ROW):
        # Verifica se o dispositivo já foi carregado do estado salvo
        if device_id not in devices:
            devices[device_id] = {"serial": None, "start_time": None, "state": "idle", "retests": 0}

        # Cria o botão do dispositivo
        button = ttk.Button(
            group_frame,
            text=f"P{col + 1}",
            style="Idle.TButton",
            image=icon,
            compound="left",
            command=lambda d=device_id: start_test(d),
        )
        button.pack(side="left", padx=3, pady=3)
        device_buttons[device_id] = button

        # Atualiza o botão com base no estado carregado
        update_button(device_id, devices[device_id]["state"])

        # Se o estado for "testing", inicia o cronômetro
        if devices[device_id]["state"] == "testing":
            update_timer(device_id)

        # Se o estado for "completed", garante que o botão fique marcado como "Concluído"
        elif devices[device_id]["state"] == "completed":
            update_button(device_id, "completed")

        device_id += 1

# Adicionar botões para os dispositivos no Grupo 2
for group in GROUP_2:
    group_frame = ttk.Frame(frame_group_2)
    group_frame.pack(fill="x", padx=5, pady=5)
    group_label = ttk.Label(group_frame, text=f"{group}:", font=("Arial", 12, "bold"))
    group_label.pack(side="left", padx=5)
    for col in range(COLS_PER_ROW):
        devices[device_id] = {"serial": None, "start_time": None, "state": "idle", "retests": 0}
        button = ttk.Button(
            group_frame,
            text=f"P{col + 1}",
            style="Idle.TButton",
            image=icon,
            compound="left",
            command=lambda d=device_id: start_test(d),
        )
        button.pack(side="left", padx=2, pady=2)
        device_buttons[device_id] = button
        # Atualiza o botão com base no estado carregado
        update_button(device_id, devices[device_id]["state"])

        # Se o estado for "testing", inicia o cronômetro
        if devices[device_id]["state"] == "testing":
            update_timer(device_id)

        device_id += 1
load_state()# Verificação do arquivo de configuração
if not os.path.exists("config.ini"):
    messagebox.showerror("Erro", "Arquivo config.ini não encontrado!")
    root.destroy()

init_log_file()
root.mainloop()
