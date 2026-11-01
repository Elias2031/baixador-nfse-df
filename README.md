# Baixador de NFS-e (ISSNet DF)

> Este sistema está sendo substituído por agentes de IA; o código foi aberto como portfólio e referência.

Automação em Python que acessa o portal do ISS do Distrito Federal (ISSNet) com certificado digital e baixa, para várias empresas e períodos, os arquivos XML das **NFS-e prestadas** e das **notas tomadas** (NFS-e e NFS-e Nacional).

## Problema de negócio

Todo mês, escritórios de contabilidade precisam reunir as notas de serviço emitidas e recebidas de cada cliente para a escrituração e a apuração do ISS. No portal, isso é feito empresa por empresa e mês a mês: localizar o contribuinte, pedir o lote de XMLs, esperar ficar disponível, baixar e ainda consultar as notas tomadas. Com dezenas de clientes, o trabalho manual toma horas. Este script percorre uma planilha de empresas e faz esse roteiro sozinho, organizando os arquivos em pastas.

## Funcionalidades

- Leitura de uma planilha Excel com as empresas e os períodos a baixar.
- Validação do CNPJ (dígitos verificadores) antes de acessar o portal.
- Configuração da seleção automática do certificado digital no Chrome (política `AutoSelectCertificateForUrls` no Registro do Windows).
- Login no ISSNet DF com certificado e seleção do contribuinte pelo CNPJ.
- **Prestador:** solicitação de NFS-e em lote, acompanhamento da solicitação e download do .zip.
- **Tomador:** consulta de notas tomadas (NFS-e e NFS-e Nacional) e download de todos os XMLs.
- Divisão automática do período em meses.
- Organização dos arquivos em `ARQUIVOS BAIXADOS/<número da empresa>/<ano>/<mês.ano>/`.
- Arquivo de aviso quando não há notas no período e relatório `relatorio_de_importacao.txt` com as ocorrências (CNPJ inválido, empresa sem notas etc.).
- Novas tentativas automáticas quando a página ou um elemento falha ao carregar.

## Stack

- Python 3.12+
- [DrissionPage](https://github.com/g1879/DrissionPage) (automação do navegador Chromium)
- pandas e openpyxl (leitura da planilha)
- python-dateutil
- `winreg` (Windows) para configurar o certificado no Chrome

## Requisitos

- Windows com Google Chrome instalado.
- Certificado digital (e-CPF/e-CNPJ) instalado no Windows, com acesso ou procuração para as empresas.
- Permissão de administrador para gravar a política do Chrome no Registro (`HKLM`).

O portal é acessado **somente por certificado digital**; o script não usa nem armazena login e senha.

## Como executar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

1. Defina as variáveis de ambiente (veja `.env.example`):
   ```bat
   set CERTIFICADO_CN=NOME DO TITULAR:00000000000
   set CERTIFICADO_URL_PATTERN=https://api.ihub.com.br/certificado/login*
   ```
2. Preencha `planilha_modelo.xlsx` (deve ser o único `.xlsx` na pasta) com as colunas:

   | RAZAO SOCIAL | NUMERO EMPRESA | CNPJ | DATA INICIAL | DATA FINAL | NOME DO CERTIFICADO |
   |---|---|---|---|---|---|
   | EMPRESA EXEMPLO LTDA | 123 | 00.000.000/0000-00 | 01/01/2025 | 31/01/2025 | (opcional) |

3. Execute, em um terminal aberto como administrador:
   ```bash
   python index.py
   ```

`altera_registro.py` também pode ser executado sozinho para apenas configurar a seleção automática do certificado.

## Estrutura de saída

```
ARQUIVOS BAIXADOS/
└── 000123/
    └── 2025/
        └── 01.2025/
            ├── PRESTADOR NFSE -<CNPJ>-01.01.2025-31.01.2025.zip
            ├── TOMADOR NFSE-<CNPJ>-01.01.2025-31.01.2025.zip
            └── NÃO FORAM ENCONTRADAS NOTAS DO TIPO TOMADOR NFSE - NACIONAL.txt
```

## Arquivos

- `index.py`: fluxo principal (planilha → portal → downloads).
- `altera_registro.py`: grava no Registro a política de seleção automática do certificado no Chrome.
- `teste.py`: versão anterior/experimental do fluxo principal, mantida como referência.
- `planilha_modelo.xlsx`: modelo vazio da planilha de entrada.

## Limitações conhecidas

- A automação depende dos seletores (XPath) das telas do ISSNet DF; mudanças no portal exigem ajustes.
- O código mantém trechos de depuração com datas fixas (ex.: `01/12/2024` em `extrair_mes_ano` e na consulta de notas tomadas), que precisam ser removidos para baixar outros períodos.

## Licença

MIT. Veja [LICENSE](LICENSE).
