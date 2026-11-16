"""
Pix Reverso - Backend Flask
"Você paga para receber uma notificação dizendo que poderia ter economizado aquele dinheiro."
"""

import os
import sys
import json
import uuid
import random
import threading
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

app = Flask(__name__, static_folder="static", template_folder="templates")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "database.json")
NOTIFY_SCRIPT = os.path.join(BASE_DIR, "notify.ps1")

# ==========================================
# BANCO DE DADOS LOCAL (JSON)
# ==========================================

def load_db():
    if not os.path.exists(DB_FILE):
        initial = {
            "transactions": [],
            "stats": {
                "total_spent": 0.0,
                "total_could_have_saved": 0.0,
                "count": 0
            }
        }
        save_db(initial)
        return initial
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"transactions": [], "stats": {"total_spent": 0.0, "total_could_have_saved": 0.0, "count": 0}}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==========================================
# MOTOR DE IRONIA E EQUIVALÊNCIAS FINANCEIRAS
# ==========================================

TONE_MESSAGES = {
    "sarcastic": [
        "Parabéns, Warren Buffett do Serasa! Você pagou R$ {amount:.2f} só para ver esta notificação. O mercado financeiro chora lágrimas de desespero.",
        "Transação aprovada com sucesso! R$ {amount:.2f} saíram voando da sua conta. Se você não tivesse feito isso, você ainda teria R$ {amount:.2f}. Gênio!",
        "Inovação bancária: seu saldo caiu R$ {amount:.2f}, e em troca você recebeu 4 linhas de texto puro arrependimento.",
        "Seu dinheiro foi embora e não volta mais. Mas olha pelo lado bom: pelo menos você tem este lembrete de que você é péssimo em finanças."
    ],
    "philosophical": [
        "O dinheiro é uma ficção social compartilhada. Mas a ausência desses R$ {amount:.2f} no seu saldo agora é um fato cosmológico imutável.",
        "Heráclito dizia que ninguém pisa duas vezes no mesmo rio. E você nunca mais verá esses R$ {amount:.2f}.",
        "O que restou dos seus R$ {amount:.2f}? Apenas a certeza de que a frugalidade era o caminho... que você escolheu não seguir.",
        "O vazio existencial e a sua conta bancária acabaram de entrar em perfeita ressonância graças a este Pix de R$ {amount:.2f}."
    ],
    "coach": [
        "ACORDA, VENCEDOR! Você acabou de queimar R$ {amount:.2f}! Enquanto você paga Pix Reverso, seu concorrente acordou às 4:45 pra vender água mineral no sinal!",
        "Mente milionária? Mais pra mente devedora! R$ {amount:.2f} jogados no lixo! Salve esse comprovante como troféu da autossabotagem!",
        "Dica do Primo Pobre: Se você guardasse esses R$ {amount:.2f} todo dia por 350 anos com juros de 12% a.a., você comprava uma lancha. Mas você preferiu clicar no botão.",
        "Você não comprou um produto, você comprou uma lição de moral de R$ {amount:.2f}. Espero que tenha aprendido (provavelmente não)."
    ],
    "guilt": [
        "Sua mãe sabe que você gastou R$ {amount:.2f} nisso? Pensa no suor, no cansaço, na marmita requentada... pra você pagar por uma notificação.",
        "Ouviu esse som? Foi o seu futuro financeiro chorando no cantinho por causa desses R$ {amount:.2f} que nunca mais voltarão.",
        "Com R$ {amount:.2f} você podia ter pago meia conta de luz, mas preferiu me remunerar pra te avisar que você não deveria ter feito isso.",
        "Seu eu do futuro acabou de te olhar com um profundo olhar de desapontamento. R$ {amount:.2f} a menos na sua aposentadoria."
    ]
}

