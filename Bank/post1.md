Below is a **complete, ready-to-import Postman collection JSON** for your Spring Boot banking app. It matches the architecture and endpoints in the detailed guide (Auth, Customer, Accounts, Transactions, Transfers, Admin) and includes **environment variables, pre-request scripts (JWT auto-storage), sample payloads, and test assertions**.

## How to use (quick steps)
1. Open **Postman** → **Import** → select/copy the JSON below.
2. Create a Postman **Environment** (e.g., `Bank Local`) with variables:
    - `baseUrl` = `http://localhost:8080`
    - `token` = *(leave empty; auto-filled by login)*
3. Run the requests in order:
    - **Auth → Register** → **Auth → Login** (token saved)
    - **Customer → Me**
    - **Accounts → Create Account**
    - **Transactions → Deposit / Withdraw**
    - **Transfers → Transfer**
    - **Transactions → History**
    - **Admin** (requires `ROLE_ADMIN`; seed admin user or set role manually)

> Tip: With H2 dev profile, you can also open `http://localhost:8080/h2-console` to verify DB state.

---

# Postman Collection JSON (copy/paste and import)

```json
{
  "info": {
    "name": "Spring Boot Bank API — Complete Collection",
    "description": "Full Postman collection for the Spring Boot Banking project (Auth, Customers, Accounts, Transactions, Transfers, Admin). Includes JWT auto-storage, sample payloads, and test assertions.",
    "version": "1.0.0",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Register Customer",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"name\": \"Alice Smith\",\n  \"email\": \"alice@example.com\",\n  \"password\": \"Password@123\",\n  \"phone\": \"9876543210\",\n  \"address\": \"123 Main St, City\"\n}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/auth/register",
              "host": ["{{baseUrl}}"],
              "path": ["api", "auth", "register"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "type": "thought"
              },
              {
                "listen": "test",
                "script": {
                  "exec": [
                    "pm.test(\"Status code is 200\", function () { pm.response.to.have.status(200); });",
                    "const json = pm.response.json();",
                    "pm.test(\"Success flag true\", function () { pm.expect(json.success).to.eql(true); });",
                    "pm.test(\"Customer returned with id and email\", function () {",
                    "  pm.expect(json.data).to.have.property('id');",
                    "  pm.expect(json.data.email).to.eql('alice@example.com');",
                    "});",
                    "console.log('Registered customer:', json.data);"
                  ],
                  "type": "text/javascript"
                }
              }
            ]
          ]
        },
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"alice@example.com\",\n  \"password\": \"Password@123\"\n}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/auth/login",
              "host": ["{{baseUrl}}"],
              "path": ["api", "auth", "login"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status code is 200\", function () { pm.response.to.have.status(200); });",
                  "const json = pm.response.json();",
                  "pm.test(\"JWT token returned\", function () {",
                  "  pm.expect(json.success).to.eql(true);",
                  "  pm.expect(json.data).to.have.property('token');",
                  "  pm.expect(json.data.token).to.be.a('string').and.not.empty;",
                  "});",
                  "if (json.data && json.data.token) {",
                  "  pm.environment.set(\"token\", json.data.token);",
                  "  console.log('JWT saved to environment variable token');",
                  "}"
                ],
                "type": "text/javascript"
              }
            }
          ]
        }
      ]
    },
    {
      "name": "Customer",
      "item": [
        {
          "name": "Get My Profile",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              }
            ],
            "url": {
              "raw": "{{baseUrl}}/api/customers/me",
              "host": ["{{baseUrl}}"],
              "path": ["api", "customers", "me"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status code is 200\", function () { pm.response.to.have.status(200); });",
                  "const json = pm.response.json();",
                  "pm.test(\"Customer profile returned\", function () {",
                  "  pm.expect(json.success).to.eql(true);",
                  "  pm.expect(json.data).to.have.property('email');",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ]
        },
        {
          "name": "Update My Profile (optional)",
          "request": {
            "method": "PUT",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              },
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"name\": \"Alice Smith (Updated)\",\n  \"phone\": \"9998887776\",\n  \"address\": \"456 New St, City\"\n}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/customers/me",
              "host": ["{{baseUrl}}"],
              "path": ["api", "customers", "me"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status code is 200\", function () { pm.response.to.have.status(200); });",
                  "const json = pm.response.json();",
                  "pm.test(\"Profile updated\", function () { pm.expect(json.success).to.eql(true); });"
                ],
                "type": "text/javascript"
              }
            }
          ]
        }
      ]
    },
    {
      "name": "Accounts",
      "item": [
        {
          "name": "Create Savings Account (with initial deposit)",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              },
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"accountType\": \"SAVINGS\",\n  \"initialDeposit\": 1000.00\n}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/accounts",
              "host": ["{{baseUrl}}"],
              "path": ["api", "accounts"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status code is 200\", function () { pm.response.to.have.status(200); });",
                  "const json = pm.response.json();",
                  "pm.test(\"Account created\", function () {",
                  "  pm.expect(json.success).to.eql(true);",
                  "  pm.expect(json.data).to.have.property('accountNumber');",
                  "  pm.expect(json.data.balance).to.eql(1000.00);",
                  "});",
                  "if (json.data && json.data.accountNumber) {",
                  "  pm.environment.set(\"savingsAccountNumber\", json.data.accountNumber);",
                  "  console.log('Savings accountNumber saved:', json.data.accountNumber);",
                  "}"
                ],
                "type": "text/javascript"
              }
            }
          ]
        },
        {
          "name": "Create Current Account (zero balance)",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              },
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"accountType\": \"CURRENT\",\n  \"initialDeposit\": 0.00\n}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/accounts",
              "host": ["{{baseUrl}}"],
              "path": ["api", "accounts"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status code is 200\", function () { pm.response.to.have.status(200); });",
                  "const json = pm.response.json();",
                  "pm.test(\"Current account created\", function () {",
                  "  pm.expect(json.success).to.eql(true);",
                  "  pm.expect(json.data).to.have.property('accountNumber');",
                  "  pm.expect(json.data.balance).to.eql(0.00);",
                  "});",
                  "if (json.data && json.data.accountNumber) {",
                  "  pm.environment.set(\"currentAccountNumber\", json.data.accountNumber);",
                  "  console.log('Current accountNumber saved:', json.data.accountNumber);",
                  "}"
                ],
                "type": "text/javascript"
              }
            }
          ]
        },
        {
          "name": "Get My Accounts",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              }
            ],
            "url": {
              "raw": "{{baseUrl}}/api/customers/me/accounts",
              "host": ["{{baseUrl}}"],
              "path": ["api", "customers", "me", "accounts"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status code is 200\", function () { pm.response.to.have.status(200); });",
                  "const json = pm.response.json();",
                  "pm.test(\"Accounts list returned\", function () {",
                  "  pm.expect(json.success).to.eql(true);",
                  "  pm.expect(json.data).to.be.an('array');",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ]
        },
        {
          "name": "Get Account by ID (replace {id})",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              }
            ],
            "url": {
              "raw": "{{baseUrl}}/api/accounts/1",
              "host": ["{{baseUrl}}"],
              "path": ["api", "accounts", "1"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status code is 200\", function () { pm.response.to.have.status(200); });",
                  "const json = pm.response.json();",
                  "pm.test(\"Account details returned\", function () { pm.expect(json.success).to.eql(true); });"
                ],
                "type": "text/javascript"
              }
            }
          ]
        }
      ]
    },
    {
      "name": "Transactions",
      "item": [
        {
          "name": "Deposit to Savings Account",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              },
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"amount\": 500.00,\n  \"description\": \"Cash deposit\"\n}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/accounts/{{savingsAccountNumber}}/deposit",
              "host": ["{{baseUrl}}"],
              "path": ["api", "accounts", "{{savingsAccountNumber}}", "deposit"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status code is 200\", function () { pm.response.to.have.status(200); });",
                  "const json = pm.response.json();",
                  "pm.test(\"Deposit successful\", function () {",
                  "  pm.expect(json.success).to.eql(true);",
                  "  pm.expect(json.data.balance).to.be.above(1000);",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ]
        },
        {
          "name": "Withdraw from Savings Account",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              },
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"amount\": 200.00,\n  \"description\": \"ATM withdrawal\"\n}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/accounts/{{savingsAccountNumber}}/withdraw",
              "host": ["{{baseUrl}}"],
              "path": ["api", "accounts", "{{savingsAccountNumber}}", "withdraw"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status code is 200\", function () { pm.response.to.have.status(200); });",
                  "const json = pm.response.json();",
                  "pm.test(\"Withdraw successful\", function () { pm.expect(json.success).to.eql(true); });"
                ],
                "type": "text/javascript"
              }
            }
          ]
        },
        {
          "name": "Transaction History (Savings)",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              }
            ],
            "url": {
              "raw": "{{baseUrl}}/api/transactions/account/{{savingsAccountNumber}}?page=0&size=10",
              "host": ["{{baseUrl}}"],
              "path": ["api", "transactions", "account", "{{savingsAccountNumber}}"],
              "query": [
                {
                  "key": "page",
                  "value": "0"
                },
                {
                  "key": "size",
                  "value": "10"
                }
              ]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status code is 200\", function () { pm.response.to.have.status(200); });",
                  "const json = pm.response.json();",
                  "pm.test(\"Transaction list returned\", function () {",
                  "  pm.expect(json.success).to.eql(true);",
                  "  pm.expect(json.data).to.have.property('content');",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ]
        },
        {
          "name": "Transaction History (Current)",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              }
            ],
            "url": {
              "raw": "{{baseUrl}}/api/transactions/account/{{currentAccountNumber}}?page=0&size=10",
              "host": ["{{baseUrl}}"],
              "path": ["api", "transactions", "account", "{{currentAccountNumber}}"],
              "query": [
                {
                  "key": "page",
                  "value": "0"
                },
                {
                  "key": "size",
                  "value": "10"
                }
              ]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status code is 200\", function () { pm.response.to.have.status(200); });",
                  "const json = pm.response.json();",
                  "pm.test(\"Transaction list returned\", function () { pm.expect(json.success).to.eql(true); });"
                ],
                "type": "text/javascript"
              }
            }
          ]
        }
      ]
    },
    {
      "name": "Transfers",
      "item": [
        {
          "name": "Transfer between accounts",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              },
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"sourceAccountNumber\": \"{{savingsAccountNumber}}\",\n  \"destinationAccountNumber\": \"{{currentAccountNumber}}\",\n  \"amount\": 300.00,\n  \"description\": \"Transfer to current account\"\n}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/transfers",
              "host": ["{{baseUrl}}"],
              "path": ["api", "transfers"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status code is 200\", function () { pm.response.to.have.status(200); });",
                  "const json = pm.response.json();",
                  "pm.test(\"Transfer successful\", function () {",
                  "  pm.expect(json.success).to.eql(true);",
                  "  pm.expect(json.data).to.have.property('reference');",
                  "  pm.expect(json.data.sourceAccount).to.eql(pm.environment.get('savingsAccountNumber'));",
                  "  pm.expect(json.data.destinationAccount).to.eql(pm.environment.get('currentAccountNumber'));",
                  "  pm.expect(json.data.amount).to.eql(300.00);",
                  "});",
                  "console.log('Transfer reference:', json.data.reference);"
                ],
                "type": "text/javascript"
              }
            }
          ]
        },
        {
          "name": "Transfer — Insufficient balance (should fail 400)",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              },
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"sourceAccountNumber\": \"{{savingsAccountNumber}}\",\n  \"destinationAccountNumber\": \"{{currentAccountNumber}}\",\n  \"amount\": 999999.00,\n  \"description\": \"Should fail\"\n}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/transfers",
              "host": ["{{baseUrl}}"],
              "path": ["api", "transfers"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status code is 400\", function () { pm.response.to.have.status(400); });",
                  "const json = pm.response.json();",
                  "pm.test(\"Error response returned\", function () {",
                  "  pm.expect(json.success).to.eql(false);",
                  "  pm.expect(json.message).to.be.a('string');",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ]
        }
      ]
    },
    {
      "name": "Admin",
      "item": [
        {
          "name": "List All Customers (ADMIN)",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              }
            ],
            "url": {
              "raw": "{{baseUrl}}/api/admin/customers",
              "host": ["{{baseUrl}}"],
              "path": ["api", "admin", "customers"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "// Expect 200 if admin, else 403",
                  "pm.test(\"Admin endpoint accessible or forbidden\", function () {",
                  "  pm.expect(pm.response.code).to.be.oneOf([200, 403]);",
                  "});",
                  "if (pm.response.code === 200) {",
                  "  const json = pm.response.json();",
                  "  pm.test(\"Customers list returned\", function () { pm.expect(json.success).to.eql(true); });",
                  "}"
                ],
                "type": "text/javascript"
              }
            }
          ]
        },
        {
          "name": "List All Accounts (ADMIN)",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              }
            ],
            "url": {
              "raw": "{{baseUrl}}/api/admin/accounts",
              "host": ["{{baseUrl}}"],
              "path": ["api", "admin", "accounts"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Admin endpoint accessible or forbidden\", function () {",
                  "  pm.expect(pm.response.code).to.be.oneOf([200, 403]);",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ]
        },
        {
          "name": "Freeze Account (ADMIN, replace {id})",
          "request": {
            "method": "PUT",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              }
            ],
            "url": {
              "raw": "{{baseUrl}}/api/admin/accounts/1/freeze",
              "host": ["{{baseUrl}}"],
              "path": ["api", "admin", "accounts", "1", "freeze"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Admin endpoint accessible or forbidden\", function () {",
                  "  pm.expect(pm.response.code).to.be.oneOf([200, 403]);",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ]
        },
        {
          "name": "Unfreeze Account (ADMIN, replace {id})",
          "request": {
            "method": "PUT",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              }
            ],
            "url": {
              "raw": "{{baseUrl}}/api/admin/accounts/1/unfreeze",
              "host": ["{{baseUrl}}"],
              "path": ["api", "admin", "accounts", "1", "unfreeze"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Admin endpoint accessible or forbidden\", function () {",
                  "  pm.expect(pm.response.code).to.be.oneOf([200, 403]);",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ]
        },
        {
          "name": "Audit Logs (ADMIN)",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              }
            ],
            "url": {
              "raw": "{{baseUrl}}/api/admin/audit-logs",
              "host": ["{{baseUrl}}"],
              "path": ["api", "admin", "audit-logs"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Admin endpoint accessible or forbidden\", function () {",
                  "  pm.expect(pm.response.code).to.be.oneOf([200, 403]);",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ]
        }
      ]
    },
    {
      "name": "Utilities",
      "item": [
        {
          "name": "Health Check (if Actuator enabled)",
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{baseUrl}}/actuator/health",
              "host": ["{{baseUrl}}"],
              "path": ["actuator", "health"]
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status code is 200 or 404 (if actuator not enabled)\", function () {",
                  "  pm.expect(pm.response.code).to.be.oneOf([200, 404]);",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ]
        }
      ]
    }
  ],
  "event": [
    {
      "listen": "prerequest",
      "script": {
        "exec": [
          "// Auto-set Authorization header for requests that need it",
          "const token = pm.environment.get(\"token\");",
          "if (token) {",
          "  pm.request.headers.add({ key: \"Authorization\", value: \"Bearer \" + token });",
          "}"
        ],
        "type": "text/javascript"
      }
    }
  ],
  "variable": [
    {
      "key": "baseUrl",
      "value": "http://localhost:8080"
    },
    {
      "key": "token",
      "value": ""
    },
    {
      "key": "savingsAccountNumber",
      "value": ""
    },
    {
      "key": "currentAccountNumber",
      "value": ""
    }
  ]
}
```

