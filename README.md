# FIIS Scraper

Este repositório contém um web scraper projetado para buscar e processar dados relacionados a fundos de investimento imobiliário (FIIS) do site BM&F Bovespa.

## Configuração e Instalação

Para usar este projeto, você primeiro precisará clonar o repositório:

```sh
git clone https://github.com/BuggedCat/fiis-crawler.git
```

Navegue até o diretório:

```sh
cd fiis-crawler
```

## Dependências

Este projeto depende de várias ferramentas, incluindo:

- Python 3.8 ou superior
- Requests
- Docker e Docker Compose

## Uso

Para usar este projeto, você precisará executar o contêiner Docker.

Você pode usar o Docker Compose para construir e executar o contêiner:

```sh
docker-compose up --build
```

Isso iniciará o aplicativo e começará o processo de raspagem de dados. O aplicativo buscará dados para cada dia no intervalo de datas especificado. Os dados são então combinados e enviados para um bucket AWS S3.

## Configuração

Você pode especificar o intervalo de datas para o processo de busca de dados através dos argumentos de linha de comando `-s` (data de início) e `-e` (data final). As datas devem estar no formato "AAAA-MM-DD".

### Docker Compose
```yaml
# No docker-compose.yml
version: '3.8'

services:
  app:
    # Outras configurações
    command: ["python", "-m", "fiis_scraper.documentos", "-s", "2023-06-20", "-e", "2023-06-30"]
```

### Terminal
```sh
python -m fiis_scraper.documentos -s "2023-06-20" -e "2023-06-30"
```

## Contribuindo

TODO

## Contato

[<img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" />](https://www.linkedin.com/in/giancarlo-lester/)
[<img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" />](https://github.com/BuggedCat)