def generate_analysis(amount, reason, tone):
    amount = float(amount)
    
    # Cálculos satíricos
    coxinhas = max(1, int(amount / 7.0))
    cafezinhos = max(1, int(amount / 4.5))
    pasteis_caldo = round(amount / 16.0, 1)
    horas_clt = round(amount / 6.90, 1) # Salário mínimo ~R$ 1518 / 220h = ~R$ 6.90/h
    minutos_clt = int(horas_clt * 60)
    celta_pct = (amount / 14000.0) * 100.0 # Celta 2004 1.0 R$ 14.000
    
    # Projeção no Tesouro Direto / CDI em 30 anos (10% a.a.)
    futuro_cdi = amount * ((1 + 0.10) ** 30)
    
    # Seleção da mensagem de acordo com o tom
    messages_pool = TONE_MESSAGES.get(tone, TONE_MESSAGES["sarcastic"])
    msg_template = random.choice(messages_pool)
    custom_message = msg_template.format(amount=amount)
    
    # Destaque de arrependimento
    main_lesson = f"Você pagou R$ {amount:.2f}. Se você NÃO tivesse feito esse Pix, você teria exatamente R$ {amount:.2f} a mais agora."
    
    equivalences = [
        {"icon": "🍗", "label": "Coxinhas de padaria", "value": f"~{coxinhas} unidades"},
        {"icon": "☕", "label": "Cafezinhos expressos", "value": f"~{cafezinhos} xícaras"},
        {"icon": "🥤", "label": "Combos Pastel + Caldo de Cana", "value": f"~{pasteis_caldo} combos"},
        {"icon": "⏰", "label": "Tempo de CLT trabalhado", "value": f"{horas_clt}h ({minutos_clt} min)"},
        {"icon": "🚗", "label": "Fatia de um Celta 2004 Prata", "value": f"{celta_pct:.4f}%"},
        {"icon": "📈", "label": "Valor no CDI em 30 anos (10% a.a.)", "value": f"R$ {futuro_cdi:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")}
    ]
    
    return {
        "main_lesson": main_lesson,
        "notification_text": custom_message,
        "equivalences": equivalences,
        "compound_future": f"R$ {futuro_cdi:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "hours_worked": horas_clt
    }

# ==========================================
# DISPARADOR DE NOTIFICAÇÃO NATIVA WINDOWS
# ==========================================

def trigger_windows_notification(title, message, subtext="Pix Reverso - Banco do Remorso"):
    try:
        cmd = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-File", NOTIFY_SCRIPT,
            "-Title", title,
            "-Message", message,
            "-Subtext", subtext
        ]
        subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    except Exception as e:
        print(f"[Erro Notificacao Windows]: {e}")

def schedule_notification(delay_seconds, title, message, subtext):
    if delay_seconds <= 0:
        trigger_windows_notification(title, message, subtext)
    else:
        timer = threading.Timer(delay_seconds, trigger_windows_notification, args=[title, message, subtext])
        timer.daemon = True
        timer.start()

# ==========================================
# GERADOR DE PAYLOAD PIX FICTÍCIO (EMV)
# ==========================================

def generate_pix_code(amount, tx_id):
    # Formata string EMV Pix padronizada brasileira para parecer 100% autêntico
    val_str = f"{amount:.2f}"
    val_field = f"54{len(val_str):02d}{val_str}"
    pix_key = "pix-reverso@arrependimento.gov.br"
    merchant_account = f"0014br.gov.bcb.pix01{len(pix_key):02d}{pix_key}"
    tx_field = f"05{len(tx_id[:25]):02d}{tx_id[:25]}"
    
    raw = (
        "000201"
        f"26{len(merchant_account):02d}{merchant_account}"
        "52040000"
        "5303986"
        f"{val_field}"
        "5802BR"
        "5925PIX REVERSO SA"
        "6009SAO PAULO"
        f"62{len(tx_field)+4:02d}{tx_field}"
        "6304E8A2"
    )
    return raw

