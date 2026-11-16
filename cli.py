#!/usr/bin/env python3
"""
Pix Reverso CLI - Linha de Comando do Arrependimento
Execute direto no terminal:
  python cli.py 50 "Comprei água gourmet"
ou simplesmente:
  python cli.py
"""

import sys
import os
import argparse
from datetime import datetime

# Garante encoding UTF-8 no terminal Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Garante import do app.py no mesmo diretório
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import generate_analysis, trigger_windows_notification, load_db, save_db

def format_currency(val):
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def print_receipt_terminal(amount, reason, tone, analysis):
    w = 56
    print("\n" + "=" * w)
    print(" 💸 BANCO CENTRAL DO ARREPENDIMENTO S.A. 💸".center(w))
    print(" Comprovante Oficial de Pix Reverso".center(w))
    print("=" * w)
    print(f" Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f" Motivo:    {reason}")
    print(f" Tom:       {tone.upper()}")
    print("-" * w)
    print(f" VALOR JOGADO FORA:       {format_currency(amount):>28}")
    print(f" O QUE VOCÊ PODERIA TER:  {format_currency(amount):>28}")
    print("-" * w)
    print(" NOTIFICAÇÃO RECEBIDA:")
    # Wrap text
    words = analysis['notification_text'].split()
    line = "   "
    for word in words:
        if len(line) + len(word) + 1 > w - 4:
            print(line)
            line = "   " + word
        else:
            line += " " + word
    if line.strip():
        print(line)
        
    print("-" * w)
    print(" EQUIVALÊNCIAS DO SEU DESPERDÍCIO:")
    for eq in analysis["equivalences"][:4]:
        print(f"   {eq['icon']} {eq['label'][:26]:<26}: {eq['value']:>18}")
    print("=" * w)
    print(" [!] Notificação enviada para o seu Windows Desktop!".center(w))
    print("=" * w + "\n")

def main():
    parser = argparse.ArgumentParser(description="Pix Reverso CLI - Pague para ser lembrado de que não devia ter pago.")
    parser.add_argument("amount", nargs="?", type=float, default=None, help="Valor do Pix (Ex: 25.50)")
    parser.add_argument("reason", nargs="?", type=str, default=None, help="Motivo do arrependimento")
    parser.add_argument("--tone", choices=["sarcastic", "coach", "philosophical", "guilt"], default="sarcastic", help="Tom da notificação")
    
    args = parser.parse_args()
    
    print("""
  +-------------------------------------------------------+
  |                 $ PIX REVERSO CLI $                   |
  |  Você paga para receber uma notificação dizendo que   |
  |         poderia ter economizado aquele dinheiro.      |
  +-------------------------------------------------------+
    """)
    
    amount = args.amount
    if amount is None:
        try:
            val_input = input(" > Digite o valor do Pix Reverso (R$): ").strip().replace(",", ".")
            amount = float(val_input) if val_input else 20.0
        except ValueError:
            print(" [Erro] Valor inválido! Usando R$ 20,00 padrão.")
            amount = 20.0
            
    reason = args.reason
    if not reason:
        reason_input = input(" > Motivo do Pix (Ex: 'Comprei podrão na esquina'): ").strip()
        reason = reason_input if reason_input else "Queimei dinheiro porque sim"
        
    tone = args.tone
    if not args.amount:
        print("\n Tons disponíveis: [1] Sarcástico  [2] Coach  [3] Filosófico  [4] Culpa")
        tone_choice = input(" > Escolha o tom (1-4) [Padrão: 1]: ").strip()
        tone_map = {"1": "sarcastic", "2": "coach", "3": "philosophical", "4": "guilt"}
        tone = tone_map.get(tone_choice, "sarcastic")

    print(f"\n [Processando Pix Reverso de {format_currency(amount)}...]")
    analysis = generate_analysis(amount, reason, tone)
    
    # Salva no banco
    db = load_db()
    receipt = {
        "id": f"PXR-CLI-{int(datetime.now().timestamp())}",
        "date": datetime.now().strftime("%d/%m/%Y às %H:%M:%S"),
        "amount": amount,
        "amount_formatted": format_currency(amount),
        "reason": reason,
        "tone": tone,
        "notification_text": analysis["notification_text"],
        "equivalences": analysis["equivalences"]
    }
    db["transactions"].insert(0, receipt)
    db["stats"]["total_spent"] = round(db["stats"].get("total_spent", 0.0) + amount, 2)
    db["stats"]["total_could_have_saved"] = db["stats"]["total_spent"]
    db["stats"]["count"] = db["stats"].get("count", 0) + 1
    save_db(db)
    
    # Dispara no Windows
    trigger_windows_notification(
        f"💸 Pix Reverso: {format_currency(amount)} Gastos!",
        analysis["notification_text"],
        f"Sabia que você teria {format_currency(amount)} a mais agora?"
    )
    
    # Exibe no terminal
    print_receipt_terminal(amount, reason, tone, analysis)

if __name__ == "__main__":
    main()
