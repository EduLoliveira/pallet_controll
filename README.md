# 📦 Pallet Controller - Sistema de Gerenciamento de Vales de Pallet

## 📋 Sobre o Projeto  
O **Pallet Controller** é um sistema completo para controle e gerenciamento de vales de pallet, desenvolvido em **Django** com **PostgreSQL (Supabase)**.  
A aplicação permite emissão, validação e acompanhamento de vales com **QR Codes**, além de controle de permissões de acesso por tipo de usuário.  

---

## 🎯 Funcionalidades Principais  

- ✅ Cadastro e autenticação de usuários  
- ✅ CRUD completo de vales de pallet  
- ✅ Geração e validação de QR Codes  
- ✅ Controle de permissões por tipo de usuário  
- ✅ Dashboard administrativo  
- ✅ Interface responsiva  
- ✅ Integração com Supabase (PostgreSQL)  
- ✅ Validação de documentos brasileiros (CPF/CNPJ)  

---

## 👥 Fluxo de Uso e Permissões  

### Cadastro e Login  
- **0.3** – Usuário realiza cadastro na área *"Cadastre-se"*  
- **0.5** – Após cadastro, é redirecionado para a tela de Login  
- **0.6** – Usuários comuns acessam área restrita com permissões limitadas (CRUD parcial)  

### Sessão e Atribuição de Registros  
- **1.0** – Sessão permanece ativa até logout manual  
- **1.1** – Registros criados/atualizados armazenam automaticamente o campo `criado_por` com ID do usuário  

### Permissões de Administradores (Staff)  
- **1.3** – Usuários staff possuem permissões totais:  
  - **1.3.5** – Exclusão de vales  
  - **1.3.7** – Alteração de estados/status  
  - **1.3.9** – Emissão e consulta de todos os registros  
- **1.4** – Atualização do status do QR Code é exclusiva para administradores (`is_staff=True`)  

### Validade dos Vales  
- **1.7** – Todos os vales emitidos têm validade até o final do dia definido na emissão  

### Objetivo da Aplicação  
- **2.0** – Gerenciamento centralizado da emissão e controle de vales de pallets para fornecedores e administradores  

---

## 🚀 Tecnologias Utilizadas  

- **Django 4.0**  
- **Python 3.8+**  
- **PostgreSQL (Supabase)**  
- **Bootstrap 5**  
- **JavaScript**  
- **QR Code Generation**  
- **Validate-docbr** (validação de documentos brasileiros)  
- **Whitenoise** (arquivos estáticos em produção)  

---

## ⚙️ Configuração do Ambiente  

### 1. Clonar o Repositório  
```bash
git clone https://github.com/EduLoliveira/pallet_controll.git
cd pallet_controll
cd pallet
```

### 2. Criar e Ativar Ambiente Virtual (venv)  
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar no Linux/Mac
source venv/bin/activate

# Ativar no Windows
venv\Scripts\activate
```

### 3. Instalar Dependências  
```bash
pip install -r requirements.txt
python.exe -m pip install --upgrade pip
```

### 4. Configurar Variáveis de Ambiente  
Copiar o arquivo **.env.example** para **.env**:  
```bash
Linux
cp env.example .env

Windows
copy env.exemple .env
```

### 5. Executar Migrações  
```bash
python manage.py migrate
```

### 6. Criar Superusuário  
```bash
python manage.py createsuperuser
```

### 7. Rodar o Servidor  
```bash
python manage.py runserver
```

---

## ✅ Acesso ao Sistema  

- **URL padrão:** http://localhost:8000  
- **Área Administrativa:** `/admin`  

---

## 📌 Observações  

- Sempre ativar o ambiente virtual antes de rodar o projeto.  
- Para desativar o ambiente virtual:  
  ```bash
  deactivate
  ```  
- Em produção, configurar variáveis de ambiente no servidor (não versionar `.env`).  
