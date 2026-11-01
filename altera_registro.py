import winreg as reg
import subprocess
import json
import os

def seleciona_certificado(empresa=None):
    # CN (Common Name) do certificado digital a ser selecionado automaticamente,
    # ex.: "NOME DO TITULAR:00000000000". Vem do parâmetro ou da variável CERTIFICADO_CN.
    empresa = empresa or os.environ.get("CERTIFICADO_CN", "")
    if not empresa:
        print("Defina a variável de ambiente CERTIFICADO_CN com o CN do certificado digital.")
        return
    try:
        # Fecha o Chrome (se necessário)
        subprocess.call(["taskkill", "/F", "/IM", "chrome.exe"], stderr=subprocess.DEVNULL)

        # Caminho da chave no Registro
        key_path = r"SOFTWARE\Policies\Google\Chrome\AutoSelectCertificateForUrls"
        
        # JSON com padrões de URLs e filtros de certificado
        json_value = {
            "pattern": os.environ.get("CERTIFICADO_URL_PATTERN", "https://api.ihub.com.br/certificado/login*"),
            "filter": {
                "SUBJECT": {
                    "CN": empresa
                }
            }
        }

        # Converte o dicionário em JSON válido
        json_string = json.dumps(json_value, indent=4)

        # Cria ou abre a chave no Registro
        key = reg.CreateKey(reg.HKEY_LOCAL_MACHINE, key_path)
        try:
            # Define o valor no Registro com identificador "1"
            reg.SetValueEx(key, "1", 0, reg.REG_SZ, json_string)
            print(f"Certificado para {empresa} configurado com sucesso!")
        finally:
            # Fecha a chave do Registro
            reg.CloseKey(key)

    except PermissionError:
        print("Erro: Permissões administrativas são necessárias para modificar o Registro.")
    except Exception as e:
        print(f"Erro ao configurar o certificado: {e}")

# Chamada da função (apenas quando executado diretamente)
if __name__ == "__main__":
    seleciona_certificado()
