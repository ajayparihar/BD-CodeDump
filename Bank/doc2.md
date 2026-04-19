# 🏦 Complete Spring Boot Banking Project — From Zero to Production

## A Full-Stack Detailed Guide (IntelliJ IDEA)

> **Target:** REST API for a Banking System
> **Stack:** Spring Boot 3.x, Java 17, Maven, MySQL, Spring Data JPA, Spring Security (Basic)
> **IDE:** IntelliJ IDEA

---

## 📁 TABLE OF CONTENTS

| # | Section |
|---|---------|
| 1 | Project Setup in IntelliJ |
| 2 | Project Architecture & Theory |
| 3 | Dependencies (pom.xml) |
| 4 | Database Design |
| 5 | Entity Layer |
| 6 | Repository Layer |
| 7 | DTO Layer |
| 8 | Service Layer (Interface + Impl) |
| 9 | Controller Layer |
| 10 | Exception Handling |
| 11 | Security (Basic Auth) |
| 12 | API Testing with Postman |
| 13 | Complete Flow Diagrams |

---

# 🚀 SECTION 1: PROJECT SETUP IN INTELLIJ IDEA

### Step-by-step:

```
1. Open IntelliJ → New Project
2. Spring Initializr
   - Project: Maven
   - Language: Java 17
   - Spring Boot: 3.2.x
   - Group: com.bank
   - Artifact: banking-app
   - Packaging: Jar
   - Dependencies: ✅ Spring Web, ✅ Spring Data JPA, ✅ MySQL Driver, 
                   ✅ Lombok, ✅ Validation, ✅ Spring Security
3. Click "Create"
```

**Project Structure After Creation:**

```
banking-app/
├── src/
│   ├── main/
│   │   ├── java/com/bank/bankingapp/
│   │   │   ├── BankingAppApplication.java          ← Main class
│   │   │   ├── config/
│   │   │   ├── controller/
│   │   │   ├── dto/
│   │   │   │   ├── request/
│   │   │   │   └── response/
│   │   │   ├── entity/
│   │   │   ├── enums/
│   │   │   ├── exception/
│   │   │   ├── repository/
│   │   │   ├── service/
│   │   │   │   ├── impl/
│   │   │   └── util/
│   │   └── resources/
│   │       ├── application.properties
│   │       └── schema.sql
│   └── test/
└── pom.xml
```

---

# 🧠 SECTION 2: PROJECT ARCHITECTURE THEORY

## Architecture Pattern: **Layered Architecture (N-Tier)**

```
┌──────────────────────────────────────────┐
│              REST CLIENT                  │  ← Postman / Browser
│              (HTTP Request)               │
├──────────────────────────────────────────┤
│          CONTROLLER LAYER                │  ← @RestController
│   (Receives request, sends response)     │  ← Validates input, calls Service
├──────────────────────────────────────────┤
│           SERVICE LAYER                  │  ← @Service
│   Interface → Impl                       │  ← Business Logic
├──────────────────────────────────────────┤
│         REPOSITORY LAYER                 │  ← @Repository (Spring Data JPA)
│   (CRUD operations on DB)                │  ← Talks to MySQL
├──────────────────────────────────────────┤
│           ENTITY / MODEL                 │  ← @Entity (JPA)
│   (Java objects = DB tables)             │
├──────────────────────────────────────────┤
│              DATABASE                    │  ← MySQL
└──────────────────────────────────────────┘
```

### 🔑 Why this architecture?

| Layer | Responsibility | Annotation |
|-------|---------------|------------|
| **Controller** | HTTP routing, request/response, validation | `@RestController` |
| **Service Interface** | Contract (what methods exist) | (none) |
| **Service Impl** | Business logic implementation | `@Service` |
| **Repository** | Database operations | `@Repository` (auto via Spring Data JPA) |
| **Entity** | Maps to DB table | `@Entity` |
| **DTO** | Data Transfer Object — carries data between layers (NOT entity) | (none) |

### 💡 Key Concepts:

> **DTO Pattern:** Never expose Entity directly via API. DTOs carry only necessary fields.
> **Interface + Impl:** Allows loose coupling. You can swap implementations.
> **Lombok:** Reduces boilerplate (getters, setters, constructors).

---

# 📦 SECTION 3: DEPENDENCIES (pom.xml)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.5</version>
    </parent>

    <groupId>com.bank</groupId>
    <artifactId>banking-app</artifactId>
    <version>1.0.0</version>
    <name>banking-app</name>

    <properties>
        <java.version>17</java.version>
    </properties>

    <dependencies>
        <!-- Web -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- JPA (Database) -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>

        <!-- MySQL -->
        <dependency>
            <groupId>com.mysql</groupId>
            <artifactId>mysql-connector-j</artifactId>
            <scope>runtime</scope>
        </dependency>

        <!-- Validation -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>

        <!-- Security -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>

        <!-- Lombok -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>

        <!-- Test -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

---