## Postman Environment (recommended)
Create an environment named **Bank Local** with:
- `baseUrl` = `http://localhost:8080`
- `token` = *(empty)*
- `savingsAccountNumber` = *(empty)*
- `currentAccountNumber` = *(empty)*

## Recommended execution order (so variables work)
1. **Auth → Register**
2. **Auth → Login** *(token auto-saved)*
3. **Customer → Get My Profile**
4. **Accounts → Create Savings Account** *(savingsAccountNumber saved)*
5. **Accounts → Create Current Account** *(currentAccountNumber saved)*
6. **Transactions → Deposit to Savings**
7. **Transactions → Withdraw from Savings**
8. **Transfers → Transfer between accounts**
9. **Transactions → Transaction History (Savings / Current)**
10. **Admin** *(only if you have an admin user with ROLE_ADMIN)*

## Notes / small adjustments (if your API differs)
- If your endpoints use **account IDs** instead of **account numbers**, replace `{{savingsAccountNumber}}` with `{{savingsAccountId}}` and save the ID instead.
- If pagination returns a different structure (e.g., `data.items`), adjust the test assertions accordingly.
- If you use Swagger/OpenAPI, you can also import directly from `http://localhost:8080/swagger-ui.html` or `http://localhost:8080/v3/api-docs`.

If you want, I can also generate **a second Postman collection focused only on edge cases** (race conditions, invalid auth, same-account transfer, inactive account, validation errors) with stronger assertions.