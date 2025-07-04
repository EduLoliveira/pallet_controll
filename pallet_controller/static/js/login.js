// ==============================================
// MÓDULOS E UTILITÁRIOS
// ==============================================

// Configurações de URLs da API
const API_URLS = {
    VALIDAR_CNPJ: window.URLS?.validarCNPJ || '/api/validarCNPJ/',
    CONSULTAR_CEP: window.URLS?.consultarCEP || '/api/consultarCEP/',
    LISTAR_ESTADOS: window.URLS?.listarEstados || '/api/estados/',
    LISTAR_MUNICIPIOS: (uf) => (window.URLS?.listarMunicipios || '/api/municipios/').replace('UF', uf)
};

// Módulo de Utilidades
const FormUtils = {
    initTooltips: function() {
        const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltips.forEach(el => new bootstrap.Tooltip(el));
    },

    setupRequiredFields: function() {
        document.querySelectorAll('[required]').forEach(element => {
            const label = document.querySelector(`label[for="${element.id}"]`);
            label?.classList.add('required-field');
        });
    },

    initFormValidation: function() {
        document.querySelectorAll('.needs-validation').forEach(form => {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    }
};

// Módulo de Máscaras
const MaskUtils = {
    applyCnpjMask: function(value) {
        value = value.replace(/\D/g, '');
        if (value.length > 14) value = value.substring(0, 14);
        return value
            .replace(/^(\d{2})/, '$1.')
            .replace(/^(\d{2})\.(\d{3})/, '$1.$2.')
            .replace(/\.(\d{3})(\d)/, '.$1/$2')
            .replace(/(\d{4})(\d)/, '$1-$2');
    },

    applyCepMask: function(value) {
        value = value.replace(/\D/g, '');
        if (value.length > 8) value = value.substring(0, 8);
        return value.replace(/^(\d{5})(\d)/, '$1-$2').replace(/-$/, '');
    },

    applyPhoneMask: function(value) {
        value = value.replace(/\D/g, '');
        const isMobile = value.length > 10;
        if (value.length > 11) value = value.substring(0, 11);
        return value
            .replace(/^(\d{2})/, '($1) ')
            .replace(/(\d{4,5})(\d)/, '$1-$2')
            .substring(0, isMobile ? 15 : 14);
    },

    initMasks: function() {
        // CNPJ
        const cnpjInput = document.getElementById('id_cnpj');
        if (cnpjInput) {
            cnpjInput.addEventListener('input', (e) => {
                e.target.value = this.applyCnpjMask(e.target.value);
            });
        }

        // CEP
        const cepInput = document.getElementById('id_cep');
        if (cepInput) {
            cepInput.addEventListener('input', (e) => {
                e.target.value = this.applyCepMask(e.target.value);
            });
        }

        // Telefone
        const telefoneInput = document.getElementById('id_telefone');
        if (telefoneInput) {
            telefoneInput.addEventListener('input', (e) => {
                e.target.value = this.applyPhoneMask(e.target.value);
            });
        }
    }
};

// Módulo de APIs
const ApiServices = {
    fetchWithTimeout: async function(url, options = {}, timeout = 8000) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });
            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            throw error;
        }
    },

    validateCNPJ: async function(cnpj) {
        try {
            const data = await this.fetchWithTimeout(
                `${API_URLS.VALIDAR_CNPJ}?cnpj=${cnpj.replace(/\D/g, '')}`
            );

            if (!data.valido) {
                throw new Error('CNPJ inválido ou não encontrado.');
            }

            return data;
        } catch (error) {
            console.error('CNPJ validation error:', error);
            throw error;
        }
    },

    searchCEP: async function(cep) {
        try {
            const data = await this.fetchWithTimeout(
                `${API_URLS.CONSULTAR_CEP}?cep=${cep.replace(/\D/g, '')}`
            );

            if (data.erro) {
                throw new Error(data.erro || 'CEP não encontrado ou inválido.');
            }

            return data;
        } catch (error) {
            console.error('CEP search error:', error);
            throw error;
        }
    },

    listStates: async function() {
        try {
            const response = await fetch(API_URLS.LISTAR_ESTADOS);
            const data = await response.json();

            if (!response.ok || !data.estados) {
                throw new Error('Failed to load states');
            }

            return data.estados;
        } catch (error) {
            console.error('States loading error:', error);
            throw error;
        }
    },

    listCities: async function(uf) {
        try {
            const response = await fetch(API_URLS.LISTAR_MUNICIPIOS(uf));
            const data = await response.json();

            if (!response.ok || !data.municipios) {
                throw new Error('Failed to load cities');
            }

            return data.municipios;
        } catch (error) {
            console.error('Cities loading error:', error);
            throw error;
        }
    }
};