# 🗃️ SECTION 4: DATABASE DESIGN

### MySQL Schema

```sql
-- src/main/resources/schema.sql (optional, JPA can auto-create)

CREATE DATABASE IF NOT EXISTS bank_db;
USE bank_db;

-- Users table
CREATE TABLE account (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(15),
    balance DECIMAL(15,2) DEFAULT 0.00,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    account_type ENUM('SAVINGS','CURRENT') DEFAULT 'SAVINGS',
    status ENUM('ACTIVE','INACTIVE','FROZEN') DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Transaction table
CREATE TABLE transaction (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    transaction_id VARCHAR(36) UNIQUE NOT NULL,
    account_number VARCHAR(20) NOT NULL,
    type ENUM('CREDIT','DEBIT','TRANSFER') NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    balance_after DECIMAL(15,2) NOT NULL,
    description VARCHAR(255),
    recipient_account VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### In `application.properties`:

```properties
# src/main/resources/application.properties

server.port=8080
spring.application.name=banking-app

# MySQL
spring.datasource.url=jdbc:mysql://localhost:3306/bank_db?useSSL=false&serverTimezone=UTC
spring.datasource.username=root
spring.datasource.password=root

# JPA
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
spring.jpa.database-platform=org.hibernate.dialect.MySQLDialect

# Security (default credentials)
spring.security.user.name=admin
spring.security.user.password=admin123
```

> ⚠️ **Install MySQL first.** Or use Docker:
> `docker run --name bank-mysql -e MYSQL_ROOT_PASSWORD=root -p 3306:3306 -d mysql:8`

---

# 🏗️ SECTION 5: ENTITY LAYER

### 📄 `src/main/java/com/bank/bankingapp/entity/Account.java`

```java
package com.bank.bankingapp.entity;

import com.bank.bankingapp.enums.AccountStatus;
import com.bank.bankingapp.enums.AccountType;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "account")
@Data                   // Lombok: getters + setters + toString + equals + hashCode
@NoArgsConstructor      // No-arg constructor (JPA needs this!)
@AllArgsConstructor     // All-arg constructor
public class Account {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String fullName;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(nullable = false)
    private String password;

    @Column(length = 15)
    private String phone;

    @Column(nullable = false, precision = 15, scale = 2)
    private BigDecimal balance = BigDecimal.ZERO;

    @Column(nullable = false, unique = true, length = 20)
    private String accountNumber;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private AccountType accountType = AccountType.SAVINGS;

    @Enumerated(EnumType.STRING)
    private AccountStatus status = AccountStatus.ACTIVE;

    @Column(updatable = false)
    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    // Lifecycle callbacks — JPA calls these automatically
    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}
```

### 📄 `src/main/java/com/bank/bankingapp/entity/Transaction.java`

```java
package com.bank.bankingapp.entity;

import com.bank.bankingapp.enums.TransactionType;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "transaction")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Transaction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String transactionId;

    @Column(nullable = false, length = 20)
    private String accountNumber;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private TransactionType type;

    @Column(nullable = false, precision = 15, scale = 2)
    private BigDecimal amount;

    @Column(nullable = false, precision = 15, scale = 2)
    private BigDecimal balanceAfter;

    @Column(length = 255)
    private String description;

    @Column(length = 20)
    private String recipientAccount; // Only for TRANSFER type

    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
    }
}
```

### 📄 `src/main/java/com/bank/bankingapp/enums/AccountType.java`

```java
package com.bank.bankingapp.enums;

public enum AccountType {
    SAVINGS,
    CURRENT
}
```

### 📄 `src/main/java/com/bank/bankingapp/enums/AccountStatus.java`

```java
package com.bank.bankingapp.enums;

public enum AccountStatus {
    ACTIVE, INACTIVE, FROZEN
}
```

### 📄 `src/main/java/com/bank/bankingapp/enums/TransactionType.java`

```java
package com.bank.bankingapp.enums;

public enum TransactionType {
    CREDIT, DEBIT, TRANSFER
}
```

> **🔑 Theory:** `@Entity` marks class as a DB table. `@Table` customizes table name.  
> `@Id + @GeneratedValue` = Primary Key auto-increment.  
> `@Enumerated(EnumType.STRING)` stores enum name ("SAVINGS") not ordinal (0).  
> `@PrePersist` / `@PreUpdate` are JPA lifecycle callbacks.

---

# 📬 SECTION 6: DTO LAYER (Data Transfer Objects)

> **Why DTO?** We don't expose password, internal IDs, etc. via API. DTOs carry only what client needs.

### 📄 `src/main/java/com/bank/bankingapp/dto/request/CreateAccountRequest.java`

```java
package com.bank.bankingapp.dto.request;

