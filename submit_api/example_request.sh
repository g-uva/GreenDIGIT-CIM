gzip -c big_example_REPLACE.ndjson | curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/x-ndjson" \
  -H "Content-Encoding: gzip" \
  --data-binary @- \
  https://mc-a4.lab.uvalight.net/gd-cim-api/submit/ndjson