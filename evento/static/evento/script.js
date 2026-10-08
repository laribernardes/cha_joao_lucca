
// =========================================================
// CHÁ DE BEBÊ JOÃO LUCCA — SCRIPT PRINCIPAL
// =========================================================

const diaperOptions = document.querySelectorAll('.diaper-option');
const diaperSelectedMessage = document.getElementById('diaperSelectedMessage');
const rsvpDiaperSize = document.getElementById('rsvpDiaperSize');
const diaperInput = document.getElementById('tamanho_fralda');
const rsvpForm = document.getElementById('rsvpForm');
const rsvpError = document.getElementById('rsvpError');

let selectedDiaper = diaperInput?.value || null;

const nomesItensPrincipais = {
    RN: 'Fralda RN',
    P: 'Fralda P',
    M: 'Fralda M',
    G: 'Fralda G',
    lenco: 'Lenço umedecido',
    pomada: 'Pomada'
};

const mimoOptions = document.querySelectorAll('.mimo-suggestion');
const mimoInput = document.getElementById('mimo');
let selectedMimo = mimoInput?.value || '';
const rsvpMimoSelected = document.getElementById('rsvpMimoSelected');

const nomesMimos = {
    macacao: 'Macacão',
    body: 'Body',
    mijao: 'Mijão',
    meia: 'Meia',
    luvinha: 'Luvinha',
    touca: 'Touca',
    manta: 'Manta',
    toalhinha_boca: 'Toalhinha de boca',
    toalha_banho: 'Toalha de banho',
    outros: 'Outros'
};

// =========================================================
// DISPONIBILIDADE DOS PRESENTES
// =========================================================

// A disponibilidade vem do Django nos cartões de presentes.
// Não usamos uma segunda lista de limites no JavaScript.

function itemIndisponivel(codigo) {
    const cartao = Array.from(diaperOptions).find(
        option => option.dataset.size === codigo
    );

    return !cartao ||
        cartao.disabled ||
        cartao.classList.contains('indisponivel');
}

function atualizarOpcoesAcompanhante(select) {
    if (!select) return;

    Array.from(select.options).forEach(option => {
        if (!option.value) return;

        option.disabled = itemIndisponivel(option.value);
    });

    if (select.value && select.selectedOptions[0]?.disabled) {
        select.value = '';
    }
}

// =========================================================
// MENSAGENS DE ERRO
// =========================================================

function mostrarErro(mensagem) {
    if (!rsvpError) return;

    rsvpError.textContent = mensagem;
    rsvpError.classList.add('active');
}

function limparErro() {
    if (!rsvpError) return;

    rsvpError.textContent = '';
    rsvpError.classList.remove('active');
}

// =========================================================
// ESCOLHA DO PRESENTE PRINCIPAL
// =========================================================

diaperOptions.forEach(option => {
    option.addEventListener('click', () => {
        if (
            option.disabled ||
            option.classList.contains('indisponivel')
        ) {
            return;
        }

        diaperOptions.forEach(item => {
            item.classList.remove('selected');
        });

        option.classList.add('selected');

        selectedDiaper = option.dataset.size;

        const nomeItem = nomesItensPrincipais[selectedDiaper];

        if (diaperInput) {
            diaperInput.value = selectedDiaper;
        }

        if (diaperSelectedMessage) {
            diaperSelectedMessage.innerHTML =
                `Presente escolhido: <strong>${nomeItem}</strong> ✓`;

            diaperSelectedMessage.classList.add('active');
        }

        if (rsvpDiaperSize) {
            rsvpDiaperSize.textContent = nomeItem;
        }

        limparErro();
    });
});

// Impede o envio de uma seleção antiga que ficou indisponível.

if (selectedDiaper && itemIndisponivel(selectedDiaper)) {
    selectedDiaper = null;

    if (diaperInput) {
        diaperInput.value = '';
    }

    if (rsvpDiaperSize) {
        rsvpDiaperSize.textContent = 'Nenhum presente selecionado';
    }

    diaperOptions.forEach(item => {
        item.classList.remove('selected');
    });
}

// =========================================================
// ESCOLHA DO MIMO
// =========================================================

mimoOptions.forEach(option => {
    option.addEventListener('click', () => {
        const mimo = option.dataset.mimo;

        // Se clicar novamente, desmarca.

        if (selectedMimo === mimo) {
            selectedMimo = '';

            option.classList.remove('selected');

            if (mimoInput) {
                mimoInput.value = '';
            }

            if (rsvpMimoSelected) {
                rsvpMimoSelected.textContent =
                    'Nenhum mimo selecionado';
            }

            return;
        }

        // Remove a seleção anterior.

        mimoOptions.forEach(item => {
            item.classList.remove('selected');
        });

        // Marca o novo mimo.

        option.classList.add('selected');

        selectedMimo = mimo;

        if (mimoInput) {
            mimoInput.value = mimo;
        }

        if (rsvpMimoSelected) {
            rsvpMimoSelected.textContent =
                nomesMimos[mimo];
        }
    });
});