import com.bank.bankingapp.enums.AccountType;
import jakarta.validation.constraints.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class CreateAccountRequest {

    @NotBlank(message = "Full name is required")
    @Size(min = 2, max = 100)
    private String fullName;

    @NotBlank(message = "Email is required")
    @Email(message = "Invalid email format")
    private String email;

    @NotBlank(message = "Password is required")
    @Size(min = 6, message = "Password must be at least 6 characters")
    private String password;

    @Pattern(regexp = "^[0-9]{10,15}$", message = "Invalid phone number")
    private String phone;

    private AccountType accountType;

    private BigDecimal initialDeposit;
}
```

### 📄 `src/main/java/com/bank/bankingapp/dto/request/DepositRequest.java`

```java
package com.bank.bankingapp.dto.request;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.math.BigDecimal;

@Data
public class DepositRequest {
    @NotBlank(message = "Account number is required")
    private String accountNumber;

    @NotNull
    @DecimalMin(value = "1.00", message = "Deposit amount must be at least 1.00")
    private BigDecimal amount;
}
```

### 📄 `src/main/java/com/bank/bankingapp/dto/request/WithdrawRequest.java` — same structure as Deposit

### 📄 `src/main/java/com/bank/bankingapp/dto/request/TransferRequest.java`

```java
package com.bank.bankingapp.dto.request;

import jakarta.validation.constraints.*;
import lombok.Data;
import java.math.BigDecimal;

@Data
public class TransferRequest {
    @NotBlank
    private String fromAccountNumber;

    @NotBlank
    private String toAccountNumber;

    @NotNull
    @DecimalMin("1.00")
    private BigDecimal amount;

    private String description;
}
```

### 📄 `src/main/java/com/bank/bankingapp/dto/response/AccountResponse.java`

```java
package com.bank.bankingapp.dto.response;

import com.bank.bankingapp.enums.AccountStatus;
import com.bank.bankingapp.enums.AccountType;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AccountResponse {
    private Long id;
    private String fullName;
    private String email;
    private String phone;
    private BigDecimal balance;
    private String accountNumber;
    private AccountType accountType;
    private AccountStatus status;
    private LocalDateTime createdAt;
}
```

### 📄 `src/main/java/com/bank/bankingapp/dto/response/TransactionResponse.java`

```java
package com.bank.bankingapp.dto.response;

import com.bank.bankingapp.enums.TransactionType;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class TransactionResponse {
    private String transactionId;
    private String accountNumber;
    private TransactionType type;
    private BigDecimal amount;
    private BigDecimal balanceAfter;
    private String description;
    private String recipientAccount;
    private LocalDateTime createdAt;
}
```

### 📄 `src/main/java/com/bank/bankingapp/dto/response/ApiResponse.java` — Generic wrapper

```java
package com.bank.bankingapp.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ApiResponse<T> {
    private boolean success;
    private String message;
    private T data;
}
```

> **🔑 Theory:** `@Valid` annotation on Controller params triggers validation.  
> DTOs prevent **over-posting** attacks (client setting fields they shouldn't).

---

# 🗄️ SECTION 7: REPOSITORY LAYER

### 📄 `src/main/java/com/bank/bankingapp/repository/AccountRepository.java`

```java
package com.bank.bankingapp.repository;

import com.bank.bankingapp.entity.Account;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface AccountRepository extends JpaRepository<Account, Long> {

    // Spring Data JPA auto-implements this!
    // Method name follows convention → Spring generates SQL behind the scenes
    Optional<Account> findByAccountNumber(String accountNumber);

    Optional<Account> findByEmail(String email);

    boolean existsByEmail(String email);

    boolean existsByAccountNumber(String accountNumber);
}
```

### 📄 `src/main/java/com/bank/bankingapp/repository/TransactionRepository.java`

```java
package com.bank.bankingapp.repository;

import com.bank.bankingapp.entity.Transaction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TransactionRepository extends JpaRepository<Transaction, Long> {

    List<Transaction> findByAccountNumberOrderByCreatedAtDesc(String accountNumber);

    List<Transaction> findByTransactionId(String transactionId);
}
```

> **🔑 Theory:** You write ZERO SQL. Spring Data JPA inspects method name:
> - `findByAccountNumber` → `SELECT * FROM account WHERE account_number = ?`
> - `findByAccountNumberOrderByCreatedAtDesc` → adds ORDER BY

---

# 🔧 SECTION 8: SERVICE LAYER (Interface + Implementation)

## 📄 `src/main/java/com/bank/bankingapp/service/AccountService.java` — Interface

```java
package com.bank.bankingapp.service;

import com.bank.bankingapp.dto.request.*;
import com.bank.bankingapp.dto.response.*;

public interface AccountService {

    // Account Management
    ApiResponse<AccountResponse> createAccount(CreateAccountRequest request);
    ApiResponse<AccountResponse> getAccountByNumber(String accountNumber);
    ApiResponse<AccountResponse> getAccountById(Long id);
    ApiResponse<AccountResponse> updateAccount(String accountNumber, UpdateAccountRequest request);
    ApiResponse<String> deleteAccount(String accountNumber);

