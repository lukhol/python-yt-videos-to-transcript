Simple application written to find transcript for all youtube videos from specified channel.

In order to run this application `.env` file has to be provided with following content:
```
AZURE_SUB=xxx
AZURE_REGION=xxx
GOOGLE_API_KEY=xxx
YT_CHANNEL_ID=xxx
```

YT api for videos is paginated but this tool does not support it (loads first 50 videos). It was not implemented because i found what i needed on the first page.

Speech to text is transformed using Azure Speech Services.