// =========================================================
// ACOMPANHANTES
// =========================================================

const addCompanionButton =
    document.getElementById('addCompanion');

const companionsContainer =
    document.getElementById('companionsContainer');

// =========================================================
// ATUALIZAR NUMERAÇÃO DOS ACOMPANHANTES
// =========================================================

function atualizarNumeracaoAcompanhantes() {
    if (!companionsContainer) return;

    const acompanhantes =
        companionsContainer.querySelectorAll('.companion-card');

    acompanhantes.forEach((companion, index) => {
        const numero = index + 1;

        const titulo =
            companion.querySelector('.companion-title');

        const nameInput =
            companion.querySelector('.companion-name');

        const typeSelect =
            companion.querySelector('.companion-type');

        const diaperSelect =
            companion.querySelector('.companion-diaper-select');

        const giftSelect =
            companion.querySelector('.companion-gift-select');

        if (titulo) {
            titulo.textContent = `Acompanhante ${numero}`;
        }

        if (nameInput) {
            nameInput.name = `acompanhante_nome_${numero}`;
        }

        if (typeSelect) {
            typeSelect.name = `acompanhante_tipo_${numero}`;
        }

        if (diaperSelect) {
            diaperSelect.name = `acompanhante_fralda_${numero}`;
        }

        if (giftSelect) {
            giftSelect.name = `acompanhante_mimo_${numero}`;
        }
    });
}

// =========================================================
// CRIAR NOVO ACOMPANHANTE
// =========================================================

function criarAcompanhante() {
    if (!companionsContainer) return;

    const companion = document.createElement('div');

    companion.className = 'companion-card';

    companion.innerHTML = `
        <div class="companion-header">
            <strong class="companion-title">
                Acompanhante
            </strong>

            <button
                type="button"
                class="remove-companion"
            >
                Remover acompanhante
            </button>
        </div>

        <label>
            Nome do acompanhante
        </label>

        <input
            type="text"
            class="companion-name"
            placeholder="Digite o nome do acompanhante"
            autocomplete="name"
            required
        >

        <label>
            Quem estará com você?
        </label>

        <select class="companion-type" required>
            <option value="">
                Selecione uma opção
            </option>

            <option value="adulto">
                Adulto
            </option>

            <option value="crianca">
                Criança
            </option>
        </select>

        <div
            class="companion-diaper"
            style="display: none;"
        >
            <label>
                Presente principal que irá levar
            </label>

            <select class="companion-diaper-select">
                <option value="">
                    Selecione uma opção
                </option>

                <option value="RN">Fralda RN</option>
                <option value="P">Fralda P</option>
                <option value="M">Fralda M</option>
                <option value="G">Fralda G</option>
                <option value="lenco">Lenço umedecido</option>
                <option value="pomada">Pomada</option>
            </select>
        </div>

        <div class="companion-gift">
            <label>
                Vai levar algum mimo?
            </label>

            <select class="companion-gift-select">
                <option value="">
                    Nenhum mimo
                </option>

                <option value="macacao">Macacão</option>
                <option value="body">Body</option>
                <option value="mijao">Mijão</option>
                <option value="meia">Meia</option>
                <option value="luvinha">Luvinha</option>
                <option value="touca">Touca</option>
                <option value="manta">Manta</option>
                <option value="toalhinha_boca">
                    Toalhinha de boca
                </option>
                <option value="toalha_banho">
                    Toalha de banho
                </option>
                <option value="outros">Outros</option>
            </select>
        </div>
    `;

    companionsContainer.appendChild(companion);

    // Elementos do novo acompanhante.

    const typeSelect =
        companion.querySelector('.companion-type');

    const diaperContainer =
        companion.querySelector('.companion-diaper');

    const diaperSelect =
        companion.querySelector('.companion-diaper-select');

    const removeButton =
        companion.querySelector('.remove-companion');

    // Bloqueia os presentes que já atingiram o limite.

    atualizarOpcoesAcompanhante(diaperSelect);

    // =====================================================
    // ADULTO OU CRIANÇA
    // =====================================================

    typeSelect.addEventListener('change', () => {
        if (typeSelect.value === 'adulto') {

            // Atualiza os presentes disponíveis.

            atualizarOpcoesAcompanhante(diaperSelect);

            diaperContainer.style.display = 'block';

            diaperSelect.required = true;

        } else {

            // Crianças não precisam escolher presente.

            diaperContainer.style.display = 'none';

            diaperSelect.required = false;

            diaperSelect.value = '';
        }
    });

    // =====================================================
    // REMOVER ACOMPANHANTE
    // =====================================================

    removeButton.addEventListener('click', () => {
        companion.style.opacity = '0';

        companion.style.transform = 'translateY(-6px)';

        setTimeout(() => {
            companion.remove();

            atualizarNumeracaoAcompanhantes();
        }, 180);
    });

    atualizarNumeracaoAcompanhantes();
}