    // Banking Operations
    ApiResponse<TransactionResponse> deposit(DepositRequest request);
    ApiResponse<TransactionResponse> withdraw(WithdrawRequest request);
    ApiResponse<TransactionResponse> transfer(TransferRequest request);

    // Balance & Statements
    ApiResponse<AccountResponse> checkBalance(String accountNumber);
    ApiResponse<java.util.List<TransactionResponse>> getStatement(String accountNumber);
}
```

## 📄 `src/main/java/com/bank/bankingapp/service/impl/AccountServiceImpl.java` — Implementation

```java
package com.bank.bankingapp.service.impl;

import com.bank.bankingapp.dto.request.*;
import com.bank.bankingapp.dto.response.*;
import com.bank.bankingapp.entity.Account;
import com.bank.bankingapp.entity.Transaction;
import com.bank.bankingapp.enums.*;
import com.bank.bankingapp.exception.*;
import com.bank.bankingapp.repository.AccountRepository;
import com.bank.bankingapp.repository.TransactionRepository;
import com.bank.bankingapp.service.AccountService;
import com.bank.bankingapp.util.AccountNumberGenerator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service                    // Spring bean — managed by IoC container
@RequiredArgsConstructor    // Lombok: generates constructor with final fields
@Slf4j                      // Lombok: gives 'log' variable for logging
public class AccountServiceImpl implements AccountService {

    private final AccountRepository accountRepository;
    private final TransactionRepository transactionRepository;
    private final AccountNumberGenerator accountNumberGenerator;

    /* =============================================
       ACCOUNT MANAGEMENT
       ============================================= */

    @Override
    @Transactional
    public ApiResponse<AccountResponse> createAccount(CreateAccountRequest request) {
        log.info("Creating account for: {}", request.getEmail());

        // 1. Validate email not already used
        if (accountRepository.existsByEmail(request.getEmail())) {
            throw new ResourceAlreadyExistsException("Email already registered: " + request.getEmail());
        }

        // 2. Build Account entity from DTO
        Account account = Account.builder()
                .fullName(request.getFullName())
                .email(request.getEmail())
                .password(request.getPassword())  // In real app: encode with BCrypt!
                .phone(request.getPhone())
                .balance(request.getInitialDeposit() != null ? 
                         request.getInitialDeposit() : BigDecimal.ZERO)
                .accountNumber(accountNumberGenerator.generate())
                .accountType(request.getAccountType() != null ? 
                            request.getAccountType() : AccountType.SAVINGS)
                .status(AccountStatus.ACTIVE)
                .build();

        // 3. Save
        Account saved = accountRepository.save(account);

        // 4. If initial deposit > 0, record transaction
        if (request.getInitialDeposit() != null && 
            request.getInitialDeposit().compareTo(BigDecimal.ZERO) > 0) {
            recordTransaction(saved, TransactionType.CREDIT, 
                            request.getInitialDeposit(), "Initial deposit");
        }

        // 5. Map Entity → Response DTO (never return Entity!)
        AccountResponse response = mapToResponse(saved);

        return ApiResponse.<AccountResponse>builder()
                .success(true)
                .message("Account created successfully")
                .data(response)
                .build();
    }

    @Override
    public ApiResponse<AccountResponse> getAccountByNumber(String accountNumber) {
        Account account = accountRepository.findByAccountNumber(accountNumber)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Account not found: " + accountNumber));

        return ApiResponse.<AccountResponse>builder()
                .success(true)
                .message("Account retrieved")
                .data(mapToResponse(account))
                .build();
    }

    @Override
    public ApiResponse<AccountResponse> checkBalance(String accountNumber) {
        Account account = accountRepository.findByAccountNumber(accountNumber)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Account not found"));

        AccountResponse response = mapToResponse(account);

        return ApiResponse.<AccountResponse>builder()
                .success(true)
                .message("Balance: " + account.getBalance())
                .data(response)
                .build();
    }

    /* =============================================
       DEPOSIT
       ============================================= */
    @Override
    @Transactional
    public ApiResponse<TransactionResponse> deposit(DepositRequest request) {
        log.info("Deposit request: {} for account {}", 
                request.getAmount(), request.getAccountNumber());

        Account account = accountRepository.findByAccountNumber(request.getAccountNumber())
                .orElseThrow(() -> new ResourceNotFoundException("Account not found"));

        // Validate account status
        validateAccountActive(account);

        // Add amount
        BigDecimal newBalance = account.getBalance().add(request.getAmount());
        account.setBalance(newBalance);
        accountRepository.save(account);

        // Record transaction
        TransactionResponse txResponse = recordTransaction(
                account, TransactionType.CREDIT, request.getAmount(), "Deposit");

        return ApiResponse.<TransactionResponse>builder()
                .success(true)
                .message("Deposit successful")
                .data(txResponse)
                .build();
    }

