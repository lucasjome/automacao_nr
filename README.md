# Leitura automatizada de certificados NR

## Instruções de uso
### Requerimentos
- Conta ativa na AWS com permissão de uso do AWS Textract. Também é necessário que o [AWS CLI](https://aws.amazon.com/pt/cli/) esteja devidamente configurado com:
`aws configure`.

- Foi desenvolvido em ambiente Linux. É necessário que o pacote `poppler` esteja instalado para que a biblioteca [pdf2image](https://pdf2image.readthedocs.io/en/latest/installation.html) funcione. Ou usar o ambiente Conda apresentado neste repositório.
### Ambiente Conda
Replicar o ambiente conda:
`conda create --name automacao_env --file conda_pkgs.txt`

Ativar o ambiente recém criado:
`conda activate automacao_env`

### Execução
Passar o caminho do cerficado NR em PDF para o arquivo `main.py`

Exemplo:

`python main.py --input_pdf <endereço-do-certificado-em-pdf>`
