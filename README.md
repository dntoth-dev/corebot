<div align="center">

# ⚙️ Core Bot

**An open-source, all-rounder application for any Discord community**

![License: AGPL v3.0](https://img.shields.io/badge/License-AGPL_v3.0-blue.svg)
![Version](https://img.shields.io/badge/Version-v0.1--stable-orange.svg)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Cloudflare](https://img.shields.io/badge/Cloudflare-Pages_Functions-F38020?logo=cloudflare&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3FCF8E?logo=supabase&logoColor=white)

[Features](#-key-features) • [Architecture](#%EF%B8%8F-tech-stack) • [Roadmap](#-roadmap) • [License](#-license) • [Support](#-issues--support)

• [Website](https://core-bot.pages.dev) •

---

</div>

## 📌 Introduction

Welcome to the official repository for **Core Bot**. Core is a multi-purpose, open-source Discord bot built to empower server staff with quick moderation GUI tools, automated anti-spam security, server insights, and engaging community utilities—all backed by a fast edge web dashboard.

The goal of this project is a Discord bot with many free-to-use commands, features and customisation, available and accessible for everyone through a modern web dashboard.

The project is under active development and regularly updated with new features and improvements.

---

## 🛡️ Key Features

* **🛡️ `/moderate` Dashboard:** An interactive GUI-driven moderation command designed for server staff to perform quick enforcement actions without memorizing complex syntax.
* **🚨 `/sentry` Defense System:** An automated, 24/7 server protection mechanism against spammers and self-bots using honeypot detection channels that softban unauthorized user-bots upon interaction.
* **⚙️ Dynamic Configuration:** Customizable guild preferences stored persistently in PostgreSQL.
* *(More features are being rolled out alongside major production releases.)*
---
## 🚧 Limitations

### ⚠️ The most recent commits are not implemented in the current website version.
Recent commits are for the new website version - still under maintenance - and lives under [https://v02a1.core-bot.pages.dev](https://v02a1.core-bot.pages.dev), which is not accessible to the public yet. The current [webpage](https://core-bot.pages.dev) is static, and features the essentials only, such as a Bot Invite Button, a Homepage, a Privacy-Policy and a Terms Of Service. **There is no dashboard in the current version!**

### ⚠️ User warnings can not be saved in the current version.
This feature will be included in a future update. It also means that moderation actions can not be logged at this time.

---
## 🛠️ Tech Stack

Core Bot combines a Python bot client with modern edge architecture:

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Bot Engine** | `Python` / `discord.py` | Handles real-time gateway events, commands, and moderation triggers. |
| **Edge Backend** | `Cloudflare Pages Functions` | Serverless REST API handlers for authentication and dashboard backend logic. |
| **Database** | `Supabase` | Persistent state, session data, and per-guild configuration using PostgreSQL and Row Level Security (RLS). |
| **Frontend** | `HTML5` / `Tailwind CSS` | Clean web management dashboard interfaced via Discord OAuth2. |

---

## 🚀 Roadmap & Project Status

Core Bot is currently on **`v0.1-stable`**. While the core infrastructure is active, public instance distribution is undergoing final testing, and the Discord OAuth2 authorisation is still under maintenance.

- [x] Core moderation commands (`/moderate`)
- [x] Automated honeypot anti-spam (`/sentry`)
- [x] Supabase database schema & configuration binding
- [ ] Cloudflare Pages Functions edge API pipeline
- [ ] Complete Discord OAuth2 login integration
- [ ] Interactive Web Dashboard UI (`manage.html`)
- [ ] Public invite link release & self-hosting documentation

---

## 📄 Privacy Policy & Data Handling

Core Bot respects user privacy and processes only the minimum data necessary to operate server features and session security. To learn how server and session data are managed, please read our [Privacy Policy](https://core-bot.pages.dev/privacy-policy).

---

## 📜 License

This project is open-source software licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

Under the terms of AGPL-3.0, any modified network-hosted version of this codebase must also make its source code publicly available under the same license. For full terms, please refer to the [`LICENSE`](./LICENSE) file in this repository.

---

## 💬 Issues & Support

If you discover a bug, security flaw, or operational error, reach out directly on Discord: **`@td.official`**