// Módulo de UI
const UIManager = {
    showLoading: function(element, message) {
        element.textContent = message;
        element.className = 'form-text text-muted d-block';
    },

    showSuccess: function(element, message) {
        element.textContent = message;
        element.className = 'valid-feedback d-block';
    },

    showError: function(element, message) {
        element.textContent = message;
        element.className = 'invalid-feedback d-block';
    },

    resetFeedback: function(element) {
        element.textContent = '';
        element.className = 'form-text';
    },

    showErrorModal: function(message) {
        const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
        const errorMessageElement = document.getElementById('errorModalMessage');
        
        errorMessageElement.textContent = message;
        errorModal.show();
    }
};

// ==============================================
// FUNÇÕES DE VALIDAÇÃO
// ==============================================

function validatePassword() {
    const password1 = document.getElementById('id_password1');
    const password2 = document.getElementById('id_password2');

    if (password1.value !== password2.value && password2.value.length > 0) {
        password2.setCustomValidity("As senhas não coincidem");
        password2.classList.add('is-invalid');
    } else {
        password2.setCustomValidity("");
        password2.classList.remove('is-invalid');
    }
}

function validatePasswordStrength() {
    const password = document.getElementById('id_password1').value;
    const indicator = document.getElementById('passwordStrength');

    if (!password) {
        indicator.textContent = '';
        return;
    }

    const strength = checkPasswordStrength(password);
    indicator.textContent = strength.message;
    indicator.className = 'form-text ' + strength.class;
}

function checkPasswordStrength(password) {
    // Verifica comprimento mínimo
    if (password.length < 8) {
        return { message: 'Senha fraca (mínimo 8 caracteres)', class: 'text-danger' };
    }

    // Verifica complexidade
    const hasNumber = /\d/.test(password);
    const hasUpper = /[A-Z]/.test(password);
    const hasLower = /[a-z]/.test(password);
    const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    let score = 0;
    if (hasNumber) score++;
    if (hasUpper) score++;
    if (hasLower) score++;
    if (hasSpecial) score++;

    if (score < 2) {
        return { message: 'Senha fraca (adicione números, maiúsculas ou caracteres especiais)', class: 'text-danger' };
    } else if (score < 4) {
        return { message: 'Senha média (pode ser melhorada)', class: 'text-warning' };
    } else {
        return { message: 'Senha forte', class: 'text-success' };
    }
}

// ==============================================
// FUNÇÕES DE PREENCHIMENTO DE DADOS
// ==============================================

function fillCompanyData(data) {
    const fields = {
        'id_razao_social': data.DsRazaoSocial || '',
        'id_nome_fantasia': data.DsNomeFantasia || '',
        'id_email': data.DsEmail || '',
        'id_site': data.DsSite || '',
        'id_inscricao_estadual': data.DsInscricaoEstadual || '',
        'id_inscricao_municipal': data.DsInscricaoMunicipal || '',
        'id_iest': data.DsIEST || '',
        'id_situacao_cadastral': data.DsSituacaoCadastral || 'Ativo',
        'id_cep': data.NrEnderecoCep ? data.NrEnderecoCep.replace(/^(\d{5})(\d{3})$/, "$1-$2") : '',
        'id_logradouro': data.DsEnderecoLogradouro || '',
        'id_numero': data.NrEnderecoNumero || '',
        'id_bairro': data.DsEnderecoBairro || '',
        'id_complemento': data.DsEnderecoComplemento || '',
    };

    Object.entries(fields).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            if (element.tagName === 'SELECT') {
                const optionExists = Array.from(element.options).some(opt => opt.value === value);
                if (optionExists) {
                    element.value = value;
                    element.classList.add('is-valid');
                }
            } else {
                element.value = value;
                if (value && value.trim() !== '') {
                    element.classList.add('is-valid');
                }
            }
        }
    });
}

async function fillAddress(addressData) {
    const elements = {
        'id_logradouro': addressData.DsEnderecoLogradouro,
        'id_numero': addressData.NrEnderecoNumero,
        'id_bairro': addressData.DsEnderecoBairro,
        'id_complemento': addressData.DsEnderecoComplemento
    };

    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element && value) {
            element.value = value;
            if (value) element.classList.add('is-valid');
        }
    });

    await fillCityState(addressData.estado, addressData.cidade);
    document.getElementById('id_numero')?.focus();
}