# ==========================================
# ROTAS DA APLICAÇÃO
# ==========================================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/pay", methods=["POST"])
def pay():
    data = request.get_json() or {}
    try:
        amount = float(data.get("amount", 10.0))
        if amount <= 0:
            return jsonify({"error": "O valor precisa ser maior que zero (ao menos um centavo de arrependimento)."}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Valor inválido informado."}), 400
    
    reason = (data.get("reason") or "Vontade incontrolável de queimar dinheiro").strip()
    tone = data.get("tone") or "sarcastic"
    delay_seconds = int(data.get("delay", 0))
    
    tx_id = str(uuid.uuid4()).replace("-", "").upper()[:16]
    now_str = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    
    # Análise de remorso
    analysis = generate_analysis(amount, reason, tone)
    
    # Cria comprovante oficial
    receipt = {
        "id": f"PXR-{tx_id}",
        "date": now_str,
        "amount": amount,
        "amount_formatted": f"R$ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "reason": reason,
        "tone": tone,
        "institution": "Banco Central do Desperdício S.A. (Código 999)",
        "payer": "Você (Mão de Peneira)",
        "receiver": "Pix Reverso - Fundo de Notificações Inúteis",
        "key": "pix-reverso@arrependimento.gov.br",
        "authentication_code": f"{uuid.uuid4()}".upper(),
        "lesson": analysis["main_lesson"],
        "notification_text": analysis["notification_text"],
        "equivalences": analysis["equivalences"],
        "compound_future": analysis["compound_future"],
        "hours_worked": analysis["hours_worked"]
    }
    
    # Salva no banco de dados local
    db = load_db()
    db["transactions"].insert(0, receipt)
    # Limita o histórico aos últimos 100
    db["transactions"] = db["transactions"][:100]
    
    db["stats"]["total_spent"] = round(db["stats"].get("total_spent", 0.0) + amount, 2)
    db["stats"]["total_could_have_saved"] = db["stats"]["total_spent"] # É exatamente o mesmo valor!
    db["stats"]["count"] = db["stats"].get("count", 0) + 1
    save_db(db)
    
    # Dispara notificação no Windows
    notify_title = f"💸 Pix Reverso: R$ {amount:.2f} Debitados!"
    notify_msg = analysis["notification_text"]
    notify_subtext = f"Sabia? Você teria R$ {amount:.2f} a mais agora."
    
    schedule_notification(delay_seconds, notify_title, notify_msg, notify_subtext)
    
    return jsonify({
        "status": "success",
        "receipt": receipt,
        "stats": db["stats"],
        "delay": delay_seconds
    })

@app.route("/api/preview-pix", methods=["POST"])
def preview_pix():
    data = request.get_json() or {}
    try:
        amount = float(data.get("amount", 25.0))
        if amount <= 0:
            amount = 25.0
    except (ValueError, TypeError):
        amount = 25.0
        
    tx_id = f"PXR{int(datetime.now().timestamp())}"
    pix_code = generate_pix_code(amount, tx_id)
    
    return jsonify({
        "amount": amount,
        "amount_formatted": f"R$ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "pix_code": pix_code,
        "tx_id": tx_id
    })

@app.route("/api/history", methods=["GET"])
def get_history():
    db = load_db()
    return jsonify({
        "transactions": db["transactions"],
        "stats": db["stats"]
    })

@app.route("/api/history", methods=["DELETE"])
def clear_history():
    db = {
        "transactions": [],
        "stats": {
            "total_spent": 0.0,
            "total_could_have_saved": 0.0,
            "count": 0
        }
    }
    save_db(db)
    return jsonify({
        "status": "cleared",
        "message": "Histórico limpo! Mas o dinheiro gasto nunca mais voltará.",
        "stats": db["stats"]
    })

@app.route("/api/test-notify", methods=["POST"])
def test_notify():
    trigger_windows_notification(
        "🔔 Teste do Pix Reverso",
        "Você ainda não pagou nada, mas já poderia ter economizado seu tempo!",
        "Sistema de Notificações Operacional"
    )
    return jsonify({"status": "ok", "message": "Notificação de teste enviada ao Windows!"})

if __name__ == "__main__":
    print("=" * 60)
    print(" 💸 PIX REVERSO INICIADO COM SUCESSO! 💸")
    print(" Acesse no seu navegador: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=False)
