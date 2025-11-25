// JavaScript para gerenciar vendas

// Função para obter o CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Função para exibir detalhes da venda
function verDetalhes(vendaId) {
    fetch(`/vendas/detalhes/${vendaId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                exibirDetalhes(data.venda);
            } else {
                alert('Erro ao carregar detalhes: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao carregar detalhes da venda');
        });
}

// Função para exibir os detalhes no modal
function exibirDetalhes(venda) {
    const modal = document.getElementById('detalhesModal');
    const content = document.getElementById('detalhesContent');
    
    // Gerar HTML dos itens
    let itensHTML = '<table class="itens-table"><thead><tr><th>Produto</th><th>Quantidade</th><th>Preço Unit.</th><th>Subtotal</th></tr></thead><tbody>';
    venda.itens.forEach(item => {
        itensHTML += `
            <tr>
                <td>${item.produto}</td>
                <td>${item.quantidade}</td>
                <td>R$ ${item.preco_unitario.toFixed(2)}</td>
                <td>R$ ${item.subtotal.toFixed(2)}</td>
            </tr>
        `;
    });
    itensHTML += '</tbody></table>';
    
    // Gerar HTML dos pagamentos
    let pagamentosHTML = '<table class="pagamentos-table"><thead><tr><th>Forma de Pagamento</th><th>Valor Total</th><th>Parcelamento</th></tr></thead><tbody>';
    venda.pagamentos.forEach(pag => {
        const parcelamento = pag.parcelas && pag.parcelas > 1 ? `${pag.parcelas}x de R$ ${(pag.valor / pag.parcelas).toFixed(2)}` : 'À vista';
        pagamentosHTML += `
            <tr>
                <td>${pag.tipo}</td>
                <td>R$ ${pag.valor.toFixed(2)}</td>
                <td>${parcelamento}</td>
            </tr>
        `;
    });
    pagamentosHTML += '</tbody></table>';
    
    // Gerar seção de parcelas detalhadas (se houver parcelamento)
    let parcelasHTML = '';
    const temParcelamento = venda.pagamentos.some(pag => pag.parcelas > 1);
    
    if (temParcelamento) {
        parcelasHTML = '<div class="section-title" style="margin-top: 24px;">Parcelas a Receber</div>';
        parcelasHTML += '<table class="parcelas-table"><thead><tr><th>Parcela</th><th>Valor / Vencimento</th><th>Status</th><th>Ações</th></tr></thead><tbody>';
        
        venda.pagamentos.forEach(pag => {
            if (pag.parcelas_detalhes && pag.parcelas_detalhes.length > 0) {
                pag.parcelas_detalhes.forEach(parcela => {
                    const statusClass = parcela.status === 'pago' ? 'status-pago' : 'status-pendente';
                    const dataPagamento = parcela.data_pagamento ? `<br><small>Pago em: ${parcela.data_pagamento}</small>` : '';
                    const dataVencimento = parcela.data_vencimento ? `<br><small>Venc.: ${parcela.data_vencimento}</small>` : '';
                    
                    parcelasHTML += `
                        <tr id="parcela-${parcela.id}">
                            <td>${parcela.numero}/${pag.parcelas}</td>
                            <td>R$ ${parcela.valor.toFixed(2)}${dataVencimento}</td>
                            <td>
                                <span class="status-badge ${statusClass}">${parcela.status_display}</span>
                                ${dataPagamento}
                            </td>
                            <td>
                                ${parcela.status === 'pendente' ? 
                                    `<button class="btn-baixar" onclick="baixarParcela(${parcela.id})">Baixar</button>` :
                                    `<span style="color: #34c759; font-size: 12px;">✓ Pago</span>`
                                }
                            </td>
                        </tr>
                    `;
                });
            }
        });
        
        parcelasHTML += '</tbody></table>';
    }
    
    // Preencher o modal com os dados
    content.innerHTML = `
        <div class="venda-info">
            <div class="venda-info-grid">
                <div class="info-item">
                    <div class="info-label">ID da Venda</div>
                    <div class="info-value">#${venda.id}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Código de Barras</div>
                    <div class="info-value">${venda.codigo_barras}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Data</div>
                    <div class="info-value">${venda.data}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Cliente</div>
                    <div class="info-value">${venda.cliente}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Usuário</div>
                    <div class="info-value">${venda.usuario}</div>
                </div>
            </div>
        </div>
        
        <div class="section-title">Itens da Venda</div>
        ${itensHTML}
        
        <div class="section-title">Formas de Pagamento</div>
        ${pagamentosHTML}
        
        ${parcelasHTML}
        
        <div class="total-section">
            <div class="total-row">
                <span>Subtotal:</span>
                <span>R$ ${venda.subtotal.toFixed(2)}</span>
            </div>
            <div class="total-row">
                <span>Desconto:</span>
                <span>R$ ${venda.desconto.toFixed(2)}</span>
            </div>
            <div class="total-row final">
                <span>Total:</span>
                <span>R$ ${venda.total.toFixed(2)}</span>
            </div>
        </div>
    `;
    
    modal.style.display = 'block';
}

// Função para fechar o modal
function fecharModal() {
    const modal = document.getElementById('detalhesModal');
    modal.style.display = 'none';
}

// Fechar modal ao clicar fora dele
window.onclick = function(event) {
    const modal = document.getElementById('detalhesModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

// Função para cancelar venda
function cancelarVenda(vendaId) {
    if (!confirm('Tem certeza que deseja cancelar esta venda? Esta ação devolverá os itens ao estoque.')) {
        return;
    }
    
    fetch(`/vendas/cancelar-venda/${vendaId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Venda cancelada com sucesso!');
            location.reload();
        } else {
            alert('Erro ao cancelar venda: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao cancelar venda');
    });
}

// Fechar modal com tecla ESC
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        fecharModal();
    }
});

// Função para baixar parcela
function baixarParcela(parcelaId) {
    if (!confirm('Confirmar a baixa desta parcela?')) {
        return;
    }
    
    fetch(`/vendas/baixar-parcela/${parcelaId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            
            // Atualizar a linha da parcela na tabela
            const row = document.getElementById(`parcela-${parcelaId}`);
            if (row) {
                const statusCell = row.cells[2];
                const acaoCell = row.cells[3];
                
                statusCell.innerHTML = `
                    <span class="status-badge status-pago">Pago</span>
                    <br><small>Pago em: ${data.data_pagamento}</small>
                `;
                
                acaoCell.innerHTML = '<span style="color: #34c759; font-size: 12px;">✓ Pago</span>';
            }
        } else {
            alert('Erro ao baixar parcela: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao baixar parcela');
    });
}