async function fillCityState(uf, cityName) {
    const estadoSelect = document.getElementById('id_estado');
    const cidadeSelect = document.getElementById('id_cidade');

    if (!estadoSelect || !cidadeSelect || !uf) return;

    estadoSelect.value = uf;
    estadoSelect.dispatchEvent(new Event('change'));

    let attempts = 0;
    const maxAttempts = 10;
    const checkInterval = 100;

    return new Promise((resolve) => {
        const checkCitySelect = setInterval(() => {
            attempts++;

            if (cidadeSelect.options.length > 1 && !cidadeSelect.disabled) {
                clearInterval(checkCitySelect);

                const cityOption = Array.from(cidadeSelect.options)
                    .find(opt => opt.text.trim().toUpperCase() === (cityName || '').trim().toUpperCase());

                if (cityOption) {
                    cidadeSelect.value = cityOption.value;
                    cidadeSelect.classList.add('is-valid');
                }

                resolve();
            } else if (attempts >= maxAttempts) {
                clearInterval(checkCitySelect);
                resolve();
            }
        }, checkInterval);
    });
}

// ==============================================
// CONFIGURAÇÃO DE EVENTOS
// ==============================================

function setupCNPJValidation() {
    const cnpjInput = document.getElementById('id_cnpj');
    const validateBtn = document.getElementById('validar-cnpj-btn');
    const feedbackDiv = document.getElementById('cnpjFeedback');

    if (!cnpjInput || !validateBtn || !feedbackDiv) return;

    validateBtn.addEventListener('click', async () => {
        const cnpj = cnpjInput.value;
        UIManager.resetFeedback(feedbackDiv);
        cnpjInput.classList.remove('is-invalid', 'is-valid');

        if (cnpj.replace(/\D/g, '').length !== 14) {
            UIManager.showError(feedbackDiv, 'CNPJ deve ter 14 dígitos.');
            cnpjInput.classList.add('is-invalid');
            return;
        }

        UIManager.showLoading(feedbackDiv, 'Validando CNPJ...');

        try {
            const data = await ApiServices.validateCNPJ(cnpj);
            UIManager.showSuccess(feedbackDiv, 'CNPJ válido.');
            cnpjInput.classList.add('is-valid');
            fillCompanyData(data);
            await fillAddress(data);
        } catch (error) {
            UIManager.showError(feedbackDiv, 'CNPJ inválido ou não encontrado.');
            cnpjInput.classList.add('is-invalid');
        }
    });
}

function setupCEPSearch() {
    const cepInput = document.getElementById('id_cep');
    const searchBtn = document.getElementById('buscar-cep-btn');
    const feedbackDiv = document.getElementById('cepFeedback');

    if (!cepInput || !searchBtn || !feedbackDiv) return;

    searchBtn.addEventListener('click', async () => {
        const cep = cepInput.value;
        UIManager.resetFeedback(feedbackDiv);
        cepInput.classList.remove('is-invalid', 'is-valid');

        if (cep.replace(/\D/g, '').length !== 8) {
            UIManager.showErrorModal("CEP inválido! Digite um CEP válido com 8 dígitos.");
            return;
        }

        UIManager.showLoading(feedbackDiv, 'Buscando CEP...');

        try {
            const data = await ApiServices.searchCEP(cep);
            UIManager.showSuccess(feedbackDiv, 'CEP encontrado.');
            cepInput.classList.add('is-valid');
            await fillAddress(data);
        } catch (error) {
            UIManager.showError(feedbackDiv, 'CEP não encontrado.');
            cepInput.classList.add('is-invalid');
        }
    });
}

function setupLocationSelects() {
    const estadoSelect = document.getElementById('id_estado');
    if (!estadoSelect) return;

    loadStates();

    estadoSelect.addEventListener('change', function() {
        if (this.value) {
            loadCities(this.value);
        } else {
            const cidadeSelect = document.getElementById('id_cidade');
            cidadeSelect.innerHTML = '<option value="">Selecione o estado primeiro</option>';
            cidadeSelect.disabled = true;
        }
    });
}

async function loadStates() {
    const estadoSelect = document.getElementById('id_estado');
    if (!estadoSelect) return;

    try {
        const states = await ApiServices.listStates();
        estadoSelect.innerHTML = '<option value="" selected disabled>Selecione...</option>';
        states.forEach(state => {
            estadoSelect.add(new Option(state.nome, state.sigla));
        });
    } catch (error) {
        estadoSelect.innerHTML = '<option value="">Erro ao carregar estados</option>';
    }
}

async function loadCities(uf) {
    const cidadeSelect = document.getElementById('id_cidade');
    if (!cidadeSelect || !uf) return;

    cidadeSelect.disabled = true;
    cidadeSelect.innerHTML = '<option value="">Carregando cidades...</option>';

    try {
        const cities = await ApiServices.listCities(uf);
        cidadeSelect.innerHTML = '<option value="" selected disabled>Selecione...</option>';
        cities.forEach(city => {
            cidadeSelect.add(new Option(city.nome, city.nome));
        });
        cidadeSelect.disabled = false;
    } catch (error) {
        cidadeSelect.innerHTML = '<option value="">Erro ao carregar cidades</option>';
        cidadeSelect.disabled = false;
    }
}