// =========================================================
// BOTÃO ADICIONAR ACOMPANHANTE
// =========================================================

if (addCompanionButton) {
    addCompanionButton.addEventListener(
        'click',
        criarAcompanhante
    );
}

// =========================================================
// VALIDAÇÃO DO FORMULÁRIO
// =========================================================

if (rsvpForm) {
    rsvpForm.addEventListener('submit', event => {
        limparErro();

        const selectedPresence =
            document.querySelector(
                'input[name="presenca"]:checked'
            );

        // Presença não selecionada.

        if (!selectedPresence) {
            event.preventDefault();

            mostrarErro(
                'Informe se você poderá estar presente.'
            );

            return;
        }

        // Convidado confirmou presença.

        if (selectedPresence.value === 'sim') {

            // Precisa escolher um presente disponível.

            if (
                !selectedDiaper ||
                itemIndisponivel(selectedDiaper)
            ) {
                event.preventDefault();

                mostrarErro(
                    'Escolha um presente principal disponível para confirmar sua presença.'
                );

                return;
            }

            // Validar acompanhantes.

            if (companionsContainer) {
                const acompanhantes =
                    companionsContainer.querySelectorAll(
                        '.companion-card'
                    );

                for (const companion of acompanhantes) {

                    const nameInput =
                        companion.querySelector('.companion-name');

                    const typeSelect =
                        companion.querySelector('.companion-type');

                    const diaperSelect =
                        companion.querySelector(
                            '.companion-diaper-select'
                        );

                    // Nome obrigatório.

                    if (!nameInput?.value.trim()) {
                        event.preventDefault();

                        mostrarErro(
                            'Informe o nome de todos os acompanhantes.'
                        );

                        nameInput?.focus();

                        return;
                    }

                    // Adulto ou criança obrigatório.

                    if (!typeSelect?.value) {
                        event.preventDefault();

                        mostrarErro(
                            'Informe se cada acompanhante é adulto ou criança.'
                        );

                        typeSelect?.focus();

                        return;
                    }

                    // Adultos precisam escolher um
                    // presente principal disponível.

                    if (
                        typeSelect.value === 'adulto' &&
                        (
                            !diaperSelect?.value ||
                            itemIndisponivel(diaperSelect.value)
                        )
                    ) {
                        event.preventDefault();

                        mostrarErro(
                            `Escolha um presente principal disponível para ${nameInput.value.trim()}.`
                        );

                        diaperSelect?.focus();

                        return;
                    }
                }
            }
        }

        // A confirmação final dos limites acontece no Django.
    });
}

// =========================================================
// NAVEGAÇÃO ENTRE AS TELAS
// =========================================================

function mostrarTela(id) {
    const atual =
        document.querySelector(
            '.convite-tela.tela-ativa'
        );

    const destino =
        document.getElementById(id);

    if (!destino || atual === destino) {
        return;
    }

    if (atual) {
        atual.classList.remove('tela-ativa');
    }

    destino.classList.add('tela-ativa');

    window.scrollTo({
        top: 0,
        behavior: 'auto'
    });
}

// =========================================================
// COMPATIBILIDADE COM MENU MOBILE ANTERIOR
// =========================================================

const menuMobileBtn =
    document.querySelector('.menu-mobile-btn');

const menuMobile =
    document.querySelector('.menu-mobile');

if (menuMobileBtn && menuMobile) {
    menuMobileBtn.addEventListener('click', () => {
        menuMobile.classList.toggle('ativo');
    });
}

function fecharMenu() {
    if (menuMobile) {
        menuMobile.classList.remove('ativo');
    }
}

// =========================================================
// ABRIR TELA FINAL APÓS CONFIRMAÇÃO
// =========================================================

if (window.abrirTelaFinal) {
    mostrarTela('final');
}

// =========================================================
// MENU HAMBÚRGUER DO CABEÇALHO
// =========================================================

function iniciarMenuHamburguer() {
    const botaoMenu =
        document.querySelector('.menu-toggle');

    const menu =
        document.querySelector('#menu-principal');

    if (!botaoMenu || !menu) {
        return;
    }

    function definirMenu(aberto) {
        menu.classList.toggle('menu-aberto', aberto);

        botaoMenu.classList.toggle('ativo', aberto);

        botaoMenu.setAttribute(
            'aria-expanded',
            String(aberto)
        );

        botaoMenu.setAttribute(
            'aria-label',
            aberto ? 'Fechar menu' : 'Abrir menu'
        );
    }

    // Abrir e fechar menu.

    botaoMenu.addEventListener('click', () => {
        definirMenu(
            !menu.classList.contains('menu-aberto')
        );
    });

    // Fechar ao selecionar uma opção.

    menu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            definirMenu(false);
        });
    });
}

if (document.readyState === 'loading') {
    document.addEventListener(
        'DOMContentLoaded',
        iniciarMenuHamburguer
    );
} else {
    iniciarMenuHamburguer();
}
