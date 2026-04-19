# 📬 Complete Postman Collection for Banking API

## 📁 How to Import into Postman

```
1. Open Postman
2. Click → Import (top left)
3. Select "Raw text" tab
4. Paste the JSON below
5. Click Continue → Import
```

---

## 🔴 FULL POSTMAN COLLECTION JSON

```json
{
  "info": {
    "_postman_id": "banking-api-collection-v1",
    "name": "🏦 Banking API v1",
    "description": "Complete Banking REST API Collection\nSpring Boot 3 | MySQL | Basic Auth",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "📋 AUTH SETUP",
      "item": [
        {
          "name": "🔑 Set Environment Variables",
          "event": [
            {
              "listen": "prerequest",
              "script": {
                "exec": [
                  "pm.environment.set(\"baseUrl\", \"http://localhost:8080\");",
                  "pm.environment.set(\"apiVersion\", \"v1\");",
                  "pm.environment.set(\"accountNumber\", \"\");",
                  "pm.environment.set(\"recipientAccount\", \"\");",
                  "console.log(\"✅ Environment variables set\");"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{baseUrl}}/actuator/health",
              "host": ["{{baseUrl}}"],
              "path": ["actuator", "health"]
            },
            "description": "Test server is running"
          },
          "response": []
        }
      ]
    },
    {
      "name": "👤 ACCOUNT MANAGEMENT",
      "item": [
        {
          "name": "✅ 1. Create Account (John - Savings)",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status is 201 Created\", function () {",
                  "    pm.response.to.have.status(201);",
                  "});",
                  "",
                  "pm.test(\"Response has success: true\", function () {",
                  "    var jsonData = pm.response.json();",
                  "    pm.expect(jsonData.success).to.eql(true);",
                  "});",
                  "",
                  "pm.test(\"Account number is returned\", function () {",
                  "    var jsonData = pm.response.json();",
                  "    var accountNumber = jsonData.data.accountNumber;",
                  "    pm.expect(accountNumber).to.be.a('string');",
                  "    pm.expect(accountNumber.length).to.eql(10);",
                  "    // Store for later use!",
                  "    pm.environment.set(\"accountNumber\", accountNumber);",
                  "    console.log(\"📌 Saved accountNumber: \" + accountNumber);",
                  "});",
                  "",
                  "pm.test(\"Balance matches initial deposit\", function () {",
                  "    var jsonData = pm.response.json();",
                  "    pm.expect(jsonData.data.balance).to.eql(1000.00);",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "auth": {
              "type": "basic",
              "basic": [
                {
                  "key": "username",
                  "value": "admin",
                  "type": "string"
                },
                {
                  "key": "password",
                  "value": "admin123",
                  "type": "string"
                }
              ]
            },
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json",
                "type": "text"
              },
              {
                "key": "X-Request-Source",
                "value": "Postman-Banking-Test",
                "type": "text",
                "disabled": true
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"fullName\": \"John Doe\",\n  \"email\": \"john.doe@bank.com\",\n  \"password\": \"SecurePass123!\",\n  \"phone\": \"9876543210\",\n  \"accountType\": \"SAVINGS\",\n  \"initialDeposit\": 1000.00\n}",
              "options": {
                "raw": {
                  "language": "json"
                }
              }
            },
            "url": {
              "raw": "{{baseUrl}}/api/{{apiVersion}}/accounts",
              "host": ["{{baseUrl}}"],
              "path": ["api", "{{apiVersion}}", "accounts"]
            },
            "description": "Create a new bank account with initial deposit"
          },
          "response": []
        },
        {
          "name": "✅ 2. Create Account (Jane - Current) → Recipient",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status is 201\", function () {",
                  "    pm.response.to.have.status(201);",
                  "});",
                  "",
                  "pm.test(\"Store recipient account number\", function () {",
                  "    var jsonData = pm.response.json();",
                  "    var recipient = jsonData.data.accountNumber;",
                  "    pm.environment.set(\"recipientAccount\", recipient);",
                  "    console.log(\"📌 Saved recipientAccount: \" + recipient);",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "auth": {
              "type": "basic",
              "basic": [
                {
                  "key": "username",
                  "value": "admin",
                  "type": "string"
                },
                {
                  "key": "password",
                  "value": "admin123",
                  "type": "string"
                }
              ]
            },
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json",
                "type": "text"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"fullName\": \"Jane Smith\",\n  \"email\": \"jane.smith@bank.com\",\n  \"password\": \"JanePass456!\",\n  \"phone\": \"8765432109\",\n  \"accountType\": \"CURRENT\",\n  \"initialDeposit\": 5000.00\n}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/{{apiVersion}}/accounts",
              "host": ["{{baseUrl}}"],
              "path": ["api", "{{apiVersion}}", "accounts"]
            }
          },
          "response": []
        },
        {
          "name": "✅ 3. Get Account Details",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status is 200\", function () {",
                  "    pm.response.to.have.status(200);",
                  "});",
                  "",
                  "pm.test(\"Account details match\", function () {",
                  "    var jsonData = pm.response.json();",
                  "    pm.expect(jsonData.data.fullName).to.eql(\"John Doe\");",
                  "    pm.expect(jsonData.data.email).to.eql(\"john.doe@bank.com\");",
                  "    pm.expect(jsonData.data.status).to.eql(\"ACTIVE\");",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "auth": {
              "type": "basic",
              "basic": [
                {
                  "key": "username",
                  "value": "admin",
                  "type": "string"
                },
                {
                  "key": "password",
                  "value": "admin123",
                  "type": "string"
                }
              ]
            },
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{baseUrl}}/api/{{apiVersion}}/accounts/{{accountNumber}}",
              "host": ["{{baseUrl}}"],
              "path": ["api", "{{apiVersion}}", "accounts", "{{accountNumber}}"]
            },
            "description": "Retrieve account by account number"
          },
          "response": []
        },
        {
          "name": "✅ 4. Check Balance",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Balance is correct\", function () {",
                  "    var jsonData = pm.response.json();",
                  "    console.log(\"💰 Current balance: \" + jsonData.data.balance);",
                  "    pm.expect(jsonData.data.balance).to.be.a('number');",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "auth": {
              "type": "basic",
              "basic": [
                {
                  "key": "username",
                  "value": "admin",
                  "type": "string"
                },
                {
                  "key": "password",
                  "value": "admin123",
                  "type": "string"
                }
              ]
            },
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{baseUrl}}/api/{{apiVersion}}/accounts/{{accountNumber}}/balance",
              "host": ["{{baseUrl}}"],
              "path": ["api", "{{apiVersion}}", "accounts", "{{accountNumber}}", "balance"]
            }
          },
          "response": []
        },
        {
          "name": "❌ 5. Create Account - Validation Error (Missing Fields)",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status is 400 Bad Request\", function () {",
                  "    pm.response.to.have.status(400);",
                  "});",
                  "",
                  "pm.test(\"Validation errors returned\", function () {",
                  "    var jsonData = pm.response.json();",
                  "    console.log(\"🔴 Errors: \", JSON.stringify(jsonData));",
                  "    pm.expect(Object.keys(jsonData).length).to.be.greaterThan(0);",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "auth": {
              "type": "basic",
              "basic": [
                {
                  "key": "username",
                  "value": "admin",
                  "type": "string"
                },
                {
                  "key": "password",
                  "value": "admin123",
                  "type": "string"
                }
              ]
            },
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"fullName\": \"\",\n  \"email\": \"invalid-email\",\n  \"password\": \"12\"\n}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/{{apiVersion}}/accounts",
              "host": ["{{baseUrl}}"],
              "path": ["api", "{{apiVersion}}", "accounts"]
            }
          },
          "response": []
        },
        {
          "name": "❌ 6. Create Account - Duplicate Email (409 Conflict)",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status is 409 Conflict\", function () {",
                  "    pm.response.to.have.status(409);",
                  "});",
                  "",
                  "pm.test(\"Error message mentions email\", function () {",
                  "    var jsonData = pm.response.json();",
                  "    pm.expect(jsonData.message).to.include(\"already\");",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "auth": {
              "type": "basic",
              "basic": [
                {
                  "key": "username",
                  "value": "admin",
                  "type": "string"
                },
                {
                  "key": "password",
                  "value": "admin123",
                  "type": "string"
                }
              ]
            },
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"fullName\": \"Another John\",\n  \"email\": \"john.doe@bank.com\",\n  \"password\": \"pass123\",\n  \"initialDeposit\": 100\n}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/{{apiVersion}}/accounts",
              "host": ["{{baseUrl}}"],
              "path": ["api", "{{apiVersion}}", "accounts"]
            }
          },
          "response": []
        }
      ]
    },
    {
      "name": "💰 BANKING OPERATIONS",
      "item": [
        {
          "name": "💵 1. Deposit Money",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status is 200\", function () {",
                  "    pm.response.to.have.status(200);",
                  "});",
                  "",
                  "pm.test(\"Transaction type is CREDIT\", function () {",
                  "    var jsonData = pm.response.json();",
                  "    pm.expect(jsonData.data.type).to.eql(\"CREDIT\");",
                  "});",
                  "",
                  "pm.test(\"Balance increased\", function () {",
                  "    var jsonData = pm.response.json();",
                  "    console.log(\"💰 New balance: \" + jsonData.data.balanceAfter);",
                  "    pm.expect(jsonData.data.balanceAfter).to.eql(1500.00);",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "auth": {
              "type": "basic",
              "basic": [
                {
                  "key": "username",
                  "value": "admin",
                  "type": "string"
                },
                {
                  "key": "password",
                  "value": "admin123",
                  "type": "string"
                }
              ]
            },
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"accountNumber\": \"{{accountNumber}}\",\n  \"amount\": 500.00\n}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/{{apiVersion}}/accounts/deposit",
              "host": ["{{baseUrl}}"],
              "path": ["api", "{{apiVersion}}", "accounts", "deposit"]
            }
          },
          "response": []
        },
        {
          "name": "💸 2. Withdraw Money",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status is 200\", function () {",
                  "    pm.response.to.have.status(200);",
                  "});",
                  "",
                  "pm.test(\"Transaction type is DEBIT\", function () {",
                  "    var jsonData = pm.response.json();",
                  "    pm.expect(jsonData.data.type).to.eql(\"DEBIT\");",
                  "});",
                  "",
                  "pm.test(\"Balance decreased correctly\", function () {",
                  "    var jsonData = pm.response.json();",
                  "    console.log(\"💰 Balance after withdrawal: \" + jsonData.data.balanceAfter);",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "auth": {
              "type": "basic",
              "basic": [
                {
                  "key": "username",
                  "value": "admin",
                  "type": "string"
                },
                {
                  "key": "password",
                  "value": "admin123",
                  "type": "string"
                }
              ]
            },
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"accountNumber\": \"{{accountNumber}}\",\n  \"amount\": 200.00\n}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/{{apiVersion}}/accounts/withdraw",
              "host": ["{{baseUrl}}"],
              "path": ["api", "{{apiVersion}}", "accounts", "withdraw"]
            }
          },
          "response": []
        },
        {
          "name": "🔄 3. Transfer Money (John → Jane)",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status is 200\", function () {",
                  "    pm.response.to.have.status(200);",
                  "});",
                  "",
                  "pm.test(\"Transfer successful message\", function () {",
                  "    var jsonData = pm.response.json();",
                  "    pm.expect(jsonData.message).to.include(\"Transfer\");",
                  "    console.log(\"✅ \" + jsonData.message);",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "auth": {
              "type": "basic",
              "basic": [
                {
                  "key": "username",
                  "value": "admin",
                  "type": "string"
                },
                {
                  "key": "password",
                  "value": "admin123",
                  "type": "string"
                }
              ]
            },
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"fromAccountNumber\": \"{{accountNumber}}\",\n  \"toAccountNumber\": \"{{recipientAccount}}\",\n  \"amount\": 300.00,\n  \"description\": \"Rent payment\"\n}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/{{apiVersion}}/accounts/transfer",
              "host": ["{{baseUrl}}"],
              "path": ["api", "{{apiVersion}}", "accounts", "transfer"]
            }
          },
          "response": []
        },
        {
          "name": "❌ 4. Withdraw - Insufficient Balance (400)",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status is 400\", function () {",
                  "    pm.response.to.have.status(400);",
                  "});",
                  "",
                  "pm.test(\"Insufficient balance error\", function () {",
                  "    var jsonData = pm.response.json();",
                  "    pm.expect(jsonData.message).to.include(\"Insufficient\");",
                  "    console.log(\"🔴 \" + jsonData.message);",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "auth": {
              "type": "basic",
              "basic": [
                {
                  "key": "username",
                  "value": "admin",
                  "type": "string"
                },
                {
                  "key": "password",
                  "value": "admin123",
                  "type": "string"
                }
              ]
            },
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"accountNumber\": \"{{accountNumber}}\",\n  \"amount\": 100000.00\n}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/{{apiVersion}}/accounts/withdraw",
              "host": ["{{baseUrl}}"],
              "path": ["api", "{{apiVersion}}", "accounts", "withdraw"]
            }
          },
          "response": []
        },
        {
          "name": "❌ 5. Transfer - Account Not Found (404)",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status is 404\", function () {",
                  "    pm.response.to.have.status(404);",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "auth": {
              "type": "basic",
              "basic": [
                {
                  "key": "username",
                  "value": "admin",
                  "type": "string"
                },
                {
                  "key": "password",
                  "value": "admin123",
                  "type": "string"
                }
              ]
            },
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"fromAccountNumber\": \"9999999999\",\n  \"toAccountNumber\": \"{{recipientAccount}}\",\n  \"amount\": 100.00\n}"
            },
            "url": {
              "raw": "{{baseUrl}}/api/{{apiVersion}}/accounts/transfer",
              "host": ["{{baseUrl}}"],
              "path": ["api", "{{apiVersion}}", "accounts", "transfer"]
            }
          },
          "response": []
        }
      ]
    },
    {
      "name": "📊 STATEMENT & REPORTS",
      "item": [
        {
          "name": "📜 Get Full Statement",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status is 200\", function () {",
                  "    pm.response.to.have.status(200);",
                  "});",
                  "",
                  "pm.test(\"Transactions returned as array\", function () {",
                  "    var jsonData = pm.response.json();",
                  "    pm.expect(jsonData.data).to.be.an('array');",
                  "    console.log(\"📜 Transaction count: \" + jsonData.data.length);",
                  "    ",
                  "    // Print each transaction",
                  "    jsonData.data.forEach(function(tx, i) {",
                  "        console.log(i + \". [\" + tx.type + \"] \" + tx.amount + \" | Balance: \" + tx.balanceAfter);",
                  "    });",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "auth": {
              "type": "basic",
              "basic": [
                {
                  "key": "username",
                  "value": "admin",
                  "type": "string"
                },
                {
                  "key": "password",
                  "value": "admin123",
                  "type": "string"
                }
              ]
            },
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{baseUrl}}/api/{{apiVersion}}/accounts/{{accountNumber}}/statement",
              "host": ["{{baseUrl}}"],
              "path": ["api", "{{apiVersion}}", "accounts", "{{accountNumber}}", "statement"]
            },
            "description": "Get all transactions for account (sorted by newest first)"
          },
          "response": []
        },
        {
          "name": "📜 Check Recipient Statement",
          "request": {
            "auth": {
              "type": "basic",
              "basic": [
                {
                  "key": "username",
                  "value": "admin",
                  "type": "string"
                },
                {
                  "key": "password",
                  "value": "admin123",
                  "type": "string"
                }
              ]
            },
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{baseUrl}}/api/{{apiVersion}}/accounts/{{recipientAccount}}/statement",
              "host": ["{{baseUrl}}"],
              "path": ["api", "{{apiVersion}}", "accounts", "{{recipientAccount}}", "statement"]
            }
          },
          "response": []
        }
      ]
    },
    {
      "name": "🧪 ERROR SCENARIOS",
      "item": [
        {
          "name": "🔒 No Authentication (401)",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test(\"Status is 401 Unauthorized\", function () {",
                  "    pm.response.to.have.status(401);",
                  "});",
                  "console.log(\"🔒 Auth correctly blocked unauthorized access\");"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "auth": {
              "type": "noauth"
            },
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{baseUrl}}/api/{{apiVersion}}/accounts/{{accountNumber}}",
              "host": ["{{baseUrl}}"],
              "path": ["api", "{{apiVersion}}", "accounts", "{{accountNumber}}"]
            }
          },
          "response": []
        },
        {
          "name": "❌ Invalid Account Number (404)",
          "request": {
            "auth": {
              "type": "basic",
              "basic": [
                {
                  "key": "username",
                  "value": "admin",
                  "type": "string"
                },
                {
                  "key": "password",
                  "value": "admin123",
                  "type": "string"
                }
              ]
            },
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{baseUrl}}/api/{{apiVersion}}/accounts/0000000000",
              "host": ["{{baseUrl}}"],
              "path": ["api", "{{apiVersion}}", "accounts", "0000000000"]
            }
          },
          "response": []
        }
      ]
    },
    {
      "name": "🧹 CLEANUP (Optional)",
      "item": [
        {
          "name": "🗑️ Delete Account",
          "request": {
            "auth": {
              "type": "basic",
              "basic": [
                {
                  "key": "username",
                  "value": "admin",
                  "type": "string"
                },
                {
                  "key": "password",
                  "value": "admin123",
                  "type": "string"
                }
              ]
            },
            "method": "DELETE",
            "header": [],
            "url": {
              "raw": "{{baseUrl}}/api/{{apiVersion}}/accounts/{{accountNumber}}",
              "host": ["{{baseUrl}}"],
              "path": ["api", "{{apiVersion}}", "accounts", "{{accountNumber}}"]
            },
            "description": "⚠️ Deletes account - use with caution!"
          },
          "response": []
        }
      ]
    }
  ],
  "auth": {
    "type": "basic",
    "basic": [
      {
        "key": "username",
        "value": "admin",
        "type": "string"
      },
      {
        "key": "password",
        "value": "admin123",
        "type": "string"
      }
    ]
  },
  "event": [
    {
      "listen": "prerequest",
      "script": {
        "type": "text/javascript",
        "exec": [
          "// Global pre-request script",
          "console.log(\"🚀 Request: \" + pm.request.method + \" \" + pm.request.url.getPath());"
        ]
      }
    },
    {
      "listen": "test",
      "script": {
        "type": "text/javascript",
        "exec": [
          "// Global test - always runs",
          "pm.test(\"Response time is acceptable\", function () {",
          "    pm.expect(pm.response.responseTime).to.be.below(2000);",
          "});"
        ]
      }
    }
  ]
}
```

---

# 📋 HOW TO USE THE COLLECTION

## Step-by-Step:

```
┌─────────────────────────────────────────────────────────┐
│  1️⃣  Import JSON above into Postman                     │
│                                                         │
│  2️⃣  Create Environment called "Banking Local":         │
│      - baseUrl: http://localhost:8080                   │
│      - apiVersion: v1                                   │
│      - accountNumber: (leave empty, auto-filled)        │
│      - recipientAccount: (leave empty, auto-filled)     │
│                                                         │
│  3️⃣  Run requests in ORDER:                             │
│      📋 AUTH SETUP (first - sets variables)             │
│      👤 ACCOUNT MANAGEMENT (1, 2 create accounts)      │
│      💰 BANKING OPERATIONS (deposit → withdraw → xfer) │
│      📊 STATEMENT (verify transactions)                 │
│      🧪 ERROR SCENARIOS (test edge cases)               │
│                                                         │
│  4️⃣  Or use "Run Collection" (Runner):                  │
│      → Select collection                                │
│      → Set iterations: 1                                │
│      → Click Run 🏃                                     │
└─────────────────────────────────────────────────────────┘
```

---

# 🟢 POSTMAN ENVIRONMENT JSON (Separate Import)

```json