function setupPasswordToggle() {
    document.querySelectorAll('.password-toggle').forEach(button => {
        button.addEventListener('click', function() {
            const inputId = this.getAttribute('data-target');
            const input = document.getElementById(inputId);
            const icon = this.querySelector('i');

            if (input.type === "password") {
                input.type = "text";
                icon.classList.replace('bi-eye', 'bi-eye-slash');
            } else {
                input.type = "password";
                icon.classList.replace('bi-eye-slash', 'bi-eye');
            }
        });
    });
}

function setupPasswordValidation() {
    const password1 = document.getElementById('id_password1');
    const password2 = document.getElementById('id_password2');
    const strengthIndicator = document.getElementById('passwordStrength');

    if (password1 && password2) {
        password1.addEventListener('input', function() {
            validatePassword();
            validatePasswordStrength();
        });

        password2.addEventListener('input', validatePassword);
    }
}

function setupFormSubmit() {
    const form = document.getElementById('PessoaJuridicaForm');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        const submitBtn = this.querySelector('.btn-submit');
        const submitText = submitBtn.querySelector('#submitText');
        const spinner = submitBtn.querySelector('#spinner');
        
        submitText.textContent = 'Processando...';
        spinner.classList.remove('d-none');
        submitBtn.disabled = true;

        if (!this.checkValidity()) {
            e.preventDefault();
            submitText.textContent = 'Cadastrar';
            spinner.classList.add('d-none');
            submitBtn.disabled = false;
            UIManager.showErrorModal("Por favor, preencha todos os campos obrigatórios corretamente!");
            return;
        }

        const password1 = document.getElementById('id_password1').value;
        const password2 = document.getElementById('id_password2').value;
        const strength = checkPasswordStrength(password1);

        if (password1 !== password2) {
            e.preventDefault();
            submitText.textContent = 'Cadastrar';
            spinner.classList.add('d-none');
            submitBtn.disabled = false;
            UIManager.showErrorModal("As senhas não coincidem! Por favor, digite a mesma senha nos dois campos.");
            return;
        }

        if (strength.class !== 'text-success') {
            e.preventDefault();
            submitText.textContent = 'Cadastrar';
            spinner.classList.add('d-none');
            submitBtn.disabled = false;
            UIManager.showErrorModal('Você deve inserir uma senha forte para prosseguir!\n\nRequisitos:\n- Mínimo 8 caracteres\n- Pelo menos 1 número\n- Pelo menos 1 letra maiúscula\n- Pelo menos 1 letra minúscula\n- Pelo menos 1 caractere especial');
            return;
        }
    });
}

function setupUsernameHint() {
    const inputUsername = document.getElementById('id_username');
    const hint = document.getElementById('loginHint');

    if (inputUsername && hint) {
        inputUsername.addEventListener('focus', () => {
            hint.classList.remove('d-none');
        });

        inputUsername.addEventListener('blur', () => {
            hint.classList.add('d-none');
        });
    }
}

function setupFormScroll() {
    const form = document.getElementById('PessoaJuridicaForm');
    if (form) {
        form.addEventListener('invalid', function(e) {
            e.preventDefault();
            const invalidField = e.target;
            invalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
            invalidField.focus();
        }, true);
    }

    const formContainer = document.getElementById('formContainer');
    if (formContainer) {
        formContainer.addEventListener('wheel', function(e) {
            if (!formContainer.contains(e.target)) return;

            const isScrollingDown = e.deltaY > 0;
            const isAtTop = this.scrollTop === 0;
            const isAtBottom = this.scrollHeight - this.scrollTop === this.clientHeight;

            if ((isScrollingDown && isAtBottom) || (!isScrollingDown && isAtTop)) {
                e.preventDefault();
            }
        }, { passive: false });
    }
}

// ==============================================
// INICIALIZAÇÃO
// ==============================================

document.addEventListener('DOMContentLoaded', function() {
    // Inicializa utilitários
    FormUtils.initTooltips();
    FormUtils.setupRequiredFields();
    FormUtils.initFormValidation();
    
    // Configura máscaras
    MaskUtils.initMasks();

    // Configura eventos
    setupCNPJValidation();
    setupCEPSearch();
    setupLocationSelects();
    setupPasswordToggle();
    setupPasswordValidation();
    setupFormSubmit();
    setupUsernameHint();
    setupFormScroll();
});