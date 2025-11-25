// PDV JavaScript - Versão 3.0 com opções de cartão
console.log(' Script PDV carregado!');

// Aguardar DOM estar completamente pronto
window.addEventListener('load', function() {
    console.log('✅ Window load event - iniciando...');
    
    setTimeout(function() {
        console.log('=== DEBUG VERSÃO 3.0 ===');
        
        // Buscar elementos
        const testeCartao = document.getElementById('cartao-opcoes');
        console.log('Busca cartao-opcoes:', testeCartao);
        
        if (!testeCartao) {
            console.error(' ERRO: Elemento cartao-opcoes NÃO ENCONTRADO!');
            console.log('Procurando no body...', document.body ? 'Body existe' : 'Body não existe');
            const pagamentoCard = document.querySelector('.pagamento-card');
            console.log('pagamento-card encontrado?', pagamentoCard);
        } else {
            console.log('✅ Elemento cartao-opcoes encontrado!');
        }
        
        inicializarPDV();
    }, 100); // Aguardar 100ms para garantir que tudo está renderizado
});

function inicializarPDV() {
    console.log('Inicializando PDV...');
    
    const modal = document.getElementById('modal-produto');
    const btnAdicionar = document.getElementById('btn-adicionar');
    const btnCancelar = document.getElementById('btn-cancelar');
    const btnFinalizar = document.getElementById('btn-finalizar');
    const modalClose = document.querySelector('.modal-close');
    const descontoInput = document.getElementById('desconto-input');
    const freteInput = document.getElementById('frete-input');
    const valorRecebidoInput = document.getElementById('valor-recebido');
    const trocoInput = document.getElementById('troco');
    const tabBtns = document.querySelectorAll('.tab-btn');
    const cartaoOpcoes = document.getElementById('cartao-opcoes');
    const parcelasGroup = document.getElementById('parcelas-group');
    const trocoGroup = document.getElementById('troco-group');
    const cartaoTipoBtns = document.querySelectorAll('.cartao-tipo-btn');
    const parcelasInput = document.getElementById('parcelas-input');
    const cartaoTipoHidden = document.getElementById('cartao-tipo');
    const cartaoParcelasHidden = document.getElementById('cartao-parcelas');
    
    let tipoSelecionado = 'dinheiro';
    let cartaoTipo = 'debito';
    
    console.log('Elementos encontrados:', {
        cartaoOpcoes: !!cartaoOpcoes,
        tabBtns: tabBtns.length,
        cartaoTipoBtns: cartaoTipoBtns.length
    });
    
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
    if (descontoInput) {
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
    }
    
    // Aplicar frete
    if (freteInput) {
        freteInput.addEventListener('change', async function() {
            const frete = parseFloat(this.value) || 0;
            
            try {
                const response = await fetch('/vendas/aplicar-frete/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: `frete=${frete}`
                });
                
                const data = await response.json();
                
                if (data.success) {
                    document.getElementById('total').textContent = data.total.toFixed(2);
                    calcularTroco();
                } else {
                    alert(data.message);
                }
            } catch (error) {
                alert('Erro ao aplicar frete');
            }
        });
    }
    
    // CRIAR elementos de cartão dinamicamente se não existirem
    function criarOpcoesCartao() {
        let cartaoDiv = document.getElementById('cartao-opcoes');
        
        if (!cartaoDiv) {
            console.log('🔧 Criando opções de cartão dinamicamente...');
            const pagamentoInputs = document.querySelector('.pagamento-inputs');
            
            if (pagamentoInputs) {
                cartaoDiv = document.createElement('div');
                cartaoDiv.id = 'cartao-opcoes';
                cartaoDiv.style.cssText = 'display: none; margin-top: 20px; padding: 20px; background: white; border: 3px solid #7b2ff7; border-radius: 10px;';
                
                cartaoDiv.innerHTML = `
                    <div style="margin-bottom: 16px;">
                        <label style="display: block; margin-bottom: 10px; font-size: 16px; font-weight: bold; color: #1d1d1f;"> Tipo de Cartão</label>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                            <button type="button" class="cartao-tipo-btn-dynamic" data-tipo="debito" style="padding: 14px; border: 2px solid #7b2ff7; border-radius: 8px; background: linear-gradient(90deg, #7b2ff7, #9b41ff); color: white; font-size: 15px; font-weight: bold; cursor: pointer;">Débito</button>
                            <button type="button" class="cartao-tipo-btn-dynamic" data-tipo="credito" style="padding: 14px; border: 2px solid #d2d2d7; border-radius: 8px; background: white; color: #1d1d1f; font-size: 15px; font-weight: bold; cursor: pointer;">Crédito</button>
                        </div>
                    </div>
                    <div id="parcelas-group-dynamic" style="display: none;">
                        <label style="display: block; margin-bottom: 10px; font-size: 16px; font-weight: bold; color: #1d1d1f;"> Número de Parcelas</label>
                        <input type="number" id="parcelas-input-dynamic" min="1" max="12" value="1" style="width: 100%; padding: 14px; border: 2px solid #d2d2d7; border-radius: 8px; font-size: 18px; font-weight: bold;">
                    </div>
                `;
                
                pagamentoInputs.appendChild(cartaoDiv);
                console.log('✅ Opções de cartão criadas!');
                
                // Adicionar eventos aos botões criados
                const btnsDebCred = cartaoDiv.querySelectorAll('.cartao-tipo-btn-dynamic');
                btnsDebCred.forEach(btn => {
                    btn.addEventListener('click', function() {
                        btnsDebCred.forEach(b => {
                            b.style.background = 'white';
                            b.style.color = '#1d1d1f';
                            b.style.borderColor = '#d2d2d7';
                        });
                        this.style.background = 'linear-gradient(90deg, #7b2ff7, #9b41ff)';
                        this.style.color = 'white';
                        this.style.borderColor = '#7b2ff7';
                        
                        const tipo = this.dataset.tipo;
                        const parcelasDiv = document.getElementById('parcelas-group-dynamic');
                        
                        if (tipo === 'credito') {
                            parcelasDiv.style.display = 'block';
                        } else {
                            parcelasDiv.style.display = 'none';
                        }
                    });
                });
            }
        }
        
        return cartaoDiv;
    }
    
    // Tabs de pagamento
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            tabBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            tipoSelecionado = this.dataset.tipo;
            
            // Obter o valor total da venda
            const total = parseFloat(document.getElementById('total').textContent);
            
            // Para PIX e Cartão, preencher automaticamente com o valor total
            if (tipoSelecionado === 'pix' || tipoSelecionado === 'cartao') {
                valorRecebidoInput.value = total.toFixed(2);
                trocoInput.value = '';
            } else {
                valorRecebidoInput.value = '';
                trocoInput.value = '';
            }
            
            // Criar ou buscar opções de cartão
            let cartaoDiv = criarOpcoesCartao();
            const trocoDiv = document.getElementById('troco-group');
            
            if (tipoSelecionado === 'cartao') {
                console.log(' Cartão selecionado!');
                if (cartaoDiv) {
                    cartaoDiv.style.display = 'block';
                    console.log(' Mostrando opções de cartão');
                }
                if (trocoDiv) {
                    trocoDiv.style.display = 'none';
                }
            } else if (tipoSelecionado === 'pix') {
                console.log(' PIX selecionado!');
                if (cartaoDiv) {
                    cartaoDiv.style.display = 'none';
                }
                if (trocoDiv) {
                    trocoDiv.style.display = 'none';
                }
            } else {
                if (cartaoDiv) {
                    cartaoDiv.style.display = 'none';
                }
                if (trocoDiv) {
                    trocoDiv.style.display = 'block';
                }
            }
        });
    });
    
    // Tipo de cartão (débito/crédito) - usando delegação de eventos
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('cartao-tipo-btn')) {
            // Remover estilo ativo de todos
            document.querySelectorAll('.cartao-tipo-btn').forEach(btn => {
                btn.style.background = 'white';
                btn.style.color = '#1d1d1f';
                btn.style.borderColor = '#d2d2d7';
            });
            
            // Adicionar estilo ativo no clicado
            e.target.style.background = 'linear-gradient(90deg, #7b2ff7, #9b41ff)';
            e.target.style.color = 'white';
            e.target.style.borderColor = '#7b2ff7';
            
            cartaoTipo = e.target.dataset.tipo;
            if (cartaoTipoHidden) cartaoTipoHidden.value = cartaoTipo;
            
            // Mostrar parcelas apenas para crédito
            const parcelasDiv = document.getElementById('parcelas-group');
            const parcelasInp = document.getElementById('parcelas-input');
            
            if (cartaoTipo === 'credito') {
                if (parcelasDiv) parcelasDiv.style.display = 'block';
            } else {
                if (parcelasDiv) parcelasDiv.style.display = 'none';
                if (parcelasInp) parcelasInp.value = '1';
                if (cartaoParcelasHidden) cartaoParcelasHidden.value = '1';
            }
        }
    });
    
    // Atualizar número de parcelas
    if (parcelasInput) {
        parcelasInput.addEventListener('change', function() {
            let parcelas = parseInt(this.value) || 1;
            if (parcelas < 1) parcelas = 1;
            if (parcelas > 12) parcelas = 12;
            this.value = parcelas;
            cartaoParcelasHidden.value = parcelas;
        });
    }
    
    // Calcular troco
    valorRecebidoInput.addEventListener('input', calcularTroco);
    
    function calcularTroco() {
        const valorRecebido = parseFloat(valorRecebidoInput.value) || 0;
        const total = parseFloat(document.getElementById('total').textContent);
        
        // Não calcular troco para cartão e PIX
        if (tipoSelecionado === 'cartao' || tipoSelecionado === 'pix') {
            trocoInput.value = '';
        } else {
            const troco = valorRecebido - total;
            
            if (troco >= 0) {
                trocoInput.value = `R$ ${troco.toFixed(2)}`;
                trocoInput.style.color = '#34c759';
            } else {
                trocoInput.value = `Falta: R$ ${Math.abs(troco).toFixed(2)}`;
                trocoInput.style.color = '#ff3b30';
            }
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
        
        // Para cartão, não precisa validar valor recebido (não tem troco)
        if (tipoSelecionado !== 'cartao' && valorRecebido < total) {
            alert('Valor insuficiente para finalizar a venda!');
            return;
        }
        
        if (!confirm('Finalizar esta venda?')) return;
        
        try {
            // Preparar dados de pagamento
            const formData = new URLSearchParams();
            formData.append('pagamento_dinheiro', document.getElementById('pagamento-dinheiro')?.value || '0');
            formData.append('pagamento_cartao', document.getElementById('pagamento-cartao')?.value || '0');
            formData.append('pagamento_pix', document.getElementById('pagamento-pix')?.value || '0');
            formData.append('pagamento_outros', document.getElementById('pagamento-outros')?.value || '0');
            
            // Adicionar informações do cartão se for pagamento com cartão
            if (tipoSelecionado === 'cartao') {
                // Buscar tipo de cartão selecionado
                const btnAtivo = document.querySelector('.cartao-tipo-btn-dynamic[style*="linear-gradient"]');
                const tipoCartao = btnAtivo ? btnAtivo.dataset.tipo : 'debito';
                
                // Buscar número de parcelas
                const parcelasInput = document.getElementById('parcelas-input-dynamic');
                const numParcelas = parcelasInput ? parcelasInput.value : '1';
                
                formData.append('cartao_tipo', tipoCartao);
                formData.append('cartao_parcelas', numParcelas);
                
                console.log('Finalizando com cartão:', tipoCartao, 'Parcelas:', numParcelas);
            }
            
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
    
    // Cliente selection
    const clienteSelect = document.getElementById('cliente-select');
    const clienteInfo = document.getElementById('cliente-info');
    
    if (clienteSelect) {
        clienteSelect.addEventListener('change', async function() {
            const clienteId = this.value;
            
            try {
                const response = await fetch('/vendas/associar-cliente/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: `cliente_id=${clienteId}`
                });
                
                const data = await response.json();
                
                if (data.success) {
                    if (clienteInfo) {
                        if (clienteId) {
                            clienteInfo.textContent = `Cliente: ${data.cliente_nome}`;
                        } else {
                            clienteInfo.textContent = 'Nenhum cliente selecionado';
                        }
                    }
                } else {
                    alert(data.message);
                }
            } catch (error) {
                console.error('Erro ao associar cliente:', error);
                alert('Erro ao associar cliente');
            }
        });
    }
    
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
}

console.log('✅ Script PDV carregado completamente!');
