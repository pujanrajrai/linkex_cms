# 📦 Django CMS - Dockerized Setup

This project is a **Django CMS** application containerized using **Docker & Docker Compose**. Below are essential commands for managing the application.

---

## 🚀 Getting Started

### **1️⃣ Build & Run Containers**
Use one of the following commands based on your needs:

#### 🔹 **Start Containers (Without Rebuilding)**
```sh
docker compose up
```

#### 🔹 **Start Containers (Force Rebuild)**
```sh
docker compose up --build
```

#### 🔹 **Start in Detached Mode (Background)**
```sh
docker compose up --build -d
```

#### 🔹 **Stop Containers**
```sh
docker compose down
```

#### 🔹 **Stop & Remove Volumes (⚠️ Deletes Database Data)**
```sh
docker compose down -v
```

---

## 🔍 Checking Running Containers

#### **List Active Containers**
```sh
docker ps
```

#### **List All Containers (Including Stopped Ones)**
```sh
docker ps -a
```

---

## 🛠️ Container Management

#### **Access a Running Container’s Shell**
```sh
docker exec -it container_name /bin/bash
```
For example:
```sh
docker exec -it cms_web /bin/bash
```

#### **View Logs of a Running Container**
```sh
docker logs container_name
```
Example:
```sh
docker logs cms_web
```

#### **Restart a Specific Container**
```sh
docker restart container_name
```

#### **Stop a Specific Container**
```sh
docker stop container_name
```

#### **Remove a Specific Container**
```sh
docker rm container_name
```

---

## 🛠️ Database Management (PostgreSQL)

#### **Connect to PostgreSQL Database Inside Docker**
```sh
docker exec -it cms_db psql -U cms_user -d cms_db
```

#### **Backup Database**
```sh
docker exec -t cms_db pg_dumpall -U cms_user > backup.sql
```

#### **Restore Database from Backup**
```sh
cat backup.sql | docker exec -i cms_db psql -U cms_user -d cms_db
```

---

## ⚡ Additional Commands

#### **Check Docker Compose Config**
```sh
docker compose config
```

#### **Prune Unused Docker Resources**
```sh
docker system prune -a
```

#### **Clean Up Unused Volumes (⚠️ Use with Caution)**
```sh
docker volume prune
```

#### **Rebuild and Restart a Specific Service**
```sh
docker compose up --build -d service_name
```
Example:
```sh
docker compose up --build -d cms_web
```

---

## 🔄 Django-Specific Commands

#### **Apply Database Migrations**
```sh
docker-compose exec cms_web python manage.py migrate
```

#### **Create a Superuser**
```sh
docker-compose exec cms_web python manage.py createsuperuser
```

#### **Collect Static Files**
```sh
docker-compose exec cms_web python manage.py collectstatic --noinput
```

---

## 🛡️ Notes
- Make sure Docker and Docker Compose are installed before running these commands.
- Replace `container_name` with the actual container name (e.g., `cms_web`, `cms_db`).
- Use `docker ps` to find the exact running container names.

---

### 🛠️ Developed with ❤️ using Django + Docker

# cms_backend
# cms_backend
# linkex_cms
