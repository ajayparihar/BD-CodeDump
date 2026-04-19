Below is a **complete, detailed, step-by-step Spring Boot “Bank” project guide** designed for **IntelliJ IDEA**, from scratch to production-ready structure. It includes **architecture theory, full banking features, file names, layer-by-layer flow, and concrete code** with explanations at every stage.

This is a **realistic banking system** (accounts, customers, transactions, transfers, authentication, authorization, auditing, validation, error handling, testing). It’s intentionally comprehensive so you learn Spring Boot properly.

---

# Table of Contents

1. [Learning goals and what you’ll build](#1-learning-goals-and-what-youll-build)
2. [Prerequisites and tools](#2-prerequisites-and-tools)
3. [Big-picture architecture (theory + diagrams)](#3-big-picture-architecture-theory--diagrams)
4. [Project setup in IntelliJ IDEA (step-by-step)](#4-project-setup-in-intellij-idea-step-by-step)
5. [Project structure (folders, files, responsibilities)](#5-project-structure-folders-files-responsibilities)
6. [Domain model design (entities and relationships)](#6-domain-model-design-entities-and-relationships)
7. [Database setup (H2/Postgres) + migrations](#7-database-setup-h2postgres--migrations)
8. [DTO pattern (why + how)](#8-dto-pattern-why--how)
9. [Repository layer (JPA)](#9-repository-layer-jpa)
10. [Service layer (business logic + transactions)](#10-service-layer-business-logic--transactions)
11. [Controller layer (REST API)](#11-controller-layer-rest-api)
12. [Validation, exception handling, and API responses](#12-validation-exception-handling-and-api-responses)
13. [Security (JWT authentication + role-based authorization)](#13-security-jwt-authentication--role-based-authorization)
14. [Banking features (complete list + implementation + flow)](#14-banking-features-complete-list--implementation--flow)
15. [Testing (unit + integration)](#15-testing-unit--integration)
16. [Logging, auditing, and observability](#16-logging-auditing-and-observability)
17. [Packaging, configuration profiles, and deployment](#17-packaging-configuration-profiles-and-deployment)
18. [Common mistakes and best practices](#18-common-mistakes-and-best-practices)
19. [Final checklist (what “done” looks like)](#19-final-checklist-what-done-looks-like)

---

# 1. Learning goals and what you’ll build

**You’ll build a Spring Boot banking system with:**

- Customer registration & profile management
- Account creation (Savings/Current)
- Deposits, withdrawals, transfers (between accounts)
- Transaction history (filters, pagination)
- Authentication & authorization (JWT, roles: CUSTOMER, ADMIN)
- Admin operations (freeze/unfreeze accounts, view all customers, audit logs)
- Validation, global exception handling, consistent API responses
- Auditing (createdAt/updatedAt, actor, source)
- Tests (JUnit + MockMvc + Testcontainers optional)

**Key Spring concepts you’ll master:**  
Controller ↔ Service ↔ Repository pattern, DTO mapping, JPA relationships, `@Transactional`, `@RestControllerAdvice`, Spring Security, JWT, Bean validation, profiles, testing, logging.

---

# 2. Prerequisites and tools

**Required**
- Java 17+ (LTS recommended)
- IntelliJ IDEA (Community or Ultimate)
- Maven (or Gradle; this guide uses Maven)
- Postman (or curl/HTTP client)

**Nice to have**
- Docker (for Postgres + Testcontainers)
- Git

---

# 3. Big-picture architecture (theory + diagrams)

## 3.1 Layered architecture (why it works)

A Spring Boot banking app typically uses **layered architecture**:

| Layer | Responsibility | Key Spring Annotations | Examples |
|---|---|---|---|
| **Controller (API)** | Handle HTTP requests/responses, input validation, auth checks | `@RestController`, `@RequestMapping`, `@PostMapping` | `AccountController`, `TransferController` |
| **Service (Business)** | Core banking rules, transaction integrity, security decisions | `@Service`, `@Transactional` | `AccountServiceImpl`, `TransferServiceImpl` |
| **Repository (Persistence)** | DB access via JPA | `@Repository`, `JpaRepository` | `AccountRepository`, `TransactionRepository` |
| **Entity (Domain)** | Domain model mapped to DB | `@Entity`, `@Table`, `@OneToMany` | `Customer`, `Account`, `Transaction` |
| **DTO (Data Transfer)** | Request/response contracts (avoid leaking entities) | `@Data`, validation annotations | `CreateAccountRequest`, `TransferResponse` |
| **Exception (Error handling)** | Centralized error responses | `@RestControllerAdvice`, `@ExceptionHandler` | `GlobalExceptionHandler` |
| **Config (Security/Swagger/Beans)** | App-wide configuration | `@Configuration`, `@EnableWebSecurity` | `SecurityConfig`, `JwtConfig` |

## 3.2 Data flow (end-to-end example: Transfer money)

1. **Client (Postman)** → `POST /api/transfers` with source/dest/account, amount
2. **TransferController** → validates request (DTO), extracts authenticated user
3. **TransferService** → checks account ownership/limits, checks balances, locks accounts conceptually (via DB transactions), creates debit/credit transactions
4. **AccountRepository** → updates balances
5. **TransactionRepository** → persists transfer entries
6. **Response** → `TransferResponse` (success/failure, reference, timestamps)

**Key banking principle:** **Atomicity** — either both debit and credit happen, or neither happens. That’s why `@Transactional` is critical.

## 3.3 Recommended package structure

```
com.bank.app
├─ BankApplication.java
├─ config/
├─ controller/
├─ dto/
│  ├─ request/
│  └─ response/
├─ entity/
├─ exception/
├─ repository/
├─ security/
├─ service/
│  └─ impl/
├─ util/
└─ validation/
```

---

# 4. Project setup in IntelliJ IDEA (step-by-step)

## Step 4.1 Create Spring Boot project
1. Open **IntelliJ IDEA** → **New Project**
2. Select **Spring Initializr**
3. Project: **Maven**, Language: **Java**
4. Spring Boot: **3.2.x** (latest stable)
5. Group: `com.bank`
6. Artifact: `bank-app`
7. Name: `bank-app`
8. Package: `com.bank.app`
9. Java: **17**
10. Add dependencies:
- **Spring Web** (REST)
- **Spring Data JPA** (DB)
- **Spring Security** (auth)
- **H2 Database** (dev)
- **PostgreSQL Driver** (prod)
- **Validation** (Bean validation)
- **Lombok** (reduce boilerplate)
- **Spring Boot DevTools** (hot reload)
- **Springdoc OpenAPI (Swagger UI)** (API docs) *(optional but great)*
- **jjwt-api / jjwt-impl / jjwt-jackson** (JWT) *(manual add if needed)*

11. Click **Finish**

## Step 4.2 Open project and verify
- File: `src/main/java/com/bank/app/BankApplication.java`
- Run it. You should see Spring Boot startup logs.

## Step 4.3 IntelliJ settings for smooth dev
- Enable annotation processing (Lombok): **Settings → Build → Compiler → Annotation Processors → Enable**
- Use Maven panel to run `clean install`
- Install Postman collection later for API testing

---

# 5. Project structure (folders, files, responsibilities)

Here’s the **complete file list** we’ll build (with purpose).

```
bank-app/
├─ pom.xml
├─ src/main/
│  ├─ resources/
│  │  ├─ application.properties
│  │  ├─ application-dev.properties
│  │  ├─ application-prod.properties
│  │  └─ data.sql (seed data)
│  └─ java/com/bank/app/
│     ├─ BankApplication.java
│     ├─ config/
│     │  ├─ OpenApiConfig.java
│     │  ├─ WebConfig.java
│     │  └─ JpaAuditingConfig.java
│     ├─ controller/
│     │  ├─ AuthController.java
│     │  ├─ CustomerController.java
│     │  ├─ AccountController.java
│     │  ├─ TransactionController.java
│     │  ├─ TransferController.java
│     │  └─ AdminController.java
│     ├─ dto/
│     │  ├─ request/
│     │  │  ├─ LoginRequest.java
│     │  │  ├─ RegisterCustomerRequest.java
│     │  │  ├─ CreateAccountRequest.java
│     │  │  ├─ DepositRequest.java
│     │  │  ├─ WithdrawRequest.java
│     │  │  └─ TransferRequest.java
│     │  └─ response/
│     │     ├─ ApiResponse.java
│     │     ├─ JwtResponse.java
│     │     ├─ CustomerResponse.java
│     │     ├─ AccountResponse.java
│     │     ├─ TransactionResponse.java
│     │     └─ TransferResponse.java
│     ├─ entity/
│     │  ├─ BaseEntity.java
│     │  ├─ Customer.java
│     │  ├─ Account.java
│     │  ├─ Transaction.java
│     │  ├─ enums/
│     │  │  ├─ AccountType.java
│     │  │  ├─ TransactionType.java
│     │  │  ├─ AccountStatus.java
│     │  │  └─ RoleName.java
│     │  └─ AuditLog.java
│     ├─ exception/
│     │  ├─ ResourceNotFoundException.java
│     │  ├─ BadRequestException.java
│     │  ├─ InsufficientBalanceException.java
│     │  ├─ AccountNotActiveException.java
│     │  └─ GlobalExceptionHandler.java
│     ├─ repository/
│     │  ├─ CustomerRepository.java
│     │  ├─ AccountRepository.java
│     │  ├─ TransactionRepository.java
│     │  └─ AuditLogRepository.java
│     ├─ security/
│     │  ├─ SecurityConfig.java
│     │  ├─ JwtAuthenticationEntryPoint.java
│     │  ├─ JwtAuthenticationFilter.java
│     │  ├─ JwtTokenProvider.java
│     │  ├─ UserDetailsServiceImpl.java
│     │  └─ UserPrincipal.java
│     ├─ service/
│     │  ├─ CustomerService.java
│     │  ├─ AccountService.java
│     │  ├─ TransactionService.java
│     │  ├─ TransferService.java
│     │  ├─ AuditService.java
│     │  └─ impl/
│     │     ├─ CustomerServiceImpl.java
│     │     ├─ AccountServiceImpl.java
│     │     ├─ TransactionServiceImpl.java
│     │     ├─ TransferServiceImpl.java
│     │     └─ AuditServiceImpl.java
│     └─ util/
│        └─ AccountNumberGenerator.java
└─ src/test/
   ├─ resources/
   │  └─ application-test.properties
   └─ java/com/bank/app/
      ├─ BankApplicationTests.java
      ├─ controller/
      │  ├─ AuthControllerTest.java
      │  ├─ AccountControllerTest.java
      │  └─ TransferControllerTest.java
      └─ service/
         └─ TransferServiceTest.java
```

---

# 6. Domain model design (entities and relationships)

## 6.1 Core entities

### (A) `BaseEntity` (auditing)
Common fields: `id`, `createdAt`, `updatedAt`, `createdBy`, `updatedBy`.

### (B) `Customer`
- `id` (Long)
- `name`, `email`, `password` (hashed)
- `phone`, `address`
- `roles` (Set<RoleName>)
- `accounts` (List<Account>)

### (C) `Account`
- `id` (Long)
- `accountNumber` (unique, generated)
- `accountType` (SAVINGS/CURRENT)
- `status` (ACTIVE/FROZEN/CLOSED)
- `balance` (BigDecimal)
- `customer` (ManyToOne)
- `transactions` (List<Transaction>)

### (D) `Transaction`
- `id` (Long)
- `transactionRef` (unique)
- `type` (DEPOSIT/WITHDRAW/TRANSFER_IN/TRANSFER_OUT)
- `amount` (BigDecimal)
- `balanceAfter` (BigDecimal)
- `description`
- `account` (ManyToOne)
- `relatedAccountId` (nullable)
- `timestamp`

### (E) `AuditLog`
- `actor`, `action`, `entity`, `entityId`, `details`, `timestamp`

## 6.2 Relationships (theory)
- **Customer ↔ Account**: One-to-many (a customer can have multiple accounts)
- **Account ↔ Transaction**: One-to-many (each account has a ledger)
- **Transfer**: Two transaction records (debit from source, credit to destination) linked by reference

This is critical for banking: you don’t “move money” — you record two entries.

---

# 7. Database setup (H2/Postgres) + migrations

## 7.1 `application.properties` (base)
```properties
server.port=8080
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
spring.jackson.serialization.write-dates-as-timestamps=false
```

## 7.2 `application-dev.properties` (H2)
```properties
spring.datasource.url=jdbc:h2:mem:bankdb;DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE
spring.datasource.driver-class-name=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=
spring.h2.console.enabled=true
spring.h2.console.path=/h2-console
```

## 7.3 `application-prod.properties` (Postgres)
```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/bankdb
spring.datasource.username=bankuser
spring.datasource.password=bankpass
spring.jpa.hibernate.ddl-auto=validate
```

## 7.4 Seed data (`data.sql`)
Optional initial roles/customers for testing.

---

# 8. DTO pattern (why + how)

### Why DTOs?
- Prevent leaking internal entity structure (passwords, internal IDs, lazy fields)
- Provide clear request/response contracts
- Enable validation at the edge (controller layer)

### Common DTOs
- `RegisterCustomerRequest` (name, email, password, phone)
- `LoginRequest` (email, password)
- `CreateAccountRequest` (accountType, initialDeposit)
- `DepositRequest`, `WithdrawRequest`, `TransferRequest`
- `AccountResponse`, `CustomerResponse`, `TransactionResponse`, `TransferResponse`

---

# 9. Repository layer (JPA)

Repositories extend `JpaRepository<Entity, Long>` and add custom queries.

**Examples**
- `CustomerRepository`: findByEmail
- `AccountRepository`: findByAccountNumber, findByCustomerId
- `TransactionRepository`: findByAccountIdOrderByTimestampDesc, findByAccountIdAndType, pagination

---

# 10. Service layer (business logic + transactions)

## 10.1 Responsibilities
- Validate business rules (minimum balance, account status, ownership)
- Coordinate multiple repositories
- Ensure **atomicity** with `@Transactional`

## 10.2 Key services
- `CustomerService`: register, get profile, update
- `AccountService`: create account, get balances, list accounts
- `TransactionService`: deposit, withdraw, history
- `TransferService`: transfer between accounts (most complex)
- `AuditService`: record actions

## 10.3 `@Transactional` theory (banking-critical)
- Starts DB transaction
- Executes multiple DB operations
- If any fails → rolls back
- If all succeed → commits
- Use `@Transactional(readOnly=true)` for queries (performance)

---

# 11. Controller layer (REST API)

Controllers define endpoints, map DTOs, enforce auth, return `ApiResponse<T>`.

**Base path:** `/api`

**Common endpoints**
- `/api/auth/register`, `/api/auth/login`
- `/api/customers/me`, `/api/customers/me/accounts`
- `/api/accounts/{id}`, `/api/accounts/{id}/balance`
- `/api/accounts/{id}/deposit`, `/api/accounts/{id}/withdraw`
- `/api/transfers`
- `/api/transactions/account/{id}`
- `/api/admin/accounts/{id}/freeze`

---

# 12. Validation, exception handling, and API responses

## 12.1 Validation
- Use `@NotBlank`, `@Email`, `@Positive`, `@DecimalMin`
- Validate in DTOs, handle `MethodArgumentNotValidException`

## 12.2 Global exception handling
- `@RestControllerAdvice`
- Convert exceptions to consistent JSON: `ApiResponse.error(message, code, details)`

## 12.3 Standard API response
```json
{
  "success": true,
  "message": "Transfer completed successfully",
  "data": {
    "reference": "TXN-2026-0001",
    "sourceAccount": "ACC-10001",
    "destinationAccount": "ACC-10002",
    "amount": 500.00,
    "timestamp": "2026-01-01T10:00:00Z"
  }
}
```

---

# 13. Security (JWT authentication + role-based authorization)

## 13.1 Security flow
1. User registers → password hashed (`BCryptPasswordEncoder`)
2. User logs in → `AuthController` returns JWT
3. Client includes `Authorization: Bearer <token>`
4. `JwtAuthenticationFilter` validates token, sets authentication in SecurityContext
5. `@PreAuthorize("hasRole('ADMIN')")` or role checks enforce access

## 13.2 Roles
- `ROLE_CUSTOMER`
- `ROLE_ADMIN`

## 13.3 Key classes
- `SecurityConfig`
- `JwtTokenProvider`
- `JwtAuthenticationFilter`
- `UserDetailsServiceImpl`
- `UserPrincipal`

---

# 14. Banking features (complete list + implementation + flow)

Below are **all banking functions** with **file name, flow, and code**.

> Note: I’ll provide **production-leaning, clean code** with clear separation. In a real bank you’d add more (limits, KYC, reconciliation, idempotency keys, rate limiting, audit retention, compliance). This is a strong, educational foundation.

---

## 14.1 Customer Management

### (1) Register customer
**Endpoint:** `POST /api/auth/register`  
**Controller:** `AuthController.java`  
**Service:** `CustomerServiceImpl.java`  
**DTO:** `RegisterCustomerRequest.java`, `CustomerResponse.java`  
**Flow**
1. Validate email uniqueness
2. Hash password
3. Assign default role `ROLE_CUSTOMER`
4. Save customer
5. Return `CustomerResponse` (no password)

**Code — `RegisterCustomerRequest.java`**
```java
package com.bank.app.dto.request;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class RegisterCustomerRequest {
    @NotBlank(message = "Name is required")
    private String name;

    @Email(message = "Invalid email")
    @NotBlank(message = "Email is required")
    private String email;

    @NotBlank(message = "Password is required")
    @Size(min = 8, message = "Password must be at least 8 characters")
    private String password;

    private String phone;
    private String address;
}
```

**Code — `Customer.java`**
```java
package com.bank.app.entity;

import com.bank.app.entity.enums.RoleName;
import jakarta.persistence.*;
import lombok.*;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

@Entity
@Table(name = "customers")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class Customer extends BaseEntity {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(nullable = false)
    private String password;

    private String phone;
    private String address;

    @ElementCollection(fetch = FetchType.EAGER)
    @Enumerated(EnumType.STRING)
    @CollectionTable(name = "customer_roles", joinColumns = @JoinColumn(name = "customer_id"))
    @Column(name = "role")
    private Set<RoleName> roles = new HashSet<>();

    @OneToMany(mappedBy = "customer", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Account> accounts;
}
```

**Code — `CustomerServiceImpl.java` (snippet)**
```java
@Service
@RequiredArgsConstructor
public class CustomerServiceImpl implements CustomerService {

    private final CustomerRepository customerRepository;
    private final PasswordEncoder passwordEncoder;

    @Override
    @Transactional
    public CustomerResponse register(RegisterCustomerRequest request) {
        if (customerRepository.findByEmail(request.getEmail()).isPresent()) {
            throw new BadRequestException("Email already in use");
        }

        Customer customer = Customer.builder()
                .name(request.getName())
                .email(request.getEmail())
                .password(passwordEncoder.encode(request.getPassword()))
                .phone(request.getPhone())
                .address(request.getAddress())
                .roles(Set.of(RoleName.ROLE_CUSTOMER))
                .build();

        Customer saved = customerRepository.save(customer);
        return mapToResponse(saved);
    }

    private CustomerResponse mapToResponse(Customer customer) {
        return CustomerResponse.builder()
                .id(customer.getId())
                .name(customer.getName())
                .email(customer.getEmail())
                .phone(customer.getPhone())
                .address(customer.getAddress())
                .roles(customer.getRoles())
                .build();
    }
}
```

**Code — `AuthController.java`**
```java
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final CustomerService customerService;
    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider jwtTokenProvider;

    @PostMapping("/register")
    public ResponseEntity<ApiResponse<CustomerResponse>> register(@Valid @RequestBody RegisterCustomerRequest request) {
        CustomerResponse response = customerService.register(request);
        return ResponseEntity.ok(ApiResponse.success("Registered successfully", response));
    }

    @PostMapping("/login")
    public ResponseEntity<ApiResponse<JwtResponse>> login(@Valid @RequestBody LoginRequest request) {
        Authentication auth = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.getEmail(), request.getPassword()));
        SecurityContextHolder.getContext().setAuthentication(auth);
        String token = jwtTokenProvider.generateToken(auth);
        return ResponseEntity.ok(ApiResponse.success("Login successful", new JwtResponse(token)));
    }
}
```

### (2) Get profile / update profile
**Endpoints:** `GET /api/customers/me`, `PUT /api/customers/me`  
**Controller:** `CustomerController.java`  
**Service:** `CustomerServiceImpl.java`

---

## 14.2 Account Management

### (1) Create account
**Endpoint:** `POST /api/accounts`  
**Controller:** `AccountController.java`  
**Service:** `AccountServiceImpl.java`  
**DTO:** `CreateAccountRequest.java`, `AccountResponse.java`  
**Entity:** `Account.java`  
**Flow**
1. Authenticated customer retrieved
2. Validate account type
3. Generate unique `accountNumber`
4. Create account with initial balance (or zero)
5. If initial deposit > 0 → create DEPOSIT transaction
6. Return `AccountResponse`

**Code — `CreateAccountRequest.java`**
```java
@Data
public class CreateAccountRequest {
    @NotNull(message = "Account type is required")
    private AccountType accountType;

    @DecimalMin(value = "0.0", inclusive = true, message = "Initial deposit must be >= 0")
    private BigDecimal initialDeposit = BigDecimal.ZERO;
}
```

**Code — `Account.java`**
```java
@Entity
@Table(name = "accounts", uniqueConstraints = @UniqueConstraint(columnNames = "account_number"))
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class Account extends BaseEntity {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "account_number", nullable = false, unique = true, length = 20)
    private String accountNumber;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private AccountType accountType;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private AccountStatus status = AccountStatus.ACTIVE;

    @Column(nullable = false, precision = 19, scale = 2)
    private BigDecimal balance = BigDecimal.ZERO;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "customer_id", nullable = false)
    private Customer customer;

    @OneToMany(mappedBy = "account", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Transaction> transactions = new ArrayList<>();
}
```

**Code — `AccountServiceImpl.java` (create account snippet)**
```java
@Service
@RequiredArgsConstructor
public class AccountServiceImpl implements AccountService {

    private final AccountRepository accountRepository;
    private final CustomerRepository customerRepository;
    private final TransactionRepository transactionRepository;
    private final AccountNumberGenerator accountNumberGenerator;

    @Override
    @Transactional
    public AccountResponse createAccount(Long customerId, CreateAccountRequest request) {
        Customer customer = customerRepository.findById(customerId)
                .orElseThrow(() -> new ResourceNotFoundException("Customer not found"));

        Account account = Account.builder()
                .accountNumber(accountNumberGenerator.generate())
                .accountType(request.getAccountType())
                .status(AccountStatus.ACTIVE)
                .balance(BigDecimal.ZERO)
                .customer(customer)
                .build();

        if (request.getInitialDeposit() != null && request.getInitialDeposit().compareTo(BigDecimal.ZERO) > 0) {
            account.setBalance(request.getInitialDeposit());
        }

        Account saved = accountRepository.save(account);

        if (request.getInitialDeposit() != null && request.getInitialDeposit().compareTo(BigDecimal.ZERO) > 0) {
            Transaction txn = Transaction.builder()
                    .transactionRef("DEP-" + System.currentTimeMillis())
                    .type(TransactionType.DEPOSIT)
                    .amount(request.getInitialDeposit())
                    .balanceAfter(saved.getBalance())
                    .description("Initial deposit")
                    .account(saved)
                    .timestamp(LocalDateTime.now())
                    .build();
            transactionRepository.save(txn);
        }

        return mapToResponse(saved);
    }
}
```

**Code — `AccountNumberGenerator.java`**
```java
@Component
public class AccountNumberGenerator {
    private final AtomicLong counter = new AtomicLong(10000);

    public String generate() {
        return String.format("ACC-%d", counter.incrementAndGet());
    }
}
```

### (2) Get account details / list accounts
**Endpoints:** `GET /api/accounts/{id}`, `GET /api/customers/me/accounts`

### (3) Freeze / unfreeze account (admin)
**Endpoints:** `PUT /api/admin/accounts/{id}/freeze`, `PUT /api/admin/accounts/{id}/unfreeze`  
**Security:** `@PreAuthorize("hasRole('ADMIN')")`

---

## 14.3 Transaction Management (Deposit / Withdraw)

### (1) Deposit
**Endpoint:** `POST /api/accounts/{id}/deposit`  
**Controller:** `TransactionController.java`  
**Service:** `TransactionServiceImpl.java`  
**DTO:** `DepositRequest.java`  
**Flow**
1. Verify account ownership (or admin)
2. Check account status ACTIVE
3. Increase balance
4. Create DEPOSIT transaction record
5. Return updated `AccountResponse`

**Code — `DepositRequest.java`**
```java
@Data
public class DepositRequest {
    @DecimalMin(value = "0.01", message = "Amount must be > 0")
    private BigDecimal amount;

    private String description;
}
```

**Code — `TransactionServiceImpl.java` (deposit snippet)**
```java
@Service
@RequiredArgsConstructor
public class TransactionServiceImpl implements TransactionService {

    private final AccountRepository accountRepository;
    private final TransactionRepository transactionRepository;

    @Override
    @Transactional
    public AccountResponse deposit(Long accountId, DepositRequest request, Long actorCustomerId) {
        Account account = accountRepository.findById(accountId)
                .orElseThrow(() -> new ResourceNotFoundException("Account not found"));

        if (!account.getCustomer().getId().equals(actorCustomerId) && !isAdmin(actorCustomerId)) {
            throw new BadRequestException("Not authorized");
        }
        if (account.getStatus() != AccountStatus.ACTIVE) {
            throw new AccountNotActiveException("Account is not active");
        }

        account.setBalance(account.getBalance().add(request.getAmount()));

        Transaction txn = Transaction.builder()
                .transactionRef("DEP-" + System.currentTimeMillis())
                .type(TransactionType.DEPOSIT)
                .amount(request.getAmount())
                .balanceAfter(account.getBalance())
                .description(request.getDescription())
                .account(account)
                .timestamp(LocalDateTime.now())
                .build();

        transactionRepository.save(txn);
        return mapAccount(account);
    }
}
```

### (2) Withdraw
**Endpoint:** `POST /api/accounts/{id}/withdraw`  
**Flow:** same as deposit, but subtract and check `balance >= amount`

**Code — withdraw check**
```java
if (account.getBalance().compareTo(request.getAmount()) < 0) {
    throw new InsufficientBalanceException("Insufficient balance");
}
account.setBalance(account.getBalance().subtract(request.getAmount()));
```

### (3) Transaction history
**Endpoint:** `GET /api/transactions/account/{id}`  
**DTO:** `TransactionResponse.java`  
**Filters:** type, fromDate, toDate, page, size

---

## 14.4 Transfers (most complex — banking-critical)

### (1) Transfer between accounts
**Endpoint:** `POST /api/transfers`  
**Controller:** `TransferController.java`  
**Service:** `TransferServiceImpl.java`  
**DTO:** `TransferRequest.java`, `TransferResponse.java`  
**Flow (atomic)**
1. Validate source and destination accounts exist
2. Validate ownership of source account (or admin)
3. Validate both accounts ACTIVE
4. Validate source balance >= amount
5. Start transaction (`@Transactional`)
6. Debit source (create TRANSFER_OUT)
7. Credit destination (create TRANSFER_IN)
8. Save both transactions with same reference
9. Commit
10. Return `TransferResponse`

**Code — `TransferRequest.java`**
```java
@Data
public class TransferRequest {
    @NotBlank(message = "Source account number is required")
    private String sourceAccountNumber;

    @NotBlank(message = "Destination account number is required")
    private String destinationAccountNumber;

    @DecimalMin(value = "0.01", message = "Amount must be > 0")
    private BigDecimal amount;

    private String description;
}
```

**Code — `TransferServiceImpl.java`**
```java
@Service
@RequiredArgsConstructor
public class TransferServiceImpl implements TransferService {

    private final AccountRepository accountRepository;
    private final TransactionRepository transactionRepository;

    @Override
    @Transactional
    public TransferResponse transfer(TransferRequest request, Long actorCustomerId) {
        Account source = accountRepository.findByAccountNumber(request.getSourceAccountNumber())
                .orElseThrow(() -> new ResourceNotFoundException("Source account not found"));

        Account destination = accountRepository.findByAccountNumber(request.getDestinationAccountNumber())
                .orElseThrow(() -> new ResourceNotFoundException("Destination account not found"));

        if (source.getId().equals(destination.getId())) {
            throw new BadRequestException("Cannot transfer to the same account");
        }

        if (!source.getCustomer().getId().equals(actorCustomerId) && !isAdmin(actorCustomerId)) {
            throw new BadRequestException("Not authorized for source account");
        }
        if (source.getStatus() != AccountStatus.ACTIVE || destination.getStatus() != AccountStatus.ACTIVE) {
            throw new AccountNotActiveException("One or both accounts are not active");
        }
        if (source.getBalance().compareTo(request.getAmount()) < 0) {
            throw new InsufficientBalanceException("Insufficient balance in source account");
        }

        String reference = "TXN-" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmssSSS"));

        // Debit source
        BigDecimal sourceBalanceAfter = source.getBalance().subtract(request.getAmount());
        source.setBalance(sourceBalanceAfter);

        Transaction debit = Transaction.builder()
                .transactionRef(reference)
                .type(TransactionType.TRANSFER_OUT)
                .amount(request.getAmount())
                .balanceAfter(sourceBalanceAfter)
                .description(request.getDescription() != null ? request.getDescription() : "Transfer to " + destination.getAccountNumber())
                .account(source)
                .relatedAccountId(destination.getId())
                .timestamp(LocalDateTime.now())
                .build();

        // Credit destination
        BigDecimal destBalanceAfter = destination.getBalance().add(request.getAmount());
        destination.setBalance(destBalanceAfter);

        Transaction credit = Transaction.builder()
                .transactionRef(reference)
                .type(TransactionType.TRANSFER_IN)
                .amount(request.getAmount())
                .balanceAfter(destBalanceAfter)
                .description(request.getDescription() != null ? request.getDescription() : "Transfer from " + source.getAccountNumber())
                .account(destination)
                .relatedAccountId(source.getId())
                .timestamp(LocalDateTime.now())
                .build();

        transactionRepository.save(debit);
        transactionRepository.save(credit);

        return TransferResponse.builder()
                .reference(reference)
                .sourceAccount(source.getAccountNumber())
                .destinationAccount(destination.getAccountNumber())
                .amount(request.getAmount())
                .timestamp(LocalDateTime.now())
                .build();
    }
}
```

**Important theory:** This method is `@Transactional`, so if saving either transaction fails, **both balances and both transactions roll back**.

---

## 14.5 Admin Operations

- `GET /api/admin/customers` — list all customers
- `GET /api/admin/accounts` — list all accounts
- `PUT /api/admin/accounts/{id}/freeze` — freeze account
- `PUT /api/admin/accounts/{id}/unfreeze`
- `GET /api/admin/audit-logs` — view audit logs

---

# 15. Testing (unit + integration)

## 15.1 Unit test (TransferService)
- Mock repositories
- Test insufficient balance, inactive account, same account, ownership

## 15.2 Integration test (TransferController)
- Use `@SpringBootTest` + `MockMvc`
- Seed test data
- Test full transfer flow with JWT

**Example skeleton**
```java
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
public class TransferControllerTest {

    @Autowired MockMvc mockMvc;
    @Autowired ObjectMapper objectMapper;

    @Test
    void transfer_success() throws Exception {
        // login, create accounts, transfer, verify transactions
    }
}
```

---

# 16. Logging, auditing, and observability

- Use `SLF4J` (`@Slf4j`)
- Create `AuditLog` on key actions (login, transfer, freeze)
- Add correlation IDs for tracing (optional but valuable)
- Use Spring Boot Actuator (optional)

---

# 17. Packaging, configuration profiles, and deployment

## 17.1 Build
- Maven: `mvn clean package`
- Jar: `target/bank-app-0.0.1-SNAPSHOT.jar`

## 17.2 Run
- Dev: `java -jar -Dspring.profiles.active=dev target/*.jar`
- Prod: `java -jar -Dspring.profiles.active=prod target/*.jar`

## 17.3 Docker (optional)
- Create `Dockerfile` + `docker-compose.yml` with Postgres

---

# 18. Common mistakes and best practices

1. **Don’t expose entities in responses** → use DTOs
2. **Don’t forget @Transactional for multi-step operations** (transfers)
3. **Never store plain passwords** → BCrypt
4. **Validate ownership** in service layer, not just controller
5. **Use BigDecimal for money** (avoid float/double)
6. **Write tests for transfer edge cases** (race conditions, balances, auth)
7. **Add idempotency keys** for payments/transfers in real systems

---

# 19. Final checklist (what “done” looks like)

- [ ] Customer register/login with JWT
- [ ] Account create/list/get
- [ ] Deposit/withdraw with transaction ledger
- [ ] Transfer between accounts with atomicity
- [ ] Transaction history with filters/pagination
- [ ] Admin freeze/unfreeze + audit logs
- [ ] Global exception handling + validation
- [ ] Unit + integration tests
- [ ] Profiles (dev H2 / prod Postgres)
- [ ] Swagger/OpenAPI docs (optional but recommended)

---

If you want, I can also generate **Postman collection JSON**, a **step-by-step IntelliJ run/debug guide**, or a **Docker + Postgres setup** with exact commands. Which do you want next?