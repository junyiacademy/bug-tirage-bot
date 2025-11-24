如果遇到提供具體的帳號資訊，可透過 Datastore REST API 去資料庫查詢取得相關資訊來使用

## 查詢流程：
1. 決定查詢哪些 kind/table 會對於 debug 有幫助
1. 可以透過 /external_codebase 的 **_model.py 來知道特定 kind/table 正確的查詢方式 
2. 請直接使用 curl 來呼叫 Datastore REST API 查詢特定 kind (API文件：https://docs.cloud.google.com/datastore/docs/reference/data/rest?authuser=1)

## Datastore REST API - gcp access token

```
$(gcp access token)
```

## 查詢方式（以UserData為例）


curl -X POST "https://datastore.googleapis.com/v1/projects/ju
nyiacademy:runQuery" \
  -H "Authorization: Bearer $(Datastore REST API - gcp access token)" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "kind": [{"name": "UserData"}],
      "filter": {
        "propertyFilter": {
          "property": {"name": "user_email"},
          "op": "EQUAL",
          "value": {"stringValue": "email"}
        }
      }
    }
  }


可以用以下欄位查詢
- user_nickname : 暱稱
- user_email: email
- user_id: 支援可查詢的 ID 格式
  - Google ID: http://googleid.junyiacademy.org/[數字ID]
  - facebook ID: http://facebookid.junyiacademy.org/[數字ID]
  - 一般 ID: http://id.junyiacademy.org/[UUID]
  - 教育雲 ID: http://eduopenid.junyiacademy.org/unique/[UUID]
  - Campus ID: http://1campusid.junyiacademy.org/unique/[UUID]


