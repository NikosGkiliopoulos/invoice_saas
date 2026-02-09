my_saas
 https://invoice-saas-85ff.onrender.com/auth/login?next=%2F
# 📊 Flask ERP & myDATA Invoicing System

Ένα ολοκληρωμένο σύστημα **Ηλεκτρονικής Τιμολόγησης και ERP** κατασκευασμένο με **Python & Flask**. Η εφαρμογή είναι πλήρως εναρμονισμένη με την Ελληνική Νομοθεσία και συνδέεται απευθείας με την πλατφόρμα **myDATA της ΑΑΔΕ** για την αποστολή παραστατικών.


<img width="1705" height="845" alt="Screenshot 2026-02-09 155940" src="https://github.com/user-attachments/assets/d0cf0300-d3e5-49f0-87d2-b82ce4e5b73c" />



## 🚀 Δυνατότητες

* **Dashboard:** Εποπτεία εσόδων, στατιστικά πωλήσεων και γραφήματα.
* **Διαχείριση Πελατών & Ειδών:** Πλήρες σύστημα καταχώρησης (CRUD) για πελάτες και προϊόντα/υπηρεσίες.
* **Έκδοση Παραστατικών:** * Τιμολόγια Πώλησης & Παροχής Υπηρεσιών.
    * Αποδείξεις Λιανικής.
    * Αυτόματος υπολογισμός ΦΠΑ και καθαρής αξίας.
* **🔌 Διασύνδεση myDATA (ΑΑΔΕ):**
    * Αυτόματη δημιουργία XML (myDATA v1.0.9).
    * Αποστολή παραστατικών σε Real-time.
    * Λήψη και αποθήκευση **MARK** και **UID**.
    * Υποστήριξη Development & Production περιβάλλοντος.
* **Εκτύπωση & PDF:** * Επαγγελματικό template σχεδιασμένο για χαρτί **A4**.
    * Δημιουργία **QR Code** (βάσει προδιαγραφών ΑΑΔΕ).
    * Υποστήριξη θερμικής εκτύπωσης (με προσαρμογή CSS).
* **Ασφάλεια:** Σύστημα Login/Register χρηστών και κρυπτογράφηση κωδικών.

## 🛠️ Τεχνολογίες

* **Backend:** Python 3, Flask, SQLAlchemy (ORM).
* **Database:** SQLite (Εύκολη μετάβαση σε PostgreSQL/MySQL).
* **Frontend:** HTML5, Jinja2, **Tailwind CSS** (για μοντέρνο UI).
* **APIs:** REST API (Requests) για επικοινωνία με ΑΑΔΕ.
* **Tools:** `qrcode`, `xml.etree` για parsing.

## 🔑 Ρυθμίσεις myDATA

1.  Κάντε Login στην εφαρμογή.
2.  Πηγαίνετε στις **Ρυθμίσεις (Settings)**.
3.  Συμπληρώστε τα στοιχεία της εταιρείας σας.
4.  Εισάγετε το **User ID** και το **Subscription Key** από το myDATA REST API (dev ή prod).

<img width="1600" height="849" alt="Screenshot 2026-02-09 160125" src="https://github.com/user-attachments/assets/f6637eaa-ef55-4012-a117-4a1f12f528d1" />
  

Aλλες εικονες:
<img width="1529" height="818" alt="Screenshot 2026-02-09 160000" src="https://github.com/user-attachments/assets/a24721c8-edb5-4fb6-b720-5965bf2edb88" />
<img width="1582" height="843" alt="Screenshot 2026-02-09 160041" src="https://github.com/user-attachments/assets/ff6e3dc1-1920-4d34-aa91-aa2a77ea0f13" />
<img width="1662" height="857" alt="Screenshot 2026-02-09 160104" src="https://github.com/user-attachments/assets/13346708-ee65-47f5-80e5-80139c2e2adb" />
<img width="1640" height="789" alt="Screenshot 2026-02-09 160305" src="https://github.com/user-attachments/assets/bffcf175-77bf-4312-85f4-7b47857655c1" />







