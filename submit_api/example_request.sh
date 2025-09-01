gzip -c big_example_REPLACE.ndjson | curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/x-ndjson" \
  -H "Content-Encoding: gzip" \
  --data-binary @- \
  https://mc-a4.lab.uvalight.net/gd-cim-api/submit/ndjson

##### TEST ######

### A. Bring services up
# 1) Set env
export JWT_TOKEN='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnb25jYWxvLmZlcnJlaXJhQHN0dWRlbnQudXZhLm5sIiwiaXNzIjoiZ3JlZW5kaWdpdC1sb2dpbi11dmEiLCJpYXQiOjE3NTY3MzA2MDcsIm5iZiI6MTc1NjczMDYwNywiZXhwIjoxNzU2ODE3MDA3fQ.Mk9V1u_yt2AeXi-XVXd7VKQ-KRBQKRABgnihw3enGCU'
export MONGO_URI='mongodb://localhost:27017/'

# 2) Start Mongo (your docker-compose or local mongod)
docker compose up -d

# 3) Run API
uvicorn login_server:app --host 0.0.0.0 --port 8000

### B. Create a user and get a token
# touch allowed_emails.txt && echo 'you@example.org' >> allowed_emails.txt
curl -s -X POST -F 'username=goncalo.ferreira@student.uva.nl' -F 'password=goncalo' http://localhost:8000/gd-cim-api/login
# Copy the JWT shown in the HTML response (or use /token-ui)

### C. Small single JSON
TOKEN=$JWT_TOKEN
curl -s -X POST http://localhost:8000/gd-cim-api/submit \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"cpu":0.7,"mem":1536}'


### D. Test/submit/batch (array+idempotency)
curl -s -X POST http://localhost:8000/gd-cim-api/submit/batch \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: 11111111-1111-1111-1111-111111111111" \
  -H "X-Batch-Seq: 0" \
  -d '[{"metric":"cpu","value":0.1},{"metric":"mem","value":2}]'
# => {"ok":true,"inserted":2,"next_expected_seq":1}

# Retry same request to verify de-dup
curl -s -X POST http://localhost:8000/gd-cim-api/submit/batch \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: 11111111-1111-1111-1111-111111111111" \
  -H "X-Batch-Seq: 0" \
  -d '[{"metric":"cpu","value":0.1},{"metric":"mem","value":2}]'
# => {"ok":true,"inserted":0,"duplicate":true,"next_expected_seq":1}

### E. Test submit NDJSON (with and without gzip)
printf '%s\n' \
'{"metric":"cpu","v":0.11}' \
'{"metric":"cpu","v":0.12}' \
'{"metric":"mem","v":123}' > tiny.ndjson

# Plain
curl -s -X POST http://localhost:8000/gd-cim-api/submit/ndjson \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary @tiny.ndjson

# Gzipped
gzip -c tiny.ndjson | curl -s -X POST http://localhost:8000/gd-cim-api/submit/ndjson \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/x-ndjson" \
  -H "Content-Encoding: gzip" \
  --data-binary @-

### F. Test with chunks
python submit_api/json_to_ndjson_chunks.py input.json out_chunks --chunk-size 10000 --gzip

python submit_api/json_to_ndjson_chunks.py input.json out_chunks \
  --gzip --exec-curl \
  --endpoint http://localhost:8000/gd-cim-api/submit/ndjson \
  --bearer "$TOKEN"