    /* =============================================
       WITHDRAW
       ============================================= */
    @Override
    @Transactional
    public ApiResponse<TransactionResponse> withdraw(WithdrawRequest request) {
        Account account = accountRepository.findByAccountNumber(request.getAccountNumber())
                .orElseThrow(() -> new ResourceNotFoundException("Account not found"));

        validateAccountActive(account);

        // ⭐ BUSINESS RULE: Check sufficient balance
        if (account.getBalance().compareTo(request.getAmount()) < 0) {
            throw new InsufficientBalanceException("Insufficient balance. Available: " 
                    + account.getBalance());
        }

        BigDecimal newBalance = account.getBalance().subtract(request.getAmount());
        account.setBalance(newBalance);
        accountRepository.save(account);

        TransactionResponse txResponse = recordTransaction(
                account, TransactionType.DEBIT, request.getAmount(), "Withdrawal");

        return ApiResponse.<TransactionResponse>builder()
                .success(true)
                .message("Withdrawal successful")
                .data(txResponse)
                .build();
    }

    /* =============================================
       TRANSFER ⭐ Most complex operation
       ============================================= */
    @Override
    @Transactional
    public ApiResponse<TransactionResponse> transfer(TransferRequest request) {
        log.info("Transfer: {} from {} to {}", 
                request.getAmount(), request.getFromAccountNumber(), 
                request.getToAccountNumber());

        // 1. Fetch both accounts
        Account fromAccount = accountRepository.findByAccountNumber(
                request.getFromAccountNumber())
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Sender account not found"));

        Account toAccount = accountRepository.findByAccountNumber(
                request.getToAccountNumber())
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Recipient account not found"));

        // 2. Validate
        validateAccountActive(fromAccount);
        validateAccountActive(toAccount);

        if (fromAccount.getBalance().compareTo(request.getAmount()) < 0) {
            throw new InsufficientBalanceException("Insufficient balance for transfer");
        }

        // 3. Perform transfer atomically (within @Transactional)
        fromAccount.setBalance(fromAccount.getBalance().subtract(request.getAmount()));
        toAccount.setBalance(toAccount.getBalance().add(request.getAmount()));

        accountRepository.save(fromAccount);
        accountRepository.save(toAccount);

        // 4. Record TWO transactions (one debit, one credit)
        recordTransaction(fromAccount, TransactionType.TRANSFER, 
                         request.getAmount(), 
                         "Transfer to " + request.getToAccountNumber());
        TransactionResponse creditTx = recordTransaction(
                toAccount, TransactionType.CREDIT, request.getAmount(),
                "Transfer from " + request.getFromAccountNumber());

        return ApiResponse.<TransactionResponse>builder()
                .success(true)
                .message("Transfer completed")
                .data(creditTx) // Return recipient's credit transaction
                .build();
    }

    /* =============================================
       STATEMENT / TRANSACTION HISTORY
       ============================================= */
    @Override
    public ApiResponse<List<TransactionResponse>> getStatement(String accountNumber) {
        Account account = accountRepository.findByAccountNumber(accountNumber)
                .orElseThrow(() -> new ResourceNotFoundException("Account not found"));

        List<TransactionResponse> transactions = transactionRepository
                .findByAccountNumberOrderByCreatedAtDesc(accountNumber)
                .stream()
                .map(this::mapTransactionToResponse)
                .collect(Collectors.toList());

        return ApiResponse.<List<TransactionResponse>>builder()
                .success(true)
                .message("Statement retrieved. Count: " + transactions.size())
                .data(transactions)
                .build();
    }

    /* =============================================
       HELPER METHODS
       ============================================= */

    private TransactionResponse recordTransaction(
            Account account, TransactionType type, BigDecimal amount, String description) {

        Transaction transaction = Transaction.builder()
                .transactionId(UUID.randomUUID().toString())
                .accountNumber(account.getAccountNumber())
                .type(type)
                .amount(amount)
                .balanceAfter(account.getBalance())
                .description(description)
                .build();

        transactionRepository.save(transaction);

        return mapTransactionToResponse(transaction);
    }

    private AccountResponse mapToResponse(Account account) {
        return AccountResponse.builder()
                .id(account.getId())
                .fullName(account.getFullName())
                .email(account.getEmail())
                .phone(account.getPhone())
                .balance(account.getBalance())
                .accountNumber(account.getAccountNumber())
                .accountType(account.getAccountType())
                .status(account.getStatus())
                .createdAt(account.getCreatedAt())
                .build();
    }

    private TransactionResponse mapTransactionToResponse(Transaction tx) {
        return TransactionResponse.builder()
                .transactionId(tx.getTransactionId())
                .accountNumber(tx.getAccountNumber())
                .type(tx.getType())
                .amount(tx.getAmount())
                .balanceAfter(tx.getBalanceAfter())
                .description(tx.getDescription())
                .recipientAccount(tx.getRecipientAccount())
                .createdAt(tx.getCreatedAt())
                .build();
    }

