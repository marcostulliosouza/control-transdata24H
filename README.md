## Controle de Testes Transdata24H ##

Este projeto foi desenvolvido para gerenciar o controle de testes de dispositivos em uma linha de produção. A aplicação permite que os usuários iniciem e finalizem testes em dispositivos, registrem falhas, e monitorem o progresso dos testes, especialmente com foco em um limite de 24 horas para a duração do teste.

### Funcionalidades ###
Iniciar Teste: Os testes podem ser iniciados para cada dispositivo, sendo necessário inserir o número de série do produto. O dispositivo passa para o estado de "testing" e começa a contar o tempo de teste.

Finalizar Teste: O usuário pode finalizar um teste, marcando-o como "Aprovado" ou "Reprovado". No caso de falha, o motivo deve ser registrado a partir de uma lista pré-definida, e o comentário adicional é opcional.

Monitoramento de Tempo: A aplicação monitora a duração de cada teste. Se o tempo de teste ultrapassar 24 horas, o status do dispositivo é automaticamente alterado para "Concluído" e o botão associado ao dispositivo ficará verde.

Armazenamento de Logs: Os resultados dos testes (aprovados ou reprovados) são armazenados em um arquivo CSV, incluindo informações sobre o dispositivo (número de série, data e hora de início e término do teste, duração, etc.).

Persistência de Estado: O estado dos dispositivos (incluindo o número de série e o estado do teste) é salvo em um arquivo JSON. Ao reiniciar a aplicação, o estado dos dispositivos é restaurado, incluindo o tempo de teste já decorrido.

Arquivos e Configuração
config.ini: Arquivo de configuração contendo a lista de motivos de falha. Este arquivo é lido ao iniciar a aplicação e é fundamental para o correto funcionamento do processo de falhas. Exemplo de conteúdo:

csharp
Copy code
[FALHAS]
motivos = Motivo desconhecido, Falha na alimentação, Falha na comunicação, Defeito físico
state.json: Arquivo que armazena o estado atual de todos os dispositivos. Ele é carregado sempre que a aplicação é iniciada, e salvo periodicamente para garantir que o estado dos dispositivos seja preservado.

logs/test24h_YYYY-MM-DD.csv: Arquivo de log onde os resultados dos testes são salvos. Ele inclui informações como o número de série do dispositivo, a data e hora de início e fim do teste, a duração do teste, o status do dispositivo e o motivo de falha (se houver).

### Como Usar ### 
Inicie a aplicação: Ao abrir a aplicação, ela exibirá os dispositivos divididos em grupos (por exemplo, "Grupo Front" e "Grupo Rear"). Cada dispositivo terá um botão associado. Clique no botão de um dispositivo para iniciar ou finalizar o teste.

Iniciar Teste: Ao clicar no botão de um dispositivo, a aplicação pedirá o número de série do produto. Após inserir o número de série, o teste será iniciado, e o tempo começará a ser monitorado.

Finalizar Teste: Após o teste ser concluído (ou após o limite de 24 horas), a aplicação permite finalizar o teste, marcando-o como "Aprovado" ou "Reprovado". Se reprovado, será solicitado o motivo da falha e um comentário.

Monitoramento Automático: A aplicação monitora automaticamente o tempo de teste, e se o dispositivo permanecer em teste por mais de 24 horas, o status será alterado para "Concluído" (botão ficará verde). Isso ocorrerá mesmo que a aplicação seja fechada e reaberta, pois o estado será restaurado do arquivo state.json.

Fechar a Aplicação: Ao tentar fechar a aplicação, será exibida uma mensagem de aviso caso haja testes em andamento. Você precisará confirmar se realmente deseja fechar a aplicação com testes em andamento.

### Requisitos ###
- Python 3.x
- Bibliotecas:
- tkinter
- configparser
- json
- csv
- os
- datetime

### Como Instalar ###
Baixe o repositório ou clone-o usando o comando:

```bash
git clone https://github.com/marcostulliosouza/control-transdata24H.git
```
Instale o Python 3.x, se ainda não tiver.

Execute o arquivo main.py para iniciar a aplicação.

Considerações Finais
A aplicação foi projetada para ser simples e eficiente, permitindo o controle de testes de dispositivos de forma intuitiva. Ela utiliza uma interface gráfica baseada em Tkinter e armazena os resultados em arquivos CSV e JSON para fácil análise e persistência de dados.