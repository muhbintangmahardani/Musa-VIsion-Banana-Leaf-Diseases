@echo off
title MusaVision - Server HP Kebun Pisang
color 0A
echo =======================================================================
echo          MusaVision - Deteksi Penyakit Daun Pisang (Musa spp.)
echo                  Mode Online HTTPS untuk HP di Kebun
echo =======================================================================
echo.
echo [1/2] Menyiapkan server lokal dan terowongan HTTPS Ngrok...
echo.

python app.py --ngrok

pause