    private void validateAccountActive(Account account) {
        if (account.getStatus() != AccountStatus.ACTIVE) {
            throw new AccountNotActiveException(
                    "Account is " + account.getStatus() + ". Cannot perform operation.");
        }
    }
}
```

> **🔑 Key Theory:**
> - `@Transactional` → wraps method in DB transaction. If exception occurs, **ROLLBACK**.
> - `@RequiredArgsConstructor` → constructor injection (better than `@Autowired` field injection).
> - `BigDecimal` for money → NEVER use `double` (floating point precision errors).
> - Service handles **business rules**: sufficient balance, account active, etc.
> - `UUID.randomUUID()` → unique transaction IDs.

### 📄 `src/main/java/com/bank/bankingapp/util/AccountNumberGenerator.java`

```java
package com.bank.bankingapp.util;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.security.SecureRandom;

@Component
@RequiredArgsConstructor
public class AccountNumberGenerator {

    private final com.bank.bankingapp.repository.AccountRepository accountRepository;

    public String generate() {
        String accountNumber;
        do {
            accountNumber = String.format("%010d", new SecureRandom().nextInt(1_000_000_000));
        } while (accountRepository.existsByAccountNumber(accountNumber));
        return accountNumber;
    }
}
```

---

# 🛡️ SECTION 9: EXCEPTION HANDLING

### 📄 `src/main/java/com/bank/bankingapp/exception/GlobalExceptionHandler.java`

```java
package com.bank.bankingapp.exception;

import com.bank.bankingapp.dto.response.ApiResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.HashMap;
import java.util.Map;

@RestControllerAdvice  // ⭐ Global exception handler for ALL controllers
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ApiResponse<Void>> handleNotFound(ResourceNotFoundException ex) {
        log.warn("Not found: {}", ex.getMessage());
        return ResponseEntity
                .status(HttpStatus.NOT_FOUND)
                .body(ApiResponse.<Void>builder()
                        .success(false)
                        .message(ex.getMessage())
                        .build());
    }

    @ExceptionHandler(ResourceAlreadyExistsException.class)
    public ResponseEntity<ApiResponse<Void>> handleConflict(ResourceAlreadyExistsException ex) {
        return ResponseEntity
                .status(HttpStatus.CONFLICT)
                .body(ApiResponse.<Void>builder()
                        .success(false)
                        .message(ex.getMessage())
                        .build());
    }

    @ExceptionHandler(InsufficientBalanceException.class)
    public ResponseEntity<ApiResponse<Void>> handleInsufficientBalance(
            InsufficientBalanceException ex) {
        return ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body(ApiResponse.<Void>builder()
                        .success(false)
                        .message(ex.getMessage())
                        .build());
    }

    @ExceptionHandler(AccountNotActiveException.class)
    public ResponseEntity<ApiResponse<Void>> handleAccountNotActive(
            AccountNotActiveException ex) {
        return ResponseEntity
                .status(HttpStatus.FORBIDDEN)
                .body(ApiResponse.<Void>builder()
                        .success(false)
                        .message(ex.getMessage())
                        .build());
    }

    // ⭐ Handles @Valid validation errors automatically!
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, String>> handleValidation(
            MethodArgumentNotValidException ex) {
        Map<String, String> errors = new HashMap<>();
        ex.getBindingResult().getAllErrors().forEach(error -> {
            String fieldName = ((FieldError) error).getField();
            String message = error.getDefaultMessage();
            errors.put(fieldName, message);
        });
        return ResponseEntity.badRequest().body(errors);
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<Void>> handleGeneric(Exception ex) {
        log.error("Unexpected error", ex);
        return ResponseEntity
                .status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ApiResponse.<Void>builder()
                        .success(false)
                        .message("Internal server error")
                        .build());
    }
}
```

### 📄 Custom Exception Classes (each in its own file):

```java
// ResourceNotFoundException.java
package com.bank.bankingapp.exception;
public class ResourceNotFoundException extends RuntimeException {
    public ResourceNotFoundException(String message) { super(message); }
}

// ResourceAlreadyExistsException.java
public class ResourceAlreadyExistsException extends RuntimeException {
    public ResourceAlreadyExistsException(String message) { super(message); }
}

// InsufficientBalanceException.java
public class InsufficientBalanceException extends RuntimeException {
    public InsufficientBalanceException(String message) { super(message); }
}

// AccountNotActiveException.java
public class AccountNotActiveException extends RuntimeException {
    public AccountNotActiveException(String message) { super(message); }
}
```

> **🔑 Theory:** `@RestControllerAdvice` = global `@ExceptionHandler`.  
> One place catches ALL exceptions. Clean separation of error handling.

---

# 🎮 SECTION 10: CONTROLLER LAYER

### 📄 `src/main/java/com/bank/bankingapp/controller/AccountController.java`

```java
package com.bank.bankingapp.controller;

import com.bank.bankingapp.dto.request.*;
import com.bank.bankingapp.dto.response.ApiResponse;
import com.bank.bankingapp.service.AccountService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/accounts")   // Base URL for all endpoints
@RequiredArgsConstructor
public class AccountController {

