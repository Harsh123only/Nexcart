# 🛒 NexCart — Full-Stack Headless E-Commerce & Email OTP Marketplace

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django REST](https://img.shields.io/badge/Django_6.1_&_DRF-092E20?style=for-the-badge&logo=django&logoColor=white)
![JWT Auth](https://img.shields.io/badge/JWT_&_Email_OTP-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![SQLite / MySQL](https://img.shields.io/badge/ACID_Transactions-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![JavaScript](https://img.shields.io/badge/Vanilla_JS_&_HTML5-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

**NexCart** is a full-stack, Amazon-inspired e-commerce marketplace featuring passwordless **6-digit Email OTP authentication**, **JWT session security**, live multi-filter catalog search, concurrency-safe checkout with row-level database inventory locking, multi-method payment processing, and a custom **Seller & Admin Command Center**.

![NexCart Storefront Preview](templates/storefront_preview.png)

---

## 🏗️ System Architecture

```mermaid
graph LR
    UI[Amazon-Style Storefront UI] -->|REST + Bearer JWT| API[Django REST Framework]
    Admin[Seller Admin Panel /admin] -->|Manage Catalog & Stock| DB[(Relational Database)]
    API -->|6-Digit OTP Verification| Mailer[Django 6.1 Mailer Engine]
    API -->|select_for_update Stock Lock| DB
    API -->|Order Confirmation Receipt| Mailer