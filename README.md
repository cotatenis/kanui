
░█████╗░░█████╗░████████╗░█████╗░████████╗███████╗███╗░░██╗██╗░██████╗
██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗╚══██╔══╝██╔════╝████╗░██║██║██╔════╝
██║░░╚═╝██║░░██║░░░██║░░░███████║░░░██║░░░█████╗░░██╔██╗██║██║╚█████╗░
██║░░██╗██║░░██║░░░██║░░░██╔══██║░░░██║░░░██╔══╝░░██║╚████║██║░╚═══██╗
╚█████╔╝╚█████╔╝░░░██║░░░██║░░██║░░░██║░░░███████╗██║░╚███║██║██████╔╝
░╚════╝░░╚════╝░░░░╚═╝░░░╚═╝░░╚═╝░░░╚═╝░░░╚══════╝╚═╝░░╚══╝╚═╝╚═════╝░


--------------------------------------------------------------------------

# Web crawler

url: [https://www.kanui.com.br/](https://www.kanui.com.br/)

# 1. Configuration
Before you run this project and for the proper running of this program you need to set up some variables inside `kanui/kanui/settings.py`.

## 1.1 GOOGLE CLOUD PLATFORM

- `GCS_PROJECT_ID` 
- `GCP_CREDENTIALS`
- `GCP_STORAGE`
- `GCP_STORAGE_CRAWLER_STATS`

## 1.2 DISCORD
- `DISCORD_WEBHOOK_URL`
- `DISCORD_THUMBNAIL_URL`


# 2. Implemented Brands
- adidas [KanuiAdidasSpider]

# 3. Build

```shell
cd kanui
make docker-build-production
```

# 4. Publish

```shell
make docker-publish-production
```

# 5. Use

```shell
docker run gcr.io/cotatenis/cotatenis-crawl-kanui:0.1.1 --brand=adidas 
```
