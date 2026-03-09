
  App dir    : /root/saruan
  Domain     : https://habarkita.com                                                          Admin      : https://habarkita.com/admin
  Log app    : /root/saruan/logs/error.log                                                    DB backup  : /root/saruan/data/undangan.db.backup (harian 03:00)
                                                                                              Cek status : sudo systemctl status habarkita
  Cek log    : journalctl -u habarkita -f                                                   
  Ganti password admin:                                                                       python3 -c "from app import hash_pw; print(hash_pw('passwordbaru'))"
  Lalu update ADMIN_PW_HASH di .env dan restart:                                              sudo systemctl restart habarkita
