# Download/Upload Containers

## Building Download Container
Within the respective directory ([`./downloader`](runner/downloader)), enter the following within the shell:
```
docker build -t <image name> -f downloader.dockerfile .
```

## Building Upload Container
Within the respective directory ([`./uploader`](runner/uploader)), enter the following within the shell:
```
docker build -t <image name> -f uploader.dockerfile .
```