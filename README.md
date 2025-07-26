# Batucada Gestão API

API RESTful desenvolvida em Django para o gerenciamento completo de uma escola de bateria, incluindo agendamento de aulas, controle de alunos, relatórios de desempenho e integrações.

---

## ✨ Funcionalidades Principais

* **Autenticação e Usuários:** Sistema completo de registro e login com tokens JWT.
* **Gerenciamento Central:** Endpoints CRUD para Alunos, Professores, Aulas e Modalidades.
* **Finalização de Aulas:** APIs para marcar presença e criar relatórios de aula detalhados com exercícios (rudimentos, ritmos, etc.).
* **Dashboards Inteligentes:** Endpoints de detalhes para Alunos, Professores e Modalidades com KPIs e dados agregados calculados.
* **Filtragem Avançada:** Sistema de filtros robusto para listagens de aulas por data, status, professor e mais.
* **Integrações:**
    * Endpoint para exportação de dados de aulas para arquivos Excel (.xlsx).
    * Geração de relatórios de desempenho de alunos com IA do Google Gemini.
* **Documentação Automática:** Documentação interativa da API com Swagger/OpenAPI.

---

## 🛠️ Tecnologias Utilizadas

* **Back-end:** Python, Django, Django REST Framework
* **Banco de Dados:** SQLite (desenvolvimento)
* **Testes:** Pytest, pytest-django
* **Autenticação:** djangorestframework-simplejwt
* **Documentação:** drf-spectacular
* **Outras Bibliotecas:** django-filter, drf-writable-nested, openpyxl, google-generativeai

---

## 🚀 Como Executar Localmente

Siga os passos abaixo para configurar e rodar o projeto no seu ambiente.

**1. Clone o repositório:**
```bash
git clone [https://github.com/MoisesAvilar/batucada-gestao-api.git](https://github.com/MoisesAvilar/batucada-gestao-api.git)
cd batucada-gestao-api
```

**2. Crie e ative um ambiente virtual:**
```bash
python -m venv venv
# No Windows
venv\Scripts\activate
# No Linux/Mac
source venv/bin/activate
```

**3. Instale as dependências:**
```bash
pip install -r requirements.txt
```

**4. Configure as variáveis de ambiente:**
* Crie uma cópia do arquivo `.env.example` (se existir) ou crie um novo arquivo `.env` na raiz do projeto.
* Preencha as variáveis necessárias:
    ```env
    SECRET_KEY='sua_chave_secreta_gerada_pelo_django'
    DEBUG=True
    GEMINI_API_KEY='sua_chave_da_api_do_gemini'
    ```

**5. Aplique as migrações do banco de dados:**
```bash
python manage.py migrate
```

**6. Crie um superusuário (opcional, para o Admin):**
```bash
python manage.py createsuperuser
```

**7. Inicie o servidor de desenvolvimento:**
```bash
python manage.py runserver_plus
```
O servidor estará rodando em `https://127.0.0.1:8000/`.

---

## 📚 Endpoints da API

A documentação completa e interativa da API está disponível em:

* **[https://127.0.0.1:8000/api/v1/docs/](https://127.0.0.1:8000/api/v1/docs/)**
