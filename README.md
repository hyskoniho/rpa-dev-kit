# RPA Development Kit

Este projeto é um kit de desenvolvimento para Robotic Process Automation (RPA), criado com base em práticas de mercado e soluções para problemas comuns enfrentados no desenvolvimento de automações. O objetivo é fornecer uma base replicável e performática para criar automações robustas e eficientes.

### Principais Componentes

- **`src/HTTP/authenticated_session.py`**: Gerencia sessões HTTP autenticadas utilizando certificados digitais.
- **`src/IMG_Clicker/engine.py`**: Ferramenta para localização de elementos na tela utilizando OCR (PaddleOCR) e reconhecimento de imagens.
- **`src/Webdriver/simple_driver.py`**: Configuração simplificada de um WebDriver para automações baseadas em navegador.

---

## Configuração

### Pré-requisitos

Certifique-se de ter os seguintes itens instalados:

- Python 3.8 ou superior
- Gerenciador de pacotes `pip`
- Dependências do projeto (instaladas automaticamente via `requirements.txt`)

### Instalação

1. Clone o repositório:

    ```bash
    git clone https://github.com/seu-usuario/rpa-dev-kit.git
    cd rpa-dev-kit
    ```

2. Crie um ambiente virtual e ative-o:

    ```python
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows
    ```

3. Instale as dependências:

    ```python
    pip install -r requirements.txt
    ```

4. Configure o arquivo `.env` com o caminho e a senha do certificado digital:

    ```properties
    CERT_PATH="C:/caminho/para/seu/certificado.pfx"
    CERT_PASS="sua_senha"
    ```

---

## Como Usar

### 1. Sessões HTTP Autenticadas

Utilize a classe `AuthSession` para realizar requisições HTTP autenticadas com certificados digitais.

Exemplo:

```python
from src.HTTP.authenticated_session import AuthSession

session = AuthSession()
response = session.get('https://www.google.com')
print(response.status_code)
```

### 2. Localização de Elementos na Tela

Use a classe `Finder` ou a função `find_element` para localizar elementos na tela via OCR ou imagens.

Exemplo:

```python
from src.IMG_Clicker.engine import find_element

coordenadas = find_element(
    mode="img",
    elements=("assets/Captura de tela 2025-04-21 161456.png",),
    zone="q1"
)
if coordenadas:
    print(f"Elemento encontrado em: {coordenadas}")
```

### 3. Automação com WebDriver

Configure um WebDriver para automações baseadas em navegador com a função `build_driver`.

Exemplo:

```python
from src.Webdriver.simple_driver import build_driver

driver, wait = build_driver()
driver.get('https://www.google.com')
print(driver.title)
driver.quit()
```

