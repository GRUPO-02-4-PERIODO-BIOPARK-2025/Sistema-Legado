// PDV JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('modal-produto');
    const btnAdicionar = document.getElementById('btn-adicionar');
    const btnCancelar = document.getElementById('btn-cancelar');
    const btnFinalizar = document.getElementById('btn-finalizar');
    const modalClose = document.querySelector('.modal-close');
    const descontoInput = document.getElementById('desconto-input');
    const valorRecebidoInput = document.getElementById('valor-recebido');
    const trocoInput = document.getElementById('troco');
    const tabBtns = document.querySelectorAll('.tab-btn');
    
    let tipoSelecionado = 'dinheiro';
    
    // Abrir modal
    btnAdicionar.addEventListener('click', () => {
        modal.classList.add('show');
    });
    
    // Fechar modal
    modalClose.addEventListener('click', () => {
        modal.classList.remove('show');
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('show');
        }
    });
    
    // Busca de produtos no modal
    const modalBusca = document.getElementById('modal-busca');
    const produtosLista = document.querySelectorAll('.produto-item');
    
    modalBusca.addEventListener('input', (e) => {
        const termo = e.target.value.toLowerCase();
        produtosLista.forEach(item => {
            const nome = item.dataset.produtoNome.toLowerCase();
            item.style.display = nome.includes(termo) ? 'flex' : 'none';
        });
    });
    
    // Adicionar produto ao carrinho
    document.querySelectorAll('.btn-selecionar').forEach(btn => {
        btn.addEventListener('click', async function() {
            const item = this.closest('.produto-item');
            const produtoId = item.dataset.produtoId;
            
            try {
                const response = await fetch('/vendas/adicionar-item/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: `produto_id=${produtoId}&quantidade=1`
                });
                
                const data = await response.json();
                
                if (data.success) {
                    location.reload();
                } else {
                    alert(data.message);
                }
            } catch (error) {
                alert('Erro ao adicionar produto');
            }
        });
    });
    
    // Incrementar quantidade
    document.querySelectorAll('.btn-increment').forEach(btn => {
        btn.addEventListener('click', async function() {
            const itemId = this.dataset.itemId;
            await atualizarQuantidade(itemId, 'incrementar');
        });
    });
    
    // Decrementar quantidade
    document.querySelectorAll('.btn-decrement').forEach(btn => {
        btn.addEventListener('click', async function() {
            const itemId = this.dataset.itemId;
            await atualizarQuantidade(itemId, 'decrementar');
        });
    });
    
    // Remover item
    document.querySelectorAll('.btn-remove').forEach(btn => {
        btn.addEventListener('click', async function() {
            if (!confirm('Remover este item?')) return;
            
            const itemId = this.dataset.itemId;
            
            try {
                const response = await fetch(`/vendas/remover-item/${itemId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    location.reload();
                } else {
                    alert(data.message);
                }
            } catch (error) {
                alert('Erro ao remover item');
            }
        });
    });
    
    // Aplicar desconto
    descontoInput.addEventListener('change', async function() {
        const desconto = parseFloat(this.value) || 0;
        
        try {
            const response = await fetch('/vendas/aplicar-desconto/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: `desconto=${desconto}`
            });
            
            const data = await response.json();
            
            if (data.success) {
                document.getElementById('total').textContent = data.total.toFixed(2);
                calcularTroco();
            } else {
                alert(data.message);
            }
        } catch (error) {
            alert('Erro ao aplicar desconto');
        }
    });
    
    // Tabs de pagamento
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            tabBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            tipoSelecionado = this.dataset.tipo;
            valorRecebidoInput.value = '';
            trocoInput.value = '';
        });
    });
    
    // Calcular troco
    valorRecebidoInput.addEventListener('input', calcularTroco);
    
    function calcularTroco() {
        const valorRecebido = parseFloat(valorRecebidoInput.value) || 0;
        const total = parseFloat(document.getElementById('total').textContent);
        const troco = valorRecebido - total;
        
        if (troco >= 0) {
            trocoInput.value = `R$ ${troco.toFixed(2)}`;
            trocoInput.style.color = '#34c759';
        } else {
            trocoInput.value = `Falta: R$ ${Math.abs(troco).toFixed(2)}`;
            trocoInput.style.color = '#ff3b30';
        }
        
        // Armazenar valor no hidden input correspondente
        const hiddenInput = document.getElementById(`pagamento-${tipoSelecionado}`);
        if (hiddenInput) {
            hiddenInput.value = valorRecebido;
        }
    }
    
    // Atualizar quantidade
    async function atualizarQuantidade(itemId, acao) {
        try {
            const response = await fetch(`/vendas/atualizar-quantidade/${itemId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: `acao=${acao}`
            });
            
            const data = await response.json();
            
            if (data.success) {
                if (data.removed) {
                    location.reload();
                } else {
                    // Atualizar UI
                    const itemCard = document.querySelector(`[data-item-id="${itemId}"]`);
                    itemCard.querySelector('.item-qty').textContent = data.quantidade;
                    itemCard.querySelector('.subtotal-valor').textContent = data.subtotal_item.toFixed(2);
                    document.getElementById('subtotal').textContent = data.subtotal.toFixed(2);
                    document.getElementById('total').textContent = data.total.toFixed(2);
                    calcularTroco();
                }
            } else {
                alert(data.message);
            }
        } catch (error) {
            alert('Erro ao atualizar quantidade');
        }
    }
    
    // Cancelar venda
    btnCancelar.addEventListener('click', async function() {
        if (!confirm('Deseja cancelar esta venda?')) return;
        
        try {
            const response = await fetch('/vendas/cancelar/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                location.reload();
            } else {
                alert(data.message);
            }
        } catch (error) {
            alert('Erro ao cancelar venda');
        }
    });
    
    // Finalizar venda
    btnFinalizar.addEventListener('click', async function() {
        const valorRecebido = parseFloat(valorRecebidoInput.value) || 0;
        const total = parseFloat(document.getElementById('total').textContent);
        
        if (valorRecebido < total) {
            alert('Valor insuficiente para finalizar a venda!');
            return;
        }
        
        if (!confirm('Finalizar esta venda?')) return;
        
        try {
            // Preparar dados de pagamento
            const formData = new URLSearchParams();
            formData.append('pagamento_dinheiro', document.getElementById('pagamento-dinheiro').value);
            formData.append('pagamento_cartao', document.getElementById('pagamento-cartao').value);
            formData.append('pagamento_pix', document.getElementById('pagamento-pix').value);
            formData.append('pagamento_outros', document.getElementById('pagamento-outros').value);
            
            const response = await fetch('/vendas/finalizar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert(`Venda finalizada com sucesso!\nTroco: R$ ${data.troco.toFixed(2)}\nCódigo: ${data.codigo_barras}`);
                location.reload();
            } else {
                alert(data.message);
            }
        } catch (error) {
            alert('Erro ao finalizar venda');
        }
    });
    
    // Helper para pegar CSRF token
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
});