    private final AccountService accountService;

    /* ─── ACCOUNT MANAGEMENT ─── */

    // POST /api/v1/accounts
    @PostMapping
    public ResponseEntity<ApiResponse<?>> createAccount(
            @Valid @RequestBody CreateAccountRequest request) {  // @Valid triggers validation!
        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(accountService.createAccount(request));
    }

    // GET /api/v1/accounts/{accountNumber}
    @GetMapping("/{accountNumber}")
    public ResponseEntity<ApiResponse<?>> getAccount(@PathVariable String accountNumber) {
        return ResponseEntity.ok(accountService.getAccountByNumber(accountNumber));
    }

    // GET /api/v1/accounts/{accountNumber}/balance
    @GetMapping("/{accountNumber}/balance")
    public ResponseEntity<ApiResponse<?>> checkBalance(
            @PathVariable String accountNumber) {
        return ResponseEntity.ok(accountService.checkBalance(accountNumber));
    }

    // DELETE /api/v1/accounts/{accountNumber}
    @DeleteMapping("/{accountNumber}")
    public ResponseEntity<ApiResponse<?>> deleteAccount(
            @PathVariable String accountNumber) {
        return ResponseEntity.ok(accountService.deleteAccount(accountNumber));
    }

    /* ─── BANKING OPERATIONS ─── */

    // POST /api/v1/accounts/deposit
    @PostMapping("/deposit")
    public ResponseEntity<ApiResponse<?>> deposit(
            @Valid @RequestBody DepositRequest request) {
        return ResponseEntity.ok(accountService.deposit(request));
    }

    // POST /api/v1/accounts/withdraw
    @PostMapping("/withdraw")
    public ResponseEntity<ApiResponse<?>> withdraw(
            @Valid @RequestBody WithdrawRequest request) {
        return ResponseEntity.ok(accountService.withdraw(request));
    }

    // POST /api/v1/accounts/transfer
    @PostMapping("/transfer")
    public ResponseEntity<ApiResponse<?>> transfer(
            @Valid @RequestBody TransferRequest request) {
        return ResponseEntity.ok(accountService.transfer(request));
    }

    /* ─── STATEMENT ─── */

