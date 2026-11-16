/**
 * Pix Reverso - Frontend Application
 * Banco do Desperdício Consciente
 */

document.addEventListener("DOMContentLoaded", () => {
    // ==========================================
    // ESTADO E ELEMENTOS
    // ==========================================
    let soundEnabled = true;
    let audioCtx = null;
    let currentReceipt = null;

    // Elementos de UI
    const pixForm = document.getElementById("pixForm");
    const amountInput = document.getElementById("amountInput");
    const reasonInput = document.getElementById("reasonInput");
    const toneSelect = document.getElementById("toneSelect");
    const delaySelect = document.getElementById("delaySelect");
    const amountPills = document.querySelectorAll(".pill");
    
    // Header & Badges
    const headerLostBalance = document.getElementById("headerLostBalance");
    const btnSoundToggle = document.getElementById("btnSoundToggle");
    const soundIcon = document.getElementById("soundIcon");
    const btnTestNotify = document.getElementById("btnTestNotify");
    
    // Estatísticas
    const statTotalSpent = document.getElementById("statTotalSpent");
    const statCouldSave = document.getElementById("statCouldSave");
    const statCoxinhas = document.getElementById("statCoxinhas");
    const statHoursWorked = document.getElementById("statHoursWorked");
    const historyList = document.getElementById("historyList");
    const btnClearHistory = document.getElementById("btnClearHistory");

    // Modal QR Code
    const qrModal = document.getElementById("qrModal");
    const btnGenerateQr = document.getElementById("btnGenerateQr");
    const btnCloseQr = document.getElementById("btnCloseQr");
    const qrContainer = document.getElementById("qrContainer");
    const modalQrAmount = document.getElementById("modalQrAmount");
    const pixCodeInput = document.getElementById("pixCodeInput");
    const btnCopyPix = document.getElementById("btnCopyPix");
    const btnConfirmQrPay = document.getElementById("btnConfirmQrPay");

    // Modal Comprovante
    const receiptModal = document.getElementById("receiptModal");
    const btnCloseReceipt = document.getElementById("btnCloseReceipt");
    const receiptContent = document.getElementById("receiptContent");
    const btnPrintReceipt = document.getElementById("btnPrintReceipt");
    const btnNewPix = document.getElementById("btnNewPix");
    const toastContainer = document.getElementById("toastContainer");

    // ==========================================
    // SÍNTESE DE ÁUDIO (WEB AUDIO API)
    // ==========================================
    function getAudioContext() {
        if (!audioCtx) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            audioCtx = new AudioContext();
        }
        if (audioCtx.state === 'suspended') {
            audioCtx.resume();
        }
        return audioCtx;
    }

    function playPaymentChime() {
        if (!soundEnabled) return;
        try {
            const ctx = getAudioContext();
            const now = ctx.currentTime;

            // Plim agudo
            const osc1 = ctx.createOscillator();
            const gain1 = ctx.createGain();
            osc1.type = "sine";
            osc1.frequency.setValueAtTime(587.33, now); // D5
            osc1.frequency.exponentialRampToValueAtTime(880, now + 0.15); // A5
            gain1.gain.setValueAtTime(0.3, now);
            gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.5);

            osc1.connect(gain1);
            gain1.connect(ctx.destination);
            osc1.start(now);
            osc1.stop(now + 0.5);
        } catch (e) {
            console.warn("Audio error:", e);
        }
    }

    function playSadRegretChime() {
        if (!soundEnabled) return;
        try {
            const ctx = getAudioContext();
            const now = ctx.currentTime;

            // Tom triste descendente
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = "triangle";
            osc.frequency.setValueAtTime(329.63, now); // E4
            osc.frequency.linearRampToValueAtTime(261.63, now + 0.3); // C4
            osc.frequency.linearRampToValueAtTime(196.00, now + 0.6); // G3
            
            gain.gain.setValueAtTime(0.25, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.8);

            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(now);
            osc.stop(now + 0.8);
        } catch (e) {
            console.warn("Audio error:", e);
        }
    }

    // Toggle de som
    btnSoundToggle.addEventListener("click", () => {
        soundEnabled = !soundEnabled;
        soundIcon.textContent = soundEnabled ? "🔊" : "🔇";
        showToast("Configuração", soundEnabled ? "Som ativado!" : "Som silenciado.");
    });

    // Solicita permissão de notificação nativa do navegador se suportado
    if ("Notification" in window && Notification.permission === "default") {
        Notification.requestPermission();
    }

    // ==========================================
    // TOAST NOTIFICATIONS INTERNAS
    // ==========================================
    function showToast(title, message, icon = "💸", duration = 6000) {
        const toast = document.createElement("div");
        toast.className = "toast";
        toast.innerHTML = `
            <div class="toast-icon">${icon}</div>
            <div class="toast-content">
                <h4>${title}</h4>
                <p>${message}</p>
            </div>
        `;
        toastContainer.appendChild(toast);

        // Dispara notificação HTML5 se permitido
        if ("Notification" in window && Notification.permission === "granted") {
            try {
                new Notification(title, {
                    body: message,
                    icon: "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>💸</text></svg>"
                });
            } catch (err) {
                // Ignore background notification restrictions
            }
        }

        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transform = "translateX(100%)";
            toast.style.transition = "all 0.3s ease";
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    // ==========================================
    // FORMATADORES
    // ==========================================
    function formatBRL(value) {
        return new Intl.NumberFormat("pt-BR", {
            style: "currency",
            currency: "BRL"
        }).format(value);
    }

    // ==========================================
    // VALORES RÁPIDOS (PILLS)
    // ==========================================
    amountPills.forEach(pill => {
        pill.addEventListener("click", () => {
            amountPills.forEach(p => p.classList.remove("active"));
            pill.classList.add("active");
            amountInput.value = parseFloat(pill.dataset.amount).toFixed(2);
        });
    });

    amountInput.addEventListener("input", () => {
        const val = parseFloat(amountInput.value);
        amountPills.forEach(p => {
            if (parseFloat(p.dataset.amount) === val) {
                p.classList.add("active");
            } else {
                p.classList.remove("active");
            }
        });
    });

    // ==========================================
    // PROCESSAMENTO DE PAGAMENTO PIX REVERSO
    // ==========================================
    async function processPixPayment(amount, reason, tone, delay) {
        const payBtn = document.getElementById("btnPayInstant");
        const spinner = document.getElementById("paySpinner");
        
        payBtn.disabled = true;
        if (spinner) spinner.style.display = "inline-block";

        try {
            const resp = await fetch("/api/pay", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ amount, reason, tone, delay })
            });

            const data = await resp.json();

            if (!resp.ok) {
                alert(data.error || "Erro ao processar o Pix Reverso.");
                return;
            }

            playPaymentChime();
            updateStatsUI(data.stats);
            currentReceipt = data.receipt;

            // Se tiver delay, informa o usuário com toast e aguarda
            if (delay > 0) {
                showToast(
                    "⏳ Pix Reverso Agendado",
                    `Você pagou ${data.receipt.amount_formatted}. A notificação de remorso chegará em ${delay} segundos!`,
                    "⏳",
                    5000
                );
                setTimeout(() => {
                    playSadRegretChime();
                    showToast(
                        "💸 O Arrependimento Bateu!",
                        data.receipt.notification_text,
                        "📉",
                        8000
                    );
                }, delay * 1000);
            } else {
                playSadRegretChime();
                showToast(
                    "💸 Pix Reverso Concluído!",
                    data.receipt.notification_text,
                    "📉",
                    8000
                );
            }

            // Exibe comprovante na tela
            renderReceiptModal(data.receipt);
            loadHistory();

        } catch (err) {
            console.error("Erro na requisição:", err);
            alert("Erro de conexão com o servidor do Pix Reverso.");
        } finally {
            payBtn.disabled = false;
            if (spinner) spinner.style.display = "none";
        }
    }

    pixForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const amount = parseFloat(amountInput.value);
        const reason = reasonInput.value.trim() || "Desperdício voluntário de recursos";
        const tone = toneSelect.value;
        const delay = parseInt(delaySelect.value, 10);

        if (isNaN(amount) || amount <= 0) {
            alert("Por favor, informe um valor maior que zero para o seu Pix Reverso.");
            return;
        }

        processPixPayment(amount, reason, tone, delay);
    });

    // ==========================================
    // QR CODE MODAL
    // ==========================================
    btnGenerateQr.addEventListener("click", async () => {
        const amount = parseFloat(amountInput.value) || 25.0;
        try {
            const resp = await fetch("/api/preview-pix", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ amount })
            });
            const data = await resp.json();

            modalQrAmount.textContent = data.amount_formatted;
            pixCodeInput.value = data.pix_code;

            // Renderiza QR Code
            qrContainer.innerHTML = "";
            if (typeof QRCode !== "undefined") {
                new QRCode(qrContainer, {
                    text: data.pix_code,
                    width: 200,
                    height: 200,
                    colorDark: "#000000",
                    colorLight: "#ffffff",
                    correctLevel: QRCode.CorrectLevel.M
                });
            }

            qrModal.classList.add("active");
        } catch (err) {
            console.error(err);
            alert("Falha ao gerar cobrança Pix.");
        }
    });

    btnCloseQr.addEventListener("click", () => {
        qrModal.classList.remove("active");
    });

    btnCopyPix.addEventListener("click", () => {
        pixCodeInput.select();
        navigator.clipboard.writeText(pixCodeInput.value).then(() => {
            const originalText = btnCopyPix.textContent;
            btnCopyPix.textContent = "✅ Copiado!";
            setTimeout(() => btnCopyPix.textContent = originalText, 2000);
        });
    });

    btnConfirmQrPay.addEventListener("click", () => {
        qrModal.classList.remove("active");
        const amount = parseFloat(amountInput.value) || 25.0;
        const reason = reasonInput.value.trim() || "Paguei via QR Code do Remorso";
        const tone = toneSelect.value;
        const delay = parseInt(delaySelect.value, 10);
        processPixPayment(amount, reason, tone, delay);
    });

    // ==========================================
    // COMPROVANTE OFICIAL DE ARREPENDIMENTO
    // ==========================================
    function renderReceiptModal(r) {
        let equivalencesHtml = "";
        if (r.equivalences && r.equivalences.length) {
            equivalencesHtml = `
                <div class="receipt-section-title">O Que Você Poderia Ter Feito Com Essa Grana:</div>
                <div class="receipt-equivalences">
                    ${r.equivalences.map(eq => `
                        <div class="eq-pill">
                            <span class="eq-icon">${eq.icon}</span>
                            <div class="eq-info">
                                <span class="eq-label">${eq.label}</span>
                                <span class="eq-val">${eq.value}</span>
                            </div>
                        </div>
                    `).join("")}
                </div>
            `;
        }

        receiptContent.innerHTML = `
            <div class="receipt-amount-box">
                <div class="receipt-amount-title">Valor Oficialmente Perdido</div>
                <div class="receipt-amount-val">${r.amount_formatted}</div>
                <div class="receipt-amount-sub">💡 Se não tivesse feito esse Pix, você teria exatamente esse valor!</div>
            </div>

            <div class="receipt-alert-box">
                <div class="receipt-alert-title">📢 Notificação Recebida:</div>
                <div class="receipt-alert-text">"${r.notification_text}"</div>
            </div>

            <div class="receipt-section-title">Dados da Transação</div>
            <div class="receipt-row">
                <span class="receipt-label">ID do Pix Reverso:</span>
                <span class="receipt-val">${r.id}</span>
            </div>
            <div class="receipt-row">
                <span class="receipt-label">Data e Hora:</span>
                <span class="receipt-val">${r.date}</span>
            </div>
            <div class="receipt-row">
                <span class="receipt-label">Motivo do Gasto:</span>
                <span class="receipt-val">${r.reason}</span>
            </div>
            <div class="receipt-row">
                <span class="receipt-label">Instituição Emissora:</span>
                <span class="receipt-val">${r.institution || "Banco Central do Desperdício S.A."}</span>
            </div>
            <div class="receipt-row">
                <span class="receipt-label">Pagador:</span>
                <span class="receipt-val">${r.payer || "Você (Mão Furada)"}</span>
            </div>
            <div class="receipt-row">
                <span class="receipt-label">Benefício Obtido:</span>
                <span class="receipt-val" style="color: #f87171;">Absolutamente Nenhum</span>
            </div>

            ${equivalencesHtml}
        `;

        receiptModal.classList.add("active");
    }

    btnCloseReceipt.addEventListener("click", () => {
        receiptModal.classList.remove("active");
    });

    btnNewPix.addEventListener("click", () => {
        receiptModal.classList.remove("active");
        amountInput.focus();
    });

    btnPrintReceipt.addEventListener("click", () => {
        window.print();
    });

    // ==========================================
    // ESTATÍSTICAS E HISTÓRICO
    // ==========================================
    function updateStatsUI(stats) {
        const total = stats.total_spent || 0.0;
        const formatted = formatBRL(total);

        headerLostBalance.textContent = formatted;
        statTotalSpent.textContent = formatted;
        statCouldSave.textContent = formatted;

        // Horas CLT e coxinhas
        const coxinhas = Math.floor(total / 7.0);
        const hours = (total / 6.90).toFixed(1);

        statCoxinhas.textContent = coxinhas;
        statHoursWorked.textContent = `${hours}h`;
    }

    async function loadHistory() {
        try {
            const resp = await fetch("/api/history");
            const data = await resp.json();

            updateStatsUI(data.stats);

            if (!data.transactions || data.transactions.length === 0) {
                historyList.innerHTML = `
                    <div class="empty-state">
                        <span class="empty-icon">📭</span>
                        <p>Nenhum Pix Reverso realizado ainda.</p>
                        <small>Seu bolso agradece. Mas até quando?</small>
                    </div>
                `;
                return;
            }

            historyList.innerHTML = data.transactions.map(item => `
                <div class="history-item" data-id="${item.id}">
                    <div class="history-meta">
                        <span class="history-reason">${item.reason}</span>
                        <div class="history-details">
                            <span>🕒 ${item.date}</span>
                            <span class="history-pill">${(item.tone || 'sarcastic').toUpperCase()}</span>
                        </div>
                    </div>
                    <div class="history-financials">
                        <span class="history-amount">-${item.amount_formatted}</span>
                        <span class="history-could-have">Teria: +${item.amount_formatted}</span>
                    </div>
                </div>
            `).join("");

            // Adiciona clique no item do histórico para ver comprovante
            document.querySelectorAll(".history-item").forEach(itemEl => {
                itemEl.addEventListener("click", () => {
                    const id = itemEl.dataset.id;
                    const found = data.transactions.find(t => t.id === id);
                    if (found) {
                        renderReceiptModal(found);
                    }
                });
            });

        } catch (err) {
            console.error("Erro ao carregar histórico:", err);
        }
    }

    btnClearHistory.addEventListener("click", async () => {
        if (!confirm("Tem certeza que deseja apagar o histórico? O histórico se apaga, mas o dinheiro gasto continua perdido para sempre!")) {
            return;
        }

        try {
            const resp = await fetch("/api/history", { method: "DELETE" });
            const data = await resp.json();
            showToast("Histórico Limpo", data.message, "🧹");
            loadHistory();
        } catch (err) {
            alert("Erro ao limpar histórico.");
        }
    });

    // Testar notificação do Windows
    btnTestNotify.addEventListener("click", async () => {
        try {
            btnTestNotify.disabled = true;
            btnTestNotify.textContent = "Enviando...";
            const resp = await fetch("/api/test-notify", { method: "POST" });
            const data = await resp.json();
            playSadRegretChime();
            showToast("Notificação Enviada!", data.message, "🔔");
        } catch (err) {
            alert("Erro ao enviar notificação de teste.");
        } finally {
            btnTestNotify.disabled = false;
            btnTestNotify.textContent = "🔔 Testar Notificação";
        }
    });

    // Fechar modais ao clicar no backdrop
    [qrModal, receiptModal].forEach(modal => {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) {
                modal.classList.remove("active");
            }
        });
    });

    // Frases randômicas que trocam no card de citação
    const randomTips = [
        `"Se você economizasse R$ 50 todo dia por 500 anos, teria R$ 9.125.000. Mas você preferiu pagar um Pix Reverso."`,
        `"O Pix Reverso é o único investimento com rentabilidade de -100% garantida pela física cuántica."`,
        `"Gastou R$ 20? Parabéns, agora você tem 0 reais e uma notificação que te humilha."`,
        `"Se dinheiro comprasse felicidade, o Pix Reverso seria a assinatura mensal da culpa."`,
        `"Dica de economia: Não faça Pix Reverso. Mas se fizer, pelo menos leia a notificação."`
    ];

    const randomTipCard = document.getElementById("randomTipCard");
    if (randomTipCard) {
        const textEl = randomTipCard.querySelector(".quote-text");
        setInterval(() => {
            if (textEl) {
                textEl.textContent = randomTips[Math.floor(Math.random() * randomTips.length)];
            }
        }, 12000);
    }

    // Inicialização
    loadHistory();
});
