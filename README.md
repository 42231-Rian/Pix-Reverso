# 💸 Pix Reverso — O Banco do Desperdício Consciente

> *"Você paga para receber uma notificação dizendo que poderia ter economizado aquele dinheiro."*

O **Pix Reverso** é uma aplicação satírica e funcional de autossabotagem e conscientização financeira. Ao realizar um Pix, o sistema debita o valor, calcula tudo o que você poderia ter comprado com essa grana e imediatamente dispara uma **notificação oficial no seu Windows** lembrando que, se você não tivesse feito aquele Pix, você ainda teria exatamente aquele dinheiro na sua conta.

---

## 🚀 Como Iniciar

### Opção 1: Clique Duplo (Mais Fácil no Windows)
Basta dar um duplo clique no arquivo:
👉 `iniciar.bat`

Ele irá abrir seu navegador padrão automaticamente em `http://127.0.0.1:5000` e iniciar o servidor.

---

### Opção 2: Pelo Terminal / Prompt de Comando
Abra o terminal nesta pasta (`C:\Users\Aluno\Documents\Pix reverso`) e execute:
```bash
python app.py
```
Em seguida, acesse no navegador: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

### Opção 3: Modo Linha de Comando (CLI)
Se você prefere queimar dinheiro direto pelo terminal sem abrir o navegador:
```bash
# Modo Interativo (com perguntas):
python cli.py

# Ou passando o valor e motivo direto:
python cli.py 50.00 "Comprei água mineral com gás no restaurante chique" --tone coach
```
Você também pode apenas dar duplo clique em `iniciar_cli.bat`!

---

## ✨ Funcionalidades do Sistema

1. **🔔 Notificações Nativas no Windows (Toast Notification)**:
   - Dispara uma notificação real no canto inferior direito do Windows 10/11 com som de lembrete do sistema.
   - Suporte a agendamento com atraso (5s, 15s, 30s) para que você sinta uma breve sensação de alívio antes da culpa bater.

2. **🧾 Comprovante Oficial de Arrependimento**:
   - Um comprovante idêntico ao dos bancos digitais (Nubank/Inter/Itaú), emitido pelo *"Banco Central do Desperdício S.A."*.
   - Informa o pagador ("Você - Mão de Peneira"), chave Pix, benefício obtido ("Absolutamente Nenhum") e botão para imprimir/salvar.

3. **🍗 Equivalências Cômicas de Desperdício**:
   Calcula instantaneamente o impacto do valor gasto:
   - Quantas coxinhas de rodoviária você jogou fora.
   - Quantos cafezinhos expressos de padaria.
   - Quantas horas reais de trabalho CLT (com base no salário mínimo).
   - Qual porcentagem de um Celta 2004 1.0 Prata você acabou de evaporar.
   - Quanto esse dinheiro renderia no CDI a 10% a.a. em 30 anos com juros compostos.

4. **🎭 4 Tons de Lição de Moral**:
   - **Sarcástico**: Deboche puro no estilo "Parabéns, Warren Buffett do Serasa".
   - **Coach Agressivo**: No melhor estilo "Primo Pobre", te mandando acordar às 4h30.
   - **Filosófico**: Niilismo cósmico sobre a ilusão do dinheiro.
   - **Culpa Familiar**: Lembra do sacrifício da sua mãe e do seu eu do futuro.

5. **📱 QR Code e Pix Copia e Cola**:
   - Gera um QR Code real compatível com o padrão EMV do Banco Central para quem quiser simular ou copiar a chave Pix.

6. **📊 Painel do Rombo (Extrato)**:
   - Total pago em Pix Reverso vs. Total que você teria se não fizesse nada (exatamente o mesmo número destacado em vermelho).
   - Histórico completo com persistência em `database.json`.

---

## 📁 Estrutura de Arquivos

```
C:\Users\Aluno\Documents\Pix reverso\
│
├── app.py                 # Backend Flask, gerador de Pix e cálculos de arrependimento
├── cli.py                 # Versão para terminal / prompt de comando
├── notify.ps1             # Script PowerShell para notificações nativas do Windows
├── database.json          # Banco de dados local com transações e estatísticas
├── iniciar.bat            # Atalho de 1 clique para iniciar o sistema Web
├── iniciar_cli.bat        # Atalho de 1 clique para o terminal
├── README.md              # Este manual de instruções
│
├── static/
│   ├── css/
│   │   └── style.css      # Estilização moderna estilo fintech (dark theme, responsivo)
│   └── js/
│       ├── app.js         # Lógica da interface, efeitos sonoros (Web Audio) e modais
│       └── qrcode.min.js  # Gerador de QR Code local (100% offline)
│
└── templates/
    └── index.html         # Página principal da aplicação
```

---

*Pix Reverso: Porque o arrependimento agora aceita QR Code.* 💸
