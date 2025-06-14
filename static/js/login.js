document.addEventListener('DOMContentLoaded', function () {
    // Máscaras e validações
    const cnpjInput = document.getElementById('id_cnpj');
    if (cnpjInput) {
        cnpjInput.addEventListener('input', function (e) {
            let value = e.target.value.replace(/\D/g, '');
            let formattedValue = '';
            if (value.length > 0) formattedValue = value.substring(0, 2);
            if (value.length > 2) formattedValue += '.' + value.substring(2, 5);
            if (value.length > 5) formattedValue += '.' + value.substring(5, 8);
            if (value.length > 8) formattedValue += '/' + value.substring(8, 12);
            if (value.length > 12) formattedValue += '-' + value.substring(12, 14);
            e.target.value = formattedValue;
        });
    }

    const cepInput = document.getElementById('id_cep');
    if (cepInput) {
        cepInput.addEventListener('input', function (e) {
            let value = e.target.value.replace(/\D/g, '');
            e.target.value = value.replace(/^(\d{5})(\d{0,3}).*/, '$1-$2').replace(/-$/, '');
        });
    }

    const telefoneInputs = document.querySelectorAll('input[name="telefone"]');
    telefoneInputs.forEach(input => {
        input.addEventListener('input', function (e) {
            let value = e.target.value.replace(/\D/g, '');
            let formattedValue = '';
            if (value.length > 0) formattedValue = '(' + value.substring(0, 2);
            if (value.length > 2) formattedValue += ') ' + value.substring(2, value.length <= 10 ? 6 : 7);
            if (value.length > (value.length <= 10 ? 6 : 7)) {
                formattedValue += '-' + value.substring(value.length <= 10 ? 6 : 7, value.length <= 10 ? 10 : 11);
            }
            e.target.value = formattedValue;
        });
    });

    // Validação do formulário
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Botão de validar CNPJ
    const validarCnpjBtn = document.getElementById('validar-cnpj');
    if (validarCnpjBtn) {
        validarCnpjBtn.addEventListener('click', function () {
            const cnpj = document.getElementById('id_cnpj').value.replace(/\D/g, '');
            if (cnpj.length === 14) {
                validarCNPJ(cnpj);
            } else {
                const feedbackDiv = document.getElementById('cnpjFeedback');
                feedbackDiv.textContent = 'CNPJ deve ter 14 dígitos';
                feedbackDiv.className = 'invalid-feedback d-block';
                document.getElementById('id_cnpj').classList.add('is-invalid');
            }
        });
    }

    // Botão de buscar CEP
    const buscarCepBtn = document.getElementById('buscar-cep');
    if (buscarCepBtn) {
        buscarCepBtn.addEventListener('click', function () {
            const cep = document.getElementById('id_cep').value.replace(/\D/g, '');
            if (cep.length === 8) {
                buscarCEP(cep);
            }
        });
    }

    // Carregar cidades quando estado for selecionado
    const estadoSelect = document.getElementById('id_estado');
    if (estadoSelect) {
        estadoSelect.addEventListener('change', function () {
            if (this.value) {
                listarMunicipiosPorUF(this.value);
            } else {
                const cidadeSelect = document.getElementById('id_cidade');
                cidadeSelect.innerHTML = '<option value="">Selecione o estado primeiro</option>';
                cidadeSelect.disabled = true;
            }
        });
    }
});