    // GET /api/v1/accounts/{accountNumber}/statement
    @GetMapping("/{accountNumber}/statement")
    public ResponseEntity<ApiResponse<?>> getStatement(
            @PathVariable String accountNumber) {
        return ResponseEntity.ok(accountService.getStatement(accountNumber));
    }
}
```

> **🔑 Theory:**
> - `@RestController` = `@Controller` + `@ResponseBody` (returns JSON automatically)
> - `@RequestMapping("/api/v1/accounts")` → base path for all methods
> - `@PathVariable` → extracts from URL: `/accounts/{accountNumber}`
> - `@RequestBody` → deserializes JSON body → Java object
> - `@Valid` → triggers Jakarta Validation on the DTO

---

# 🔐 SECTION 11: SPRING SECURITY (Basic Auth)

### 📄 `src/main/java/com/bank/bankingapp/config/SecurityConfig.java`

```java
package com.bank.bankingapp.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())   // Disable CSRF for API (we use tokens later)
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/v1/accounts/**").authenticated()  // All banking APIs need auth
                // .requestMatchers("/api/v1/accounts/**").permitAll()   // ← For testing
            )
            .httpBasic(basic -> {});  // Basic Authentication

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();  // ⭐ Use for real password encoding!
    }
}
```

> **⚠️ Note:** For now, use `permitAll()` while testing. Later, implement JWT.

---

# 📊 SECTION 12: COMPLETE API FLOW DIAGRAM

```
CLIENT (Postman)
    │
    │  POST /api/v1/accounts
    │  { "fullName": "John Doe", "email": "john@email.com", ... }
    │
    ▼
Controller (AccountController.createAccount())
    │  @Valid checks DTO fields
    │  ✅ valid? → call service
    │  ❌ invalid? → GlobalExceptionHandler → 400 Bad Request
    │
    ▼
Service (AccountServiceImpl.createAccount())
    │  Check email duplicate (Repository)
    │  Generate account number
    │  Build Account entity
    │  Save (Repository)
    │  Record initial deposit transaction
    │  Map Entity → AccountResponse DTO
    │
    ▼
Repository (AccountRepository.save()) → MySQL INSERT
Repository (TransactionRepository.save()) → MySQL INSERT
    │
    │  @Transactional ensures BOTH succeed or NONE
    │
    ▼
Controller ← returns ResponseEntity<ApiResponse<AccountResponse>>
    │
    ▼
CLIENT receives:
    {
      "success": true,
      "message": "Account created successfully",
      "data": {
        "accountNumber": "1234567890",
        "fullName": "John Doe",
        "balance": 1000.00,
        ...
      }
    }
```

### 💰 Transfer Flow:

```
POST /api/v1/accounts/transfer
{ "fromAccountNumber": "1234567890", 
  "toAccountNumber": "0987654321", 
  "amount": 500 }

Controller → Service.transfer()
    │
    ├─ Fetch sender (Repository) ✅
    ├─ Fetch recipient (Repository) ✅
    ├─ Validate sender ACTIVE ✅
    ├─ Validate recipient ACTIVE ✅
    ├─ Check balance >= 500 ✅
    │
    ├─ sender.balance -= 500  → save()
    ├─ recipient.balance += 500 → save()
    │   (@Transactional = atomic)
    │
    ├─ Record DEBIT transaction for sender
    ├─ Record CREDIT transaction for recipient
    │
    └─ Return success
```

---

# 🧪 SECTION 13: POSTMAN TEST SEQUENCE

| # | Method | URL | Body (JSON) | Expected |
|---|--------|-----|-------------|----------|
| 1 | POST | `/api/v1/accounts` | `{ "fullName":"John", "email":"john@b.com", "password":"pass123", "initialDeposit":1000 }` | 201 Created |
| 2 | GET | `/api/v1/accounts/1234567890` | - | 200 OK |
| 3 | GET | `/api/v1/accounts/1234567890/balance` | - | 200 OK |
| 4 | POST | `/api/v1/accounts/deposit` | `{ "accountNumber":"1234567890", "amount":500 }` | 200 OK |
| 5 | POST | `/api/v1/accounts/withdraw` | `{ "accountNumber":"1234567890", "amount":200 }` | 200 OK |
| 6 | POST | `/api/v1/accounts/transfer` | `{ "fromAccountNumber":"1234567890", "toAccountNumber":"0987654321", "amount":300 }` | 200 OK |
| 7 | GET | `/api/v1/accounts/1234567890/statement` | - | 200 OK (list of transactions) |
| 8 | POST | `/api/v1/accounts/withdraw` | `{ "accountNumber":"1234567890", "amount":10000 }` | 400 (Insufficient) |

> 💡 **In Postman:** For Basic Auth → Authorization tab → Type: Basic Auth → Username: `admin` Password: `admin123`

---

# 📋 SECTION 14: ALL FILES SUMMARY

| # | File | Layer | Purpose |
|---|------|-------|---------|
| 1 | `BankingAppApplication.java` | Main | `@SpringBootApplication` entry point |
| 2 | `Account.java` | Entity | DB table mapping |
| 3 | `Transaction.java` | Entity | DB table mapping |
| 4 | `AccountType.java` | Enum | SAVINGS/CURRENT |
| 5 | `AccountStatus.java` | Enum | ACTIVE/INACTIVE/FROZEN |
| 6 | `TransactionType.java` | Enum | CREDIT/DEBIT/TRANSFER |
| 7 | `CreateAccountRequest.java` | DTO Req | Input for create |
| 8 | `DepositRequest.java` | DTO Req | Input for deposit |
| 9 | `TransferRequest.java` | DTO Req | Input for transfer |
| 10 | `AccountResponse.java` | DTO Res | Output for account |
| 11 | `TransactionResponse.java` | DTO Res | Output for transaction |
| 12 | `ApiResponse.java` | DTO Res | Generic wrapper |
| 13 | `AccountRepository.java` | Repository | DB operations on Account |
| 14 | `TransactionRepository.java` | Repository | DB operations on Transaction |
| 15 | `AccountService.java` | Service Interface | Contract |
| 16 | `AccountServiceImpl.java` | Service Impl | Business logic |
| 17 | `AccountNumberGenerator.java` | Util | Generates unique account # |
| 18 | `AccountController.java` | Controller | REST endpoints |
| 19 | `GlobalExceptionHandler.java` | Exception | Global error handling |
| 20 | `SecurityConfig.java` | Config | Spring Security |
| 21 | `application.properties` | Config | DB + server config |
| 22 | `pom.xml` | Build | Maven dependencies |

---

# ✅ FINAL CHECKLIST BEFORE RUNNING

```
☐ MySQL running on port 3306 (or update properties)
☐ IntelliJ: Maven reload (click 🔄 in Maven tool window)
☐ Lombok plugin installed in IntelliJ (Settings → Plugins → search "Lombok")
☐ Enable Annotation Processing (Settings → Build → Compiler → Annotation Processors ✅)
☐ Run BankingAppApplication.java (▶ green arrow)
☐ Console shows: Started BankingAppApplication in X seconds
☐ Test in Postman!
```

### Run Command (alternative):
```bash
mvn spring-boot:run
```

> **🎯 This is a production-grade foundation.** Next steps you can add:
> - 🔐 JWT Authentication (replace Basic Auth)
> - 📧 Email notification on transaction
> - 📊 Actuator for monitoring
> - 🧪 Unit tests with Mockito
> - 🐳 Docker Compose (MySQL + App)
> - 📝 Swagger/OpenAPI documentation (`springdoc-openapi`)