async function validarCNPJ(cnpj) {
    const feedbackDiv = document.getElementById('cnpjFeedback');
    feedbackDiv.textContent = 'Validando CNPJ...';
    feedbackDiv.className = 'form-text text-muted d-block';

    try {
        const response = await fetch(`{% url 'validar_cnpj_api' %}?cnpj=${cnpj}`);
        const data = await response.json();

        if (response.ok && data.valido) {
            feedbackDiv.textContent = 'CNPJ válido';
            feedbackDiv.className = 'valid-feedback d-block';
            document.getElementById('id_cnpj').classList.add('is-valid');

            // Preencher campos automaticamente
            if (data.razao_social) {
                document.getElementById('id_razao_social').value = data.razao_social;
            }
            if (data.nome_fantasia) {
                document.getElementById('id_nome_fantasia').value = data.nome_fantasia;
            }
            if (data.email) {
                document.getElementById('id_email_empresa').value = data.email;
            }
            if (data.cep) {
                document.getElementById('id_cep').value = data.cep.replace(/^(\d{5})(\d{3})$/, '$1-$2');
            }
            if (data.situacao_cadastral) {
                document.getElementById('id_situacao_cadastral').value = data.situacao_cadastral;
            }

            // Preencher endereço se disponível
            if (data.logradouro || data.bairro || data.cidade || data.estado) {
                preencherEnderecoCompleto(data);
            }
        } else {
            feedbackDiv.textContent = data.erro || 'CNPJ inválido ou não encontrado';
            feedbackDiv.className = 'invalid-feedback d-block';
            document.getElementById('id_cnpj').classList.add('is-invalid');
        }
    } catch (error) {
        console.error('Erro ao validar CNPJ:', error);
        feedbackDiv.textContent = 'Erro ao conectar com o serviço de validação';
        feedbackDiv.className = 'invalid-feedback d-block';
        document.getElementById('id_cnpj').classList.add('is-invalid');
    }
}

async function buscarCEP(cep) {
    const feedbackDiv = document.getElementById('cepFeedback');
    feedbackDiv.textContent = 'Buscando CEP...';
    feedbackDiv.className = 'form-text text-muted d-block';

    try {
        const response = await fetch(`{% url 'consultar_cep_api' %}?cep=${cep}`);
        const data = await response.json();

        if (response.ok && !data.erro) {
            feedbackDiv.textContent = 'CEP encontrado';
            feedbackDiv.className = 'valid-feedback d-block';
            document.getElementById('id_cep').classList.add('is-valid');

            preencherEnderecoCompleto(data);
            document.getElementById('id_numero').focus();
        } else {
            feedbackDiv.textContent = data.erro || 'CEP não encontrado';
            feedbackDiv.className = 'invalid-feedback d-block';
            document.getElementById('id_cep').classList.add('is-invalid');
        }
    } catch (error) {
        console.error('Erro ao buscar CEP:', error);
        feedbackDiv.textContent = 'Erro ao conectar com o serviço de CEP';
        feedbackDiv.className = 'invalid-feedback d-block';
        document.getElementById('id_cep').classList.add('is-invalid');
    }
}

function preencherEnderecoCompleto(data) {
    if (data.logradouro) {
        document.getElementById('id_logradouro').value = data.logradouro;
    }
    if (data.bairro) {
        document.getElementById('id_bairro').value = data.bairro;
    }
    if (data.complemento) {
        document.getElementById('id_complemento').value = data.complemento;
    }
    if (data.estado) {
        document.getElementById('id_estado').value = data.estado;
        // Disparar evento de change para carregar cidades
        const event = new Event('change');
        document.getElementById('id_estado').dispatchEvent(event);

        // Esperar carregar as cidades e selecionar a correta
        setTimeout(() => {
            if (data.cidade) {
                const cidadeSelect = document.getElementById('id_cidade');
                for (let i = 0; i < cidadeSelect.options.length; i++) {
                    if (cidadeSelect.options[i].text.trim().toUpperCase() === data.cidade.trim().toUpperCase()) {
                        cidadeSelect.value = cidadeSelect.options[i].value;
                        break;
                    }
                }
            }
        }, 500);
    }
}

async function listarMunicipiosPorUF(uf) {
    const cidadeSelect = document.getElementById('id_cidade');
    cidadeSelect.disabled = true;
    cidadeSelect.innerHTML = '<option value="">Carregando cidades...</option>';

    try {
        const response = await fetch(`{% url 'listar_municipios_api' 'XX' %}`.replace('XX', uf));
        const data = await response.json();

        if (response.ok && data.municipios) {
            cidadeSelect.innerHTML = '<option value="">Selecione...</option>';
            data.municipios.forEach(municipio => {
                const option = document.createElement('option');
                option.value = municipio.nome;
                option.textContent = municipio.nome;
                cidadeSelect.appendChild(option);
            });
            cidadeSelect.disabled = false;
        } else {
            cidadeSelect.innerHTML = '<option value="">Erro ao carregar cidades</option>';
            cidadeSelect.disabled = false;
        }
    } catch (error) {
        console.error('Erro ao carregar municípios:', error);
        cidadeSelect.innerHTML = '<option value="">Erro na requisição</option>';
        cidadeSelect.disabled = false;
    }
}
